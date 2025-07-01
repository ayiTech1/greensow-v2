from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts.models.profile import EmployeeProfile
from accounts.permissions import  IsEmployeeOnly
from accounts.serializers.profile import EmployeeProfileSerializer
from accounts.utils.profile_notify import notify_managers_about_profile
from accounts.utils.profile import get_employee_profile
 



class EmployeeProfileManageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]
 

    @action(detail=False, methods=['post'], url_path='create')
    def create_profile(self, request):
        serializer = EmployeeProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = EmployeeProfile.objects.create_profile(user=request.user, **serializer.validated_data)
            notify_managers_about_profile(user_type="employee", user_email=request.user.email)
            return Response(EmployeeProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   

    @action(detail=False, methods=['put'], url_path='update')
    def update_profile(self, request):
        profile = get_employee_profile(request.user)
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
        profile = get_employee_profile(request.user)
        if profile:
            EmployeeProfile.objects.delete_profile(profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    