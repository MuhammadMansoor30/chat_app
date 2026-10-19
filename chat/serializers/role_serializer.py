from rest_framework import serializers
from chat.models import Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ('created_at', 'created_by', 'updated_at', 'updated_by', 'deleted')
