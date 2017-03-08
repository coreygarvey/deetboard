from django import forms
from models import Product
from django.utils.translation import ugettext_lazy as _
import re

class ProductForm(forms.ModelForm):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Name"))
	class Meta:
		model = Product
		fields = ['title']
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(ProductForm, self).__init__(*args, **kwargs)
		print kwargs


	def clean(self):
		cleaned_data = super(ProductForm,self).clean()
		try:
			dupeProduct = Product.objects.get(title__iexact=cleaned_data.get('title'))
			raise forms.ValidationError(_("Already a product with that name."))
		except Product.DoesNotExist:
			pass

		super(ProductForm, self).clean()

