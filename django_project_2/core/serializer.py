from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer
from rest_framework import serializers

class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name']

class CustomUserSerializer(UserSerializer):
    # password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['first_name', 'last_name', 'email']

