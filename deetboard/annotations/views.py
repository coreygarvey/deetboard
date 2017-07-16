from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import re
from models import Annotation
from screenshots.models import Screenshot

# Create your views here.
@csrf_exempt
def annotations(request):

	if request.method == 'POST':
		print "Got the POST!"
		print request.body
		annoJson = json.loads(request.body)
		srcFull = annoJson["src"]
		text = annoJson["text"]
		context = annoJson["context"]
		
		annoShape = annoJson["shapes"][0]
		shapeType = annoShape["type"]
		style = annoShape["style"]

		shapeGeom = annoShape["geometry"]
		x_val = shapeGeom["x"]
		y_val = shapeGeom["y"]
		width = shapeGeom["width"]
		height = shapeGeom["height"]
		

		
		print srcFull
		src = re.search('(screenshots\/\S+)', srcFull).group(0)
		print src
		print text
		print context
		print shapeType
		print style
		print x_val
		print y_val
		print width
		print height
		

		screenshot = Screenshot.objects.get(image=src)
		annotation = Annotation(screenshot=screenshot)
		annotation.admin = request.user
		annotation.src = src
		annotation.text = text
		annotation.context = context
		annotation.shapeType = shapeType
		annotation.style = style
		annotation.x_val = x_val
		annotation.y_val = y_val
		annotation.width = width
		annotation.height = height
	
		annotation.save()

		print screenshot
		print annotation
		# Handle post method
	else:  # request.method == 'GET'
		# Handle get method
		print "looks like a GET"


@csrf_exempt
def annotation_search(request):

	if request.method == 'POST':
		print "Got a search post!"
		# Handle post method
	else:  # request.method == 'GET'
		# Handle get method
		print request
		print "looks like a GET"
		

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
		
		annotation1['src'] = 'http://127.0.0.1:8000/media/screenshots/Screen_Shot_2017-07-16_at_9.20.27_AM_Es7AskN.png';
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
		