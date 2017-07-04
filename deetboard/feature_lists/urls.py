"""
Called from the project core.api, which is then passed to root:
	url(r'^', include('feature_lists.urls')),
"""

#from django.conf.urls.defaults import patterns, url
from django.conf.urls import url
import views as feature_lists_views

urlpatterns = [
	url(
		regex=r"^engagement-lists/$",
		view=feature_lists_views.EngagementListList.as_view(),
		name="engagemet_lists"
	),
	url(
		regex=r"^engagement-lists/(?P<slug>[-\w]+)/$",
		view=feature_lists_views.EngagementListDetail.as_view(),
		name="engagement_lists"
	),
	url(
		regex=r"^top-lists/$",
		view=feature_lists_views.TopListList.as_view(),
		name="top_lists"
	),
	url(
		regex=r"^top-lists/(?P<slug>[-\w]+)/$",
		view=feature_lists_views.TopListDetail.as_view(),
		name="top_lists"
	),
]