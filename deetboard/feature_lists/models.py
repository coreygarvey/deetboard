from __future__ import unicode_literals

from django.db import models
from core.models import TimeStampedModel

class FeatureList(TimeStampedModel):
    title = models.CharField(max_length=50)
    comment = models.CharField(max_length=50)
    public = models.BooleanField(default=True)
    
    def __str__(self):
        return "%s" % (self.title)

    class Meta:
        abstract = True
        ordering = ('title',)

class EngagementList(FeatureList):
    admins = models.ManyToManyField('accounts.Account', related_name='elists_admin')
    client = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.title)
        
class TopList(FeatureList):
    admins = models.ManyToManyField('accounts.Account', related_name='tlists_admin')
    def __str__(self):
        return "%s" % (self.title)