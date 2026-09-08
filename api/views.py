from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Application, Candidate, Employer, JobListing, Notification, Resume
from .serializers import (
    ApplicationSerializer,
    ApplicationStatusUpdateSerializer,
    CandidateSignupSerializer,
    EmailTokenObtainPairSerializer,
    EmployerSignupSerializer,
    JobListingSerializer,
    NotificationSerializer,
    ResumeSerializer,
)


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "employer_profile")


class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "candidate_profile")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def employer_signup(request):
    serializer = EmployerSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    employer = serializer.save()
    refresh = RefreshToken.for_user(employer.user)
    return Response(
        {
            "message": "Employer account created.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "employer": {"id": employer.id, "company_name": employer.company_name, "email": employer.user.email},
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def candidate_signup(request):
    serializer = CandidateSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    candidate = serializer.save()
    refresh = RefreshToken.for_user(candidate.user)
    return Response(
        {
            "message": "Candidate account created.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "candidate": {
                "id": candidate.id,
                "full_name": candidate.user.get_full_name(),
                "email": candidate.user.email,
            },
        },
        status=status.HTTP_201_CREATED,
    )


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


# ---------------------------------------------------------------------------
# Job listings
# ---------------------------------------------------------------------------

class JobListingListCreateView(generics.ListCreateAPIView):
    serializer_class = JobListingSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsEmployer()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = JobListing.objects.filter(status=JobListing.Status.OPEN).select_related("employer")

        title = self.request.query_params.get("title")
        location = self.request.query_params.get("location")
        job_type = self.request.query_params.get("job_type")
        category = self.request.query_params.get("category")
        salary_min = self.request.query_params.get("salary_min")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if salary_min:
            queryset = queryset.filter(salary_min__gte=salary_min)

        return queryset


class JobListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobListingSerializer
    queryset = JobListing.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsEmployer()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method not in permissions.SAFE_METHODS and obj.employer.user_id != request.user.id:
            self.permission_denied(request, message="You can only manage your own job listings.")


class MyJobListingsView(generics.ListAPIView):
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_queryset(self):
        return JobListing.objects.filter(employer=self.request.user.employer_profile)


# ---------------------------------------------------------------------------
# Resumes
# ---------------------------------------------------------------------------

class ResumeListCreateView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user.candidate_profile)


class ResumeDeleteView(generics.DestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user.candidate_profile)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

class ApplyToJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def perform_create(self, serializer):
        application = serializer.save()
        Notification.objects.create(
            user=application.job.employer.user,
            notification_type=Notification.NotificationType.APPLICATION_RECEIVED,
            message=f"{application.candidate} applied to {application.job.title}",
            link=f"/jobs/{application.job.id}/applications/",
        )


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user.candidate_profile).select_related("job", "resume")


class JobApplicationsView(generics.ListAPIView):
    """Employer view: list all applications for one of their own job listings."""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_queryset(self):
        job_id = self.kwargs["job_id"]
        job = JobListing.objects.filter(id=job_id, employer=self.request.user.employer_profile).first()
        if job is None:
            return Application.objects.none()
        return Application.objects.filter(job=job).select_related("candidate", "resume")


class UpdateApplicationStatusView(generics.UpdateAPIView):
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsEmployer]
    queryset = Application.objects.all()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if obj.job.employer.user_id != request.user.id:
            self.permission_denied(request, message="You can only manage applications for your own job listings.")

    def perform_update(self, serializer):
        application = serializer.save()
        Notification.objects.create(
            user=application.candidate.user,
            notification_type=Notification.NotificationType.STATUS_UPDATE,
            message=f"Your application to {application.job.title} is now '{application.get_status_display()}'",
            link=f"/applications/{application.id}/",
        )


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    notification = Notification.objects.filter(id=pk, user=request.user).first()
    if notification is None:
        return Response({"message": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
    notification.is_read = True
    notification.save()
    return Response({"message": "Marked as read."}, status=status.HTTP_200_OK)

# Create your views here.
