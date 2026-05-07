from __future__ import annotations

from django.conf import settings
from django.db import models


class RoastPost(models.Model):
    class Category(models.TextChoices):
        OUTFIT = "outfit", "Roast My Outfit"
        FACE = "face", "Roast My Face"
        SETUP = "setup", "Roast My Setup"
        RESUME = "resume", "Roast My Resume"
        DATING_PROFILE = "dating_profile", "Roast My Dating Profile"
        PORTFOLIO = "portfolio", "Roast My Portfolio"
        ROOM = "room", "Roast My Room"
        BIO = "bio", "Roast My Bio"

    class RoastStyle(models.TextChoices):
        FRIENDLY = "friendly", "Friendly Roast"
        BRUTAL = "brutal", "Brutal Roast"
        GEN_Z = "gen_z", "Gen Z Mode"
        CORPORATE = "corporate", "Corporate Reviewer"
        ANIME_VILLAIN = "anime_villain", "Anime Villain"
        THERAPIST = "therapist", "Therapist But Honest"
        BRITISH = "british", "British Insult Mode"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        FOLLOWERS = "followers", "Followers"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        REJECTED = "rejected", "Rejected"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roast_posts")
    category = models.CharField(max_length=32, choices=Category.choices)
    roast_style = models.CharField(max_length=32, choices=RoastStyle.choices, default=RoastStyle.FRIENDLY)
    media = models.ImageField(upload_to="roasts/%Y/%m/", blank=True, null=True)
    media_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    text_content = models.TextField(blank=True)
    ai_roast = models.TextField(blank=True)
    ai_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    aura = models.CharField(max_length=120, blank=True)
    vibe_tags = models.JSONField(default=list, blank=True)
    improvement_tips = models.JSONField(default=list, blank=True)
    visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.PUBLIC)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    moderation_status = models.JSONField(default=dict, blank=True)
    reaction_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    bookmark_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    heat_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "visibility", "-created_at"]),
            models.Index(fields=["category", "status", "-created_at"]),
            models.Index(fields=["-heat_score", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_category_display()} by {self.user_id}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roast_comments")
    roast_post = models.ForeignKey(RoastPost, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=600)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-upvotes", "-created_at"]
        indexes = [
            models.Index(fields=["roast_post", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    @property
    def score(self) -> int:
        return self.upvotes - self.downvotes

    def __str__(self) -> str:
        return f"Comment {self.pk} on {self.roast_post_id}"


class CommentVote(models.Model):
    class Vote(models.IntegerChoices):
        DOWN = -1, "Downvote"
        UP = 1, "Upvote"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_votes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes")
    value = models.SmallIntegerField(choices=Vote.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "comment"], name="unique_comment_vote"),
        ]


class Reaction(models.Model):
    class EmojiType(models.TextChoices):
        FIRE = "fire", "Fire"
        LAUGH = "laugh", "Laugh"
        WOW = "wow", "Wow"
        SPARKLES = "sparkles", "Sparkles"
        HELP = "helpful", "Helpful"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roast_reactions")
    roast_post = models.ForeignKey(RoastPost, on_delete=models.CASCADE, related_name="reactions")
    emoji_type = models.CharField(max_length=16, choices=EmojiType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "roast_post", "emoji_type"], name="unique_post_reaction"),
        ]


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    roast_post = models.ForeignKey(RoastPost, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "roast_post"], name="unique_bookmark"),
        ]


class Report(models.Model):
    class Reason(models.TextChoices):
        HARASSMENT = "harassment", "Harassment"
        HATE = "hate", "Hate or slurs"
        SEXUAL = "sexual", "Sexual content"
        VIOLENCE = "violence", "Violence"
        SPAM = "spam", "Spam"
        OTHER = "other", "Other"

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_made")
    roast_post = models.ForeignKey(RoastPost, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=24, choices=Reason.choices)
    details = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["is_resolved", "-created_at"])]
