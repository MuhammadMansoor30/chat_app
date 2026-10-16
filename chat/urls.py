from django.urls import path
from chat.consumer import ChatConsumer

urlpatterns = [

]

websocket_pattern = [
    path("ws/chat/", ChatConsumer.as_asgi()),
]
