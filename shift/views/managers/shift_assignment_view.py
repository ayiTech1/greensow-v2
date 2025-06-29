from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shift.models import ShiftAssignment
from shift.serializers.shift.assignment import AssignemtSerializer, AssignmentDetailSerializer
from accounts.permissions import IsManagerOnly


class ShiftAssignmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsManagerOnly]

    def list_assignments_by_status(self, request, status_label):
        date = request.query_params.get('date')
        filters = {
            'shift__manager': request.user,
            'status': status_label
        }
        if date:
            filters['shift__date'] = date

        assignments = ShiftAssignment.objects.select_related('shift').filter(**filters).order_by('-created_at')
        serializer = AssignemtSerializer(assignments, many=True, context={'request': request})
        return Response({
            "count": assignments.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve_assignment_by_status(self, request, pk, status_label):
        try:
            assignment = ShiftAssignment.objects.select_related('shift').get(
                pk=pk, shift__manager=request.user, status=status_label
            )
        except ShiftAssignment.DoesNotExist:
            return Response({'detail': f'{status_label.capitalize()} shift not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentDetailSerializer(assignment, context={'request': request})
        return Response({"assignment": serializer.data}, status=status.HTTP_200_OK)

    # ----------- Taken Assignments -----------
    @action(detail=False, methods=['get'], url_path='taken-assignments')
    def taken_assignments(self, request):
        return self.list_assignments_by_status(request, 'taken')

    @action(detail=True, methods=['get'], url_path='taken-assignment-detail')
    def taken_assignment_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(request, pk, 'taken')

    # ----------- Completed Assignments -----------
    @action(detail=False, methods=['get'], url_path='completed-assignments')
    def completed_assignments(self, request):
        return self.list_assignments_by_status(request, 'completed')

    @action(detail=True, methods=['get'], url_path='completed-assignment-detail')
    def completed_assignment_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(request, pk, 'completed')

    # ----------- Ongoing Assignments -----------
    @action(detail=False, methods=['get'], url_path='ongoing-assignments')
    def ongoing_assignments(self, request):
        return self.list_assignments_by_status(request, 'ongoing')

    @action(detail=True, methods=['get'], url_path='ongoing-assignment-detail')
    def ongoing_assignment_detail(self, request, pk=None):
        return self.retrieve_assignment_by_status(request, pk, 'ongoing')
