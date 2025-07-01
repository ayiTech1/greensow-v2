from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.models import OneTimePassword
from accounts.utils.mfa_notify import send_code_to_user_email, send_code_to_user_phone

MAX_ATTEMPTS = 5 
RESEND_COOLDOWN_SECONDS = 60  



class BaseOTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True)

    def get_otp_object(self, otp_code, *, purpose):
       
        try:
            return OneTimePassword.objects.get(code=otp_code, purpose=purpose)
        except OneTimePassword.DoesNotExist:
            raise ValidationError("Invalid OTP code.")

    def validate_otp_common(self, otp_obj):
        if not otp_obj.is_valid():
            raise ValidationError("OTP code has expired.")
        if otp_obj.failed_attempts >= MAX_ATTEMPTS:
            raise ValidationError("Too many failed attempts. Request a new OTP.")



class BaseOTPSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=['email', 'phone_number'])

    def validate_method_and_contact(self, user, method):
        if method == 'email':
            contact = user.email
            if not contact:
                raise serializers.ValidationError({'email': 'User has no email address.'})
        elif method == 'phone_number':
            contact = user.phone_number
            if not contact:
                raise serializers.ValidationError({'phone_number': 'User has no phone number.'})
        else:
            raise serializers.ValidationError('Invalid method.')
        return contact

    def validate_cooldown(self, user, purpose):
        latest_otp = OneTimePassword.objects.filter(user=user, purpose=purpose).order_by('-created_at').first()
        if latest_otp and (timezone.now() - latest_otp.created_at < timedelta(seconds=RESEND_COOLDOWN_SECONDS)):
            seconds_remaining = RESEND_COOLDOWN_SECONDS - (timezone.now() - latest_otp.created_at).seconds
            raise serializers.ValidationError(f"Please wait {seconds_remaining} seconds before requesting a new OTP.")

    def send_otp(self, method, contact, purpose):
        if method == 'email':
            send_code_to_user_email.delay(contact, purpose)
        else:
            send_code_to_user_phone.delay(contact, purpose)
