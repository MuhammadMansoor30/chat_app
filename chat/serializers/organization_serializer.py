from rest_framework import serializers
from chat.models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


    def to_representation(self, instance):
        created_by_name = instance.created_by.full_name if instance.created_by else None
        updated_by_name = instance.updated_by.full_name if instance.updated_by else None
        instance = super().to_representation(instance)
        instance['created_by_name'] = created_by_name
        instance['updated_by_name'] = updated_by_name
        
        return instance
