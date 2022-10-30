from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from conversations.models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .paginaters import MessagePagination


class ConversationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()
    lookup_field = 'name'

    def get_queryset(self):
        queryset = Conversation.objects.filter(
            name__contains=self.request.user.username
        )
        return queryset

    def get_serializer_context(self):
        context = super(ConversationViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        context.update({ 'user': self.request.user})
        return context


class MessageViewSet(ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.none()
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_name = self.request.GET.get('conversation')
        queryset = (
            Message.objects.filter(
                conversation__name__contains=self.request.user.username,
            )
            .filter(conversation__name=conversation_name)
            .order_by('-timestamp')
        )
        return queryset
