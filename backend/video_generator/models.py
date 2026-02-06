from django.db import models
import uuid


class VideoJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song_title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    progress = models.IntegerField(default=0)
    message = models.TextField(blank=True, null=True)
    video_file = models.CharField(max_length=500, blank=True, null=True)
    segments = models.JSONField(default=list, blank=True)  # Store segment data (lyrics, image, video)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)  # Flag to signal cancellation

    def __str__(self):
        return f"{self.song_title} - {self.status}"
