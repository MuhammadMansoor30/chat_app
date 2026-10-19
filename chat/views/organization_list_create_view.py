from chat.decorator import permission_required
from chat.serializers import OrganizationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chat.models import Organization
from rest_framework.generics import ListAPIView
from chat.util import CustomPagination
from chat.filters import OrganizationFilter
from datetime import datetime

class OrganizationListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter

    @permission_required(['organization_read'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        

    def get_queryset(self):
        if self.request.user.id == 1:
            return Organization.objects.filter(deleted=False)
        
        return Organization.objects.filter(id= self.request.user.organization.id, deleted=False)

    @permission_required(['organization_create'])
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user, updated_at=datetime.now())
            return Response({"msg": "Organization Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
    
