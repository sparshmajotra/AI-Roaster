from __future__ import annotations

from django.contrib import admin

from apps.moderation.models import ModerationAction


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "target_user", "roast_post", "created_by", "expires_at", "created_at")
    list_filter = ("action",)
    search_fields = ("target_user__username", "reason")
