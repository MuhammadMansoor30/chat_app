from rest_framework import serializers
from chat.models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):
        sender_name = instance.sender.full_name if instance.sender else None
        receiver_name = instance.conversation.receiver.full_name if instance.conversation.receiver else None
        instance = super().to_representation(instance)
        instance['sender_name'] = sender_name
        instance['receiver_name'] = receiver_name
        
        return instance
