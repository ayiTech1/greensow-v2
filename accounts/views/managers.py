from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts.models import EmployeeProfile, EmployerProfile
from accounts.permissions import  IsManagerOnly
from accounts.stores.functions import get_or_empty_response
from accounts.utils.otp_notify import notify_user
from accounts.stores.constants import  PROFILE_APPROVED_MESSAGE, PROFILE_APPROVED_SUBJECT, PROFILE_REJECTED_MESSAGE, PROFILE_REJECTED_SUBJECT
from django.http import HttpResponse
from accounts.serializers.profile import EmployeeProfileSerializer, EmployerProfileSerializer
import logging
import csv
from accounts.utils.profile_notify import  notify_user_status
 


logger = logging.getLogger(__name__)



class EmployerManagerDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManagerOnly]

    @action(detail=False, methods=['get'], url_path='pending-employers')
    def pending_employers(self, request):
        queryset = EmployerProfile.objects.filter(status='pending')
        return get_or_empty_response(queryset, EmployerProfileSerializer, "No employer profile awaiting approval.")
    
    @action(detail=False, methods=['get'], url_path='approved-employers')
    def approved_employers(self, request):
        queryset = EmployerProfile.objects.filter(status='approved')
        return get_or_empty_response(queryset, EmployerProfileSerializer, "No employer approved profile .")


    @action(detail=True, methods=['post'], url_path='approve-employer')
    def approve_employer(self, request, pk=None):
        try:
            profile = EmployerProfile.objects.get(pk=pk)
            profile.status = 'approved'
            profile.save()
            notify_user(subject=PROFILE_APPROVED_SUBJECT, message=PROFILE_APPROVED_MESSAGE, recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='approved', message=PROFILE_APPROVED_MESSAGE)
            logger.info(f"Employer profile {pk} approved by manager {request.user.email}")
            return Response({'detail': 'Profile approved'}, status=status.HTTP_200_OK)
        except EmployerProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=True, methods=['post'], url_path='reject-employer')
    def reject_employer(self, request, pk=None):
        try:
            profile = EmployerProfile.objects.get(pk=pk)
            profile.status = 'rejected'
            profile.save()
            notify_user(subject=PROFILE_REJECTED_SUBJECT, message=PROFILE_REJECTED_MESSAGE, recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='rejected', message=PROFILE_REJECTED_MESSAGE )
            logger.info(f"Employer profile {pk} rejected by manager {request.user.email}")
            return Response({'detail': 'Profile rejected'}, status=status.HTTP_200_OK)
        except EmployerProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=False, methods=['get'], url_path='export-approved-employers')
    def export_approved_employers(self, request):
        approved = EmployerProfile.objects.filter(status='approved')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="approved_employers.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Company Name', 'Industry', 'User Email', 'Last Submitted'])
        for emp in approved:
            writer.writerow([emp.id, emp.company_name, emp.industry, emp.user.email, emp.last_submitted])
        return response
    
    @action(detail=True, methods=['post'], url_path='suspend-employer')
    def suspend_employer(self, request, pk=None):
        try:
            profile = EmployerProfile.objects.get(pk=pk)
            profile.status = 'suspended'
            profile.save()
            suspend_message = "Your employer profile has been suspended by the manager."
            notify_user(subject="Profile Suspended", message=suspend_message, recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='suspended', message=suspend_message)
            logger.info(f"Employer profile {pk} suspended by manager {request.user.email}")
            return Response({'detail': 'Profile suspended'}, status=status.HTTP_200_OK)
        except EmployerProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='activate-employer')
    def activate_employer(self, request, pk=None):
        try:
            profile = EmployerProfile.objects.get(pk=pk)
            profile.status = 'approved'
            profile.save()
            activate_message = "Your employer profile has been activated by the manager."
            notify_user(subject="Profile Activated", message=activate_message, recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='activated', message=activate_message)
            logger.info(f"Employer profile {pk} activated by manager {request.user.email}")
            return Response({'detail': 'Profile activated'}, status=status.HTTP_200_OK)
        except EmployerProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


         


class EmployeeManagerDashboardViewSet(viewsets.ViewSet):
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
    
    @action(detail=True, methods=['post'], url_path='approve-employee')
    def approve_employee(self, request, pk=None):
        try:
            profile = EmployerProfile.objects.get(pk=pk)
            profile.status = 'approved'
            profile.save()
            notify_user(subject=PROFILE_APPROVED_SUBJECT, message=PROFILE_APPROVED_MESSAGE, recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='approved', message=PROFILE_APPROVED_MESSAGE)
            logger.info(f"Employee profile {pk} approved by manager {request.user.email}")
            return Response({'detail': 'Profile approved'}, status=status.HTTP_200_OK)
        except EmployerProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=True, methods=['post'], url_path='reject-employee')
    def reject_employee(self, request, pk=None):
        try:
            profile = EmployeeProfile.objects.get(pk=pk)
            profile.status = 'rejected'
            profile.save()
            notify_user(subject=PROFILE_REJECTED_SUBJECT, message=PROFILE_REJECTED_MESSAGE , recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='rejected', message=PROFILE_REJECTED_MESSAGE )
            logger.info(f"Employee profile {pk} rejected by manager {request.user.email}")
            return Response({'detail': 'Profile rejected'}, status=status.HTTP_200_OK)
        except EmployerProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=False, methods=['get'], url_path='export-approved-employees')
    def export_approved_employees(self, request):
        approved = EmployeeProfile.objects.filter(status='approved')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="approved_employees.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Company Name', 'Industry', 'User Email', 'Last Submitted'])
        for emp in approved:
            writer.writerow([emp.id, emp.company_name, emp.industry, emp.user.email, emp.last_submitted])
        return response
    
    @action(detail=True, methods=['post'], url_path='suspend-employee')
    def suspend_employee(self, request, pk=None):
        try:
            profile = EmployeeProfile.objects.get(pk=pk)
            profile.status = 'suspended'
            profile.save()
            suspend_message = "Your employee profile has been suspended by the manager."
            notify_user(subject="Profile Suspended", message=suspend_message, recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='suspended', message=suspend_message)
            logger.info(f"Employee profile {pk} suspended by manager {request.user.email}")
            return Response({'detail': 'Profile suspended'}, status=status.HTTP_200_OK)
        except EmployeeProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='activate-employee')
    def activate_employee(self, request, pk=None):
        try:
            profile = EmployeeProfile.objects.get(pk=pk)
            profile.status = 'approved'
            profile.save()
            activate_message = "Your employee profile has been activated by the manager."
            notify_user(subject="Profile Activated", message=activate_message, recipient_email=profile.user.email)
            notify_user_status(user_id=profile.user.id, status='activated', message=activate_message)
            logger.info(f"Employee profile {pk} activated by manager {request.user.email}")
            return Response({'detail': 'Profile activated'}, status=status.HTTP_200_OK)
        except EmployeeProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)