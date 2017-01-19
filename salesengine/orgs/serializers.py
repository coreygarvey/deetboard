from rest_framework import serializers
from models import Org, Expert, Skill
from accounts.models import Account


class OrgSerializer(serializers.Serializer):
    admin = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    accounts = serializers.PrimaryKeyRelatedField(many=True, queryset=Account.objects.all())
    class Meta:
        model = Org
        fields = ('admin', 'title', 'accounts')

class ExpertSerializer(serializers.Serializer):
    account = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Expert
        fields = ('account')

class SkillSerializer(serializers.Serializer):
    experts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Skill
        fields = ('title', 'category', 'experts')