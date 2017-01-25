from django.shortcuts import render
from models import Org, Expert, Skill
from serializers import OrgSerializer, ExpertSerializer, SkillSerializer
from rest_framework import generics, permissions

from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
import services
from core.permissions import IsAdminOrReadOnly
from forms import OrgForm


from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from django.views.decorators.csrf import csrf_protect

from django.views.generic import CreateView
from braces.views import LoginRequiredMixin


class OrgCreateView(LoginRequiredMixin, CreateView):
    form_class = OrgForm
    template_name = 'registration/org_create_form.html'
    success_url = '/accounts/new_org/create_org/'

    def form_valid(self, form):        
        form.instance.admin = self.request.user
        #self.request.user.
        return super(OrgCreateView, self).form_valid(form)
    def form_invalid(self, form):
        return HttpResponse("Form is invalid")

"""
# Invitations after Org is created
# Pull from AccountRegistrationView
def org_invite(request):
    extra_questions = get_questions(request)
    form = OrgInviteForm(request.POST or None, extra=extra_questions)
    if form.is_valid():
        for (question, answer) in form.extra_answers():
            save_answer(request, question, answer)
        return redirect("create_user_success")

    return render_to_response("signup/form.html", {'form': form})
"""

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
