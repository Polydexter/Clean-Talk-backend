from email import message
from django.contrib.auth import get_user_model
from rest_framework import serializers

from conversations.models import Conversation, Message
from users.serializers import UserSerializer


User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'id',
            'conversation',
            'from_user',
            'to_user',
            'content',
            'timestamp',
            'read',
        )
    
    def get_conversation(self, obj):
        return str(obj.conversation.id)

    def get_from_user(self, obj):
        return UserSerializer(obj.from_user).data
    
    def get_to_user(self, obj):
        return UserSerializer(obj.to_user).data


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying active conversations, last
    message, unread messages count, etc.
    """
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'name', 'other_user', 'last_message', 'unread_count')

    def get_last_message(self, obj):
        messages = obj.messages.all().order_by('-timestamp')
        if not messages.exists():
            return None
        message = messages[0]
        return MessageSerializer(message).data

    def get_other_user(self, obj):
        usernames = obj.name.split('__')
        context = {}
        for username in usernames:
            if username != self.context['user'].username:
                other_user = User.objects.get(username=username)
                return UserSerializer(other_user, context=context).data

    def get_unread_count(self, obj):
        unread_count = obj.messages.filter(to_user=self.context['user'], read=False).count()
        return unread_count

