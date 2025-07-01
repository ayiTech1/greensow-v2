from django.forms import ValidationError
from rest_framework import serializers
from accounts.models.user import User
from accounts.serializers.baseserializers import BaseOTPVerificationSerializer, BaseOTPSerializer
from accounts.stores.constants import OTP_ACCOUNT_VERIFICATION, OTP_PASSWORD_RESET
from accounts.models.otp import OneTimePassword
from accounts.utils.access_token import get_tokens_for_user
from accounts.utils.temp_token import generate_temp_token



class AccountVerificationOTPRequestSerializer(BaseOTPSerializer):
    def validate(self, attrs):
        user_id = self.context['user_id']
        method = attrs.get('method')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("Invalid user.")

        purpose = OTP_ACCOUNT_VERIFICATION

        contact = self.validate_method_and_contact(user, method)
        self.validate_cooldown(user, purpose)

        attrs.update({
            'user': user,
            'contact': contact,
            'method': method,
            'purpose': purpose
        })
        return attrs

    def save(self):
        data = self.validated_data
        OneTimePassword.objects.filter(
            user=data['user'],
            purpose=data['purpose']
        ).delete()
        self.send_otp(data['method'], data['contact'], data['purpose'])



class VerifyAccountOTPSerializer(BaseOTPVerificationSerializer):
    def validate(self, attrs):
        otp_code = attrs.get("otp")
        otp_obj = self.get_otp_object(otp_code, purpose=OTP_ACCOUNT_VERIFICATION)
        self.validate_otp_common(otp_obj)
        user = otp_obj.user

        if not user.is_verified:
            user.is_verified = True
            user.save()

        otp_obj.delete()
        attrs["user"] = user
        attrs["tokens"] = get_tokens_for_user(user)
        return attrs

class VerifyPasswordResetOTPSerializer(BaseOTPVerificationSerializer):
    def validate(self, attrs):
        otp_code = attrs.get("otp")
        otp_obj = self.get_otp_object(otp_code, purpose=OTP_PASSWORD_RESET)
        self.validate_otp_common(otp_obj)
        user = otp_obj.user

        otp_obj.delete()
        temp_token = generate_temp_token(user)
        attrs["user"] = user
        attrs["temp_token"] = temp_token
        return attrs

class ResendAccountVerificationOTPSerializer(BaseOTPSerializer):
    def validate(self, attrs):
        user_id = self.context.get('user_id')
        method = attrs.get('method')
        purpose = OTP_ACCOUNT_VERIFICATION  

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Invalid user.'})

        contact = self.validate_method_and_contact(user, method)
        self.validate_cooldown(user, purpose)

        attrs.update({
            'user': user,
            'contact': contact,
            'method': method,
            'purpose': purpose
        })
        return attrs

    def save(self):
        data = self.validated_data
        OneTimePassword.objects.filter(
            user=data['user'],
            purpose=data['purpose']
        ).delete()
        self.send_otp(data['method'], data['contact'], data['purpose'])


class ResendPasswordResetOTPSerializer(BaseOTPSerializer):
    def validate(self, attrs):
        user_id = self.context.get('user_id')
        method = attrs.get('method')
        purpose = OTP_PASSWORD_RESET  

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Invalid user.'})

        contact = self.validate_method_and_contact(user, method)
        self.validate_cooldown(user, purpose)

        attrs.update({
            'user': user,
            'contact': contact,
            'method': method,
            'purpose': purpose
        })
        return attrs

    def save(self):
        data = self.validated_data
        OneTimePassword.objects.filter(
            user=data['user'],
            purpose=data['purpose']
        ).delete()
        self.send_otp(data['method'], data['contact'], data['purpose'])
