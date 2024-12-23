import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Add the user to the comments group
        await self.channel_layer.group_add("comments", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the comments group
        await self.channel_layer.group_discard("comments", self.channel_name)

    async def send_comment(self, event):
        # Send the comment to the WebSocket
        await self.send(
            text_data=json.dumps(
                {"content": event["content"], "timestamp": event["timestamp"]}
            )
        )
