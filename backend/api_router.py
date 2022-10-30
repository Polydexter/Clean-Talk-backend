from rest_framework.routers import SimpleRouter

from conversations.api.views import ConversationViewSet, MessageViewSet

router = SimpleRouter()
router.register('conversations', ConversationViewSet),
router.register('messages', MessageViewSet),

app_name = 'api'
urlpatterns = router.urls