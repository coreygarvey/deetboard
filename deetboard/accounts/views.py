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
from django.core.urlresolvers import reverse
from django.template import RequestContext

from django.contrib.auth.models import Group

from django.contrib.auth.views import login as login_view

from django.contrib.auth.backends import ModelBackend

from models import Account
from forms import AccountRegistrationForm, MyRegistrationForm, MyActivationForm, ProfileUpdateForm, AdminInvitationForm, ReactivateForm, FindOrgForm, GeneralInvitationForm
from serializers import AccountSerializer
from orgs.models import Org
from braces.views import LoginRequiredMixin

from rest_framework import generics, permissions
from core.permissions import IsAdminOrReadOnly

from registration import signals
from registration.views import RegistrationView as BaseRegistrationView

from PIL import Image

import re


REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')

class RegistrationTypeView(TemplateView):
    template_name = "registration/registration_type.html"

class ActivationKeyMixin(object):

    def get_activation_key(self, user, org_pk=None):
        """
        Generate the activation key which will be emailed to the user.
        """

        return signing.dumps(
            #obj=getattr(user, user.USERNAME_FIELD),
            obj={"username": getattr(user, user.USERNAME_FIELD),
                 "org_pk": org_pk},
            salt=REGISTRATION_SALT
        )

class ActivationContextMixin(object):
    def get_activation_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        return {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

class ActivationEmailMixin(object):
    def send_activation_email(self, user, org=None, current_user=None):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.
        """
        if org is not None:
            activation_key = self.get_activation_key(user, org.id)
        else:
            activation_key = self.get_activation_key(user)
        
        context = self.get_activation_context(activation_key)
        context.update({
            'user': user,
            'current_user': current_user,
            'org': org
        })

        subject = render_to_string(self.email_subject_template,
                                   context)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(self.email_body_template,
                                   context)
        html_message = render_to_string(self.email_body_html_template, 
                                    context)
        
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL, 
                        html_message=html_message)

class InvitationAllowedMixin(object):
    def invitation_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        return getattr(settings, 'INVITATION_OPEN', True)

class RegistrationMixin(object):
    def register(self, email):
        new_user = self.create_inactive_user(email)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

class RegistrationView(ActivationContextMixin, ActivationKeyMixin, 
                        ActivationEmailMixin, RegistrationMixin, BaseRegistrationView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is simply the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """
    email_body_template = 'registration/emails/activation_email_body.txt'
    email_body_html_template = 'registration/emails/activation_email_body.html'
    email_subject_template = 'registration/emails/activation_email_subject.txt'
    form_class = MyRegistrationForm
    template_name = 'registration/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect('/home/')
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

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

class ActivationView(UpdateView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.
    """
    disallowed_url = 'registration_disallowed'
    success_url = None
    template_name = 'registration/activate.html'
    form_class = MyActivationForm
    model = Account

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(ActivationView, self).get_context_data(**kwargs)
        activation_key = self.kwargs.get('activation_key')
        activation_message = self.validate_key(activation_key)
        username = activation_message.get("username")
        if username is not None:
            user = self.get_user(username)
        context['new_user'] = user
        return context

    def get_object(self):
        activation_key = self.kwargs.get('activation_key')
        activation_message = self.validate_key(activation_key)
        username = activation_message.get("username")
        if username is not None:
            user = self.get_user(username)
            # Other options for field => Blank or email prefix
            #user.username = ""
            #user.save()
            #domain_search = re.search("@[\w.]+", current_user.email)
            #domain = domain_search.group()
            return get_object_or_404(Account, pk=user.id)
        current_user = self.request.user
        return Account.objects.get(id=current_user)

    def form_valid(self, form, *args, **kwargs):
        # Try to activate user when form submitted is valid
        activation_key = self.kwargs['activation_key']
        activation_message = self.activate(activation_key)
        username = activation_message.get('username')
        # Obtain user with username, 
        #   checks to make sure validation worked correctly
        activated_user = self.get_user(username)
        org_id = activation_message.get('org_pk')
        if activated_user:
            # CAN THIS BE activated_user = ??
            updated_user = form.save(commit=False)
            updated_user.is_active = True
            password = form.cleaned_data['password']
            updated_user.set_password(password)
            updated_user.save()
            # Connect user with org
            if org_id is not None:
                org = Org.objects.get(id=org_id)
                updated_user.orgs.add(org)
                updated_user.primary_org = org
                updated_user.save()
            signals.user_activated.send(
                sender=self.__class__,
                user=activated_user,
                request=self.request
            )
            # Determine next move based on account's org
            success_url = self.get_success_url(activated_user, org_id)
            # Login user after updated and saved
            login(self.request, updated_user, backend='django.contrib.auth.backends.ModelBackend')
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        # Return form if it doesn't activate user
        return self.render_to_response(self.template_name, self.get_context_data(form=form))

    def activate(self, activation_key):
        # This is safe even if, somehow, there's no activation key,
        # because unsign() will raise BadSignature rather than
        # TypeError on a value of None.
        print "activation_key"
        print activation_key  
        activation_message = self.validate_key(activation_key)
        if activation_message is not None:
            username = activation_message.get('username')
            org_id = activation_message.get('org_id')
            user = self.get_user(username)
            if user is not None:
                user.save()
                return activation_message
        return False

    def get_success_url(self, user, org_id):
        # Users without org will create new
        if org_id is None:
            return ('new_org', (), {})
        else:
            return reverse('general_invitation',args=(org_id,))

    def validate_key(self, activation_key):
        #Verify that the activation key is valid and within the
        #permitted activation time window, returning the username if
        #valid or ``None`` if not.
        try:
            results = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return results
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



class InvitationView(ActivationContextMixin, ActivationKeyMixin, 
                    ActivationEmailMixin, InvitationAllowedMixin, RegistrationMixin, FormView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is simply the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """
    # Must change so invited flow is different when activating, no Org creation
    email_body_template = 'registration/emails/invitation_email_body.txt'
    email_body_html_template = 'registration/emails/invitation_email_body.html'
    email_subject_template = 'registration/emails/invitation_email_subject.txt'
    """
    Base class for user invitation views.
    """
    disallowed_url = 'invitation_disallowed'
    form_class = AdminInvitationForm
    success_url = None
    template_name = 'registration/invitation-front.html'


    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.
        """
        if not self.invitation_allowed():
            return redirect(self.disallowed_url)
        return super(InvitationView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Use this to add extra context."""
        context = super(InvitationView, self).get_context_data(**kwargs)
        current_user = self.request.user
        domain_search = re.search("@[\w.]+", current_user.email)
        domain = domain_search.group()
        context['domain'] = domain
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        context['org'] = org

        return context

    def form_valid(self, form):
        # Need to protect for only admin of org
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)

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
                new_user.save()
                new_user.orgs.add(org)        

        # Allow all users with domain to register
        if form.cleaned_data['inviteEmail'] == True:
            org.email_all=True
        else:
            org.email_all=False
        org.save()
        success_url = self.get_success_url(org_pk)

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


    def get_success_url(self, org_id):
        # Users without org will create new, send to make product
        if org_id is None:
            return ('new_org', (), {})
        else:
            return reverse('product_create_first',args=(org_id,))

    def create_inactive_user(self, email):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        if Account.objects.filter(email=email).count() == 1:
            user = Account.objects.get(email=email)
        else:
            user = Account(email=email)
            # Username set to email, must not show in ActivationForm
            user.username = email
            user.is_active = False
            user.save()
        # Add org to user profile
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        user.orgs.add(org)
        self.send_activation_email(user, org, current_user=self.request.user)

        return user

class GeneralInvitationView(InvitationView):
    form_class = GeneralInvitationForm

    def form_valid(self, form):
        # Protect for only users in org
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
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
                new_user.save()
                new_user.orgs.add(org)

                # Find group for this Org, add user, set view perm
                groupName = org.title + str(org.pk)
                orgUserGroup = Group.objects.get(name=groupName)
                new_user.groups.add(orgUserGroup)

                success_url = self.get_success_url()

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)

class HomeInvitationView(GeneralInvitationView):
    template_name = 'accounts/invitation.html'

class ReactivateView(ActivationContextMixin, ActivationKeyMixin, 
                    ActivationEmailMixin, InvitationAllowedMixin, FormView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is simply the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """
    # Must change so invited flow is different when activating, no Org creation
    email_body_template = 'registration/emails/activation_email.txt'
    email_body_html_template = 'registration/emails/activation_email_body.html'
    email_subject_template = 'registration/emails/activation_email_subject.txt'
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
        return super(ReactivateView, self).dispatch(*args, **kwargs)

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

    def get_success_url(self):
        return ('invitation_complete', (), {})


class FindOrgView(ActivationContextMixin, ActivationKeyMixin, 
                InvitationAllowedMixin, RegistrationMixin, FormView):
    """
    Search for user's email domain to see if there is a team
    open to all emails from that domain. If so, soft register and
    send authentication email. Otherwise, send sorry email
    """
    # Must change so invited flow is different when activating, no Org creation
    join_org_email_body_template = 'registration/emails/join_org_email_body.txt'
    join_org_email_body_html_template = 'registration/emails/join_org_email_body.html'
    join_org_email_subject_template = 'registration/emails/join_org_email_subject.txt'

    no_org_email_body_template = 'registration/emails/no_org_email_body.txt'
    no_org_email_body_html_template = 'registration/emails/no_org_email_body.html'
    no_org_email_subject_template = 'registration/emails/no_org_email_subject.txt'

    multi_org_email_body_template = 'registration/emails/multi_org_email_body.txt'
    multi_org_email_body_html_template = 'registration/emails/multi_org_email_body.html'
    multi_org_email_subject_template = 'registration/emails/multi_org_email_subject.txt'

    disallowed_url = 'invitation_disallowed'
    form_class = FindOrgForm
    success_url = None
    template_name = 'registration/find_org.html'


    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.
        """
        if not self.invitation_allowed():
            return redirect(self.disallowed_url)
        return super(FindOrgView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        new_user = self.register(email)
      
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

    def get_success_url(self):
        return ('find_org_complete', (), {})

    def user_org(self, email):
        domain = re.search("@[\w.]+", email)
        # Get all orgs through filter. Return array regardless
        try:
            myOrgs = Org.objects.filter(email_domain=domain.group())
            return list(myOrgs)
        except:
            return []

    def create_inactive_user(self, email):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        if Account.objects.filter(email=email).count() == 1:
            user = Account.objects.get(email=email)
        else:
            user = Account(email=email)
            # Username set to email, must not show in ActivationForm
            user.username = email
            user.is_active = False
            user.save()

        user_orgs = self.user_org(email)
        org_count = len(user_orgs)

        self.send_activation_email(user,user_orgs)
        return user

    def send_activation_email(self, user, user_orgs):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.
        """
        email_orgs = {}
        # This will the key to create a new org
        activation_key = self.get_activation_key(user, None)
        context = self.get_activation_context(activation_key)
        org_count = len(user_orgs)
        for org in user_orgs:
            org_id = org.id
            activation_key = self.get_activation_key(user, org_id)
            email_orgs[activation_key] = org

        context.update({
            'email_orgs': email_orgs,
        })
        if org_count == 0:
            subject_var = self.no_org_email_subject_template
            message_var = self.no_org_email_body_template
            html_message_var = self.no_org_email_body_html_template
        else:
            if org_count == 1:
                subject_var = self.join_org_email_subject_template
                message_var = self.join_org_email_body_template
                html_message_var = self.join_org_email_body_html_template                
            else:
                subject_var = self.multi_org_email_subject_template
                message_var = self.multi_org_email_body_template
                html_message_var = self.multi_org_email_body_html_template

        subject = render_to_string(subject_var,context)
        message = render_to_string(message_var,context)
        html_message = render_to_string(html_message_var,context)
        # Force subject to a single line to avoid header-injection
            # issues.
        subject = ''.join(subject.splitlines())
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL, 
                        html_message=html_message)


def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/')
    else:
        return login_view(request)

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

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.
    """
    disallowed_url = 'registration_disallowed'
    success_url = None
    template_name = "accounts/profile-update.html"
    form_class = ProfileUpdateForm
    model = Account

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        return context

    def get_object(self):
        current_user = self.request.user
        return current_user

    def form_valid(self, form, *args, **kwargs):
        updated_user = form.save(commit=False)
        password = form.cleaned_data['password']
        updated_user.set_password(password)
        updated_user.save()

        # Connect user with org
        """
        if org_id is not None:
            org = Org.objects.get(id=org_id)
            updated_user.orgs.add(org)
        signals.user_activated.send(
            sender=self.__class__,
            user=activated_user,
            request=self.request
        )
        """
        # Determine next move based on account's org
        success_url = self.get_success_url()

        login(self.request, updated_user, backend='django.contrib.auth.backends.ModelBackend')
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)
        

    def get_success_url(self):
        return reverse('profile',args=())


    def get_user(self, username):        
        #Given the verified username, look up and return the
        #corresponding user account if it exists, or ``None`` if it
        #doesn't.
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username,
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

class ProfileView(TemplateView):
    """
    View the User's Profile
    """
    disallowed_url = 'registration_disallowed'
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(ProfileView, self).get_context_data(**kwargs)
        user = self.request.user
        print "user after new page"
        print user
        user_orgs = user.orgs.all()
        context['user'] = user
        context['user_orgs'] = user_orgs
        return context



    def get_user(self, username):        
        #Given the verified username, look up and return the
        #corresponding user account if it exists, or ``None`` if it
        #doesn't.
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username,
        }
        try:
            user = User.objects.get(**lookup_kwargs)
            return user
        except User.DoesNotExist:
            return None

class ProfilePublicView(TemplateView):
    """
    View any User's Profile
    """
    disallowed_url = 'registration_disallowed'
    template_name = "accounts/profile-public.html"

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(ProfilePublicView, self).get_context_data(**kwargs)
        
        user = self.request.user
        profile_user_pk = self.kwargs['pk']
        profile_user = Account.objects.get(pk=profile_user_pk)

        profile_user_orgs = profile_user.orgs.all()
        context['user'] = user
        context['profile_user'] = profile_user
        context['profile_user_orgs'] = profile_user_orgs
        return context

    def get_user(self, username):        
        #Given the verified username, look up and return the
        #corresponding user account if it exists, or ``None`` if it
        #doesn't.
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username,
        }
        try:
            user = User.objects.get(**lookup_kwargs)
            return user
        except User.DoesNotExist:
            return None
