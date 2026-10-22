from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from chat.serializers import UserSerializer, RoleLoginSerializer
from chat.util import get_tokens_for_user, get_permissions_from_roles
from chat.models import User

class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        roles = request.user.roles.all()
        permissions = get_permissions_from_roles(roles)
        roles_data = RoleLoginSerializer(roles, many=True).data

        data = UserSerializer(request.user, context={'request': request}).data
        user = User.objects.get(id = data['id'])
        tokens = get_tokens_for_user(user)
        data['roles'] = roles_data
        data['permissions'] = permissions

        response = Response()
        response.headers['random_value_1'] = tokens['access']
        response.headers['random_value_2'] = tokens['refresh']

        response.data = {"user": data}
        response.status_code = status.HTTP_200_OK
        return response

