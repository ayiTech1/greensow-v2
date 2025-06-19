from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from accounts.serializers.baseserializers import BaseOTPSerializer
from accounts.stores.constants import OTP_PURPOSE_PASSWORD_RESET
from accounts.models.user import  User
from accounts.models.otp import OneTimePassword
from accounts.utils.otp_notify import   send_code_to_user_phone


RESEND_COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5

class PasswordResetRequestSerializer(BaseOTPSerializer):
    phone_number = serializers.CharField(max_length=13)
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone_number': "No user is associated with this phone number."})
        purpose = OTP_PURPOSE_PASSWORD_RESET  
        self.validate_cooldown(user, purpose)
        attrs['user'] = user
        attrs['phone_number'] = phone_number
        attrs['purpose'] = purpose
        return attrs
    def save(self):
        user = self.validated_data['user']
        phone_number = self.validated_data['phone_number']
        purpose = self.validated_data['purpose']
        OneTimePassword.objects.filter(user=user, purpose=purpose).delete()
        send_code_to_user_phone.delay(phone_number, purpose)


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
