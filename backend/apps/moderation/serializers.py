from __future__ import annotations

from rest_framework import serializers

from apps.moderation.models import ModerationAction
from apps.roasts.serializers import ReportSerializer, RoastPostSerializer


class ModerationActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationAction
        fields = ["id", "target_user", "roast_post", "created_by", "action", "reason", "expires_at", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]


class ModerationQueueSerializer(serializers.Serializer):
    pending_posts = RoastPostSerializer(many=True)
    reported_posts = ReportSerializer(many=True)
