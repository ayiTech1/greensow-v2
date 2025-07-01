from rest_framework.decorators import action, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.middleware.temp_auth import TempTokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from accounts.stores.functions import update_last_login
from accounts.stores.constants import OTP_ACCOUNT_VERIFICATION, OTP_PASSWORD_RESET
from accounts.utils.throttles import OTPThrottle
from accounts.serializers.mfa import AccountVerificationOTPRequestSerializer, OTPRequestSerializer, ResendAccountVerificationOTPSerializer, ResendPasswordResetOTPSerializer, VerifyAccountOTPSerializer, VerifyOneTimePasswordSerializer, ResendOTPSerializer, VerifyPasswordResetOTPSerializer
from accounts.serializers.reset_pwd import PasswordResetRequestSerializer, SetNewPasswordSerializer
from accounts.views.baseviews import BaseViewSet
from rest_framework.exceptions import ValidationError

User = get_user_model()

class MultifactorAuthenticationViewSet(BaseViewSet):

    @action(detail=True, methods=['post'],url_path='request-account-verify-otp')
    def request_account_verify_otp(self, request, pk=None):
        serializer = AccountVerificationOTPRequestSerializer(
            data=request.data,
            context={'request': request, 'user_id': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.handle_success("OTP sent for account verification.")


    @action(detail=False, methods=['post'], url_path='verify-account',authentication_classes=[TempTokenAuthentication])
    def verify_account_otp(self, request):
        serializer = VerifyAccountOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data["tokens"]
        return self.handle_success({
            "message": "Account verified successfully.",
            "access_token": tokens["access"],
            "refresh_token": tokens["refresh"],
        })


    @action(detail=False, methods=['post'], url_path='verify-reset-password-otp', authentication_classes=[TempTokenAuthentication])
    def verify_password_reset_otp(self, request):
        serializer = VerifyPasswordResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        temp_token = serializer.validated_data["temp_token"]
        return self.handle_success({
            "message": "OTP verified. You may now reset your password.",
            "temp_token": temp_token,
        })
    

   
    @action(detail=True, methods=['post'], url_path='resend-account-verify-otp', throttle_classes=[OTPThrottle])
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


    @action(detail=True,  methods=['post'], url_path='resend-password-reset-otp', throttle_classes=[OTPThrottle])
    def resend_password_reset_otp(self, request, pk=None):
        try:
            serializer = ResendPasswordResetOTPSerializer(
                data=request.data,
                context={'request': request, 'user_id': pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.handle_success("Password reset OTP resent successfully.")
        except ValidationError as e:
            return self.handle_error("Resend failed.", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Resend failed.", exc=e)


   

    @action(detail=False, methods=['post'], url_path='password-reset-request', permission_classes=[AllowAny])
    def password_reset_request(self, request):
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return self.handle_success("OTP sent to phone number for password reset.", )
        except ValidationError as e:
            return self.handle_error("Password reset request failed.",  status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Password reset request failed.",  exc=e)

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

    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return self.handle_error("Refresh token is required.",)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            self.logger.info(f"User {request.user.email} logged out from current session.")
            return self.handle_success("Logout successful.", )
        except Exception as e:
            return self.handle_error("Token is invalid or expired.",  exc=e)

   