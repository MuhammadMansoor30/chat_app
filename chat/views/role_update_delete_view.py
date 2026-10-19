from chat.decorator import permission_required
from chat.serializers import RoleSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from chat.models import Role, Permission
from django.db import transaction
from datetime import datetime

class RoleDetailView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            raise Http404

    @permission_required(['role_read'])
    def get(self, request, pk, format=None):
        role = self.get_object(pk)
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @permission_required(['role_update'])
    def put(self, request, pk, format=None):
        try:
            data = request.data

            name = data.get('name', None)
            code_name = data.get('code_name', None)
            permissions_data = data.get('permissions', None)
            if self.request.user.is_staff:
                if not name or not code_name or not permissions_data:
                    return Response({'msg': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

                permissions_data = data.pop('permissions')

                with transaction.atomic():
                    role = self.get_object(pk)
                    role.name = name
                    role.code_name = code_name
                    role.permissions.clear()
                    role.updated_by = request.user
                    role.updated_at = datetime.now()
                    role.save()

                    for perm in permissions_data:
                        permission = Permission.objects.get(pk=perm['id'])
                        role.permissions.add(permission)

                return Response({'msg': 'Role updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg':'You do not have permission to perform this action'},  status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'msg': 'Server error'}, status=status.HTTP_400_BAD_REQUEST)

    @permission_required(['role_delete'])
    def delete(self, request, pk, format=None):
        role = self.get_object(pk)
        role.updated_by = request.user
        role.updated_at = datetime.now()
        role.delete()
        return Response({'msg': 'Role deleted successfully'}, status=status.HTTP_200_OK)