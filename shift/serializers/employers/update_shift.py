from rest_framework import serializers
from shift.models import Shift
from shift.utils.total_pay import calculate_and_save_total_pay

    

class EmployerUpdateShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        exclude = ['manager']

    def update(self, instance, validated_data):
        if instance.status != 'pending':
            raise serializers.ValidationError("Only pending shifts can be updated.")

        request = self.context['request']
        user = request.user

        if instance.employer != user:
            raise serializers.ValidationError("You do not have permission to update this shift.")

        validated_data.pop('employer', None)
        validated_data.pop('manager', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        instance = calculate_and_save_total_pay(instance)

        return instance
