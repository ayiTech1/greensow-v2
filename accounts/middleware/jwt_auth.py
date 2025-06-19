# yourapp/middleware/jwt_auth.py

from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
import jwt
from django.conf import settings

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token['user_id']
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = parse_qs(query_string).get("token", [None])[0]

        if token is None:
            scope["user"] = AnonymousUser()
            return await super().__call__(scope, receive, send)

        try:
            validated = UntypedToken(token)
            scope["user"] = await get_user(validated)
        except (InvalidToken, jwt.DecodeError):
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
