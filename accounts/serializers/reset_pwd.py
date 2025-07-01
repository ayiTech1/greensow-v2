from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from accounts.serializers.baseserializers import BaseOTPSerializer
from accounts.stores.constants import OTP_PASSWORD_RESET
from accounts.models.user import  User
from accounts.models.otp import OneTimePassword
from accounts.utils.temp_token import generate_temp_token


RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5
   
class PasswordResetOTPRequestSerializer(BaseOTPSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'No user with this email.'})

        method = attrs.get('method')  # 'email' or 'sms'
        purpose = OTP_PASSWORD_RESET

        contact = self.validate_method_and_contact(user, method)
        self.validate_cooldown(user, purpose)

        # Generate temp token now — one-time use for password reset
        temp_token = generate_temp_token(user)

        attrs.update({
            'user': user,
            'contact': contact,
            'method': method,
            'purpose': purpose,
            'temp_token': temp_token,
        })
        return attrs

    def save(self):
        data = self.validated_data
        # Remove any previous OTPs for this purpose
        OneTimePassword.objects.filter(
            user=data['user'],
            purpose=data['purpose']
        ).delete()

        # Send the OTP
        self.send_otp(data['method'], data['contact'], data['purpose'])

        return {'temp_token': data['temp_token']}


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        password = attrs.get('new_password')
        confirm = attrs.get('confirm_password')
        if password != confirm:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(password) 
        return attrs
    def save(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()
