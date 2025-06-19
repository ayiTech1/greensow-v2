from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from accounts.models import User

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        request = self.context.get('request')
        user = authenticate(request, email=attrs['email'], password=attrs['password'])
        if not user:
            raise AuthenticationFailed("Invalid credentials. Please try again.")

        allowed_roles = ['employer', 'employee']
        if user.role is None or user.role.name.lower() not in allowed_roles:
            raise AuthenticationFailed("Only employer and employee roles are allowed to log in from this endpoint.")

        attrs['user'] = user
        return attrs


class ManagerLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        request = self.context.get('request')
        user = authenticate(request, email=attrs['email'], password=attrs['password'])
        if not user:
            raise AuthenticationFailed("Invalid credentials.")

        if not user.role or user.role.name.lower() != 'manager':
            raise AuthenticationFailed("Only users with the 'manager' role are allowed to log in here.")

        attrs['user'] = user
        return attrs