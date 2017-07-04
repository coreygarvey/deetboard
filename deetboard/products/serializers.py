from rest_framework import serializers
from models import Product, Feature, Link


class ProductSerializer(serializers.Serializer):
    admins = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ('admins','title')


class FeatureSerializer(serializers.Serializer):
    admins = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    screenshots = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    experts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    feature_lists = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    skills = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Feature
        fields = ('admins', 'title', 'description', 'product',
                'screenshots', 'experts', 'feature_lists', 
                'skills')


class LinkSerializer(serializers.Serializer):
    admin = serializers.PrimaryKeyRelatedField(read_only=True)
    feature = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Link
        fields = ('admin', 'title', 'description', 'url', 'feature')