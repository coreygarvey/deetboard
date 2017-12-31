from django.shortcuts import render, redirect
from models import Question, Response
from serializers import QuestionSerializer, ResponseSerializer
from rest_framework import generics
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import UpdateView
from django.http import HttpResponse
from django.views import View
import services
from django.conf import settings
from django.template.loader import render_to_string
from forms import QuestionForm, QuestionFeaturesForm, ResponseForm
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

    ask_question_email_body_template = 'questions/emails/ask_question_email_body.txt'
    ask_question_email_body_html_template = 'questions/emails/ask_question_email_body.html'
    ask_question_email_subject_template = 'questions/emails/ask_question_email_subject.txt'

    # Check that user has permission to create questions in this org
    def dispatch(self, *args, **kwargs):
        user = self.request.user
        org_pk = self.kwargs['opk']
        org = Org.objects.get(pk=org_pk)
        feature_create_perm = user.has_perm('orgs.create_quest', org)
        if(not feature_create_perm):
            return redirect('/home/')
        return super(QuestionCreateView, self).dispatch(*args, **kwargs)
    
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
        current_user = self.request.user
        form.instance.user_asking = current_user
        form.instance.admin = current_user
        
        # Redirect user if they don't have permission
        if(not current_user.has_perm('create_quest', org)):
            return HttpResponseRedirect('/home/')

        question = form.save(commit=False)
        question.save()

        # If created in a feature, add to features field and send email
        if 'fpk' in self.kwargs:
            feature_pk = self.kwargs['fpk']
            feature = Feature.objects.get(pk=feature_pk)
            question.features.add(feature)
            # Only send email if part of a feature
            self.send_question_emails(question, feature)

        return super(QuestionCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(QuestionCreateView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs

    def send_question_emails(self, question, feature):
        """
        Send an email to all experts asking the question.
        """
        # Get the question txt
        # Insert necessary information into context
        # Create messages and variables
        # Render text to string
        # Get experts of feature
        # Email all experts
        
        question_pk = question.pk
        print "question_pk: " 
        print question_pk

        question_text = question.text
        print "question-text: " 
        print question_text

        asker_un = question.user_asking.username
        print "asker_un: " 
        print asker_un


        context = {}
        context.update({
            'question_pk': question_pk,
            'question_text': question_text,
            'asker': asker_un,
        })

        subject_var = self.ask_question_email_subject_template
        message_var = self.ask_question_email_body_template
        html_message_var = self.ask_question_email_body_html_template
        
        subject = render_to_string(subject_var,context)
        message = render_to_string(message_var,context)
        html_message = render_to_string(html_message_var,context)
        # Force subject to a single line to avoid header-injection
            # issues.
        subject = ''.join(subject.splitlines())
        
        experts = feature.experts.all()
        for expert in experts:
            expert.email_user(subject, message, settings.DEFAULT_FROM_EMAIL, 
                        html_message=html_message)



    def get_success_url(self):
        question = self.object
        product = self.object.product
        org = product.org
        feature = question.features.all()[0]
        print "feature ID: "
        print feature.id
        groupName = org.title + str(org.pk)
        orgUserGroup = Group.objects.get(name=groupName)
        assign_perm('view_quest', orgUserGroup, question)
        current_user = self.request.user
        assign_perm('questions.delete_question', current_user, question)

        return reverse('question_home', 
        			args=(
        				self.object.product.org.id,
        				self.object.product.id,
                        feature.id,
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
        feature_pk = self.kwargs['fpk']
        feature = Feature.objects.get(pk=feature_pk)
        user_orgs = user.orgs.all()
        org_products = org.products.all()
        prod_features = product.features.all()
        question_pk = self.kwargs['qpk']
        question = Question.objects.get(pk=question_pk)
        responses = question.responses.all()
        question_features = question.features.all()
        context['user'] = user
        context['org'] = org
        context['product'] = product
        context['feature'] = feature
        context['user_orgs'] = user_orgs
        context['prod_features'] = prod_features
        context['org_products'] = org_products
        context['question'] = question
        context['responses'] = responses
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

class ResponseCreateView(LoginRequiredMixin, CreateView):
    form_class = ResponseForm
    template_name = 'responses/response-create-home.html'

    # Check that user has permission to create questions in this org
    def dispatch(self, *args, **kwargs):
        user = self.request.user
        feature_pk = self.kwargs['fpk']
        feature = Feature.objects.get(pk=feature_pk)
        response_create_perm = user.has_perm('products.create_response', feature)
        if(not response_create_perm):
            return redirect('/home/')
        return super(ResponseCreateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(ResponseCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['opk']
        org = Org.objects.get(pk=org_pk)
        user_orgs = user.orgs.all()
        products = org.products.all()
        product_pk = self.kwargs['ppk']
        product = Product.objects.get(pk=product_pk)
        features = product.features.all()
        feature_pk = self.kwargs['fpk']
        feature = Feature.objects.get(pk=feature_pk)
        quest_pk = self.kwargs['pk']
        question = Question.objects.get(pk=quest_pk)
        context['user'] = user
        context['org'] = org
        context['user_orgs'] = user_orgs
        context['org_products'] = products
        context['product'] = product
        context['prod_features'] = features
        context['question'] = question
        context['feature'] = feature
            
        return context

    def form_valid(self, form):        
        feat_pk = self.kwargs['fpk']
        feature = Feature.objects.get(pk=feat_pk)
        quest_pk = self.kwargs['pk']
        question = Question.objects.get(pk=quest_pk)
        current_user = self.request.user
        form.instance.question = question
        form.instance.admin = current_user
        form.instance.user_responder = current_user
        form.instance.accepted = False
        
        # Redirect user if they don't have permission
        if(not current_user.has_perm('create_response', feature)):
            return HttpResponseRedirect('/home/')

        response = form.save(commit=False)
        response.save()

        return super(ResponseCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ResponseCreateView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs

    def get_success_url(self):
        response = self.object

        product = response.question.product
        org = product.org
        groupName = org.title + str(org.pk)
        orgUserGroup = Group.objects.get(name=groupName)
        assign_perm('view_response', orgUserGroup, response)
        current_user = self.request.user
        assign_perm('questions.delete_response', current_user, response)

        return reverse('question_home', 
                    args=(
                        self.object.question.product.org.id,
                        self.object.question.product.id,
                        self.object.question.id
                        )
                    )



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