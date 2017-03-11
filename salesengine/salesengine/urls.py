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
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from django.contrib.auth.views import login, password_reset_confirm, password_reset_complete

from accounts.forms import AccountRegistrationForm, MyRegistrationForm, MyActivationForm

from views import home
from accounts.views import register, register_success, logout_page, custom_login
from accounts.views import RegistrationTypeView, RegistrationView, ActivationView, InvitationView, HomeInvitationView, GeneralInvitationView, ReactivateView, FindOrgView, ProfileUpdateView, ProfileView

from views import IndexView
from orgs.views import FrontOrgCreateView, HomeOrgCreateView, OrgHomeView
from products.views import ProductCreateView, ProductView, FeatureCreateView, FeatureView
from questions.views import QuestionCreateView, QuestionView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^orgs/', include('orgs.urls'), name="org"),

    url(r'^api/', include('core.api'), name="api"),
    #url(r'^login/$', login),
    url(r'^login/$', custom_login),
    url(r'^logout/$', logout_page),


    # Account Registration Views
    # Remove this?!
    url(r'^accounts/register/$', 
        RegistrationTypeView.as_view()
    ),

    url(r'^$',
        RegistrationView.as_view(),
        name='landing',
    ), 

    url(r'^new_org/$',
        RegistrationView.as_view(),
        name='new_org',
    ), 

    url(r'^activate/(?P<activation_key>[-:\w]+)/$',
        ActivationView.as_view(),
        name='activate',
    ),

    url(r'^create_org/',
        FrontOrgCreateView.as_view(),
        name = 'new_org'
    ),

    url(r'^new_org/invitation/(?P<pk>\d+)/$',
        InvitationView.as_view(),
        name='new_org_invitation_front',
    ),

    url(r'^invitation/(?P<pk>\d+)/$',
        GeneralInvitationView.as_view(),
        name='general_invitation',
    ),

    url(r'^find_org/$',
        FindOrgView.as_view(),
        name='find_org',
    ),

    # Page shown after invitations sent
    url(r'^find_org/complete/$',
        TemplateView.as_view(
            template_name='registration/find_org_complete.html'
        ),
        name='find_org_complete'
    ),

    url(r'^reactivate/$',
        ReactivateView.as_view(),
        name='reactivate',
    ), 

    url(r'^accounts/login/$', 
        login,
    ), # If user is not login it will redirect to login page
     
    # Page shown after invitations sent
    url(r'^invitation/complete/$',
        TemplateView.as_view(
            template_name='registration/invitation_complete.html'
        ),
        name='invitation_complete'
    ),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm'),

    url(r'^reset/complete/$', password_reset_complete, name='password_reset_complete'),

    url(r'^accounts/', include('registration.backends.hmac.urls')),
    
    url(r'^register/success/$', register_success),
    

    url(r'^contact/$',
        TemplateView.as_view(
            template_name='contact.html'
        ),
        name='contact'
    ),

    url(r'^product/$',
        TemplateView.as_view(
            template_name='product.html'
        ),
        name='product'
    ),

    url(r'^pricing/$',
        TemplateView.as_view(
            template_name='pricing.html'
        ),
        name='pricing'
    ),


    # After Registration
    url(r'^home/$', 
        home,
        name = 'home'
    ),

    # After Registration
    url(r'^home/profile/$', 
        ProfileView.as_view(
            ),
        name = 'profile'
    ),

    # Team Home
    url(r'^home/(?P<pk>\d+)/$$', 
        OrgHomeView.as_view(
            ),
        name = 'org_home'
    ),
    

    # Create Org
    url(r'^home/create-team/$',
        HomeOrgCreateView.as_view(
            ),
        name = 'org_create_home'
    ),


    url(r'^home/(?P<pk>\d+)/invitation/$',
        HomeInvitationView.as_view(),
        name='new_org_invitation_home',
    ),

    url(r'^home/(?P<pk>\d+)/create-product/$',
        ProductCreateView.as_view(),
        name='product_create_home',
    ),

    url(r'^home/(?P<opk>\d+)/(?P<ppk>\d+)/$',
        ProductView.as_view(),
        name='product_home',
    ),

    url(r'^home/(?P<opk>\d+)/(?P<ppk>\d+)/create-feature/$',
        FeatureCreateView.as_view(),
        name='feature_create_home',
    ),

    url(r'^home/(?P<opk>\d+)/(?P<ppk>\d+)/(?P<fpk>\d+)/$',
        FeatureView.as_view(),
        name='feature_home',
    ),

    url(r'^home/(?P<opk>\d+)/(?P<ppk>\d+)/(?P<fpk>\d+)/ask-a-question/$',
        QuestionCreateView.as_view(),
        name='question_create_home',
    ),

    url(r'^home/(?P<opk>\d+)/(?P<ppk>\d+)/question/(?P<qpk>\d+)/$',
        QuestionView.as_view(),
        name='question_home',
    ),

    #url(r'^join_org/$', start),


]

urlpatterns += staticfiles_urlpatterns()
