from django.shortcuts import render
from models import EngagementList, TopList
from serializers import EngagementListSerializer, TopListSerializer
from rest_framework import generics
from django.http import HttpResponse
from django.views import View
import services

class EngagementListList(generics.ListCreateAPIView):
    queryset = EngagementList.objects.all()
    serializer_class = EngagementListSerializer

class EngagementListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = EngagementList.objects.all()
    serializer_class = EngagementListSerializer


class TopListList(generics.ListCreateAPIView):
    queryset = TopList.objects.all()
    serializer_class = TopListSerializer

class TopListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TopList.objects.all()
    serializer_class = TopListSerializer