"""salesengine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView


from django.contrib.auth.views import login
from registration.backends.hmac.views import RegistrationView

from accounts.forms import AccountRegistrationForm, MyRegistrationForm, MyRegistrationForm2
from accounts.views import register, register_success, logout_page, home, ActivationView2

from views import IndexView
from orgs.views import OrgCreateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^orgs/', include('orgs.urls'), name="org"),

    url(r'^api/', include('core.api'), name="api"),

    url(r'^$', login),
    url(r'^logout/$', logout_page),
    url(r'^accounts/activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ),
        name='registration_activation_complete'),

    url(r'^accounts/login/$', login), # If user is not login it will redirect to login page
    url(r'^accounts/register/$',
        RegistrationView.as_view(
            #form_class=AccountRegistrationForm
            form_class=MyRegistrationForm
        ),
        name='registration_register',
    ),
    url(r'^accounts/activate/(?P<activation_key>[-:\w]+)/$',
        ActivationView2.as_view(
            form_class=MyRegistrationForm2
            ),
        name='registration_activate'),
    #url(r'^accounts/', include('registration.backends.hmac.urls')),
    
    

    url(r'^register/$', register),
    url(r'^register/success/$', register_success),
    url(r'^home/$', home),
    
    url(r'^org_create/$', OrgCreateView.as_view())
    #url(r'^join_org/$', start),


]
