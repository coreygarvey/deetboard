from django.shortcuts import render
from django.core.urlresolvers import reverse
from models import Product, Feature, Link
from serializers import ProductSerializer, FeatureSerializer, LinkSerializer
from rest_framework import generics
from django.views.generic import CreateView, TemplateView
from braces.views import LoginRequiredMixin
from forms import ProductForm
from orgs.models import Org

from django.http import HttpResponse
from django.views import View
import services




class ProductCreateView(LoginRequiredMixin, CreateView):
    form_class = ProductForm
    template_name = 'products/product-create-home.html'
    
    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)
        user_orgs = user.orgs.all()
        products = org.products.all()
        context['user'] = user
        context['org'] = org
        context['user_orgs'] = user_orgs
        context['org_products'] = products
        return context

    def form_valid(self, form):        
        org_pk = self.kwargs['pk']
        org = Org.objects.get(pk=org_pk)

        form.instance.org = org

        
        return super(ProductCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ProductCreateView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('product_home', args=(self.object.org.id,self.object.id))

class ProductHomeView(TemplateView):
    """
    
    """
    template_name = "products/product-home.html"

    def get_context_data(self, **kwargs):
        """Use this to add extra context (the user)."""
        context = super(ProductHomeView, self).get_context_data(**kwargs)
        user = self.request.user
        org_pk = self.kwargs['opk']
        org = Org.objects.get(pk=org_pk)
        product_pk = self.kwargs['ppk']
        product = Product.objects.get(pk=product_pk)
        user_orgs = user.orgs.all()
        org_products = org.products.all()
        context['user'] = user
        context['org'] = org
        context['product'] = product
        context['user_orgs'] = user_orgs
        context['org_products'] = org_products
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



class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class FeatureList(generics.ListCreateAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

class FeatureDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer


class LinkList(generics.ListCreateAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer

class LinkDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer