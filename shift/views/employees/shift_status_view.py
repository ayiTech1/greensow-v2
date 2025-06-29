from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shift.models import ShiftAssignment
from shift.serializers.shift.assignment import AssignemtSerializer, AssignmentDetailSerializer
from accounts.permissions import IsEmployeeOnly


class EmployeeShiftStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployeeOnly]

    def list_assignments_by_status(self, request, status_label):
        date_str = request.query_params.get('date')
        filters = {'employee': request.user, 'status': status_label}

        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                filters['shift__date'] = date_obj
            except ValueError:
                return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        assignments = ShiftAssignment.objects.select_related('shift').filter(**filters).order_by('-created_at')
        serializer = AssignemtSerializer(assignments, many=True, context={'request': request})
        return Response({
            "count": assignments.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve_assignment_by_status(self, request, pk, status_label):
        try:
            assignment = ShiftAssignment.objects.select_related('shift').get(
                pk=pk, employee=request.user, status=status_label
            )
        except ShiftAssignment.DoesNotExist:
            return Response({"detail": f"{status_label.capitalize()} shift not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentDetailSerializer(assignment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Taken
    @action(detail=False, methods=['get'], url_path='taken-shifts')
    def taken_shifts(self, request):
        return self.list_assignments_by_status(request, 'taken')

    @action(detail=True, methods=['get'], url_path='taken-detail')
    def taken_shift_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(request, pk, 'taken')

    # Ongoing
    @action(detail=False, methods=['get'], url_path='ongoing-shifts')
    def ongoing_shifts(self, request):
        return self.list_assignments_by_status(request, 'ongoing')

    @action(detail=True, methods=['get'], url_path='ongoing-detail')
    def ongoing_shift_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(request, pk, 'ongoing')

    # Completed
    @action(detail=False, methods=['get'], url_path='completed-shifts')
    def completed_shifts(self, request):
        return self.list_assignments_by_status(request, 'completed')

    @action(detail=True, methods=['get'], url_path='completed-detail')
    def completed_shift_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(request, pk, 'completed')
