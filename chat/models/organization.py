from django.db import models
from simple_history.models import HistoricalRecords
from chat.models import AtByMixin

class Organization(AtByMixin):
    name                = models.CharField(max_length=100)
    history             = HistoricalRecords()

    def __str__(self):
        return self.name
