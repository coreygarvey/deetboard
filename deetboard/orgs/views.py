from django.shortcuts import render
from models import Org, Expert, Skill
from serializers import OrgSerializer, ExpertSerializer, SkillSerializer
from rest_framework import generics, permissions

from django.contrib.auth.models import Group

from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.core.urlresolvers import reverse
import services
from core.permissions import IsAdminOrReadOnly
from forms import OrgForm

from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from django.views.decorators.csrf import csrf_protect

from django.views.generic import CreateView, TemplateView, DetailView
from braces.views import LoginRequiredMixin
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm

import re

class OrgCreateView(LoginRequiredMixin, CreateView):
    form_class = OrgForm
    
    def form_valid(self, form):        
        form.instance.admin = self.request.user
        
        

        email = self.request.user.email
        domain = re.search("@[\w.]+", email)
        # Need to check domain against common domains
        form.instance.email_domain = domain.group()

        
        return super(OrgCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(OrgCreateView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs


class FrontOrgCreateView(OrgCreateView):
    template_name = 'orgs/org-create-front.html'

    def get_success_url(self):
        org_pk = self.object.id
        org = Org.objects.get(pk=org_pk)
        current_user = self.request.user
        current_user.save()
        current_user.orgs.add(org)

        # Give permissions to admin
        assign_perm('delete_org', current_user, org)

        # Create group for this Org, add user, set view perm
        groupName = org.title + str(org.pk)
        orgUserGroup = Group.objects.create(name=groupName)
        current_user.groups.add(orgUserGroup)
        assign_perm('view_org', orgUserGroup, org)
        assign_perm('create_prod', orgUserGroup, org)
        assign_perm('create_feat', orgUserGroup, org)
        assign_perm('create_anno', orgUserGroup, org)
        assign_perm('create_quest', orgUserGroup, org)

        if current_user.primary_org is None:
            current_user.primary_org = org
            current_user.save()
        return reverse('new_org_invitation_front',args=(self.object.id,))

class HomeOrgCreateView(OrgCreateView):
    template_name = 'orgs/org-create-home.html'

    def get_success_url(self):
        org_pk = self.object.id
        org = Org.objects.get(pk=org_pk)
        current_user = self.request.user
        current_user.save()
        current_user.orgs.add(org)

        # Give permissions to admin
        assign_perm('delete_org', current_user, org)


        # Create group for this Org, add user, set view perm
        groupName = org.title + str(org.pk)
        orgUserGroup = Group.objects.create(name=groupName)
        current_user.groups.add(orgUserGroup)
        assign_perm('view_org', orgUserGroup, org)
        assign_perm('create_prod', orgUserGroup, org)
        assign_perm('create_feat', orgUserGroup, org)
        assign_perm('create_anno', orgUserGroup, org)
        assign_perm('create_quest', orgUserGroup, org)
        
        return reverse('new_org_invitation_home',args=(self.object.id,))



class OrgHomeView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    
    """
    model = Org
    template_name = "orgs/org-home.html"
    permission_required = 'orgs.view_org'

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(OrgHomeView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        user_orgs = user.orgs.all()
        products = org.products.all()
        context['user'] = user
        context['org'] = org
        context['user_orgs'] = user_orgs
        context['products'] = products
        return context

    def get_user(self, username):        
        #Given the verified username, look up and return the
        #corresponding user account if it exists, or ``None`` if it
        #doesn't.
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username,
        }
        try:
            user = User.objects.get(**lookup_kwargs)
            return user
        except User.DoesNotExist:
            return None

class OrgProductsView(TemplateView):
    """
    
    """
    template_name = "orgs/org-products.html"

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(OrgProductsView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        user_orgs = user.orgs.all()
        products = org.products.all()
        context['user'] = user
        context['org'] = org
        context['user_orgs'] = user_orgs
        context['products'] = products
        return context



    def get_user(self, username):        
        #Given the verified username, look up and return the
        #corresponding user account if it exists, or ``None`` if it
        #doesn't.
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username,
        }
        try:
            user = User.objects.get(**lookup_kwargs)
            return user
        except User.DoesNotExist:
            return None



class OrgList(generics.ListCreateAPIView):
    queryset = Org.objects.all()
    serializer_class = OrgSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class OrgDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Org.objects.all()
    serializer_class = OrgSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                            IsAdminOrReadOnly,)

class ExpertList(generics.ListCreateAPIView):
    queryset = Expert.objects.all()
    serializer_class = ExpertSerializer

class ExpertDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expert.objects.all()
    serializer_class = ExpertSerializer


class SkillList(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class SkillDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
