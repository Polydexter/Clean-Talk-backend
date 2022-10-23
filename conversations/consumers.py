from email import message
import json
from select import select
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from conversations.models import Conversation

class ChatConsumer(JsonWebsocketConsumer):
    """
    TODO: description
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_name = None
        self.conversation = None

    def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            return
        else:
            print(f"Hello, {self.user.username}!")
        self.accept()
        self.conversation_name = f"{self.scope['url_route']['kwargs']['conversation_name']}"
        self.conversation = Conversation.objects.get_or_create(name=self.conversation_name)
        async_to_sync(self.channel_layer.group_add)(
            self.conversation_name,
            self.channel_name,
        )
    
    def disconnect(self, close_code):
        print('Bye, client!')
        return super().disconnect(close_code)
        
    # Receive message from websocket
    def receive_json(self, content, **kwargs):
        # Check message type, specified by client
        message_type = content['type']
        if message_type =='chat_message':
            # Send every chat message to all the members of the group
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    # Custom method for sending msg back to the group, defined further along
                    'type': 'chat_message_echo',
                    'message': content['message'],
                }
            )
        return super().receive_json(content, **kwargs)

    # Custom method for echo feature
    def chat_message_echo(self, event):
        self.send_json(event)
