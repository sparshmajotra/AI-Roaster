from __future__ import annotations

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        LIKE = "like", "Like"
        COMMENT = "comment", "Comment"
        FOLLOW = "follow", "Follow"
        ROAST_COMPLETE = "roast_complete", "Roast complete"
        ACHIEVEMENT = "achievement", "Achievement"
        MODERATION = "moderation", "Moderation"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_sent",
    )
    type = models.CharField(max_length=32, choices=Type.choices)
    reference_id = models.CharField(max_length=64, blank=True)
    message = models.CharField(max_length=240)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["type", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.type} for {self.user_id}"
