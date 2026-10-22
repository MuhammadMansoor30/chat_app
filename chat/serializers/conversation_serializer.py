from rest_framework import serializers
from chat.models import Conversation

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'

    def to_representation(self, instance):
        organization_name = instance.organization.full_name if instance.organization else None
        instance = super().to_representation(instance)
        instance['organization_name'] = organization_name
        
        return instance
