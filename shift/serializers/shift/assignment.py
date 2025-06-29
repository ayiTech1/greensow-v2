from rest_framework import serializers
from shift.models import ShiftAssignment

class AssignemtSerializer(serializers.ModelSerializer):
    shift_id = serializers.IntegerField(source='shift.id')
    name = serializers.CharField(source='shift.name')
    company_name = serializers.CharField(source='shift.company_name')
    date = serializers.DateField(source='shift.date')
    start_time = serializers.TimeField(source='shift.start_time')
    end_time = serializers.TimeField(source='shift.end_time')
    address = serializers.CharField(source='shift.address')

    class Meta:
        model = ShiftAssignment
        fields = [
            'id', 'shift_id', 'name', 'company_name', 'date',
            'start_time', 'end_time', 'address', 'status'
        ]
        read_only_fields = fields

class AssignmentDetailSerializer(serializers.ModelSerializer):
    shift_id = serializers.IntegerField(source='shift.id')
    name = serializers.CharField(source='shift.name')
    company_name = serializers.CharField(source='shift.company_name')
    date = serializers.DateField(source='shift.date')
    start_time = serializers.TimeField(source='shift.start_time')
    end_time = serializers.TimeField(source='shift.end_time')
    address = serializers.CharField(source='shift.address')
    base_pay = serializers.DecimalField(source='shift.base_pay', max_digits=10, decimal_places=2)
    bonus_pay = serializers.DecimalField(source='shift.bonus_pay', max_digits=10, decimal_places=2)
    total_pay = serializers.DecimalField(source='shift.total_pay', max_digits=10, decimal_places=2)

    class Meta:
        model = ShiftAssignment
        fields = [
            'id', 'shift_id', 'name', 'company_name', 'date',
            'start_time', 'end_time', 'address',
            'base_pay', 'bonus_pay', 'total_pay',
            'actual_start_time', 'actual_end_time',
            'status', 'completed_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
