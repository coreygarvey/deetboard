from django import forms
from models import Product, Feature
from django.utils.translation import ugettext_lazy as _
import re
from accounts.models import Account
from deetboard.fields import UserModelMultipleChoiceField
#from deetboard.validators import validate_unique

class ProductForm(forms.ModelForm):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Name"))
	class Meta:
		model = Product
		fields = ['title', 'description', 'image']
		widgets = {
          'description': forms.Textarea(attrs={'rows':4}),
        }
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(ProductForm, self).__init__(*args, **kwargs)
		self.fields["image"].required = False
		print kwargs


	def clean(self):
		cleaned_data = super(ProductForm,self).clean()
		'''
		CURRENTLY ALLOWING DUPLICATE PRODUCT NAMES
		try:
			dupeProduct = Product.objects.get(title__iexact=cleaned_data.get('title'))
			raise forms.ValidationError(_("Already a product with that name."))
		except Product.DoesNotExist:
			pass
		'''

		super(ProductForm, self).clean()


class ProductUpdateForm(forms.ModelForm):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Name"))
	image = forms.ImageField()

	class Meta:
		model = Product
		fields = ['title', 'description', 'image',]
		widgets = {
          'description': forms.Textarea(attrs={'rows':4}),
        }
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(ProductUpdateForm, self).__init__(*args, **kwargs)
		print kwargs


	def clean(self):
		cleaned_data = super(ProductUpdateForm,self).clean()
		'''
		CURRENTLY ALLOWING DUPLICATE PRODUCT NAMES
		try:
			dupeProduct = Product.objects.get(title__iexact=cleaned_data.get('title'))
			raise forms.ValidationError(_("Already a product with that name."))
		except Product.DoesNotExist:
			pass
		'''

		super(ProductUpdateForm, self).clean()

class FeatureForm(forms.ModelForm):
	#title = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Name"))
	#description = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(required=False, max_length=100,rows=8, cols=12)), label=_("Description"))
	#experts = UserModelMultipleChoiceField(queryset=Account.objects.all(), widget=forms.CheckboxSelectMultiple())
	#.filter(product__name='product_name')
	class Meta:
		model = Feature
		fields = ['title', 'description', 'experts',]
		labels = {
			'title': _('Name'),
			'description': _('Description'),
			'experts': _('Experts')
		}
		widgets = {
			'title': forms.TextInput(attrs=dict(max_length=30)),
			'description': forms.Textarea(attrs=dict(max_length=100, rows=8, cols=12)),
			'experts': forms.CheckboxSelectMultiple(),
		}

		querysets = {
			'experts': Account.objects.all(),
		}
		field_classes = {
			'title': forms.CharField,
			'description': forms.CharField,
			'experts': UserModelMultipleChoiceField,
		}
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		
		# Get org_accounts to set expert choices
		org_accounts = kwargs.pop('org_accounts', None)
		
		super(FeatureForm, self).__init__(*args, **kwargs)

		self.fields['description'].required = False
		self.fields['experts'].required = False
		
		self.fields['experts'].queryset = org_accounts
		#self.fields['experts'].queryset = [(e.first_name, e.last_name) for e in org_accounts]
		#self.fields['title'].validators.append(validate_unique)
		


	def clean(self):
		
		'''
		try:
			dupeProduct = Feature.objects.get(title__iexact=cleaned_data.get('title'))
			print "Already a product with that name."
			raise forms.ValidationError(_("Already a product with that name."))
		except Feature.DoesNotExist:
			pass
		'''
		super(FeatureForm, self).clean()

class FeatureUpdateForm(forms.ModelForm):
	"""
	Form for updating a feature.
	"""
	screenshot = forms.ImageField()

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
	
		# Get org_accounts to set expert choices
		org_accounts = kwargs.pop('org_accounts', None)
		
		super(FeatureUpdateForm, self).__init__(*args, **kwargs)

		self.fields['description'].required = False
		self.fields['experts'].required = False
		
		self.fields['experts'].queryset = org_accounts

	class Meta:
  		model = Feature
		fields = ['title', 'description', 'experts', 'screenshot']
		labels = {
			'title': _('Name'),
			'description': _('Description'),
			'experts': _('Experts'),
		}
		widgets = {
			'title': forms.TextInput(attrs=dict(max_length=30)),
			'description': forms.Textarea(attrs=dict(max_length=100, rows=8, cols=12)),
			'experts': forms.CheckboxSelectMultiple(),
		}

		field_classes = {
			'title': forms.CharField,
			'description': forms.CharField,
			'experts': UserModelMultipleChoiceField,
		}


'''
'''
class FeatureScreenshotForm(FeatureForm):
	screenshot = forms.ImageField()

	class Meta(FeatureForm.Meta):
		fields = FeatureForm.Meta.fields + ['screenshot']
		field_classes = {
			'screenshot': forms.ImageField,
		}

	def __init__(self, *args, **kwargs):
		super(FeatureScreenshotForm, self).__init__(*args, **kwargs)
		self.fields['screenshot'].required = False



class FeatureScreenshotUpdateForm(FeatureUpdateForm):
	screenshot = forms.ImageField()

	class Meta(FeatureUpdateForm.Meta):
		fields = FeatureUpdateForm.Meta.fields + ['screenshot']
		field_classes = {
			'screenshot': forms.ImageField,
		}

	def __init__(self, *args, **kwargs):
		super(FeatureScreenshotUpdateForm, self).__init__(*args, **kwargs)
		self.fields['screenshot'].required = False




