# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']

class UserUpdateSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'new_password']

    def update(self, instance, validated_data):
        if 'new_password' in validated_data:
            instance.set_password(validated_data.pop('new_password'))
        return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
