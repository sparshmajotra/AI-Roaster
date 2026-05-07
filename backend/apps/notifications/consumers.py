from __future__ import annotations

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.notifications.services import notification_group


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        requested_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])

        if not user or not user.is_authenticated or user.id != requested_user_id:
            await self.close(code=4401)
            return

        self.group_name = notification_group(user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_created(self, event):
        await self.send_json(event["payload"])
