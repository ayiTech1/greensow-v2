from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from shift.models import Shift

from accounts.permissions import IsManagerOnly
from core.response import error_response, success_response
from shift.serializers.managers.create_shift import ManagerCreateShiftSerializer
from shift.serializers.managers.delete_shift import ManagerDeleteShiftSerializer
from shift.serializers.managers.update_shift import ManagerUpdateShiftSerializer
from shift.utils.shift_notify import (
    notify_employer_shift_created_by_manager,
    notify_employer_shift_deleted_by_manager,
    notify_employer_shift_status,
)


class ShiftManageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManagerOnly]

    @action(detail=False, methods=['post'], url_path='create')
    def create_shift(self, request):
        """Manager creates a shift for an employer."""
        serializer = ManagerCreateShiftSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            shift = serializer.save()
            if shift.employer:
                notify_employer_shift_created_by_manager(shift)
            return success_response(
                "Shift created successfully.",
                status=status.HTTP_201_CREATED
            )
        return error_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update')
    def update_shift(self, request, pk=None):
        """Manager updates a shift."""
        shift = get_object_or_404(Shift, pk=pk)
        serializer = ManagerUpdateShiftSerializer(shift, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Shift updated successfully.",
                status=status.HTTP_200_OK
            )
        return error_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_shift(self, request, pk=None):
        """Manager deletes a shift."""
        shift = get_object_or_404(Shift, pk=pk)
        serializer = ManagerDeleteShiftSerializer(instance=shift)
        serializer.validate({})
        serializer.delete()
        notify_employer_shift_deleted_by_manager(shift)
        return success_response(
            "Shift deleted successfully.",
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_shift(self, request, pk=None):
        """Manager approves a pending shift."""
        shift = get_object_or_404(Shift, pk=pk, status='pending')
        shift.status = 'approved'
        shift.manager = request.user
        shift.save()
        notify_employer_shift_status(shift, approved=True)
        return success_response(
            "Shift approved successfully.",
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_shift(self, request, pk=None):
        """Manager rejects a pending shift."""
        shift = get_object_or_404(Shift, pk=pk, status='pending')
        shift.status = 'rejected'
        shift.manager = request.user
        shift.save()
        notify_employer_shift_status(shift, approved=False)
        return success_response(
            "Shift rejected successfully.",
            status=status.HTTP_200_OK
        )
