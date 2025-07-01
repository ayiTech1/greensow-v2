# views/auth.py
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.utils.access_token import blacklist_refresh_token
from accounts.utils.temp_token import generate_temp_token
from accounts.utils.mfa_notify import send_code_to_user_email
from accounts.serializers.register import ManagerRegisterSerializer
from accounts.serializers.login import ManagerLoginSerializer
from accounts.views.baseviews import BaseViewSet
from rest_framework.exceptions import ValidationError, AuthenticationFailed

User = get_user_model()

class ManagerAuthViewSet(BaseViewSet):
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request):
        try:
            serializer = ManagerRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            send_code_to_user_email.delay(user.email)
           
            return self.handle_success(
                f"Hi {user.username}, you have been registered as a manager. Check your email for a verification code.", 
                status_code=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return self.handle_error("Validation failed.", status_code=400, errors=e.detail)
        except Exception as e:
            return self.handle_error("Manager registration failed.", status_code=500, exc=e)
        

        
    @action(detail=False, methods=['post'], url_path='login', permission_classes=[AllowAny])
    def login(self, request):
        serializer = ManagerLoginSerializer(data=request.data, context={'request': request})
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