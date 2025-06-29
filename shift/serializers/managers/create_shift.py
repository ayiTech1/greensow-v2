from rest_framework import serializers
from shift.models import Shift
from accounts.models.profile import EmployerProfile
from shift.utils.total_pay import calculate_and_save_total_pay

class ManagerCreateShiftSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True)
    manager = serializers.PrimaryKeyRelatedField(read_only=True)
    total_pay = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Shift
        exclude = ['employer', 'manager']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        company_name = validated_data.pop('company_name')

        try:
            employer_profile = EmployerProfile.objects.select_related('user').get(
                company_name__iexact=company_name,
                status='approved'  # optional: only use approved employers
            )
            employer = employer_profile.user
        except EmployerProfile.DoesNotExist:
            raise serializers.ValidationError({
                'company_name': 'No approved employer found with that company name.'
            })

        shift = Shift.objects.create(
            employer=employer,
            manager=user,
            status='approved',
            **validated_data
        )

        return calculate_and_save_total_pay(shift)