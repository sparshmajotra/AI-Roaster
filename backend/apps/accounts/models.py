from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.URLField(blank=True)
    bio = models.CharField(max_length=240, blank=True)
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_edges")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_edges")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow_edge"),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="prevent_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["follower", "created_at"]),
            models.Index(fields=["following", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.follower_id} -> {self.following_id}"
