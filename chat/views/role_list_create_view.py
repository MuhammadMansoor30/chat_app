from chat.decorator import permission_required
from chat.serializers import RoleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chat.models import Role, Permission
from django.db import transaction
from rest_framework.generics import ListAPIView
from chat.util import CustomPagination
from chat.filters import RoleFilter

class RoleListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = RoleSerializer
    filterset_class = RoleFilter

    @permission_required(['role_read'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        

    def get_queryset(self):
        if self.request.user.id == 1:
            return Role.objects.filter(deleted=False).exclude(id__in=[1])
        
        self_roles = self.request.user.roles.all()
        return Role.objects.filter(deleted=False).exclude(id__in=self_roles).order_by('-id')

    @permission_required(['role_create'])
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            name = data.get('name', None)
            code_name = data.get('code_name', None)
            permission_data = data.get('permissions', None)
            if self.request.user.is_staff:
                if not name or not code_name or permission_data is None:
                    return Response({'msg': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

                permissions_data = data.pop('permissions')

                with transaction.atomic():
                    role = Role(**data)
                    role.save()

                    for perm in permissions_data:
                        permission = Permission.objects.get(pk=perm['id'])
                        role.permissions.add(permission)

                    role.created_by = request.user
                    role.save()

                return Response({'msg': 'Role created successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg':'You do not have permission to perform this action'},  status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': 'Server error'}, status=status.HTTP_400_BAD_REQUEST)
