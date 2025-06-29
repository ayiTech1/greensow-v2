from rest_framework import serializers
from django.utils import timezone
from shift.models import ShiftAssignment

class StartShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAssignment
        fields = ['id']  

    def validate(self, attrs):
        request = self.context['request']
        assignment = self.instance
        shift = assignment.shift
        now = timezone.localtime().time()

        # Ensure employee owns this assignment
        if assignment.employee != request.user:
            raise serializers.ValidationError("You are not authorized to start this shift.")

        # Shift must be in 'taken' state
        if assignment.status != 'taken':
            raise serializers.ValidationError("Only shifts with 'taken' status can be started.")

        # Prevent starting after already started
        if assignment.actual_start_time:
            raise serializers.ValidationError("This shift has already been started.")

        # Prevent starting too early
        if now < shift.start_time:
            raise serializers.ValidationError("You can only start the shift at or after the scheduled start time.")

        return attrs

    def update(self, instance, validated_data):
        instance.status = 'ongoing'
        instance.actual_start_time = timezone.localtime().time()
        instance.save()
        return instance
