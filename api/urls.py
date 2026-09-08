from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ApplyToJobView,
    EmailTokenObtainPairView,
    JobApplicationsView,
    JobListingDetailView,
    JobListingListCreateView,
    MyApplicationsView,
    MyJobListingsView,
    NotificationListView,
    ResumeDeleteView,
    ResumeListCreateView,
    UpdateApplicationStatusView,
    candidate_signup,
    employer_signup,
    mark_notification_read,
)

urlpatterns = [
    # Auth
    path("employers/signup/", employer_signup, name="employer_signup"),
    path("candidates/signup/", candidate_signup, name="candidate_signup"),
    path("login/", EmailTokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_refresh"),

    # Job listings
    path("jobs/", JobListingListCreateView.as_view(), name="job_list_create"),
    path("jobs/<int:pk>/", JobListingDetailView.as_view(), name="job_detail"),
    path("jobs/mine/", MyJobListingsView.as_view(), name="my_job_listings"),

    # Resumes
    path("resumes/", ResumeListCreateView.as_view(), name="resume_list_create"),
    path("resumes/<int:pk>/", ResumeDeleteView.as_view(), name="resume_delete"),

    # Applications
    path("applications/apply/", ApplyToJobView.as_view(), name="apply_to_job"),
    path("applications/mine/", MyApplicationsView.as_view(), name="my_applications"),
    path("jobs/<int:job_id>/applications/", JobApplicationsView.as_view(), name="job_applications"),
    path("applications/<int:pk>/status/", UpdateApplicationStatusView.as_view(), name="update_application_status"),

    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notification_list"),
    path("notifications/<int:pk>/read/", mark_notification_read, name="mark_notification_read"),
]