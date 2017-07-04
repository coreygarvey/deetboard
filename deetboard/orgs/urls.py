"""
Called from the project core.api, which is then passed to root:
	url(r'^', include('orgs.urls')),
"""

#from django.conf.urls.defaults import patterns, url
from django.conf.urls import url
from views import FrontOrgCreateView
import views as org_views

urlpatterns = [
	url(
		regex=r"^create/$",
		view=FrontOrgCreateView.as_view(),
		name="create"
	),
	
	url(
		regex=r"^orgs/$",
		view=org_views.OrgList.as_view(),
		name="orgs"
	),
	url(
		regex=r"^orgs/(?P<slug>[-\w]+)/$",
		view=org_views.OrgDetail.as_view(),
		name="orgs"
	),
	url(
		regex=r"^experts/$",
		view=org_views.ExpertList.as_view(),
		name="experts"
	),
	url(
		regex=r"^experts/(?P<slug>[-\w]+)/$",
		view=org_views.ExpertDetail.as_view(),
		name="experts"
	),
	url(
		regex=r"^skills/$",
		view=org_views.SkillList.as_view(),
		name="skills"
	),
	url(
		regex=r"^skills/(?P<slug>[-\w]+)/$",
		view=org_views.SkillDetail.as_view(),
		name="skills"
	),
]