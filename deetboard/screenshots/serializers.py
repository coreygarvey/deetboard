from rest_framework import serializers
from models import Screenshot


class ScreenshotSerializer(serializers.Serializer):
	admin = serializers.PrimaryKeyRelatedField(read_only=True)
	class Meta:
		model = Screenshot
		fields = ('admin', 'title', 'file_path', 'feature', 'question')