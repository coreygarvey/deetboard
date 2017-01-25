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