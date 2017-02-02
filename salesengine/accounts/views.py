from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, get_user_model, authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView, UpdateView
from django.conf import settings
from django.core import signing
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from models import Account
from forms import AccountRegistrationForm, MyRegistrationForm, MyActivationForm, InvitationForm, ReactivateForm, FindOrgForm
from serializers import AccountSerializer
from orgs.models import Org

from rest_framework import generics, permissions
from core.permissions import IsAdminOrReadOnly

from registration import signals
from registration.views import ActivationView as BaseActivationView
from registration.views import RegistrationView as BaseRegistrationView

import re


REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')

# HMAC
class AccountRegistrationView(BaseRegistrationView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is simply the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """
    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'
    form_class = MyRegistrationForm

    def register(self, form):
        new_user = self.create_inactive_user(form)
        signals.user_registered.send(sender=self.__class__,
                                 user=new_user,
                                 request=self.request)
        return new_user

    def get_success_url(self, user):
        return ('registration_complete', (), {})

    def create_inactive_user(self, form):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        new_user = form.save(commit=False)
        form_email = form.cleaned_data['email']
        new_user.is_active = False
        new_user.save()
        self.send_activation_email(new_user)
        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return signing.dumps(
            obj=getattr(user, user.USERNAME_FIELD),
            salt=REGISTRATION_SALT
        )

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        return {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context.update({
            'user': user
        })
        subject = render_to_string(self.email_subject_template,
                                   context)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(self.email_body_template,
                                   context)
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)




#HMAC
class AccountActivationView(UpdateView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.
    """
    disallowed_url = 'registration_disallowed'
    success_url = None
    template_name = 'registration/activation_form.html'
    form_class = MyActivationForm
    model = Account


    def get_object(self):
        activation_key = self.kwargs.get('activation_key')
        username = self.validate_key(activation_key)
        if username is not None:
            user = self.get_user(username)
            return get_object_or_404(Account, pk=user.id)
        print 'User'
        print self.request.user
        return Account.objects.get(id=self.request.user.id)

    def form_valid(self, form, *args, **kwargs):
        # Try to activate user when form submitted is valid
        activation_key = self.kwargs['activation_key']
        activated_user = self.activate(self.args, self.kwargs)
        if activated_user:
            updated_user = form.save(commit=False)
            updated_user.is_active = True
            password = form.cleaned_data['password']
            updated_user.set_password(password)
            updated_user.save()
            signals.user_activated.send(
                sender=self.__class__,
                user=activated_user,
                request=self.request
            )

            # Determine if account is already a part of Org
            if updated_user.org is None:
                new_org = True
            else:  
                new_org = False
            print 'updated_user.org:'
            print updated_user.org
            success_url = self.get_success_url(activated_user, new_org)
            # Login user after updated and saved
            login(self.request, updated_user)
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        # Return form if it doesn't activate user
        return self.render_to_response(self.template_name, self.get_context_data(form=form))


    def activate(self, *args, **kwargs):
        # This is safe even if, somehow, there's no activation key,
        # because unsign() will raise BadSignature rather than
        # TypeError on a value of None.
        activation_key = self.kwargs.get('activation_key')
        print activation_key
        username = self.validate_key(activation_key)
        print username
        if username is not None:
            user = self.get_user(username)
            print user
            print 'About to make active'
            if user is not None:
                user.is_active = True
                user.save()
                print 'User is_active: '
                print user.is_active
                return user
        return False

    def get_success_url(self, user, new_org):
        if new_org:
            return ('new_org', (), {})
        else:
            return ('/', (), {})

    def validate_key(self, activation_key):
        
        #Verify that the activation key is valid and within the
        #permitted activation time window, returning the username if
        #valid or ``None`` if not.
        
        try:
            username = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return username
        # SignatureExpired is a subclass of BadSignature, so this will
        # catch either one.
        except signing.BadSignature:
            return None

    def get_user(self, username):
        
        #Given the verified username, look up and return the
        #corresponding user account if it exists, or ``None`` if it
        #doesn't.
        
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username,
            'is_active': False
        }
        try:
            user = User.objects.get(**lookup_kwargs)
            return user
        except User.DoesNotExist:
            return None


    def form_invalid(self, form):
        # tl;dr -- this method is implemented to work around Django
        # ticket #25548, which is present in the Django 1.9 release
        # (but not in Django 1.8 or 1.10).
        #
        # The longer explanation is that in Django 1.9,
        # FormMixin.form_invalid() does not pass the form instance to
        # get_context_data(). This causes get_context_data() to
        # construct a new form instance with the same data in order to
        # put it into the template context, and then any access to
        # that form's ``errors`` or ``cleaned_data`` runs that form
        # instance's validation. The end result is that validation
        # gets run twice on an invalid form submission, which is
        # undesirable for performance reasons.
        #
        # Manually implementing this method, and passing the form
        # instance to get_context_data(), solves this issue (which was
        # fixed in Django 1.9.1 and so is not present in Django
        # 1.10).
        return self.render_to_response(self.get_context_data(form=form))

class AccountRegistrationTypeView(TemplateView):
    template_name = "registration/registration_type.html"



class InvitationView(FormView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is simply the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """
    # Must change so invited flow is different when activating, no Org creation
    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'
    """
    Base class for user invitation views.
    """
    disallowed_url = 'invitation_disallowed'
    form_class = InvitationForm
    success_url = None
    template_name = 'registration/invitation_form.html'


    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.
        """
        if not self.invitation_allowed():
            return redirect(self.disallowed_url)
        return super(InvitationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        invited_users = [
            form.cleaned_data['invite1'],
            form.cleaned_data['invite2'],
            form.cleaned_data['invite3'],
        ]
        for invite in invited_users:
            # This should check that invite is valid email, not just filled in
            if invite != '':
                print "Registering invite: " + invite
                new_user = self.register(invite)
        
        # Allow all users with domain to register
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        if form.cleaned_data['inviteEmail'] == True:
            org.email_all=True
        else:
            org.email_all=False
        org.save()

        success_url = self.get_success_url()


        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)


    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def invitation_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        return getattr(settings, 'INVITATION_OPEN', True)


    def register(self, email):
        new_user = self.create_inactive_user(email)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self):
        return ('invitation_complete', (), {})

    def create_inactive_user(self, email):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        new_user = Account(email=email)
        # Username set to email, must not show in ActivationForm
        new_user.username = email
        new_user.is_active = False
        # Add org to user profile
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        new_user.org = org
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return signing.dumps(
            obj=getattr(user, user.USERNAME_FIELD),
            salt=REGISTRATION_SALT
        )

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        return {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context.update({
            'user': user
        })
        subject = render_to_string(self.email_subject_template,
                                   context)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(self.email_body_template,
                                   context)
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


class AccountReactivateView(FormView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is simply the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """
    # Must change so invited flow is different when activating, no Org creation
    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'
    """
    Base class for user invitation views.
    """
    disallowed_url = 'invitation_disallowed'
    form_class = ReactivateForm
    success_url = None
    template_name = 'registration/reactivate_form.html'


    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.
        """
        if not self.invitation_allowed():
            return redirect(self.disallowed_url)
        return super(AccountReactivateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        print "Reactivating: " + email
        user = Account.objects.get(email=email)
        print user
        print user.email
        print user.USERNAME_FIELD
        self.send_activation_email(user)
        print "Sent successfully!"
        success_url = self.get_success_url()

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)


    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def invitation_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        return getattr(settings, 'INVITATION_OPEN', True)


    def register(self, email):
        new_user = self.create_inactive_user(email)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self):
        return ('invitation_complete', (), {})

    def create_inactive_user(self, email):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        new_user = Account(email=email)
        # Username set to email, must not show in ActivationForm
        new_user.username = email
        new_user.is_active = False
        # Add org to user profile
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        new_user.org = org
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return signing.dumps(
            obj=getattr(user, user.USERNAME_FIELD),
            salt=REGISTRATION_SALT
        )

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        return {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context.update({
            'user': user
        })
        subject = render_to_string(self.email_subject_template,
                                   context)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(self.email_body_template,
                                   context)
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)



class AccountFindOrgView(FormView):
    """
    Search for user's email domain to see if there is a team
    open to all emails from that domain. If so, soft register and
    send authentication email. Otherwise, send sorry email
    """
    # Must change so invited flow is different when activating, no Org creation
    pos_email_body_template = 'registration/domain_activation_email.txt'
    pos_email_subject_template = 'registration/domain_activation_email_subject.txt'
    """
    Base class for user invitation views.
    """
    disallowed_url = 'invitation_disallowed'
    form_class = FindOrgForm
    success_url = None
    template_name = 'registration/find_org_form.html'


    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.
        """
        if not self.invitation_allowed():
            return redirect(self.disallowed_url)
        return super(AccountFindOrgView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        print "Finding org for: " + email
        #user = Account.objects.get(email=email)

        domain = re.search("@[\w.]+", email)
        print "Domain: "
        print domain.group()
        try:
            myOrg = Org.objects.get(email_domain=domain.group())
            print "Found it!"
        except:
            print "Couldn't find it!"
        #self.send_activation_email(user)
        #print "Sent successfully!"
        success_url = self.get_success_url()

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)


    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def invitation_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        return getattr(settings, 'INVITATION_OPEN', True)


    def register(self, email):
        new_user = self.create_inactive_user(email)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self):
        return ('invitation_complete', (), {})

    def create_inactive_user(self, email):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        new_user = Account(email=email)
        # Username set to email, must not show in ActivationForm
        new_user.username = email
        new_user.is_active = False
        # Add org to user profile
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        new_user.org = org
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return signing.dumps(
            obj=getattr(user, user.USERNAME_FIELD),
            salt=REGISTRATION_SALT
        )

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        return {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context.update({
            'user': user
        })
        subject = render_to_string(self.pos_email_subject_template,
                                   context)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(self.pos_email_body_template,
                                   context)
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)





@csrf_protect
def register(request):
    if request.method == 'POST':
        form = AccountRegistrationForm(request.POST)
        if form.is_valid():
            account = Account.objects.create_user(
            email=form.cleaned_data['email'],
            role=form.cleaned_data['role'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password1'],
            )
            send_activation_email(email)
            return HttpResponseRedirect('/register/success/')
        return render(
	 		request, 
	 		'registration/register.html', 
	 		{'form': form}
	 	)
    else:
        form = AccountRegistrationForm()
 	return render(
 		request, 
 		'registration/register.html', 
 		{'form': form}
 	)
 
def register_success(request):
    return render_to_response(
    'registration/success.html',
    )
 
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
 
@login_required
def home(request):
    return render_to_response(
        'home.html',
        { 
            'user': request.user,
            'admin_org': Org.objects.get(admin=request.user)
        }
    )

def start(request):
    return render(request, 'start.html')


class AccountListApi(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class AccountDetailApi(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                            IsAdminOrReadOnly,)