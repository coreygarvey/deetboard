from django import forms
from models import Question
from django.utils.translation import ugettext_lazy as _
import re

class QuestionForm(forms.ModelForm):
	text = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Text"))
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