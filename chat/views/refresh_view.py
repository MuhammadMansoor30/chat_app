from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from chat.util import set_access_cookies, set_refresh_cookies
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.conf import settings

class RefreshView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        response = Response()

        refresh_token = request.COOKIES.get('refresh_token', None)
        if not refresh_token:
            refresh_token = request.data.get('refresh_token', None)

        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST) 

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        set_access_cookies(response, str(refresh.access_token))

        if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
            if settings.SIMPLE_JWT['BLACKLIST_AFTER_ROTATION']:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            set_refresh_cookies(response, str(refresh))

        response.headers['random_value_1'] = refresh.access_token
        response.headers['random_value_2'] = refresh
        
        return response
