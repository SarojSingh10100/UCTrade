from django.db import models


class Video(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/', null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_trial = models.BooleanField(default=False, help_text="Whether this video is available for trial viewing")
    trial_duration = models.PositiveIntegerField(default=300, help_text="Trial duration in seconds (default 5 minutes)")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('enrolled', 'Enrolled Users Only'),
            ('premium', 'Premium Users Only')
        ],
        default='enrolled',
        help_text="Who can access this video"
    )

    def __str__(self):
        return f"{self.title} ({'Trial' if self.is_trial else 'Full'})"
