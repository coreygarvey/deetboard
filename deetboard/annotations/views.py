from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def annotations(request):

    if request.method == 'POST':
        print "Got the POST!"
        print request.POST
        # Handle post method
    else:  # request.method == 'GET'
        # Handle get method
        print "looks like a GET"
