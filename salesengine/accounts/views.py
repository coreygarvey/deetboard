from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect

from models import Account
from forms import AccountRegistrationForm
from serializers import AccountSerializer
from orgs.models import Org

from rest_framework import generics, permissions
from core.permissions import IsAdminOrReadOnly






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