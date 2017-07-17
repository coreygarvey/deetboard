from django import forms
from models import Product, Feature
from django.utils.translation import ugettext_lazy as _
import re
from accounts.models import Account
from deetboard.fields import UserModelMultipleChoiceField

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

class FeatureForm(forms.ModelForm):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Name"))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(required=False, max_length=100,rows=8, cols=12)), label=_("Description"))
	experts = UserModelMultipleChoiceField(queryset=Account.objects.all(), widget=forms.CheckboxSelectMultiple())
	#.filter(product__name='product_name')
	class Meta:
		model = Feature
		fields = ['title', 'description', 'experts',]
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		
		# Get org_accounts to set expert choices
		org_accounts = kwargs.pop('org_accounts', None)
		
		super(FeatureForm, self).__init__(*args, **kwargs)
		
		self.fields['experts'].queryset = org_accounts
		#self.fields['experts'].queryset = [(e.first_name, e.last_name) for e in org_accounts]


	def clean(self):
		cleaned_data = super(FeatureForm,self).clean()
		try:
			dupeProduct = Feature.objects.get(title__iexact=cleaned_data.get('title'))
			raise forms.ValidationError(_("Already a product with that name."))
		except Feature.DoesNotExist:
			pass

		super(FeatureForm, self).clean()

class FeatureScreenshotForm(FeatureForm):
	screenshot = forms.ImageField()

	class Meta(FeatureForm.Meta):
		fields = FeatureForm.Meta.fields + ['screenshot']




