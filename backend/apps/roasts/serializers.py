from __future__ import annotations

from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer
from apps.roasts.models import Bookmark, Comment, CommentVote, Reaction, Report, RoastPost


class FlexibleChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            normalized = data.strip()
            label_to_value = {str(label): value for value, label in self.choices.items()}
            if normalized in label_to_value:
                return label_to_value[normalized]
        return super().to_internal_value(data)


class RoastPostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = FlexibleChoiceField(choices=RoastPost.Category.choices)
    roast_style = FlexibleChoiceField(choices=RoastPost.RoastStyle.choices)
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    roast_style_label = serializers.CharField(source="get_roast_style_display", read_only=True)
    media_url = serializers.SerializerMethodField()
    media = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = RoastPost
        fields = [
            "id",
            "author",
            "category",
            "category_label",
            "roast_style",
            "roast_style_label",
            "media",
            "media_url",
            "source_url",
            "text_content",
            "ai_roast",
            "ai_score",
            "aura",
            "vibe_tags",
            "improvement_tips",
            "visibility",
            "is_anonymous",
            "status",
            "moderation_status",
            "reaction_count",
            "comment_count",
            "bookmark_count",
            "share_count",
            "heat_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "ai_roast",
            "ai_score",
            "aura",
            "vibe_tags",
            "improvement_tips",
            "status",
            "moderation_status",
            "reaction_count",
            "comment_count",
            "bookmark_count",
            "share_count",
            "heat_score",
            "created_at",
            "updated_at",
        ]

    def get_author(self, obj) -> dict:
        if obj.is_anonymous:
            return {
                "id": None,
                "username": "anonymous",
                "avatar": "",
                "bio": "",
                "xp": 0,
                "level": 0,
                "followers_count": 0,
                "created_at": obj.created_at.isoformat(),
            }
        return PublicUserSerializer(obj.user).data

    def get_media_url(self, obj) -> str:
        if obj.media_url:
            return obj.media_url
        if obj.media:
            request = self.context.get("request")
            url = obj.media.url
            return request.build_absolute_uri(url) if request else url
        return ""

    def validate(self, attrs):
        has_media = bool(attrs.get("media")) or bool(getattr(self.instance, "media", None))
        has_media_url = bool(attrs.get("media_url")) or bool(getattr(self.instance, "media_url", ""))
        has_text = bool(attrs.get("text_content")) or bool(getattr(self.instance, "text_content", ""))
        has_source = bool(attrs.get("source_url")) or bool(getattr(self.instance, "source_url", ""))

        if not any([has_media, has_media_url, has_text, has_source]):
            raise serializers.ValidationError("Add image, text, or source URL content before requesting a roast.")
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(source="user", read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "roast_post", "content", "upvotes", "downvotes", "score", "is_hidden", "created_at"]
        read_only_fields = ["id", "author", "roast_post", "upvotes", "downvotes", "score", "is_hidden", "created_at"]


class CommentVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentVote
        fields = ["id", "comment", "value", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["id", "roast_post", "emoji_type", "created_at"]
        read_only_fields = ["id", "created_at"]


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ["id", "roast_post", "created_at"]
        read_only_fields = ["id", "created_at"]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "roast_post", "reason", "details", "is_resolved", "created_at"]
        read_only_fields = ["id", "is_resolved", "created_at"]
