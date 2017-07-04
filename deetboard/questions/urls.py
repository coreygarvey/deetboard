"""
Called from the project core.api, which is then passed to root:
	url(r'^', include('questions.urls')),
"""

#from django.conf.urls.defaults import patterns, url
from django.conf.urls import url
import views as question_views

urlpatterns = [
	url(
		regex=r"^questions/$",
		view=question_views.QuestionList.as_view(),
		name="questions"
	),
	url(
		regex=r"^questions/(?P<slug>[-\w]+)/$",
		view=question_views.QuestionDetail.as_view(),
		name="questions"
	),
	url(
		regex=r"^responses/$",
		view=question_views.ResponseList.as_view(),
		name="responses"
	),
	url(
		regex=r"^responses/(?P<slug>[-\w]+)/$",
		view=question_views.ResponseDetail.as_view(),
		name="responses"
	),
]