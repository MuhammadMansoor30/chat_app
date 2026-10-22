from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat.permissions import LoggingHasAPIKey
from chat.models import User
from chat.serializers import UserSerializer, RoleLoginSerializer
from django.contrib.auth import authenticate
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from chat.util import get_tokens_for_user, set_access_cookies, set_refresh_cookies, get_permissions_from_roles
import requests, os, json

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (LoggingHasAPIKey,)

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user = User.objects.get(username=data['username'])
            if user.type == User.MAIN_APP_USER:  
                res = requests.post(url=os.getenv("APP_LOGIN_URL"), data=json.dumps(data), headers={"Content-Type": "application/json"})
                if res.status_code == 200:
                    user.set_password(data.get("password"))
                    user.save()
                else:
                    return Response({"msg": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            res = requests.post(url=os.getenv("APP_LOGIN_URL"), data=json.dumps(data), headers={"Content-Type": "application/json"})
            if res.status_code == 200:
                res_data = res.json()

                user = User.objects.create(username=res_data['username'], cnic=res_data['cnic'], first_name=res_data['first_name'], last_name=res_data['last_name'], mobile=res_data['mobile'], gender=res_data['gender'], type=User.MAIN_APP_USER)

                user.set_password(data.get("password"))
                user.save()

        authenticated_user = authenticate(username=data.get('username'), password=data.get('password'))
        if authenticated_user.deleted:
            return Response({"msg": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

        authenticated_user.last_login = datetime.now()
        response = Response()
        tokens = get_tokens_for_user(authenticated_user)

        # Add cookies if its web app else go for headers
        set_access_cookies(response, tokens['access'])
        set_refresh_cookies(response, tokens['refresh'])

        serializer = UserSerializer(authenticated_user)
        data = serializer.data

        roles = user.roles.all()
        permissions = get_permissions_from_roles(roles)

        data['roles'] = RoleLoginSerializer(roles, many=True).data
        data['permissions'] = permissions

        response.status_code = status.HTTP_200_OK
        response.headers['random_value_1'] = tokens['access']
        response.headers['random_value_2'] = tokens['refresh']
        
        response.data = {"msg": "Login Successful", "user": data}

        return response