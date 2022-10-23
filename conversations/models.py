from email.policy import default
from unicodedata import name
import uuid

from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable = False)
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=User, blank=True)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()
    
    def remove(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f"{self.name}({self.get_online_count()})"

    
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_from_user')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_to_uers')
    content = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user.username} to {self.to_user.username}: {self.content} [{self.timestamp}]"