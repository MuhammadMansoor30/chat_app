from django.db import models
from chat.models import AtByMixin

class Message(AtByMixin):
    TEXT = 0
    PICTURE = 1
    VIDEO = 2
    DOCUMENT = 3
    MESSAGE_TYPES = ((TEXT, "Text"),
    (PICTURE, "Image"),
    (VIDEO, "Video"),
    (DOCUMENT, "Document"))

    PENDING = 0
    SENT = 1
    DELIEVERED = 2
    SEEN = 3
    STATUS_TYPES = ((PENDING, "Pending"),
    (SENT, "Sent"),
    (DELIEVERED, "Delievered"),
    (SEEN, "Seen"))

    message         = models.CharField(max_length=255, null=True, blank=True)
    sender          = models.ForeignKey("User", related_name="+", on_delete=models.DO_NOTHING)
    conversation    = models.ForeignKey("Conversation", related_name="conversation", on_delete=models.DO_NOTHING)
    type            = models.IntegerField(choices=MESSAGE_TYPES, default=MESSAGE_TYPES[0][0])
    attachment      = models.CharField(max_length=255, null = True, blank = True)
    status          = models.IntegerField(choices=STATUS_TYPES, default=STATUS_TYPES[0][0])


    def __str__(self):
        return f"{self.sender.full_name} sent a {self.type}"
