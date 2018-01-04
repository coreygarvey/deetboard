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
import stripe
import datetime
import time


stripe.api_key = "sk_test_3aMNJsprXJcMdh1KffsskjMB"

class OrgCreateView(LoginRequiredMixin, CreateView):
    form_class = OrgForm
    
    def form_valid(self, form):        
        # Create org with current user as admin of group and customer
        current_user = self.request.user
        form.instance.admin = current_user
        
        email = current_user.email
        domain = re.search("@[\w.]+", email)
        # Need to check domain against common domains
        form.instance.email_domain = domain.group()

        org = form.instance

        self.create_initial_subscription(current_user, org)
        return super(OrgCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(OrgCreateView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs

    def create_initial_subscription(self, current_user, org):
        # Retrieve customer from user's stripe_id
        customer_id = current_user.stripe_id
        # Set your secret key: remember to change this to your live secret key in production
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        import stripe
        stripe.api_key = "sk_test_3aMNJsprXJcMdh1KffsskjMB"
        
        # End now + 3 minutes and print that time
        now = datetime.datetime.now()
        now_plus_3 = now + datetime.timedelta(minutes = 3)
        now_plus_3_int = int(now_plus_3.strftime("%s"))


        subscription = stripe.Subscription.create(
          customer=customer_id,
          items=[
            {
              "plan": "basic-plan",
            },
          ],

          trial_end=now_plus_3_int,
        )

        # Initial org subscription
        subscription_id = subscription.id
        # trial or monthly
        subscription_type = "trial"
        # active, inactive, or failed (CC not working)
        subscription_status = "inactive"

        current_period_start = datetime.datetime.fromtimestamp(subscription.current_period_start)
        current_period_end = datetime.datetime.fromtimestamp(subscription.current_period_end)
        subscription_amount = round(subscription.plan.amount/float(100), 2)

        print "Subscription details being stored: "
        print subscription_id
        # trial or monthly
        print subscription_type
        # active, inactive, or failed (CC not working)
        print subscription_status

        print current_period_start
        print current_period_end
        print subscription_amount

        org.set_subscription(subscription_id, subscription_type,
                                subscription_status, current_period_start,
                                current_period_end, subscription_amount)
        org.update_sub_status_int()
        


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
        
        # Indicate if user is admin to 
        org_admin = org.admin
        if user == org.admin:
            print "User is admin of this org:"
            context['admin'] = True
        else:
            context['admin'] = False

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

class OrgPaymentView(LoginRequiredMixin, TemplateView):
#class OrgPaymentView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    
    """
    template_name = "orgs/org-payment.html"
    
    # Use permissions like below instead of dispatch for protecting pages
    #permission_required = 'orgs.view_org'
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        if user != org.admin:
            url = reverse('org_home', kwargs={'pk': org_pk})
            return HttpResponseRedirect(url)
        return super(OrgPaymentView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(OrgPaymentView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        
        context['user'] = user
        print user.cc_last_four
        context['org'] = org
        
        # Indicate if user is admin to 
        org_admin = org.admin
        if user == org.admin:
            context['admin'] = True

            #if org.subscription_id:
                #subscription_id = org.subscription_id
                #subscription = stripe.Subscription.retrieve(subscription_id)
                
               
                #trial_end = subscription['trial_end']
                #sub_status = subscription['status']
                
                # Check if still in trial
                #created = datetime.datetime.fromtimestamp(
                #            int(subscription["created"])
                #            ).strftime('%B %-d, %Y')

                #current_end_date = datetime.datetime.fromtimestamp(
                #                int(subscription["current_period_end"])
                #                ).strftime('%B %-d, %Y')
                #context['current_end_date'] = current_end_date

                # Only get current_start for users not in trial
                #if sub_status != "trialing":
                #    current_start_date = datetime.datetime.fromtimestamp(
                #                    int(subscription["current_period_start"])
                #                    ).strftime('%B %-d, %Y')
                #    context['current_start_date'] = current_start_date
                

                #next_payment_amount = "%.2f" % round(subscription["plan"]["amount"]/float(100), 2)
                #context['next_payment_amount'] = next_payment_amount
                

                #if sub_status == "trialing":
                #    print "not"
                #else:
                    # Out of trial
                    # If paid bill
                #    print "great"

            # Include admin payment details
            if user.cc_last_four:
                context['user_cc'] = True
            else:
                context['user_cc'] = False

        

        else:
            context['admin'] = False

        return context


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
