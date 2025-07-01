from rest_framework import serializers
from rest_framework.exceptions import  AuthenticationFailed
from django.contrib.auth import authenticate
from accounts.models import User

    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        request = self.context.get("request")

        user = authenticate(request, email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials.")

        if not user.role or user.role.name.lower() not in ["employer", "employee"]:
            raise AuthenticationFailed("Only employers and employees are allowed.")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        return validated_data["user"]




class ManagerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get('request')

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(request, email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials.")

        if not user.role or user.role.name.lower() != 'manager':
            raise AuthenticationFailed("Only users with the 'manager' role are allowed to log in here.")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        return validated_data['user']
