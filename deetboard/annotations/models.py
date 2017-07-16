from __future__ import unicode_literals

from django.db import models
from core.models import TimeStampedModel

# Create your models here.
class Annotation(TimeStampedModel):
	screenshot = models.ForeignKey('screenshots.Screenshot', related_name='annotations')
	admin = models.ForeignKey('accounts.Account', related_name='admin')
	src = models.CharField(max_length=150)
	text = models.TextField()
	context = models.CharField(max_length=150)
	shapeType = models.CharField(max_length=50)
	style = models.CharField(max_length=150)
	x_val = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
	y_val = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
	width = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
	height = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
	

	def __str__(self):
		return "%s : %s" % (self.screenshot, self.text)
    
	class Meta:
		ordering = ('screenshot',)