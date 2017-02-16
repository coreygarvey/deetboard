from django import forms
from models import Org
from django.utils.translation import ugettext_lazy as _
import re

class OrgForm(forms.ModelForm):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs=dict(required=False, max_length=30)), label=_("Name"))
	class Meta:
		model = Org
		fields = ['title']
	def clean_email_domain(self):
		print "here"
		email = self.request.user.email
			
		print email
		domain = re.search("@[\w.]+", email)
		email_domain = domain.group()
		"""
		if Org.objects.filter(email_domain=email_domain).exists():
			print "exists"
			raise forms.ValidationError(
				u'Another person already started an org with the domain %s.' % email_domain)
		"""
		return email_domain
	
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(OrgForm, self).__init__(*args, **kwargs)
		print kwargs


	def clean(self):
		cleaned_data = super(OrgForm,self).clean()
		try:
			dupeOrg = Org.objects.get(title__iexact=cleaned_data.get('title'))
			raise forms.ValidationError(_("Already an organization with that name."))
		except Org.DoesNotExist:
			pass

		self.clean_email_domain()

		super(OrgForm, self).clean()


"""
class UserCreationForm(forms.Form):
    invite1 = forms.EmailField()
    invite2 = forms.EmailField()
    invite3 = forms.EmailField()

    def clean(self):
        
        # Apply the reserved-name validator to the username.
        
        # This is done in clean() because Django does not currently
        # have a non-ugly way to just add a validator to an existing
        # field on a form when subclassing; the standard approach is
        # to re-declare the entire field in order to specify the
        # validator. That's not an option here because we're dealing
        # with the user model and we don't know -- given custom users
        # -- how to declare the username field.
        #
        # So defining clean() and attaching the error message (if
        # there is one) to the username field is the least-ugly
        # solution.
        username_value = self.cleaned_data.get(User.USERNAME_FIELD)
        if username_value is not None:
            try:
                if hasattr(self, 'reserved_names'):
                    reserved_names = self.reserved_names
                else:
                    reserved_names = validators.DEFAULT_RESERVED_NAMES
                validator = validators.ReservedNameValidator(
                    reserved_names=reserved_names
                )
                validator(username_value)
            except ValidationError as v:
                self.add_error(User.USERNAME_FIELD, v)
        super(MyRegistrationForm, self).clean()
"""