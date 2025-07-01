from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, throttle_classes
from rest_framework.permissions import AllowAny
from accounts.middleware.temp_auth import TempTokenAuthentication
from accounts.stores.functions import update_last_login
from accounts.utils.mfa_notify import send_code_to_user_email
from accounts.stores.constants import OTP_ACCOUNT_VERIFICATION, OTP_PASSWORD_RESET
from accounts.utils.throttles import OTPThrottle
from accounts.serializers.mfa import  OTPRequestSerializer,  VerifyOneTimePasswordSerializer, ResendOTPSerializer
from accounts.serializers.register import  ManagerRegisterSerializer, UserRegisterSerialiszer
from accounts.serializers.login  import   LoginSerializer, ManagerLoginSerializer
from accounts.serializers.reset_pwd  import  PasswordResetRequestSerializer,  SetNewPasswordSerializer
import logging



logger = logging.getLogger(__name__)

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='create-account', permission_classes=[AllowAny])
    @throttle_classes([OTPThrottle])
    def register(self, request):
        serializer = UserRegisterSerialiszer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_instance = serializer.instance
        send_code_to_user_email.delay(user_instance.email)
        return Response({'message': f'Hi {user_instance.username}, thanks for signing up to Greensnow. Check your email for a verification code.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='create-manager', permission_classes=[AllowAny])
    def register_manager(self, request):
            serializer = ManagerRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_instance = serializer.save()
            send_code_to_user_email.delay(user_instance.email)
            return Response({'message': f'Hi {user_instance.username}, you have been registered as a manager. Check your email for a verification code.'}, status=status.HTTP_201_CREATED)
    

    @action(detail=False, methods=['post'], url_path='login', permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Login successful. OTP verification required.'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='login-manager', permission_classes=[AllowAny])
    def login_manager(self, request):
        serializer = ManagerLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Manager login successful.'}, status=status.HTTP_200_OK)

        
    @action(detail=False, methods=['post'], url_path='request-otp', permission_classes=[AllowAny])
    @throttle_classes([OTPThrottle])
    def request_otp(self, request):
        serializer = OTPRequestSerializer(data=request.data, context={'request': request, 'purpose': OTP_ACCOUNT_VERIFICATION})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': f"OTP sent to {serializer.validated_data['method']} successfully."}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='verify-account', permission_classes=[AllowAny])
    def verify_otp(self, request):
        purpose = request.query_params.get("purpose", OTP_ACCOUNT_VERIFICATION)
        serializer = VerifyOneTimePasswordSerializer( data=request.data,context={"request": request, "purpose": purpose})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if purpose == OTP_ACCOUNT_VERIFICATION:
            update_last_login(user)
            logger.info(f"Last login updated for user: {user.email}")
            tokens = serializer.validated_data["tokens"]
            return Response({"message": "Account verified", "access_token": str(tokens["access"]), "refresh_token": str(tokens["refresh"]),}, status=status.HTTP_200_OK)
        elif purpose == OTP_PASSWORD_RESET:
            temp_token = serializer.validated_data["temp_token"]
            return Response({"message": "OTP verified. You may now reset your password.", "temp_token": temp_token,}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='resend-otp', authentication_classes=[TempTokenAuthentication])
    @throttle_classes([OTPThrottle])  
    def resend_otp(self, request):
        purpose = request.query_params.get('purpose', OTP_ACCOUNT_VERIFICATION) 
        serializer = ResendOTPSerializer(data=request.data, context={'request': request, 'purpose': purpose})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'OTP resent successfully.'}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='password-reset-request', permission_classes=[AllowAny])
    def password_reset_request(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)      
        return Response({"message": "OTP sent to phone number for password reset."},status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='set-password', authentication_classes=[TempTokenAuthentication])
    def set_password(self, request):
        user = request.user  
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)