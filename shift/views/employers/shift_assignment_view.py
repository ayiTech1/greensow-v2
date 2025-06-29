from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shift.models import ShiftAssignment
from shift.serializers.shift.assignment import AssignemtSerializer, AssignmentDetailSerializer
from accounts.permissions import IsEmployerOnly
from datetime import datetime


class EmployersShiftAssignmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]

    def list_assignments_by_status(self, status_label, request):
        date_filter = request.query_params.get('date')
        queryset = ShiftAssignment.objects.select_related('shift', 'employee').filter(
            shift__employer=request.user,
            status=status_label
        ).order_by('-created_at')

        if date_filter:
            try:
                parsed_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                queryset = queryset.filter(shift__date=parsed_date)
            except ValueError:
                return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssignemtSerializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve_assignment_by_status(self, pk, status_label, request):
        try:
            assignment = ShiftAssignment.objects.select_related('shift', 'employee').get(
                pk=pk,
                shift__employer=request.user,
                status=status_label
            )
        except ShiftAssignment.DoesNotExist:
            return Response({"detail": f"{status_label.capitalize()} shift not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentDetailSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------ TAKEN ------------------
    @action(detail=False, methods=['get'], url_path='taken-shifts')
    def taken_shifts(self, request):
        return self.list_assignments_by_status("taken", request)

    @action(detail=True, methods=['get'], url_path='taken-detail')
    def taken_shift_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(pk, "taken", request)

    # ------------------ COMPLETED ------------------
    @action(detail=False, methods=['get'], url_path='completed-shifts')
    def completed_shifts(self, request):
        return self.list_assignments_by_status("completed", request)

    @action(detail=True, methods=['get'], url_path='completed-detail')
    def completed_shift_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(pk, "completed", request)

    # ------------------ ONGOING ------------------
    @action(detail=False, methods=['get'], url_path='ongoing-shifts')
    def ongoing_shifts(self, request):
        return self.list_assignments_by_status("ongoing", request)

    @action(detail=True, methods=['get'], url_path='ongoing-detail')
    def ongoing_shift_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(pk, "ongoing", request)
