from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.contrib.auth import login as django_login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from accounts.utils.access_token import get_tokens_for_user 

class UserSocialAuthViewSet(viewsets.ViewSet):

    def handle_social_login(self, request, adapter_class, allowed_roles):
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
            if role not in allowed_roles:
                raise ValidationError(f"Invalid role. Allowed: {allowed_roles}")
            user.role = role
            user.save()
        elif user.role not in allowed_roles:
            raise ValidationError(f"Access denied for role '{user.role}'. Allowed: {allowed_roles}")

        django_login(request, user)

        tokens = get_tokens_for_user(user)  

        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        })

    @action(detail=False, methods=['post'])
    def google(self, request):
        return self.handle_social_login(request, GoogleOAuth2Adapter, allowed_roles=['employer', 'employee'])

    @action(detail=False, methods=['post'])
    def apple(self, request):
        return self.handle_social_login(request, AppleOAuth2Adapter, allowed_roles=['employer', 'employee'])
