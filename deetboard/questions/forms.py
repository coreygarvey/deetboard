from django import forms
from models import Question, Response
from products.models import Feature
from django.utils.translation import ugettext_lazy as _
import re

class QuestionForm(forms.ModelForm):
	text = forms.CharField(required=True, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Text"))
	class Meta:
		model = Question
		fields = ['text']
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(QuestionForm, self).__init__(*args, **kwargs)
		print kwargs


	def clean(self):
		cleaned_data = super(QuestionForm,self).clean()

		super(QuestionForm, self).clean()

class QuestionFeaturesForm(forms.ModelForm):
	features = forms.ModelMultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple(), queryset=Feature.objects.all())

	class Meta:
		model = Question
		fields = ['features']
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(QuestionFeaturesForm, self).__init__(*args, **kwargs)
		print kwargs


	def clean(self):
		cleaned_data = super(QuestionFeaturesForm,self).clean()

		super(QuestionFeaturesForm, self).clean()

class ResponseForm(forms.ModelForm):
	text = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 10, 'cols': 40, 'class' : 'response-input'}), label=_("Text"))
	class Meta:
		model = Response
		fields = ['text']
		
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(ResponseForm, self).__init__(*args, **kwargs)
		print kwargs


	def clean(self):
		cleaned_data = super(ResponseForm,self).clean()

		super(ResponseForm, self).clean()