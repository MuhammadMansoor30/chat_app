from chat.decorator import permission_required
from chat.serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chat.models import Message
from rest_framework.generics import ListAPIView
from chat.util import CustomPagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chat.util import send_message
from django.db import transaction
from datetime import datetime

class ConversationListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = MessageSerializer

    @permission_required(['message_read'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def get_queryset(self):
        return Message.objects.filter(conversation = self.request.GET.get("conversation"), deleted=False).order_by("-created_at")

    @permission_required(['messages_create'])
    def post(self, request, *args, **kwargs):
        sender_id = request.data.get("sender")
        recipient_id = request.data.get("recipient")
        content = request.data.get('content')

        if sender_id and recipient_id is None:
            return Response({"msg": "Please select a valid sender and recipient"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            message = send_message(sender_id, recipient_id, content, request.user)
            serializer = MessageSerializer(message)

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"conversation_{message.conversation.id}",
            {
                "type": "chat.message",
                "message": serializer.data,
            },
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)