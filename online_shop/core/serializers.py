from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()
class CustomUserCreateSerializer(UserCreateSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ['email', 'password', 'password2']

    def validate(self, attrs):
        password2 = attrs.pop('password2')
        user = User(**attrs)
        password = attrs.get("password")
        if password != password2:
            raise serializers.ValidationError('passwords are not match')

        try:
            validate_password(password, user)
        except ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def perform_create(self, validated_data):
        email = validated_data['email']
        username = email.split('@')[0]
        with transaction.atomic():
            user = User.objects.create_user(username=username, **validated_data)
            # if settings.SEND_ACTIVATION_EMAIL:
            #     user.is_active = False
            #     user.save(update_fields=["is_active"])
            return user

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        pass
