from rest_framework.decorators import action, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from accounts.middleware.temp_auth import TempTokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from accounts.stores.functions import update_last_login
from accounts.utils.access_token import blacklist_refresh_token
from accounts.utils.temp_token import generate_temp_token
from accounts.utils.mfa_notify import send_code_to_user_email
from accounts.stores.constants import OTP_ACCOUNT_VERIFICATION, OTP_PASSWORD_RESET
from accounts.utils.throttles import OTPThrottle
from accounts.serializers.mfa import OTPRequestSerializer, VerifyOneTimePasswordSerializer, ResendOTPSerializer
from accounts.serializers.register import  UserRegisterSerialiszer
from accounts.serializers.login import LoginSerializer
from accounts.serializers.reset_pwd import PasswordResetRequestSerializer, SetNewPasswordSerializer
from accounts.views.baseviews import BaseViewSet
from rest_framework.exceptions import ValidationError, AuthenticationFailed

User = get_user_model()

class UserAuthViewSet(BaseViewSet):

    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    @throttle_classes([OTPThrottle])
    def register(self, request):
        try:
            serializer = UserRegisterSerialiszer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            send_code_to_user_email.delay(user.email)
            
            return self.handle_success(
                f"Hi {user.username}, thanks for signing up to Greensnow. Check your email for a verification code.",     
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return self.handle_error(
                "Validation failed.",
                status_code=400,
                errors=e.detail
            )

        except Exception as e:
            return self.handle_error(
                "Unexpected error during registration.",
                status_code=500,
                exc=e
            )

    

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return self.handle_success(
            "Login credentials valid. OTP required.",
            {"user_id": user.id}
        )

    

    @action(detail=False, methods=['post'])
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return self.handle_error(
                message="Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        result, http_status = blacklist_refresh_token(refresh_token)
        return self.handle_success(result, status_code=http_status)