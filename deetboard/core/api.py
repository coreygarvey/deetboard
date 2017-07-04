"""
Called from the project root's urls.py URLConf:
	url(r"^/", include("core.api"), namespace = "api"),
"""

#from django.conf.urls.defaults import patterns, url
from rest_framework import routers
from django.conf.urls import url, include

urlpatterns = [
	url(r'^', include('accounts.urls')),
	url(r'^', include('products.urls')),
	url(r'^', include('feature_lists.urls')),
	url(r'^', include('screenshots.urls')),
	url(r'^', include('questions.urls')),
]