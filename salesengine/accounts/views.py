from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, get_user_model, authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView, UpdateView
from django.conf import settings
from django.core import signing


from models import Account
from forms import AccountRegistrationForm, MyRegistrationForm2
from serializers import AccountSerializer
from orgs.models import Org

from rest_framework import generics, permissions
from core.permissions import IsAdminOrReadOnly

from registration import signals
from registration.views import ActivationView as BaseActivationView


REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')



#HMAC
class ActivationView2(UpdateView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.
    """
    disallowed_url = 'registration_disallowed'
    success_url = None
    template_name = 'registration/activation_form.html'
    form_class = MyRegistrationForm2
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

        #### See get() method below #####
        # Try to activate user when form submitted is valid
        activation_key = self.kwargs['activation_key']
        activated_user = self.activate(self.args, self.kwargs)
        if activated_user:
            updated_user = form.save(commit=False)
            updated_user.is_active = True
            password = form.cleaned_data['password']
            #  Use set_password here
            updated_user.set_password(password)
            updated_user.save()
            signals.user_activated.send(
                sender=self.__class__,
                user=activated_user,
                request=self.request
            )
            success_url = self.get_success_url(activated_user)


            login(self.request, updated_user)
            
            try:
                to, args, kwargs = success_url
                print 'redirect url:'
                print to
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        #return super(ActivationView, self).dispatch(*args, **kwargs)
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

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})

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


"""
# ACTIVATION VIEW
    def get(self, *args, **kwargs):
        #The base get logic; Return a form for the user
        #to change necessary fields in their profile.
        #Post will lead to activation
        
        activated_user = self.activate(*args, **kwargs)
        if activated_user:
            signals.user_activated.send(
                sender=self.__class__,
                user=activated_user,
                request=self.request
            )
            success_url = self.get_success_url(activated_user)
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        return super(ActivationView, self).get(*args, **kwargs)

    def activate(self, *args, **kwargs):
        # This is safe even if, somehow, there's no activation key,
        # because unsign() will raise BadSignature rather than
        # TypeError on a value of None.
        username = self.validate_key(kwargs.get('activation_key'))
        if username is not None:
            user = self.get_user(username)
            if user is not None:
                user.is_active = True
                user.save()
                return user
        return False

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})

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

"""





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