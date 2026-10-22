from django.db import models
from chat.models import AtByMixin

class Conversation(AtByMixin):
    participants      = models.ManyToManyField("User", related_name="conversations")
    last_message      = models.CharField(max_length=255)
    organization      = models.ForeignKey("Organization", related_name="+", on_delete=models.DO_NOTHING, null=True, blank=True)
    last_message_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{', '.join(str(c) for c in self.participants.all())}"