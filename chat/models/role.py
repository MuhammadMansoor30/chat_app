from django.db import models
from chat.models.at_by_mixin import AtByMixin
from simple_history.models import HistoricalRecords

class Role(AtByMixin):
    name                = models.CharField(max_length=100)
    code_name           = models.CharField(max_length=50)
    permissions         = models.ManyToManyField('Permission', related_name='roles')
    organization        = models.ForeignKey('Organization', related_name='organization', blank=True, null=True, on_delete=models.DO_NOTHING)
    history             = HistoricalRecords()

    def __str__(self):
        return self.name
