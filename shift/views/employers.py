from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from shift.models import Shift
from shift.serializers.employers import ShiftEmployerSerializer
from accounts.permissions import IsEmployerOnly
from shift.utils.response import success_response

class EmployerShiftViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]

    def get_queryset(self, status_filter=None):
        user = self.request.user
        queryset = Shift.objects.filter(employer=user)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')

    def list(self, request):
        """List all shifts for the authenticated employer (optionally filtered by status)"""
        status_filter = request.query_params.get('status')
        shifts = self.get_queryset(status_filter)
        serializer = ShiftEmployerSerializer(shifts, many=True)
        return success_response("Shifts retrieved successfully.", serializer.data)

    @action(detail=False, methods=['post'], url_path='create')
    def create_shift(self, request):
        """Employer creates their own shift."""
        serializer = ShiftEmployerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return success_response("Shift created successfully.", status_code=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='update')
    def update_shift(self, request, pk=None):
        """Employer updates their own pending shift"""
        shift = get_object_or_404(Shift, pk=pk, employer=request.user)
        serializer = ShiftEmployerSerializer(shift, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return success_response("Shift updated successfully.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_shift(self, request, pk=None):
        """Employer deletes their own pending shift"""
        shift = get_object_or_404(Shift, pk=pk, employer=request.user)
        serializer = ShiftEmployerSerializer(instance=shift, context={'request': request})
        serializer.validate_delete()
        shift.delete()
        return success_response("Shift deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_shifts(self, request):
        """Employer views their own pending shifts"""
        shifts = self.get_queryset('pending')
        if not shifts.exists():
            return Response({"detail": "No pending shifts found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShiftEmployerSerializer(shifts, many=True)
        return success_response("Pending shifts retrieved successfully.", serializer.data)

    @action(detail=False, methods=['get'], url_path='approved')
    def approved_shifts(self, request):
        """Employer views their own approved shifts"""
        shifts = self.get_queryset('approved')
        if not shifts.exists():
            return Response({"detail": "No approved shifts found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShiftEmployerSerializer(shifts, many=True)
        return success_response("Approved shifts retrieved successfully.", serializer.data)

    @action(detail=False, methods=['get'], url_path='rejected')
    def rejected_shifts(self, request):
        """Employer views their own rejected shifts"""
        shifts = self.get_queryset('rejected')
        if not shifts.exists():
            return Response({"detail": "No rejected shifts found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShiftEmployerSerializer(shifts, many=True)
        return success_response("Rejected shifts retrieved successfully.", serializer.data)
