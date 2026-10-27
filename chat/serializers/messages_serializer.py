from rest_framework import serializers
from chat.models import Message
from minio import Minio
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):
        sender_name = instance.sender.full_name if instance.sender else None
        attachment = instance.attachment if instance.attachment else None
        instance = super().to_representation(instance)
        instance['sender_name'] = sender_name
        instance['attachment'] = self.fetch_attachments(attachment) if attachment else None
        return instance

    def fetch_attachments(self, filename):
        client = Minio(os.environ["BUCKET_HOST"],access_key=os.environ["BUCKET_KEY"],secret_key=os.environ["BUCKET_SECRET"])
        bucket_name = os.environ["BUCKET_NAME"]

        url = client.get_presigned_url(
            "GET",
            bucket_name,
            filename,
            expires=timedelta(minutes=5),
        )

        return url