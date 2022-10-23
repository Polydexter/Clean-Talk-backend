from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('<conversation_name>/', consumers.ChatConsumer.as_asgi()),
]