from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts.models import EmployeeProfile, EmployerProfile
from accounts.permissions import  IsManagerOnly
from accounts.stores.functions import get_or_empty_response
from accounts.serializers.profile import EmployeeProfileSerializer, EmployerProfileSerializer
import logging

 


logger = logging.getLogger(__name__)

class ManagerEmployerProfileStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManagerOnly]

    @action(detail=False, methods=['get'], url_path='pending-employers')
    def pending_employers(self, request):
        queryset = EmployerProfile.objects.filter(status='pending')
        return get_or_empty_response(queryset, EmployerProfileSerializer, "No employer profile awaiting approval.")
    
    @action(detail=False, methods=['get'], url_path='approved-employers')
    def approved_employers(self, request):
        queryset = EmployerProfile.objects.filter(status='approved')
        return get_or_empty_response(queryset, EmployerProfileSerializer, "No employer approved profile .")

         


class ManagerEmployeeProfileStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManagerOnly]
    
    @action(detail=False, methods=['get'], url_path='pending-employees')
    def pending_employees(self, request):
        queryset = EmployeeProfile.objects.filter(status='pending')
        return get_or_empty_response(queryset, EmployeeProfileSerializer, "No employee profile awaiting approval.")
    @action(detail=False, methods=['get'], url_path='pending-employees')

    @action(detail=False, methods=['get'], url_path='pending-employees')
    def approved_employees(self, request):
        queryset = EmployeeProfile.objects.filter(status='approved')
        return get_or_empty_response(queryset, EmployeeProfileSerializer, "No employee approved profile.")
    