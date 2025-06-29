from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from shift.models import Shift
from shift.serializers.shift.shift_serializer import ShiftSerializer, ShiftDetailSerializer
from accounts.permissions import IsEmployerOnly


class EmployerShiftStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]

    def list_shifts_by_status(self, request, status_label):
        queryset = Shift.objects.filter(employer=request.user, status=status_label).order_by('-created_at')
        serializer = ShiftSerializer(queryset, many=True)
        return Response({
            "total_count": queryset.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve_shift_by_status(self, request, pk, status_label):
        shift = get_object_or_404(Shift, pk=pk, employer=request.user, status=status_label)
        serializer = ShiftDetailSerializer(shift)
        return Response({"shift": serializer.data}, status=status.HTTP_200_OK)

    # ---------- APPROVED ----------
    @action(detail=False, methods=['get'], url_path='approved-shifts')
    def approved_shifts(self, request):
        return self.list_shifts_by_status(request, "approved")

    @action(detail=True, methods=['get'], url_path='approved-detail')
    def approved_shift_detail(self, request, pk=None):
        return self.retrieve_shift_by_status(request, pk, "approved")

    # ---------- PENDING ----------
    @action(detail=False, methods=['get'], url_path='pending-shifts')
    def pending_shifts(self, request):
        return self.list_shifts_by_status(request, "pending")

    @action(detail=True, methods=['get'], url_path='pending-detail')
    def pending_shift_detail(self, request, pk=None):
        return self.retrieve_shift_by_status(request, pk, "pending")

    # ---------- REJECTED ----------
    @action(detail=False, methods=['get'], url_path='rejected-shifts')
    def rejected_shifts(self, request):
        return self.list_shifts_by_status(request, "rejected")

    @action(detail=True, methods=['get'], url_path='rejected-detail')
    def rejected_shift_detail(self, request, pk=None):
        return self.retrieve_shift_by_status(request, pk, "rejected")
