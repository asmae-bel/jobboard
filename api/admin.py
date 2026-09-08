from django.contrib import admin


from .models import Application, Candidate, Employer, JobListing, Notification, Resume

admin.site.register(Employer)
admin.site.register(Candidate)
admin.site.register(Resume)
admin.site.register(JobListing)
admin.site.register(Application)
admin.site.register(Notification)

# Register your models here.
