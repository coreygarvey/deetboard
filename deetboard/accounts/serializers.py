from rest_framework import serializers
from models import Account

class AccountSerializer(serializers.Serializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    password = serializers.CharField(source='user.password')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    org = serializers.PrimaryKeyRelatedField(read_only=True)
    features_following = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'password', 'first_name', 
        	'last_name', 'org', 'notifs', 'role', 'features_following')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = Account.objects.create(
            email=validated_data['user.email'],
        )

        user.set_password(validated_data['user.password'])
        user.save()

        return user