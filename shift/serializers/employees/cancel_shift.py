from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta

from shift.models import ShiftAssignment

class CancelShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAssignment
        fields = ['id']

    def validate(self, attrs):
        assignment = self.instance
        user = self.context['request'].user
        shift = assignment.shift

        # Only the assigned employee can cancel
        if assignment.employee != user:
            raise serializers.ValidationError("You are not authorized to cancel this shift.")

        # Only 'taken' or 'ongoing' shifts can be canceled
        if assignment.status != 'taken':
            raise serializers.ValidationError("Only shifts in 'taken' can be cancelled.")

        # Cannot cancel within 30 minutes of start time
        now = timezone.localtime()
        shift_datetime = timezone.make_aware(datetime.combine(shift.date, shift.start_time))
        if shift_datetime - now <= timedelta(minutes=30):
            raise serializers.ValidationError("You can only cancel a shift at least 30 minutes before it starts.")

        return attrs

    def update(self, instance, validated_data):
        instance.status = 'cancelled'
        instance.save()

        return instance
