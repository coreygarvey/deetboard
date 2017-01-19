"""
Called from the project core.api, which is then passed to root:
	url(r'^', include('products.urls')),
"""

#from django.conf.urls.defaults import patterns, url
from django.conf.urls import url
import views as prod_views

urlpatterns = [
	url(
		regex=r"^products/$",
		view=prod_views.ProductList.as_view(),
		name="products"
	),
	url(
		regex=r"^productss/(?P<slug>[-\w]+)/$",
		view=prod_views.ProductDetail.as_view(),
		name="products"
	),
	url(
		regex=r"^features/$",
		view=prod_views.FeatureList.as_view(),
		name="features"
	),
	url(
		regex=r"^features/(?P<slug>[-\w]+)/$",
		view=prod_views.FeatureDetail.as_view(),
		name="features"
	),
	url(
		regex=r"^links/$",
		view=prod_views.LinkList.as_view(),
		name="links"
	),
	url(
		regex=r"^links/(?P<slug>[-\w]+)/$",
		view=prod_views.LinkDetail.as_view(),
		name="links"
	),
]