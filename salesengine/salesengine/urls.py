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


from django.contrib.auth.views import login, password_reset_confirm, password_reset_complete
#from registration.backends.hmac.views import RegistrationView

from accounts.forms import AccountRegistrationForm, MyRegistrationForm, MyActivationForm
from accounts.views import register, register_success, logout_page, home, AccountActivationView, AccountRegistrationView, AccountRegistrationTypeView, InvitationView, AccountReactivateView, AccountFindOrgView, MultiActivationView

from views import IndexView
from orgs.views import OrgCreateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^orgs/', include('orgs.urls'), name="org"),

    url(r'^api/', include('core.api'), name="api"),
    url(r'^$', login),
    url(r'^logout/$', logout_page),

    url(r'^accounts/register/$', AccountRegistrationTypeView.as_view()),


    url(r'^accounts/activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ),
        name='registration_activation_complete'),

    url(r'^accounts/login/$', login), # If user is not login it will redirect to login page
    

    # URLs for registration when creating new organization
    # Registration
    url(r'^accounts/new_org/register/$',
        AccountRegistrationView.as_view(),
        name='registration_register',
    ),  

    url(r'^accounts/new_org/activate/(?P<activation_key>[-:\w]+)/$',
        AccountActivationView.as_view(),
        name='new_org_registration_activate'),

    url(r'^accounts/multi/activate/org/(?P<org_id>[0-9]+)/(?P<activation_key>[-:\w]+)/$',
        MultiActivationView.as_view(),
        name='multi_registration_activate'),

    url(r'^accounts/new_org/create_org/',
        OrgCreateView.as_view(
            ),
        name = 'new_org'),


    # Reauthenticate with an email
    url(r'^accounts/reactivate/$',
        AccountReactivateView.as_view(),
        name='registration_reactivate',
    ),  

    # Invitations to coworkers after Org is created
    #url(r'^accounts/new_org/invite/&', org_invite)

    url(r'^orgs/(?P<pk>\d+)/invitation/$',
        InvitationView.as_view(),
        name='new_org_invitation',
    ),

    url(r'^accounts/invitation/complete/$',
        TemplateView.as_view(
            template_name='registration/invitation_complete.html'
        ),
        name='invitation_complete'),



    
    url(r'^accounts/find_org/register/$',
        AccountFindOrgView.as_view(),
        name='registration_register',
    ),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm'),

    url(r'^reset/complete/$', password_reset_complete, name='password_reset_complete'),

    
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    
    

    
    url(r'^register/success/$', register_success),
    url(r'^home/$', home),
    
    url(r'^org_create/$', OrgCreateView.as_view())
    #url(r'^join_org/$', start),
]
