from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from shift.models import ShiftAssignment
from accounts.serializers import RatingSerializer  
from core.response import success_response, error_response

class RatingViewSet(viewsets.ViewSet):
    
    @action(detail=True, methods=['post'], url_path='rate')
    def rate(self, request, pk=None):
        shift_assignment = get_object_or_404(ShiftAssignment, pk=pk)
        serializer = RatingSerializer(data=request.data, context={
            'request': request,
            'shift_assignment': shift_assignment
        })
        if serializer.is_valid():
            serializer.save()
            return success_response("Rating submitted successfully.", serializer.data, status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
