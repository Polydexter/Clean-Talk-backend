from django.db import close_old_connections
from rest_framework_simplejwt.token import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs


class TokenAuthMiddleware:
    """
    Custom token middleware for authenticating websocket
    connections with JWT.
    """
    pass
