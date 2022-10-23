from django.db import close_old_connections
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs


@database_sync_to_async
def get_user(token):
    """
    Gets user from database and avoids conflict with asynchronous code
    """
    from django.contrib.auth.models import AnonymousUser

    try:
        # This will raise an error if token is not valid
        UntypedToken(token)
        # Decode validated token
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = get_user_model().objects.get(id=decoded_data['user_id'])
    except (InvalidToken, TokenError) as error:
        print(error)
    
    return user or AnonymousUser


class TokenAuthMiddleware:
    """
    Custom token middleware for authenticating websocket
    connections with JWT.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        
        # Prevent usage of timed out connections
        close_old_connections()

        # Get the token
        token = parse_qs(scope["query_string"].decode('utf8'))['token'][0]

        # Try to authenticate

        # Get user id
        user = await get_user(token)
        scope['token'] = token
        scope['user'] = user

        # Return the inner application
        return await self.app(scope, receive, send)
