from __future__ import unicode_literals

from django.db import models
from core.models import TimeStampedModel

class Screenshot(TimeStampedModel):
    admin = models.ForeignKey('accounts.Account', related_name='screenshots_admin')
    title = models.CharField(max_length=50)
    file_path = models.FileField()
    feature = models.ForeignKey('products.Feature', 
    						on_delete=models.CASCADE,
    						blank=True,
                            related_name='screenshots')
    question = models.ForeignKey('questions.Question', 
    						on_delete=models.CASCADE,
    						blank=True,
                            related_name='screenshots')
    
    def __str__(self):
        return "%s" % (self.title)
    
    class Meta:
        ordering = ('title',)
