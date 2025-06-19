from rest_framework import serializers
from shift.models import Shift
from shift.stores.functions import apply_shift_update, calculate_and_save_total_pay

class ShiftEmployerSerializer(serializers.ModelSerializer):
    employer_id = serializers.IntegerField(read_only=True)
    total_pay = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)  

    class Meta:
        model = Shift
        exclude = ['manager']  

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        validated_data['employer'] = user
        validated_data['status'] = 'pending'
        shift = Shift.objects.create(**validated_data)
        return calculate_and_save_total_pay(shift)

    def update(self, instance, validated_data):
        if instance.status != 'pending':
            raise serializers.ValidationError("Only pending shifts can be updated.")
        return apply_shift_update(instance, validated_data)

    def validate_delete(self):
        """Call this manually before attempting to delete the instance"""
        if self.instance.status != 'pending':
            raise serializers.ValidationError("Only pending shifts can be deleted.")
