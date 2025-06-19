from datetime import date
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from accounts.models.user import  Role, User



RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5

class UserRegisterSerialiszer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    role = serializers.SlugRelatedField(queryset=Role.objects.all(), slug_field='name')
    class Meta:
        model = User
        fields = ['email', 'username', 'role', 'phone_number', 'date_of_birth', 'address', 'password', 'password2']
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        validate_password(attrs['password']) 
        dob = attrs.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 16:
                raise serializers.ValidationError({'date_of_birth': 'User must be at least 16 years old.'})
        allowed_roles = ['employer', 'employee']
        if attrs['role'].name.lower() not in allowed_roles:
            raise serializers.ValidationError({'role': 'Only employer and employee roles are allowed for registration.'})
        return attrs
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)    
        return user



class ManagerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'username', 'phone_number', 'date_of_birth', 'address', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        validate_password(attrs['password'])

        dob = attrs.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise serializers.ValidationError({'date_of_birth': 'Manager must be at least 18 years old.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_manager(**validated_data)
