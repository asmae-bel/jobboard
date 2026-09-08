from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Application, Candidate, Employer, JobListing, Notification, Resume

User = get_user_model()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class EmployerSignupSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    website = serializers.URLField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["company_name"],
        )
        return Employer.objects.create(
            user=user,
            company_name=validated_data["company_name"],
            website=validated_data.get("website", ""),
            location=validated_data.get("location", ""),
        )


class CandidateSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    phone = serializers.CharField(required=False, allow_blank=True)
    headline = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        full_name = validated_data["full_name"].strip()
        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
        )
        return Candidate.objects.create(
            user=user,
            phone=validated_data.get("phone", ""),
            headline=validated_data.get("headline", ""),
            skills=validated_data.get("skills", ""),
            location=validated_data.get("location", ""),
        )


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        user = authenticate(username=user_obj.username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        refresh = self.get_token(user)

        role = "employer" if hasattr(user, "employer_profile") else "candidate" if hasattr(user, "candidate_profile") else None

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": role,
        }


# ---------------------------------------------------------------------------
# Job listings
# ---------------------------------------------------------------------------

class JobListingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="employer.company_name", read_only=True)
    applications_count = serializers.IntegerField(source="applications.count", read_only=True)

    class Meta:
        model = JobListing
        fields = [
            "id", "title", "description", "category", "location", "job_type",
            "salary_min", "salary_max", "status", "deadline", "posted_at",
            "updated_at", "company_name", "applications_count",
        ]
        read_only_fields = ["id", "posted_at", "updated_at", "company_name", "applications_count"]

    def validate(self, attrs):
        salary_min = attrs.get("salary_min", getattr(self.instance, "salary_min", None))
        salary_max = attrs.get("salary_max", getattr(self.instance, "salary_max", None))
        if salary_min is not None and salary_max is not None and salary_max < salary_min:
            raise serializers.ValidationError("salary_max cannot be less than salary_min.")
        return attrs

    def create(self, validated_data):
        employer = self.context["request"].user.employer_profile
        return JobListing.objects.create(employer=employer, **validated_data)


# ---------------------------------------------------------------------------
# Resumes
# ---------------------------------------------------------------------------

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ["id", "title", "file", "is_default", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]

    def create(self, validated_data):
        candidate = self.context["request"].user.candidate_profile
        return Resume.objects.create(candidate=candidate, **validated_data)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source="candidate.user.get_full_name", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    resume_file = serializers.FileField(source="resume.file", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id", "job", "job_title", "candidate_name", "resume", "resume_file",
            "cover_letter", "status", "applied_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "applied_at", "updated_at", "job_title", "candidate_name", "resume_file"]

    def validate_job(self, value):
        if value.status != JobListing.Status.OPEN:
            raise serializers.ValidationError("This job is not currently accepting applications.")
        return value

    def validate_resume(self, value):
        request = self.context["request"]
        if value.candidate.user_id != request.user.id:
            raise serializers.ValidationError("You can only apply using your own resume.")
        return value

    def create(self, validated_data):
        candidate = self.context["request"].user.candidate_profile
        job = validated_data["job"]
        if Application.objects.filter(job=job, candidate=candidate).exists():
            raise serializers.ValidationError("You have already applied to this job.")
        return Application.objects.create(candidate=candidate, **validated_data)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status"]


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "notification_type", "message", "link", "is_read", "created_at"]
        read_only_fields = fields