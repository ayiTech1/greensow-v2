from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from accounts.utils.throttles import OTPThrottle
from accounts.serializers.mfa import AccountVerificationOTPRequestSerializer,  ResendAccountVerificationOTPSerializer, VerifyAccountOTPSerializer
from accounts.views.baseviews import BaseViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle

User = get_user_model()


class OTPThrottle(UserRateThrottle):
    scope = 'otp'

class MultifactorAuthenticationViewSet(BaseViewSet):

    @action(detail=True, methods=['post'],url_path='request-account-verify-otp',  permission_classes=[AllowAny])
    def request_account_verify_otp(self, request, pk=None):
        serializer = AccountVerificationOTPRequestSerializer(
            data=request.data,
            context={'request': request, 'user_id': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.handle_success("OTP sent for account verification.")


    @action(detail=False, methods=['post'], url_path='verify-account',  permission_classes=[AllowAny])
    def verify_account_otp(self, request):
        serializer = VerifyAccountOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data["tokens"]
        return self.handle_success({
            "message": "Account verified successfully.",
            "access_token": tokens["access"],
            "refresh_token": tokens["refresh"],
        })
    

   
    @action(detail=True, methods=['post'], url_path='resend-account-verify-otp', throttle_classes=[OTPThrottle], permission_classes=[AllowAny])
    def resend_account_verify_otp(self, request, pk=None):
        try:
            serializer = ResendAccountVerificationOTPSerializer(
                data=request.data,
                context={'request': request, 'user_id': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.handle_success("Account verification OTP resent successfully.")
        except ValidationError as e:
            return self.handle_error("Resend failed.", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Resend failed.", exc=e)


  
   