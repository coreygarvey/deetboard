from django.shortcuts import render

from django.shortcuts import render
from models import Screenshot
from serializers import ScreenshotSerializer
from rest_framework import generics

from django.http import HttpResponse
from django.views import View
import services

class ScreenshotList(generics.ListCreateAPIView):
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer

class ScreenshotDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer