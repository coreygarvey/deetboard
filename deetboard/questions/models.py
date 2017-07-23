from __future__ import unicode_literals

from django.db import models
from core.models import TimeStampedModel

class Question(TimeStampedModel):
    admin = models.ForeignKey('accounts.Account', related_name='questions_admin')
    title = models.CharField(max_length=100)
    text = models.TextField()
    product = models.ForeignKey('products.Product', related_name='questions')
    features = models.ManyToManyField('products.Feature', related_name='questions')
    user_asking = models.ForeignKey('accounts.Account', related_name='questions_asked')
    skills = models.ManyToManyField('orgs.Skill', related_name='questions')
    screenshots = models.ManyToManyField('screenshots.Screenshot', related_name='questions')
    
    def __str__(self):
        return "%s" % (self.text)
    
    class Meta:
        ordering = ('created',)
        permissions = (
            ("view_quest", "View question"),
        )


class Response(TimeStampedModel):
    admin = models.ForeignKey('accounts.Account', related_name='responses_admin')
    question = models.ManyToManyField(Question, related_name='responses')
    text = models.TextField()
    user_responder = models.ForeignKey('accounts.Account', related_name='responses')
    accepted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('accepted','created')
