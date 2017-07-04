from rest_framework import serializers
from models import EngagementList, TopList


class EngagementListSerializer(serializers.Serializer):
	admins = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
	class Meta:
		model = EngagementList
		fields = ('admins', 'title', 'comment', 'public', 'client', 'category')


class TopListSerializer(serializers.Serializer):
	admins = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
	class Meta:
		model = TopList
		fields = ('admins', 'title', 'comment', 'public')