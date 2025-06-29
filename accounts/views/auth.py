# views/auth.py
from rest_framework.decorators import action, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from accounts.middleware.temp_auth import TempTokenAuthentication
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from accounts.stores.functions import update_last_login
from accounts.utils.token_utils import generate_temp_token
from accounts.utils.otp_notify import send_code_to_user_email
from accounts.stores.constants import OTP_ACCOUNT_VERIFICATION, OTP_PASSWORD_RESET
from accounts.utils.throttles import OTPThrottle, SocialLoginThrottle
from accounts.serializers.otp import OTPRequestSerializer, VerifyOneTimePasswordSerializer, ResendOTPSerializer
from accounts.serializers.register import ManagerRegisterSerializer, UserRegisterSerialiszer
from accounts.serializers.login import LoginSerializer, ManagerLoginSerializer
from accounts.serializers.reset_pwd import PasswordResetRequestSerializer, SetNewPasswordSerializer
from accounts.views.baseviews import BaseViewSet
import requests
from jose import jwt
from rest_framework.exceptions import ValidationError

User = get_user_model()

class AuthViewSet(BaseViewSet):

    @action(detail=False, methods=['post'], url_path='create-account', permission_classes=[AllowAny])
    @throttle_classes([OTPThrottle])
    def register(self, request):
        try:
            serializer = UserRegisterSerialiszer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            send_code_to_user_email.delay(user.email)
            temp_token = generate_temp_token(user)

            return self.handle_success(
                f"Hi {user.username}, thanks for signing up to Greensnow. Check your email for a verification code.",
                {"temp_token": temp_token},
                code="GS2002",
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return self.handle_error(
                "Validation failed.",
                code="GS4000",
                status_code=400,
                errors=e.detail
            )

        except Exception as e:
            return self.handle_error(
                "Unexpected error during registration.",
                code="GS5000",
                status_code=500,
                exc=e
            )

    @action(detail=False, methods=['post'], url_path='create-manager', permission_classes=[AllowAny])
    def register_manager(self, request):
        try:
            serializer = ManagerRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            send_code_to_user_email.delay(user.email)
            temp_token = generate_temp_token(user)
            return self.handle_success(
                f"Hi {user.username}, you have been registered as a manager. Check your email for a verification code.",
                {"temp_token": temp_token},
                code="GS2002",
                status_code=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return self.handle_error("Validation failed.", code="GS4001", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Manager registration failed.", code="GS4002", status_code=500, exc=e)

    @action(detail=False, methods=['post'], url_path='login', permission_classes=[AllowAny])
    def login(self, request):
        try:
            serializer = LoginSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            temp_token = generate_temp_token(user)
            return self.handle_success("Login successful. OTP verification required.", {"temp_token": temp_token}, code="GS2001")
        except ValidationError as e:
            return self.handle_error("Validation failed.", code="GS4003", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Login failed.", code="GS4004", exc=e)

    @action(detail=False, methods=['post'], url_path='login-manager', permission_classes=[AllowAny])
    def login_manager(self, request):
        try:
            serializer = ManagerLoginSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            temp_token = generate_temp_token(user)
            return self.handle_success("Manager login successful.", {"temp_token": temp_token}, code="GS2003")
        except ValidationError as e:
            return self.handle_error("Validation failed.", code="GS4005", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Manager login failed.", code="GS4006", exc=e)

    @action(detail=False, methods=['post'], url_path='verify-account', authentication_classes=[TempTokenAuthentication])
    def verify_otp(self, request):
        try:
            purpose = request.data.get("purpose", OTP_ACCOUNT_VERIFICATION)
            serializer = VerifyOneTimePasswordSerializer(
                data=request.data,
                context={"request": request, "purpose": purpose}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            if purpose == OTP_ACCOUNT_VERIFICATION:
                update_last_login(user)
                tokens = serializer.validated_data["tokens"]
                return self.handle_success("Account verified successfully.", {
                    "access_token": str(tokens["access"]),
                    "refresh_token": str(tokens["refresh"]),
                }, code="GS2004")

            elif purpose == OTP_PASSWORD_RESET:
                temp_token = serializer.validated_data["temp_token"]
                return self.handle_success("OTP verified. You may now reset your password.", {"temp_token": temp_token}, code="GS2005")

        except ValidationError as e:
            return self.handle_error("OTP verification failed.", code="GS4007", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("OTP verification failed.", code="GS4008", exc=e)

    @action(detail=False, methods=['post'], url_path='request-otp', authentication_classes=[TempTokenAuthentication])
    @throttle_classes([OTPThrottle])
    def request_otp(self, request):
        try:
            serializer = OTPRequestSerializer(data=request.data, context={'request': request, 'purpose': OTP_ACCOUNT_VERIFICATION})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.handle_success(f"OTP sent to {serializer.validated_data['method']} successfully.", code="GS2006")
        except ValidationError as e:
            return self.handle_error("OTP request failed.", code="GS4009", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("OTP request failed.", code="GS4010", exc=e)

    @action(detail=False, methods=['post'], url_path='resend-otp', authentication_classes=[TempTokenAuthentication])
    @throttle_classes([OTPThrottle])
    def resend_otp(self, request):
        try:
            purpose = request.query_params.get('purpose', OTP_ACCOUNT_VERIFICATION)
            serializer = ResendOTPSerializer(data=request.data, context={'request': request, 'purpose': purpose})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.handle_success("OTP resent successfully.", code="GS2007")
        except ValidationError as e:
            return self.handle_error("OTP resend failed.", code="GS4011", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("OTP resend failed.", code="GS4012", exc=e)

    @action(detail=False, methods=['post'], url_path='password-reset-request', permission_classes=[AllowAny])
    def password_reset_request(self, request):
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return self.handle_success("OTP sent to phone number for password reset.", code="GS2008")
        except ValidationError as e:
            return self.handle_error("Password reset request failed.", code="GS4013", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Password reset request failed.", code="GS4014", exc=e)

    @action(detail=False, methods=['post'], url_path='set-password', authentication_classes=[TempTokenAuthentication])
    def set_password(self, request):
        try:
            user = request.user
            serializer = SetNewPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return self.handle_success("Password reset successful.", code="GS2009")
        except ValidationError as e:
            return self.handle_error("Password reset failed.", code="GS4015", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Password reset failed.", code="GS4016", exc=e)

    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return self.handle_error("Refresh token is required.", code="GS4017")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            self.logger.info(f"User {request.user.email} logged out from current session.")
            return self.handle_success("Logout successful.", code="GS2010")
        except Exception as e:
            return self.handle_error("Token is invalid or expired.", code="GS4018", exc=e)

    @action(detail=False, methods=['post'], url_path='social-login', permission_classes=[AllowAny])
    @throttle_classes([SocialLoginThrottle])
    def social_login(self, request):
        provider = request.data.get("provider")
        id_token = request.data.get("id_token")

        if not provider or not id_token:
            return self.handle_error(
                message="Provider and id_token are required.",
                code="GS4019"
            )

        if provider not in ["google", "apple"]:
            return self.handle_error(
                message="Unsupported provider.",
                code="GS4020"
            )

        try:
            if provider == "google":
                user_info = requests.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
                ).json()
                email = user_info.get("email")

            elif provider == "apple":
                decoded = jwt.decode(id_token, options={"verify_signature": False})
                email = decoded.get("email") or f"{decoded['sub']}@apple.com"

            if not email:
                return self.handle_error(message="Email not found in token", code="GS4021")

            user, created = User.objects.get_or_create(email=email, defaults={
                "username": email.split("@")[0]
            })

            if created or not SocialAccount.objects.filter(user=user, provider=provider).exists():
                SocialAccount.objects.get_or_create(user=user, provider=provider, uid=email)

            refresh = RefreshToken.for_user(user)
            return self.handle_success(
                message="Login successful.",
                code="GS2001",
                data={
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    }
                }
            )

        except Exception as e:
            self.logger.exception("Social login error")
            return self.handle_error(
                message="Authentication failed.",
                code="GS5001",
                exc=e
            )
