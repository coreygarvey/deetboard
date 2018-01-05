from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from orgs.models import Org
from orgs.views import OrgHomeView


class IndexView(TemplateView):
    template_name = 'index.html'

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


@login_required
def home(request):
    current_user = request.user
    user_orgs = current_user.orgs.all()
    admin_orgs = Org.objects.filter(admin=current_user)
    primary_org = current_user.primary_org
    

    if primary_org:
        return redirect('org_home', pk=primary_org.id)
    
    return render_to_response(
        'home/home.html',
        { 
            'user': current_user,
            'user_orgs': user_orgs,
            'admin_orgs': admin_orgs
        }
    )

@login_required
def home_dash(request):
    current_user = request.user
    user_orgs = current_user.orgs.all()
    admin_orgs = Org.objects.filter(admin=current_user)
    
    return render_to_response(
        'home/home.html',
        { 
            'user': current_user,
            'user_orgs': user_orgs,
            'admin_orgs': admin_orgs
        }
    )


def stripe_webhooks(request):
    print "REQUEST FROM WEBHOOKS"
    print request

    # Write Pseudocode for each of the webhooks that will be sent for different payments and resulting actions
    # Add next payment date to Org
    # For failed payment, determine where and how payment will be paid
'''
    charge_success
        send email
        if sub_status_int <= 1
            set org_subscription_type to monthly

        update org_status = paid
        if unpaid_invoice: 
            set=''
            Change subscription to make startdate now and end date 1 cycle from now

        update sub_status_int

        retrieve subscription:
            update org.current_period_start
            update org.current_period_end


    charge_failure
        send emaii
        if sub_status_int <= 1
            set org subscription_type to monthly

        update org_status = unpaid
        
        get org_subscription_id
        get subscription and customer invoice linked to subscription 
        update org_unpaid_invoice = invoice

        update sub_status_int
'''
    #charge_fail




