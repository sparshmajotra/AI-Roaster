from __future__ import annotations

from django.contrib import admin

from apps.roasts.models import Bookmark, Comment, CommentVote, Reaction, Report, RoastPost


@admin.register(RoastPost)
class RoastPostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category", "roast_style", "status", "visibility", "ai_score", "heat_score", "created_at")
    list_filter = ("category", "roast_style", "status", "visibility", "is_anonymous")
    search_fields = ("user__username", "text_content", "ai_roast", "aura")
    readonly_fields = ("created_at", "updated_at", "heat_score")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "roast_post", "upvotes", "downvotes", "is_hidden", "created_at")
    list_filter = ("is_hidden",)
    search_fields = ("user__username", "content")


admin.site.register(Reaction)
admin.site.register(Bookmark)
admin.site.register(CommentVote)
admin.site.register(Report)
