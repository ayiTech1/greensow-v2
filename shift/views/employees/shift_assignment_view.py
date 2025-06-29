from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shift.models import Shift, ShiftAssignment
from shift.serializers.employees.cancel_shift import CancelShiftSerializer
from shift.serializers.employees.complete_shift import CompleteShiftSerializer
from shift.serializers.employees.take_shift import TakeShiftSerializer
from shift.serializers.employees.start_shift import StartShiftSerializer
from shift.serializers.employees.available_shift import (
    AvailableShiftSerializer,
    AvailableShiftDetailSerializer
)
from accounts.permissions import IsEmployeeOnly

from shift.utils.shift_notify import (
    notify_shift_taken,
    notify_shift_started,
    notify_shift_cancelled,
    notify_shift_completed
)


class EmployeeShiftAssignmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]

    @action(detail=False, methods=['get'], url_path='available-shifts')
    def available_shifts(self, request):
        date = request.query_params.get('date')
        shifts = Shift.objects.filter(status='approved', is_active=True)

        if date:
            shifts = shifts.filter(date=date)

        serializer = AvailableShiftSerializer(shifts, many=True, context={'request': request})
        return Response({
            "total_count": len(serializer.data),
            "shifts": serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='available-shift-detail')
    def available_shift_detail(self, request, pk=None):
        try:
            shift = Shift.objects.get(id=pk, status='approved', is_active=True)
        except Shift.DoesNotExist:
            return Response({"detail": "Shift not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AvailableShiftDetailSerializer(shift, context={'request': request})
        return Response({"shift": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='take')
    def take_shift(self, request):
        serializer = TakeShiftSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            assignment = serializer.save()

            # Notify employer and manager that employee took the shift
            notify_shift_taken(assignment)

            return Response({"shift_taken": True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='start')
    def start_shift(self, request, pk=None):
        try:
            assignment = ShiftAssignment.objects.select_related('shift').get(pk=pk, employee=request.user)
        except ShiftAssignment.DoesNotExist:
            return Response({"detail": "Shift assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StartShiftSerializer(assignment, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Notify employer and manager that employee started the shift
            notify_shift_started(assignment)

            return Response({"started": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='cancel')
    def cancel_shift(self, request, pk=None):
        try:
            assignment = ShiftAssignment.objects.select_related('shift').get(pk=pk, employee=request.user)
        except ShiftAssignment.DoesNotExist:
            return Response({"detail": "Shift assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CancelShiftSerializer(assignment, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Notify employer and manager that employee cancelled the shift
            notify_shift_cancelled(assignment)

            return Response({"cancelled": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='complete')
    def complete_shift(self, request, pk=None):
        try:
            assignment = ShiftAssignment.objects.select_related('shift').get(pk=pk, employee=request.user)
        except ShiftAssignment.DoesNotExist:
            return Response({"detail": "Shift assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompleteShiftSerializer(assignment, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Notify employer and manager that employee completed the shift
            notify_shift_completed(assignment)

            return Response({"completed": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
