from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from shift.models import Shift
from accounts.models import User
from shift.stores.functions import apply_shift_update, calculate_and_save_total_pay


class ShiftManagerSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True)
    manager_id = serializers.IntegerField(read_only=True)
    total_pay = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Shift
        exclude = ['employer', 'manager']  

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        company_name = validated_data.pop('company_name')

        try:
            employer = User.objects.get(role__name='employer', company_name__iexact=company_name)
        except User.DoesNotExist:
            raise serializers.ValidationError({'company_name': 'No employer found with that company name.'})

        shift = Shift.objects.create(
            employer=employer,
            manager=user,
            status='approved',
            **validated_data
        )
       
        return calculate_and_save_total_pay(shift)

    def update(self, instance, validated_data):
        return apply_shift_update(instance, validated_data)
    
    
    def delete(self):
        request = self.context.get('request')
        shift = self.instance

        if shift.manager != request.user:
            raise PermissionDenied("You are not authorized to delete this shift.")
        
        # Optional: prevent deleting approved shifts
        if shift.status == 'approved':
            raise serializers.ValidationError("Approved shifts cannot be deleted.")
