from rest_framework import serializers
from models import Question, Response


class QuestionSerializer(serializers.Serializer):
	admin = serializers.PrimaryKeyRelatedField(read_only=True)
	class Meta:
		model = Question
		fields = ('admin', 'title', 'text', 'features',
				'user_asking', 'skills')


class ResponseSerializer(serializers.Serializer):
	admin = serializers.PrimaryKeyRelatedField(read_only=True)
	class Meta:
		model = Response
		fields = ('admin', 'question', 'test', 
        		'user_responder', 'accepted')