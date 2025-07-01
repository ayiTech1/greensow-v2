from rest_framework.decorators import action
from accounts.middleware.temp_auth import TempTokenAuthentication
from django.contrib.auth import get_user_model
from accounts.serializers.mfa import VerifyPasswordResetOTPSerializer
from accounts.utils.throttles import OTPThrottle
from accounts.serializers.reset_pwd import PasswordResetOTPRequestSerializer, SetNewPasswordSerializer
from accounts.views.baseviews import BaseViewSet
from rest_framework.exceptions import ValidationError

User = get_user_model()

class ResetPasswordViewSet(BaseViewSet):

    @action(detail=False, methods=['post'], url_path='request-password-reset-otp', throttle_classes=[OTPThrottle])
    def request_password_reset_otp(self, request):
        try:
            serializer = PasswordResetOTPRequestSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            result = serializer.save()
            return self.handle_success(
                "OTP sent for password reset.",
                {"temp_token": result['temp_token']},
            )
        except ValidationError as e:
            return self.handle_error("OTP request failed.", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("OTP request failed.", exc=e)
        

    @action(detail=False, methods=['post'], url_path='verify-reset-password-otp', authentication_classes=[TempTokenAuthentication])
    def verify_password_reset_otp(self, request):
        serializer = VerifyPasswordResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        temp_token = serializer.validated_data["temp_token"]
        return self.handle_success({
            "message": "OTP verified. You may now reset your password.",
            "temp_token": temp_token,
        })

    @action(detail=False, methods=['post'], url_path='set-password', authentication_classes=[TempTokenAuthentication])
    def set_password(self, request):
        try:
            user = request.user
            serializer = SetNewPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return self.handle_success("Password reset successful.", )
        except ValidationError as e:
            return self.handle_error("Password reset failed.", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Password reset failed.",  exc=e)

   