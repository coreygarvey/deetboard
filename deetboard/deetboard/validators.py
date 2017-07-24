from django.core.exceptions import ValidationError
from products.models import Feature

def validate_unique(value):
	''' Raise ValidationError if
		value is not unique
	'''
	if (Feature.objects.filter(title__iexact=value)).exists():
		raise ValidationError("Invalid feature title")