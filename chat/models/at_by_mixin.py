from django.db import models

class AtByMixin(models.Model):
    created_at          = models.DateTimeField(auto_now_add=True)
    created_by          = models.ForeignKey('User', related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    updated_at          = models.DateTimeField(auto_now=True, db_index=True)
    updated_by          = models.ForeignKey('User', related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    deleted             = models.BooleanField(default=False)
    deleted_at          = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
    
    def delete(self):
        self.deleted = True
        self.save()
        
    def permdelete(self):
        return super().delete()