from rest_framework import serializers
from chat.models import Conversation

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'

    def to_representation(self, instance):
        organization_name = instance.organization.name if instance.organization else None
        last_message_by_name = instance.last_message_by.full_name if instance.last_message_by else None
        participants = instance.participants.all().values("id", "full_name")
        instance = super().to_representation(instance)
        instance['organization_name'] = organization_name
        instance['last_message_by_name'] = last_message_by_name
        instance['participants'] = participants
        
        return instance
