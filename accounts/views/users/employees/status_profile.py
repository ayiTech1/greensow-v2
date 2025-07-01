from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts.models.profile import EmployeeProfile
from accounts.permissions import CanViewEmployeeProfile, IsEmployeeOnly
from accounts.serializers.profile import EmployeeProfileSerializer
from accounts.utils.profile import get_employee_profile


class EmployeeProfileStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]

    @action(detail=False, methods=['get'], url_path='me')
    def retrieve_profile(self, request):
        profile = get_employee_profile(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployeeProfileSerializer(profile).data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, CanViewEmployeeProfile], url_path='view')
    def view_employee_profile(self, request, pk=None):
        profile = get_object_or_404(EmployeeProfile, pk=pk)
        serializer = EmployeeProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)