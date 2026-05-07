from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import Follow, User


@admin.register(User)
class RoastlyUserAdmin(UserAdmin):
    list_display = ("username", "email", "level", "xp", "followers_count", "is_private", "is_staff")
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets + (
        ("Roastly profile", {"fields": ("avatar", "bio", "xp", "level", "followers_count", "following_count", "is_private")}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
