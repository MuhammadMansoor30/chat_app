from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status
from chat.util import unset_cookies


class LogoutView(APIView):
    # permission_classes = (IsAuthenticated, )
    permission_classes = ()

    def post(self, request):
        data = request.COOKIES
        if not data:
            data = request.data

        try:
            RefreshToken(data.get('refresh_token')).blacklist()
        except TokenError as e:
            return Response({'msg': "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST)

        response = Response()
        unset_cookies(response)

        response.status_code = status.HTTP_204_NO_CONTENT

        return response