from chat.decorator import permission_required
from chat.serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chat.models import Message
from rest_framework.views import APIView
from django.http import Http404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class MessagesDetailView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return Message.objects.get(pk=pk)
        except:
            return Http404
    
    def get(self, request, pk, *args, **kwargs):
        message = self.get_object(pk)
        conversation_id = request.query_params.get("conversation_id", None)
        serializer = MessageSerializer(message)

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"conversation_{conversation_id}",
            {
                "type": "chat.message",
                "message": serializer.data
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @permission_required(['message_delete'])
    def delete(self, request, pk):
        message = self.get_object(pk)
        message.delete = True
        message.updated_by = request.user
        message.save()

        return Response({"msg": "Message Deleted Successfully"}, status=status.HTTP_200_OK)