from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts.models import  EmployerProfile
from accounts.permissions import  IsEmployerOnly
from accounts.serializers.profile import  EmployerProfileSerializer
import logging
from accounts.utils.profile_notify import notify_managers_about_profile
from accounts.utils.profile import get_employer_profile
 
logger = logging.getLogger(__name__)




class EmployerProfileManageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]

    @action(detail=False, methods=['post'], url_path='create')
    def create_profile(self, request):
        serializer = EmployerProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = EmployerProfile.objects.create_profile(user=request.user, **serializer.validated_data)
            notify_managers_about_profile(user_type="employer", user_email=request.user.email)
            return Response(EmployerProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path='update')
    def update_profile(self, request):
        profile = get_employer_profile(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = EmployerProfile.objects.update_profile(profile, **serializer.validated_data)
            notify_managers_about_profile(user_type="employer", user_email=request.user.email)
            return Response(EmployerProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_profile(self, request):
        profile = get_employer_profile(request.user)
        if profile:
            EmployerProfile.objects.delete_profile(profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
