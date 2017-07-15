from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Create your views here.
@csrf_exempt
def annotations(request):

    if request.method == 'POST':
        print "Got the POST!"
        print request.body
        jsonObj = json.loads(request.body)
        source = jsonObj["src"]
        print source
        # Handle post method
    else:  # request.method == 'GET'
        # Handle get method
        print "looks like a GET"


@csrf_exempt
def annotation_search(request):

    if request.method == 'POST':
        print "Got the POST!"
        print request.POST
        

        # Handle post method
    else:  # request.method == 'GET'
		# Handle get method
		print request
		print "looks like a GET"
        
		myReturn = '{"src":"http://127.0.0.1:8000/static/photos/YosemiteProfile.jpg","text":"new","shapes":[{"type":"rect","geometry":{"x":0.7125,"y":0.05333333333333334,"width":0.2125,"height":0.15555555555555556},"style":{}}],"context":"http://127.0.0.1:8000/home/team/8/prod/2/create-feature/"}';

		shapes = [];
		shape1 = {};
		shape1['type'] = 'rect';
		rectGeometry = {};
		rectGeometry["x"] = 0.7125;
		rectGeometry["y"] = 0.05333;
		rectGeometry["width"] = 0.215;
		rectGeometry["height"] = 0.16;
		shape1['geometry'] = rectGeometry;
		shape1['style'] = {};
		shapes.append(shape1);


		returnData = {};



		annotation1 = {}
		
		annotation1['src'] = 'http://127.0.0.1:8000/static/photos/YosemiteProfile.jpg';
		annotation1['shapes'] = shapes;
		annotation1['context'] = "http://127.0.0.1:8000/home/team/8/prod/2/create-feature/";
		annotation1['text'] = "FUCK YEAH";

		annotation1Object = {};
		annotation1Object['_id'] = 1;
		annotation1Object['_source'] = annotation1;

		annotations=[]
		annotations.append(annotation1Object);
		hits = {};
		hits['hits'] = annotations;
		returnData['hits'] = hits;
		print returnData;
		return JsonResponse(returnData);
		