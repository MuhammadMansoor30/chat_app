import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from chat.models import User
from chat.util import send_message
from chat.serializers import MessageSerializer
import traceback

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Each user receives messages through their own group.
        self.user_group = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name,
        )

        await self.accept()
        # await self.send(text_data=json.dumps({"message": "WebSocket Connected"}))

    async def disconnect(self, close_code):
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name,
            )

    # runs whenever the frontend sends a JSON message.
    async def receive_json(self, data, **kwargs):
        try:
            # Check and update according to my flow
            message = await send_message(self.user.id, data["recipient_id"], data["content"], "text", self.user, data)

            # Notify the sender and recipient.
            for user_id in {message.sender.id, int(data["recipient_id"])}:
                await self.channel_layer.group_send(
                    f"user_{user_id}",
                    {
                        "type": "chat.message",  # executes chat_message func
                        "message": MessageSerializer(message).data,
                    },
                )

        except (KeyError, ValueError, TypeError) as e:
            print(traceback.format_exc())
            await self.send_json({
                "type": "error",
                "detail": "Invalid recipient or message content.",
            })
        except User.DoesNotExist:
            await self.send_json({
                "type": "error",
                "detail": "Recipient not found.",
            })

    # A custom event handler that is defined to deliver messages received through Channels.
    async def chat_message(self, event):
        await self.send_json({
            "type": "message",
            "message": event["message"],
        })


# Old 
# class ChatConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         user = self.scope['user']
#         # print(user)

#         # if not user.is_authenticated:
#         #     await self.close(code=4401)
#         #     return

#         await self.accept()
#         await self.send(text_data=json.dumps({"message": "WebSocket Connected"}))
#         # return await super().connect()

#     async def receive(self, text_data = None, bytes_data = None, **kwargs):
#         if text_data:
#             await self.send(text_data=json.dumps({"message": text_data}))
#         # return await super().receive(text_data, bytes_data, **kwargs)

#     async def disconnect(self, code):
#         pass
#         # return await super().disconnect(code)
