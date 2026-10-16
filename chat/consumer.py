import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        # print(user)

        # if not user.is_authenticated:
        #     await self.close(code=4401)
        #     return

        await self.accept()
        await self.send(text_data=json.dumps({"message": "WebSocket Connected"}))
        # return await super().connect()

    async def receive(self, text_data = None, bytes_data = None, **kwargs):
        if text_data:
            await self.send(text_data=json.dumps({"message": text_data}))
        # return await super().receive(text_data, bytes_data, **kwargs)

    async def disconnect(self, code):
        pass
        # return await super().disconnect(code)