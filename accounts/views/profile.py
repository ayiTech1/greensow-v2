from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts import models
from accounts.models import  EmployerProfile
from accounts.models.profile import EmployeeProfile
from accounts.permissions import CanViewEmployeeProfile, IsEmployeeOnly, IsEmployerOnly
from accounts.serializers.profile import EmployeeProfileSerializer, EmployerProfileSerializer
import logging
from accounts.utils.profile_notify import notify_managers_about_profile
 


logger = logging.getLogger(__name__)

class EmployerProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]

    def get_object(self, user):
        return EmployerProfile.objects.filter(user=user).first()

    @action(detail=False, methods=['post'], url_path='create')
    def create_profile(self, request):
        serializer = EmployerProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = EmployerProfile.objects.create_profile(user=request.user, **serializer.validated_data)
            notify_managers_about_profile(user_type="employer", user_email=request.user.email)
            return Response(EmployerProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], url_path='me')
    def retrieve_profile(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployerProfileSerializer(profile).data)

    @action(detail=False, methods=['put'], url_path='update')
    def update_profile(self, request):
        profile = self.get_object(request.user)
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
        profile = self.get_object(request.user)
        if profile:
            EmployerProfile.objects.delete_profile(profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]

    def get_object(self, user):
        return EmployeeProfile.objects.filter(user=user).first()

    @action(detail=False, methods=['post'], url_path='create')
    def create_profile(self, request):
        serializer = EmployeeProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = EmployeeProfile.objects.create_profile(user=request.user, **serializer.validated_data)
            notify_managers_about_profile(user_type="employee", user_email=request.user.email)
            return Response(EmployeeProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='me')
    def retrieve_profile(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployeeProfileSerializer(profile).data)

    @action(detail=False, methods=['put'], url_path='update')
    def update_profile(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = EmployeeProfile.objects.update_profile(profile, **serializer.validated_data)
            notify_managers_about_profile(user_type="employee", user_email=request.user.email)
            return Response(EmployeeProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_profile(self, request):
        profile = self.get_object(request.user)
        if profile:
            EmployeeProfile.objects.delete_profile(profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, CanViewEmployeeProfile], url_path='view')
    def view_employee_profile(self, request, pk=None):
        profile = get_object_or_404(EmployeeProfile, pk=pk)
        serializer = EmployeeProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)