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

        return User.objects.get(pk=user_id, is_active=True)

    except (TokenError, KeyError, TypeError, ValueError):
        return AnonymousUser()

    except get_user_model().DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope = dict(scope)

        headers = dict(scope.get("headers", []))
        raw_token = None

        authorization = headers.get(b"authorization", b"").decode("latin1")

        parts = authorization.split()

        if len(parts) == 2 and parts[0].lower() == "bearer":
            raw_token = parts[1]

        if not raw_token:
            cookie_header = headers.get(b"cookie", b"").decode("latin1")

            cookies = SimpleCookie()
            cookies.load(cookie_header)

            cookie_name = settings.SIMPLE_JWT.get("AUTH_ACCESS_COOKIE")

            if cookie_name:
                cookie = cookies.get(cookie_name)

                if cookie:
                    raw_token = cookie.value

        if raw_token:
            scope["user"] = await get_user_from_token(raw_token)
        else:
            scope["user"] = AnonymousUser()

        await self.app(scope, receive, send)