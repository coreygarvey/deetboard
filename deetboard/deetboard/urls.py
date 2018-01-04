"""deetboard URL Configuration

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
from django.conf.urls.static import static

from django.contrib.auth.views import login, password_reset_confirm, password_reset_complete

from accounts.forms import AccountRegistrationForm, MyRegistrationForm, MyActivationForm

from views import home, home_dash
from accounts.views import register, register_success, logout_page, custom_login, RemoveCCView
from accounts.views import RegistrationTypeView, RegistrationView, ActivationView, InvitationView, HomeInvitationView, GeneralInvitationView, ReactivateView, FindOrgView, ProfileUpdateView, ProfileView, ProfilePublicView

from views import IndexView
from orgs.views import FrontOrgCreateView, HomeOrgCreateView, OrgHomeView, OrgPaymentView, OrgProductsView
from products.views import ProductCreateView, ProductView, ProductCreateFirstView, ProductUpdateView, ProductDeleteView, FeatureCreateView, FeatureCreateFirstView, FeatureView, FeatureListView, FeatureUpdateView, FeatureDeleteView
from questions.views import QuestionCreateView, QuestionView, QuestionListView, ResponseCreateView

from annotations.views import annotations, annotation_search

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

    url(r'^invitation/(?P<pk>\d+)?(.*)$',
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

    url(r'^first-sub/$',
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
    url(r'^home/dashboard/$', 
        home_dash,
        name = 'home_dash'
    ),

    # After Registration
    url(r'^home/profile/$', 
        ProfileView.as_view(
            ),
        name = 'profile'
    ),

     # Remove Account Card
    url(r'^home/profile/delete-card/$', 
        RemoveCCView.as_view(
            ),
        name = 'remove_cc'
    ),

    # After Registration
    url(r'^home/profile/update/$', 
        ProfileUpdateView.as_view(
            ),
        name = 'profile_update'
    ),

    url(r'^home/profile/(?P<pk>\d+)/$', 
        ProfilePublicView.as_view(
            ),
        name = 'profile_public'
    ),

    # Team Home
    url(r'^home/team/(?P<pk>\d+)/$', 
        OrgHomeView.as_view(
            ),
        name = 'org_home'
    ),

    # Team Payments
    url(r'^home/team/(?P<pk>\d+)/payment/$', 
        OrgPaymentView.as_view(
            ),
        name = 'org_payment'
    ),
    
    url(r'^home/team/(?P<pk>\d+)/products/$', 
        OrgProductsView.as_view(
            ),
        name = 'org_products'
    ),
    

    # Create Org
    url(r'^home/create-team/$',
        HomeOrgCreateView.as_view(
            ),
        name = 'org_create_home'
    ),


    url(r'^home/team/(?P<pk>\d+)/invitation/$',
        HomeInvitationView.as_view(),
        name='new_org_invitation_home',
    ),

    url(r'^home/team/(?P<pk>\d+)/create-product/first$',
        ProductCreateFirstView.as_view(),
        name='product_create_first',
    ),

    url(r'^home/team/(?P<pk>\d+)/create-product/$',
        ProductCreateView.as_view(),
        name='product_create_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<pk>\d+)/$',
        ProductView.as_view(),
        name='product_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<pk>\d+)/update/$',
        ProductUpdateView.as_view(),
        name='product_update',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<pk>\d+)/delete/$',
        ProductDeleteView.as_view(),
        name='product_delete',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/create-feature/first$',
        FeatureCreateFirstView.as_view(),
        name='feature_create_first',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/create-feature/$',
        FeatureCreateView.as_view(),
        name='feature_create_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/feature/(?P<pk>\d+)/$',
        FeatureView.as_view(),
        name='feature_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/feature/(?P<pk>\d+)/update/$',
        FeatureUpdateView.as_view(),
        name='feature_update',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/feature/(?P<pk>\d+)/delete/$',
        FeatureDeleteView.as_view(),
        name='feature_delete',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/features/$',
        FeatureListView.as_view(),
        name='feature_list_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/questions/$',
        QuestionListView.as_view(),
        name='question_list_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/feature/(?P<fpk>\d+)/ask-a-question/$',
        QuestionCreateView.as_view(),
        name='feature_create_question',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/ask-a-question/$',
        QuestionCreateView.as_view(),
        name='product_question_create',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/feature/(?P<fpk>\d+)/question/(?P<qpk>\d+)/$',
        QuestionView.as_view(),
        name='question_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/question/(?P<qpk>\d+)/$',
        QuestionView.as_view(),
        name='question_home',
    ),

    url(r'^home/team/(?P<opk>\d+)/prod/(?P<ppk>\d+)/feature/(?P<fpk>\d+)/question/(?P<pk>\d+)/respond$',
        ResponseCreateView.as_view(),
        name='question_create_response',
    ),

    #url(r'^join_org/$', start),
    # Annotations
    url(r'^annotations/annotation/$', 
        annotations,
        name = 'annotations'
    ),

    url(r'^annotations/_search$', 
        annotation_search,
        name = 'annotation_search'
    ),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

