"""
Called from the project core.api, which is then passed to root:
	url(r'^', include('accounts.urls')),
"""

from django.conf.urls import url
import views as account_views

urlpatterns = [
	url(
		regex=r"^accounts/$",
		view=account_views.AccountListApi.as_view(),
		name="accounts"
	),
	url(
		regex=r"^accounts/(?P<slug>[-\w]+)/$",
		view=account_views.AccountDetailApi.as_view(),
		name="accounts"
	),
]