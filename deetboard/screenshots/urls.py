"""
Called from the project core.api, which is then passed to root:
	url(r'^', include('screenshots.urls')),
"""

#from django.conf.urls.defaults import patterns, url
from django.conf.urls import url
import views as screenshot_views

urlpatterns = [
	url(
		regex=r"^screenshots/$",
		view=screenshot_views.ScreenshotList.as_view(),
		name="screenshots"
	),
	url(
		regex=r"^screenshots/(?P<slug>[-\w]+)/$",
		view=screenshot_views.ScreenshotDetail.as_view(),
		name="screenshots"
	),
]