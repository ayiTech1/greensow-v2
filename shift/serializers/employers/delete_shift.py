from rest_framework import serializers
from shift.models import Shift


class EmployerDeleteShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        exclude = ['manager']

    def check_can_delete(self):
        """Call this before deleting"""
        if self.instance.status != 'pending':
            raise serializers.ValidationError("Only pending shifts can be deleted.")
