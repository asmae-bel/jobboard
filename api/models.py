
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

class Employer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile",
    )
    company_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    logo = models.ImageField(upload_to="employer_logos/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class Candidate(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )
    phone = models.CharField(max_length=20, blank=True)
    headline = models.CharField(max_length=200, blank=True, help_text="e.g. 'Frontend Developer'")
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated list of skills")
    location = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def skills_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]


class Resume(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="resumes/%Y/%m/")
    is_default = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.candidate} - {self.title}"


# ---------------------------------------------------------------------------
# Job listings
# ---------------------------------------------------------------------------

class JobListing(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"
        REMOTE = "remote", "Remote"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        DRAFT = "draft", "Draft"

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="job_listings")
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=150)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    deadline = models.DateField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["status", "posted_at"]),
            models.Index(fields=["location"]),
            models.Index(fields=["category"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(salary_max__isnull=True)
                | models.Q(salary_min__isnull=True)
                | models.Q(salary_max__gte=models.F("salary_min")),
                name="salary_max_gte_salary_min",
            ),
        ]

    def __str__(self):
        return f"{self.title} @ {self.employer.company_name}"


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

class Application(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        HIRED = "hired", "Hired"

    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    resume = models.ForeignKey(Resume, on_delete=models.PROTECT, related_name="applications")
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ("job", "candidate")
        indexes = [
            models.Index(fields=["job", "status"]),
            models.Index(fields=["candidate", "applied_at"]),
        ]

    def __str__(self):
        return f"{self.candidate} -> {self.job} ({self.status})"


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        APPLICATION_RECEIVED = "application_received", "Application Received"
        STATUS_UPDATE = "status_update", "Status Update"
        SYSTEM = "system", "System"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.message[:50]}"

# Create your models here.
