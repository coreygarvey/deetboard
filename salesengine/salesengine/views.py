from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from orgs.models import Org


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
    return render_to_response(
        'home/home.html',
        { 
            'user': current_user,
            'user_orgs': user_orgs,
            'admin_orgs': admin_orgs
        }
    )