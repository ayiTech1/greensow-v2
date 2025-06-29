from rest_framework import serializers
from django.utils import timezone
from datetime import datetime

from shift.models import ShiftAssignment


class CompleteShiftSerializer(serializers.ModelSerializer):
    completed_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ShiftAssignment
        fields = ['id', 'completed_notes']

    def validate(self, attrs):
        assignment = self.instance
        user = self.context['request'].user
        shift = assignment.shift
        now = timezone.localtime()

        # Only the assigned employee can complete
        if assignment.employee != user:
            raise serializers.ValidationError("You are not authorized to complete this shift.")

        # Shift must be ongoing to complete
        if assignment.status != 'ongoing':
            raise serializers.ValidationError("Only ongoing shifts can be completed.")

        # Check if shift has ended
        shift_end = timezone.make_aware(datetime.combine(shift.date, shift.end_time))
        if now < shift_end:
            raise serializers.ValidationError("You can only complete the shift after the scheduled end time.")

        return attrs

    def update(self, instance, validated_data):
        instance.status = 'completed'
        instance.actual_end_time = timezone.localtime().time()
        instance.completed_notes = validated_data.get('completed_notes', '')
        instance.save()
        return instance
