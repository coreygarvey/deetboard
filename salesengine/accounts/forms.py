from django import forms
from django.contrib.auth import get_user_model

from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from models import Account

from . import validators

class AccountRegistrationForm(RegistrationForm):



	class Meta:
		model = Account
		fields = ['email']
		#fields = ['email', 'role', 'first_name', 'last_name']


User = get_user_model()

class MyRegistrationForm(ModelForm):
    """
    Form for registering a new user account.
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    Subclasses should feel free to add any additional validation they
    need, but should take care when overriding ``save()`` to respect
    the ``commit=False`` argument, as several registration workflows
    will make use of it to create inactive user accounts.
    """
    # Explicitly declared here because Django's default
    # UserCreationForm, which we subclass, does not require this field
    # but workflows in django-registration which involve explicit
    # activation step do require it. If you need an optional email
    # field, simply subclass and declare the field not required.
    email = forms.EmailField(
        #help_text=_(u'email address'),
        required=True
    )

    class Meta:
        model = Account
        fields = [
            User.USERNAME_FIELD,
            'email',
        ]
        required_css_class = 'required'

    def clean(self):
        """
        Apply the reserved-name validator to the username.
        """
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