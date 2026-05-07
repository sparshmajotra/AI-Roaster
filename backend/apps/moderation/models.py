from __future__ import annotations

from django.conf import settings
from django.db import models


class ModerationAction(models.Model):
    class Action(models.TextChoices):
        WARN = "warn", "Warn"
        HIDE_POST = "hide_post", "Hide post"
        TEMP_BAN = "temp_ban", "Temporary ban"
        SHADOW_BAN = "shadow_ban", "Shadow ban"
        RESTORE = "restore", "Restore"

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moderation_actions",
        null=True,
        blank=True,
    )
    roast_post = models.ForeignKey(
        "roasts.RoastPost",
        on_delete=models.CASCADE,
        related_name="moderation_actions",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    action = models.CharField(max_length=24, choices=Action.choices)
    reason = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["action", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.action} at {self.created_at:%Y-%m-%d}"
