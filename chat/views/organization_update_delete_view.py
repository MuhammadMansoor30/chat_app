from chat.decorator import permission_required
from chat.serializers import OrganizationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chat.models import Organization
from rest_framework.views import APIView
from django.http import Http404
from datetime import datetime

class OrganizationDetailView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return Organization.objects.get(pk=pk)
        except:
            return Http404
    
    def get(self, request, pk, *args, **kwargs):
        organization = self.get_objects(pk)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @permission_required(['organization_update'])
    def put(self, request, pk, *args, **kwargs):
        organization = self.get_objects(pk)
        serializer = self.serializer_class(organization, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user, updated_at=datetime.now())
            return Response({"msg": "Organization Updated Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
    
    @permission_required(['organization_delete'])
    def delete(self, request, pk, *args, **kwargs):
        organization = self.get_objects(pk)
        organization.updated_by = request.user
        organization.delete()

        return Response({"msg": "Organization Deleted Successfully"}, status=status.HTTP_200_OK)
    
