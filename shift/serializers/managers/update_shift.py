from rest_framework import serializers
from shift.models import Shift
from shift.utils.total_pay import calculate_and_save_total_pay



class ManagerUpdateShiftSerializer(serializers.ModelSerializer):
    total_pay = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Shift
        exclude = ['employer', 'manager']  

    def update(self, instance, validated_data):
        """
        Allow manager to update any editable fields.
        Recalculate total pay if base or bonus pay changes.
        """
        request = self.context.get('request')
        user = request.user

        #  check is manager
        if not hasattr(user, 'role') or user.role.name != 'manager':
            raise serializers.ValidationError("Only managers can update shifts.")

        
        validated_data.pop('employer', None)
        validated_data.pop('manager', None)  # Manager shouldn't overwrite manager

        # Apply updates
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.manager = user 
        instance.save()

        # Recalculate total pay if needed
        return calculate_and_save_total_pay(instance)
