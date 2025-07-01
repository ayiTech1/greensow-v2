from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.contrib.auth import login as django_login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from accounts.utils.access_token import get_tokens_for_user  # ✅ reusable

class ManagerSocialAuthViewSet(viewsets.ViewSet):
    """
    Social login restricted to Manager role only.
    """

    def handle_manager_login(self, request, adapter_class):
        view = SocialLoginView.as_view(adapter_class=adapter_class)
        response = view(request._request)
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"error": "Authentication failed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.role:
            role = request.data.get('role')
            if role != 'manager':
                raise ValidationError("Only manager role is allowed for this endpoint.")
            user.role = role
            user.save()
        elif user.role != 'manager':
            raise ValidationError(f"Access denied for role '{user.role}'. Only manager allowed.")

        django_login(request, user)

        tokens = get_tokens_for_user(user) 

        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        })

    @action(detail=False, methods=['post'])
    def google(self, request):
        return self.handle_manager_login(request, GoogleOAuth2Adapter)

    @action(detail=False, methods=['post'])
    def apple(self, request):
        return self.handle_manager_login(request, AppleOAuth2Adapter)
