import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ProfileConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_status",
            "status": event["status"],
            "message": event["message"],
            "title": event.get("title"),
            "notification_id": event.get("notification_id"),
            "timestamp": event.get("timestamp"),
        }))
