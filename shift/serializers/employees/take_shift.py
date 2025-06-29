from rest_framework import serializers
from django.core.exceptions import PermissionDenied
from shift.models import Shift, ShiftAssignment

class TakeShiftSerializer(serializers.ModelSerializer):
    shift_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ShiftAssignment
        fields = ['shift_id']

    def validate(self, attrs):
        """
        Validate shift eligibility and conflict checks before taking it.
        """
        request = self.context['request']
        user = request.user
        shift_id = attrs['shift_id']

        if not user.is_employee:
            raise PermissionDenied("Only employees can take shifts.")

        if user.employee_profile.approval_status != 'approved':
            raise PermissionDenied("Your profile must be approved to take shifts.")

        try:
            shift = Shift.objects.get(pk=shift_id)
        except Shift.DoesNotExist:
            raise serializers.ValidationError("Shift not found.")

        if shift.status != 'approved':
            raise PermissionDenied("Only approved shifts can be taken.")

        # Check if the shift is fully booked
        current_taken = ShiftAssignment.objects.filter(shift=shift).exclude(status='cancelled').count()
        if current_taken >= shift.total_openings:
            raise serializers.ValidationError("This shift is fully booked.")

        # Check if user already took the shift
        if ShiftAssignment.objects.filter(shift=shift, employee=user).exists():
            raise serializers.ValidationError("You have already taken this shift.")

        # Check for overlapping shifts
        overlapping_assignments = ShiftAssignment.objects.filter(
            employee=user,
            shift__date=shift.date,
            shift__start_time__lt=shift.end_time,
            shift__end_time__gt=shift.start_time,
        ).exclude(status='cancelled')

        if overlapping_assignments.exists():
            raise serializers.ValidationError("This shift overlaps with another shift you've taken.")

        self.shift = shift  # Cache for create()
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        shift = self.shift

        return ShiftAssignment.objects.create(
            shift=shift,
            employee=user,
            status='taken'
        )
