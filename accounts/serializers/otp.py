from django.forms import ValidationError
from rest_framework import serializers
from accounts.serializers.baseserializers import BaseOTPVerificationSerializer, BaseOTPSerializer
from accounts.stores.constants import OTP_PURPOSE_ACCOUNT_VERIFICATION, OTP_PURPOSE_PASSWORD_RESET
from accounts.models.otp import OneTimePassword
from accounts.utils.token_utils import generate_temp_token, mark_temp_token_verified



class OTPRequestSerializer(BaseOTPSerializer):
    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        method = attrs.get('method')
        purpose = self.context.get('purpose')  
        contact = self.validate_method_and_contact(user, method)
        self.validate_cooldown(user, purpose)
        attrs.update({'user': user, 'contact': contact, 'method': method, 'purpose': purpose })
        return attrs
    def save(self):
        data = self.validated_data
        OneTimePassword.objects.filter(user=data['user'], purpose=data['purpose']).delete()
        self.send_otp(data['method'], data['contact'], data['purpose'])



class VerifyOneTimePasswordSerializer(BaseOTPVerificationSerializer):
    def validate(self, attrs):
        otp_code = attrs.get("otp")
        purpose = self.context.get("purpose")
        request = self.context.get("request")
        if not purpose:
            raise ValidationError("Purpose is missing internally.")
        otp_obj = self.get_otp_object(otp_code, purpose)
        self.validate_otp_common(otp_obj)
        user = otp_obj.user
        if purpose == OTP_PURPOSE_ACCOUNT_VERIFICATION:
            if not user.is_verified:
                user.is_verified = True
                user.save()
            attrs["tokens"] = user.tokens()

        elif purpose == OTP_PURPOSE_PASSWORD_RESET:
            attrs["temp_token"] = generate_temp_token(user)
        otp_obj.delete()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        mark_temp_token_verified(token)
        
        attrs["user"] = user
        return attrs


class ResendOTPSerializer(BaseOTPSerializer):
    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        method = attrs.get('method')
        purpose = self.context.get('purpose')
        if purpose not in [OTP_PURPOSE_ACCOUNT_VERIFICATION, OTP_PURPOSE_PASSWORD_RESET]:
            raise serializers.ValidationError({'purpose': 'Invalid or missing purpose.'})
        contact = self.validate_method_and_contact(user, method)
        self.validate_cooldown(user, purpose)
        attrs.update({'user': user, 'contact': contact, 'method': method, 'purpose': purpose})
        return attrs
    def save(self):
        data = self.validated_data
        OneTimePassword.objects.filter(user=data['user'], purpose=data['purpose'],).delete()
        self.send_otp(data['method'], data['contact'], data['purpose'])

