from rest_framework import serializers
from chat.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        exclude = ('last_login', 'created_by', 'updated_by', 'created_at', 'updated_at', 'deleted', 'is_staff',)

    def to_representation(self, instance):
        organization_name = instance.organization.name if instance.organization else None
        
        instance = super().to_representation(instance)
        instance['organization_name'] = organization_name
        
        return instance
