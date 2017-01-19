from django import forms
from models import Org
from django.utils.translation import ugettext_lazy as _

class OrgForm(forms.ModelForm):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Name"))

	def clean(self):
		cleaned_data = super(OrgForm, self).clean()
		try:
			dupeOrg = Org.objects.get(title__iexact=cleaned_data.get('title'))
			raise forms.ValidationError(_("Already an organization with that name."))
		except Org.DoesNotExist:
			pass
		#return self.cleaned_data

	class Meta:
		model = Org
		fields = ['title']