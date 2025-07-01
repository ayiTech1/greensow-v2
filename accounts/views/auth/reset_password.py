from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from accounts.middleware.temp_auth import TempTokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from accounts.utils.throttles import OTPThrottle
from accounts.serializers.reset_pwd import PasswordResetRequestSerializer, SetNewPasswordSerializer
from accounts.views.baseviews import BaseViewSet
from rest_framework.exceptions import ValidationError

User = get_user_model()

class ResetPasswordViewSet(BaseViewSet):

    @action(detail=False, methods=['post'], url_path='request-password-reset-otp', throttle_classes=[OTPThrottle])
    def request_password_reset_otp(self, request):
        try:
            serializer = PasswordResetRequestSerializer(data=request.data, context={'request': request})
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

   