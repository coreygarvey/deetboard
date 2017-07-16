from __future__ import unicode_literals

from django.db import models
from core.models import TimeStampedModel


class Screenshot(TimeStampedModel):
    admins = models.ManyToManyField('accounts.Account', related_name='screenshots_admin')
    title = models.CharField(max_length=50, blank=True)
    image = models.FileField(upload_to='screenshots/')

    """
    feature = models.ManyToManyField('products.Feature', 
                            on_delete=models.CASCADE,
                            blank=True,
                            null=True,
                            related_name='screenshots')
    """
    """
    question = models.ManyToManyField('questions.Question', 
                            on_delete=models.CASCADE,
                            blank=True,
                            null=True,
                            related_name='screenshots')
    """

    def __str__(self):
        return "%s" % (self.title)
    
    class Meta:
        ordering = ('title',)

