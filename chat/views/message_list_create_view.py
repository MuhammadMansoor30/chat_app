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
from chat.util import send_message_sync
from minio import Minio
from minio.error import S3Error
from pathlib import Path
from dotenv import load_dotenv
import os, mimetypes

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

class MessageListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = MessageSerializer

    @permission_required(['message_read'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def get_queryset(self):
        return Message.objects.filter(conversation = self.request.GET.get("conversation"), deleted=False).order_by("created_at")

    @permission_required(['message_create'])
    def post(self, request, *args, **kwargs):
        
        for fil in request.data.getlist("content[]"):
            sender_id = request.user.id
            recipient_id = request.data.get("recipient_id")

            if sender_id and recipient_id is None:
                return Response({"msg": "Please select a valid sender and recipient"}, status=status.HTTP_400_BAD_REQUEST)

            file_path = f"test_pdf/{fil.name}"
            content_type, _ = mimetypes.guess_type(fil.name)

            # if not content_type:
            #     content_type = 'application/octet-stream'     
            # try:
            #     client = Minio(os.environ("BUCKET_HOST"),access_key=os.environ("BUCKET_KEY"),secret_key=os.environ("BUCKET_SECRET"))
            #     bucket_name = os.environ("BUCKET_NAME")
    
            #     client.put_object(bucket_name = bucket_name, object_name = file_path , data = fil, length = fil.size, content_type=content_type)
            # except S3Error as e:
            #     print(e)

            message = send_message_sync(sender_id, recipient_id, file_path, content_type, request.user, request.data) 
            serializer = MessageSerializer(message)

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f"user_{sender_id}",
                {
                    "type": "chat.message",
                    "message": serializer.data,
                },
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)