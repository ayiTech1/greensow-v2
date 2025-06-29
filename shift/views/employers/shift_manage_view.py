from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from shift.models import Shift
from accounts.permissions import IsEmployerOnly
from core.response import success_response, error_response
from shift.serializers.employers.create_shift import  EmployerCreateShiftSerializer
from shift.serializers.employers.delete_shift import EmployerDeleteShiftSerializer
from shift.serializers.employers.update_shift import EmployerUpdateShiftSerializer
from shift.utils.shift_notify import notify_manager_shift_deleted_by_employer, notify_manager_shift_updated_by_employer, notify_managers_about_shift


class EmployersShiftManageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]

    @action(detail=False, methods=['post'], url_path='create')
    def create_shift(self, request):
        """Employer creates their own shift."""
        serializer = EmployerCreateShiftSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                notify_managers_about_shift(serializer.instance)
                return success_response("Shift created successfully.", status.HTTP_201_CREATED)
            except Exception as e:
                # print("🔴 EXCEPTION:", str(e))
                raise  # this will show the full traceback in docker logs
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update')
    def update_shift(self, request, pk=None):
        shift = get_object_or_404(Shift, pk=pk)

        serializer = EmployerUpdateShiftSerializer(
            shift, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            updated_shift = serializer.save()
            notify_manager_shift_updated_by_employer(serializer.instance)
            return success_response({
                "success": True,
                "message": "Shift updated successfully.",
                "data": EmployerUpdateShiftSerializer(updated_shift).data
            }, status=status.HTTP_200_OK)

        return error_response({
            "success": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_shift(self, request, pk=None):
        """Employer deletes their own pending shift."""
        shift = get_object_or_404(Shift, pk=pk, employer=request.user)
        serializer = EmployerDeleteShiftSerializer(instance=shift, context={'request': request})
        serializer.validate_delete()
        if shift.manager:
            notify_manager_shift_deleted_by_employer(shift)
        shift.delete()
        return success_response("Shift deleted successfully.", status.HTTP_204_NO_CONTENT)
