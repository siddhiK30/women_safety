from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.room_name = f"location_updates_{self.user.id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def location_update(self, event):
        await self.send(text_data=json.dumps(event["message"]))
        
    async def sharing_stopped(self, event):
        await self.send(text_data=json.dumps(event["message"]))
