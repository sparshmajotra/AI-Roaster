from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


def notification_group(user_id: int) -> str:
    return f"notifications_{user_id}"


def create_notification(*, user, type: str, message: str, actor=None, reference_id: object = "") -> Notification:
    notification = Notification.objects.create(
        user=user,
        actor=actor,
        type=type,
        message=message[:240],
        reference_id=str(reference_id or ""),
    )
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            notification_group(user.pk),
            {
                "type": "notification.created",
                "payload": NotificationSerializer(notification).data,
            },
        )
    return notification
