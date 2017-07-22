from django.shortcuts import render
from models import Question, Response
from serializers import QuestionSerializer, ResponseSerializer
from rest_framework import generics
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import UpdateView
from django.http import HttpResponse
from django.views import View
import services
from forms import QuestionForm, QuestionFeaturesForm
from braces.views import LoginRequiredMixin
from orgs.models import Org
from products.models import Product, Feature
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm


class QuestionCreateView(LoginRequiredMixin, CreateView):
    form_class = QuestionForm
    template_name = 'questions/question-create-home.html'
    
    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['opk']
        org = Org.objects.get(pk=org_pk)
        user_orgs = user.orgs.all()
        products = org.products.all()
        product_pk = self.kwargs['ppk']
        product = Product.objects.get(pk=product_pk)
        features = product.features.all()
        context['user'] = user
        context['org'] = org
        context['user_orgs'] = user_orgs
        context['org_products'] = products
        context['product'] = product
        context['prod_features'] = features
        if 'fpk' in self.kwargs:
            feature_pk = self.kwargs['fpk']
            feature = Feature.objects.get(pk=feature_pk)
            context['feature'] = feature
        return context

    def form_valid(self, form):        
        org_pk = self.kwargs['opk']
        org = Org.objects.get(pk=org_pk)
        prod_pk = self.kwargs['ppk']
        product = Product.objects.get(pk=prod_pk)
        form.instance.product = product
        form.instance.user_asking = self.request.user
        form.instance.admin = self.request.user

        current_user = self.request.user
        # Redirect user if they don't have permission
        if(not current_user.has_perm('create_quest', org)):
            return HttpResponseRedirect('/home/')

        question = form.save(commit=False)
        question.save()

        return super(QuestionCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(QuestionCreateView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs

    def get_success_url(self):
        question = self.object
        if 'fpk' in self.kwargs:
            feature_pk = self.kwargs['fpk']
            feature = Feature.objects.get(pk=feature_pk)
            question.features.add(feature)

        product = self.object.product
        org = product.org
        groupName = org.title + str(org.pk)
        orgUserGroup = Group.objects.get(name=groupName)
        assign_perm('view_quest', orgUserGroup, question)
        current_user = self.request.user
        assign_perm('questions.delete_question', current_user, question)

        return reverse('question_home', 
        			args=(
        				self.object.product.org.id,
        				self.object.product.id,
        				self.object.id
        				)
        			)

class QuestionView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    
    """
    form_class = QuestionFeaturesForm
    template_name = "questions/question-home.html"
    model = Question
    permission_required = 'questions.view_quest'

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(QuestionView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['opk']
        org = Org.objects.get(pk=org_pk)
        product_pk = self.kwargs['ppk']
        product = Product.objects.get(pk=product_pk)
        user_orgs = user.orgs.all()
        org_products = org.products.all()
        prod_features = product.features.all()
        question_pk = self.kwargs['qpk']
        question = Question.objects.get(pk=question_pk)
        question_features = question.features.all()
        context['user'] = user
        context['org'] = org
        context['product'] = product
        context['user_orgs'] = user_orgs
        context['prod_features'] = prod_features
        context['org_products'] = org_products
        context['question'] = question
        context['question_features'] = question_features
        context['form'].fields['features'].queryset = Feature.objects.filter(product=product)

        print context

        


        return context

    def get_object(self):
        question_pk = self.kwargs['qpk']
        question = Question.objects.get(pk=question_pk)
        print "Question!"
        print question
        return question

    def form_valid(self, form):        
        question = form.save(commit=False)
        question.save()

        return super(QuestionView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(QuestionView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs

    def get_success_url(self):
        question_pk = self.object.id
        question = Question.objects.get(pk=question_pk)
        if 'fpk' in self.kwargs:
            feature_pk = self.kwargs['fpk']
            feature = Feature.objects.get(pk=feature_pk)
            question.features.add(feature)
        return reverse('question_home', 
                    args=(
                        self.object.product.org.id,
                        self.object.product.id,
                        self.object.id
                        )
                    )

class QuestionListView(TemplateView):
    """
    
    """
    template_name = "questions/question-list-home.html"

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(QuestionListView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['opk']
        org = Org.objects.get(pk=org_pk)
        product_pk = self.kwargs['ppk']
        product = Product.objects.get(pk=product_pk)
        user_orgs = user.orgs.all()
        org_products = org.products.all()
        prod_features = product.features.all()
        prod_questions = Question.objects.filter(product=product)
        context['user'] = user
        context['org'] = org
        context['product'] = product
        context['user_orgs'] = user_orgs
        context['prod_features'] = prod_features
        context['org_products'] = org_products
        context['prod_questions'] = prod_questions
        print context
        return context

class QuestionList(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ResponseList(generics.ListCreateAPIView):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer

class ResponseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer