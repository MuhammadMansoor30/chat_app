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
from datetime import datetime, timedelta

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
        return Message.objects.filter(conversation = self.request.GET.get("conversation"), deleted=False).order_by("-created_at")

    @permission_required(['message_create'])
    def post(self, request, *args, **kwargs):
        sender_id = request.user.id
        recipients = request.data.get("recipients[]")
        conversation_id = request.data.get("conversation_id")
        group_name = request.data.get("group_name")
        message_ids = []
        urls = []

        if sender_id is None and len(recipients) == 0:
            return Response({"msg": "Please select a valid sender and recipient"}, status=status.HTTP_400_BAD_REQUEST)
        
        client = Minio(os.environ["BUCKET_HOST"],access_key=os.environ["BUCKET_KEY"],secret_key=os.environ["BUCKET_SECRET"])
        if request.data.get("type") == "file":
            for fil in request.data.getlist("content[]"):
                file_path = f"chat_app/{conversation_id}/{fil}"
                content_type, _ = mimetypes.guess_type(fil)

                url = client.presigned_put_object(os.environ["BUCKET_NAME"], file_path, expires=timedelta(hours=2))

                message = send_message_sync(sender_id, recipients, group_name, file_path, content_type, request.user, request.data) 
                serializer = MessageSerializer(message)

                urls.append(url)
                message_ids.append(serializer.data['id'])

            return Response({"message_id": message_ids, "urls": urls}, status=status.HTTP_201_CREATED)
        else:
            audio_file = request.data.get("content")

            file_name = f"Audio_{datetime.now()}" 
            file_path = f"chat_app/{conversation_id}/{file_name}"
            content_type = audio_file.content_type

            url = client.presigned_put_object(os.environ["BUCKET_NAME"], file_path, expires=timedelta(hours=2))

            message = send_message_sync(sender_id, recipients, group_name, file_path, content_type, request.user, request.data) 
            serializer = MessageSerializer(message)

            return Response({"message_id": serializer.data["id"], "urls": url}, status=status.HTTP_201_CREATED)
