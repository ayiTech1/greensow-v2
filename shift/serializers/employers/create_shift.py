from rest_framework import serializers
from shift.models import Shift
from shift.utils.total_pay import calculate_and_save_total_pay


class EmployerCreateShiftSerializer(serializers.ModelSerializer):
    employer = serializers.PrimaryKeyRelatedField(read_only=True)
    total_pay = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Shift
        exclude = ['manager']

    def create(self, validated_data):
        user = self.context['request'].user

    
        employer_profile = getattr(user, 'employer_profile', None)
        if employer_profile is None:
            raise serializers.ValidationError("Employer profile is missing. Complete your employer profile first.")

        
        if employer_profile.status != 'approved':
            raise serializers.ValidationError("Your employer profile must be approved before creating shifts.")

        validated_data['employer'] = user
        validated_data['status'] = 'pending'
        validated_data['company_name'] = employer_profile.company_name

        shift = Shift.objects.create(**validated_data)
        return calculate_and_save_total_pay(shift)