from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from shift.models import Shift
from shift.serializers.managers import ManagerShiftSerializer
from shift.stores.functions import (
    get_approved_shift_summary_grouped,
    get_pending_shift_summary_grouped,
    get_rejected_shift_summary_grouped,
    get_approved_shift_detail,
    get_pending_shift_detail,
    get_rejected_shift_detail,
)
from accounts.permissions import IsManagerOnly
from shift.utils.response import error_response, success_response



class ManagerShiftViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManagerOnly]

    def list(self, request):
        """List all shifts optionally filtered by status"""
        status_filter = request.query_params.get('status')
        shifts = Shift.objects.filter(status=status_filter) if status_filter else Shift.objects.all()
        serializer = ManagerShiftSerializer(shifts, many=True)
        return success_response("Shifts fetched successfully.", serializer.data)

    @action(detail=False, methods=['post'], url_path='create')
    def create_shift(self, request):
        """Manager creates a shift for an employer by specifying company name"""
        serializer = ManagerShiftSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            shift = serializer.save()
            return success_response("Shift created successfully.")
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_shift(self, request, pk=None):
        """Manager deletes a shift"""
        shift = get_object_or_404(Shift, pk=pk)
        serializer = ManagerShiftSerializer(instance=shift, context={'request': request})
        
        try:
            serializer.delete()
        except serializers.ValidationError as e:
            return error_response(str(e.detail[0]), status.HTTP_403_FORBIDDEN)
        except PermissionDenied as e:
            return error_response(str(e.detail), status.HTTP_403_FORBIDDEN)
        shift.delete()
        return success_response("Shift deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)


    @action(detail=True, methods=['post'], url_path='approve')
    def approve_shift(self, request, pk=None):
        shift = get_object_or_404(Shift, pk=pk, status='pending')
        shift.status = 'approved'
        shift.manager = request.user
        shift.save()
        return success_response("Shift approved successfully.")

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_shift(self, request, pk=None):
        shift = get_object_or_404(Shift, pk=pk, status='pending')
        shift.status = 'rejected'
        shift.manager = request.user
        shift.save()
        return success_response("Shift rejected successfully.")

    # ----------- Approved ------------
    @action(detail=False, methods=['get'], url_path='approved-shifts')
    def approved_shifts(self, request):
        data = get_approved_shift_summary_grouped()
        if not data.get('summary'):
            return error_response("No approved shifts available.", status.HTTP_404_NOT_FOUND)
        return success_response("Approved shifts fetched successfully.", data)

    @action(detail=True, methods=['get'], url_path='approved-shift-detail')
    def approved_shift_detail(self, request, pk=None):
        shift, error = get_approved_shift_detail(pk)
        if error:
            return error_response(error['message'], error['status'])
        return success_response("Approved shift detail retrieved.", ManagerShiftSerializer(shift).data)

    # ----------- Pending ------------
    @action(detail=False, methods=['get'], url_path='pending-shifts')
    def pending_shifts(self, request):
        data = get_pending_shift_summary_grouped()
        if not data.get('summary'):
            return error_response("No pending shifts available.", status.HTTP_404_NOT_FOUND)
        return success_response("Pending shifts fetched successfully.", data)

    @action(detail=True, methods=['get'], url_path='pending-shift-detail')
    def pending_shift_detail(self, request, pk=None):
        shift, error = get_pending_shift_detail(pk)
        if error:
            return error_response(error['message'], error['status'])
        return success_response("Pending shift detail retrieved.", ManagerShiftSerializer(shift).data)

    # ----------- Rejected ------------
    @action(detail=False, methods=['get'], url_path='rejected-shifts')
    def rejected_shifts(self, request):
        data = get_rejected_shift_summary_grouped()
        if not data.get('summary'):
            return error_response("No rejected shifts available.", status.HTTP_404_NOT_FOUND)
        return success_response("Rejected shifts fetched successfully.", data)

    @action(detail=True, methods=['get'], url_path='rejected-shift-detail')
    def rejected_shift_detail(self, request, pk=None):
        shift, error = get_rejected_shift_detail(pk)
        if error:
            return error_response(error['message'], error['status'])
        return success_response("Rejected shift detail retrieved.", ManagerShiftSerializer(shift).data)
