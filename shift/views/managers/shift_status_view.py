# shift/views/shift_status.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shift.models import Shift
from shift.serializers.shift.shift_serializer import ShiftSerializer, ShiftDetailSerializer
from accounts.permissions import IsManagerOnly


class ShiftStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManagerOnly]

    def list_shifts_by_status(self, status_label):
        queryset = Shift.objects.filter(status=status_label).order_by('-created_at')
        serializer = ShiftSerializer(queryset, many=True)
        return Response({
            "total_count": queryset.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve_shift_by_status(self, pk, status_label):
        try:
            shift = Shift.objects.get(pk=pk, status=status_label)
        except Shift.DoesNotExist:
            return Response({"detail": f"{status_label.capitalize()} shift not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShiftDetailSerializer(shift)
        return Response({"shift": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='approved-shifts')
    def approved_shifts(self, request):
        return self.list_shifts_by_status("approved")

    @action(detail=True, methods=['get'], url_path='approved-shift-detail')
    def approved_shift_detail(self, request, pk=None):
        return self.retrieve_shift_by_status(pk, "approved")

    @action(detail=False, methods=['get'], url_path='pending-shifts')
    def pending_shifts(self, request):
        return self.list_shifts_by_status("pending")

    @action(detail=True, methods=['get'], url_path='pending-shift-detail')
    def pending_shift_detail(self, request, pk=None):
        return self.retrieve_shift_by_status(pk, "pending")

    @action(detail=False, methods=['get'], url_path='rejected-shifts')
    def rejected_shifts(self, request):
        return self.list_shifts_by_status("rejected")

    @action(detail=True, methods=['get'], url_path='rejected-shift-detail')
    def rejected_shift_detail(self, request, pk=None):
        return self.retrieve_shift_by_status(pk, "rejected")
