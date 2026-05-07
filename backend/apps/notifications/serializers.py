from __future__ import annotations

from rest_framework import serializers

from apps.accounts.serializers import PublicUserSerializer
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = PublicUserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "actor", "type", "reference_id", "message", "is_read", "created_at"]
        read_only_fields = fields
