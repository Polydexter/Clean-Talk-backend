import json
from uuid import UUID
from asgiref.sync import async_to_sync
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.generic.websocket import JsonWebsocketConsumer
from conversations.models import Conversation, Message
from conversations.api.serializers import MessageSerializer

User = get_user_model()


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class ChatConsumer(JsonWebsocketConsumer):
    """
    Consumer for a single conversation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_name = None
        self.conversation = None

    def connect(self):
        self.user = self.scope['user']
        # Refuse connection if user is not authenticated
        if self.user is AnonymousUser:
            return
        self.accept()
        # Get or create a conversation
        self.conversation_name = f"{self.scope['url_route']['kwargs']['conversation_name']}"
        self.conversation, created = Conversation.objects.get_or_create(name=self.conversation_name)
        # Send a list of online users to the group
        async_to_sync(self.channel_layer.group_add)(
            self.conversation_name,
            self.channel_name,
        )
        self.send_json(
            {
                'type': 'online_user_list',
                'users': [user.username for user in self.conversation.online.all()],
            }
        )
        # Notify the group when a user has joined the conversation
        async_to_sync(self.channel_layer.group_send)(
            self.conversation_name,
            {
                'type': 'user_join',
                'user': self.user.username,
            }
        )
        self.conversation.online.add(self.user)
        # Send last 20 messages of the conversation
        all_messages = self.get_messages()
        message_count = len(all_messages)
        messages = all_messages[0:20]
        self.send_json({
            'type': 'last_20_messages',
            "messages": MessageSerializer(messages, many=True).data,
            'total_count': message_count,
            'has_more': message_count > 20,
        })
    
    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    'type': 'user_leave',
                    'user': self.user.username,
                }
            )
            self.conversation.online.remove(self.user)
        return super().disconnect(close_code)
        
    # Receive message from websocket
    def receive_json(self, content, **kwargs):
        # Check message type, specified by client
        message_type = content['type']
        if message_type =='chat_message':
            message = Message.objects.create(
                from_user=self.user,
                to_user=self.get_receiver(),
                content=content['message'],
                conversation=self.conversation
            )
            # Send chat message to all the members of the group
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    # Custom method for sending msg back to the group, defined further along
                    'type': 'chat_message_echo',
                    'message': MessageSerializer(message).data,
                },
            )
            notification_group_name = self.get_receiver().username + "__notifications"
            async_to_sync(self.channel_layer.group_send)(
                notification_group_name,
                {
                    "type": "new_message_notification",
                    "name": self.user.username,
                    "message": MessageSerializer(message).data
                },
            )
        if message_type == "typing":
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "typing",
                    "user": self.user.username,
                    "typing": content["typing"],
                }
            )
        if message_type == 'read_messages':
            messages_to_me = self.conversation.messages.filter(to_user=self.user)
            messages_to_me.update(read=True)
            # Update unread message count
            unread_count = Message.objects.filter(to_user=self.user, read=False).count()
            async_to_sync(self.channel_layer.group_send)(
                self.user.username + "__notifications",
                {
                    "type": "unread_count",
                    "unread_count": unread_count
                }
            )
        return super().receive_json(content, **kwargs)

    # Custom methods for each message type
    def chat_message_echo(self, event):
        self.send_json(event)

    def user_join(self, event):
        self.send_json(event)

    def user_leave(self, event):
        self.send_json(event)
    
    def typing(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)

    # Auxliary methods for consumer-level methods
    def get_receiver(self):
        usernames = self.conversation.name.split('__')
        receiver = [username for username in usernames if username != self.user.username][0]
        return User.objects.get(username=receiver)

    def get_messages(self):
        usernames = self.conversation_name.split('__')
        id_list = []
        for username in usernames:
            id_list += [User.objects.get(username=username)]
        messages = Message.objects.filter(
                Q(from_user=id_list[0], to_user=id_list[1]) | Q(from_user=id_list[1], to_user=id_list[0])
            ).order_by("-timestamp")
        return messages

    @classmethod
    def encode_json(cls, content):
        return json.dumps(content, cls=UUIDEncoder)


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.notification_group_name = None

    def connect(self):
        self.user = self.scope['user']
        # Refuse connection if user is not authenticated
        if self.user is AnonymousUser:
            return       
        self.accept()
        unread_count = Message.objects.filter(to_user=self.user, read=False).count()
        self.send_json(
            {
                "type": "unread_count",
                "unread_count": unread_count,
            }
        )
        self.notification_group_name = self.user.username + "__notifications"
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name,
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)

    def new_message_notification(self, event):
        self.send_json(event)

    def unread_count(self, event):
        self.send_json(event)