from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts.permissions import  IsEmployerOnly
from accounts.serializers.profile import  EmployerProfileSerializer
from accounts.utils.profile import get_employer_profile



class EmployerProfileStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]
      
    @action(detail=False, methods=['get'], url_path='view-profile')
    def view_profile(self, request):
        profile = get_employer_profile(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployerProfileSerializer(profile).data)