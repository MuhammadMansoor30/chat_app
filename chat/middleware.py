from http.cookies import SimpleCookie

from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

@database_sync_to_async
def get_user_from_token(raw_token):
    try:
        token = AccessToken(raw_token)
        user_id = token["user_id"]

        User = get_user_model()

        return User.objects.get(pk=user_id, deleted=False)

    except (TokenError, KeyError, TypeError, ValueError) as e:
        return AnonymousUser()

    except get_user_model().DoesNotExist as e:
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        headers = scope.get("query_string")
        raw_token = headers.decode("utf-8").split("=")[1]

        if raw_token:
            scope["user"] = await get_user_from_token(raw_token)
        else:
            scope["user"] = AnonymousUser()

        await self.app(scope, receive, send)