from rest_framework import serializers
from shift.models import Shift, ShiftAssignment

class AvailableShiftSerializer(serializers.ModelSerializer):
    filled = serializers.SerializerMethodField()
    remaining_openings = serializers.SerializerMethodField()
    is_taken = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = [
            'id', 'company_name', 'name', 'address', 'date', 'start_time',
            'filled', 'remaining_openings', 'is_taken'
        ]

    def get_filled(self, obj):
        return ShiftAssignment.objects.filter(shift=obj).exclude(status='cancelled').count()

    def get_remaining_openings(self, obj):
        return max(obj.total_openings - self.get_filled(obj), 0)

    def get_is_taken(self, obj):
        user = self.context['request'].user
        return ShiftAssignment.objects.filter(shift=obj, employee=user).exclude(status='cancelled').exists()



class AvailableShiftDetailSerializer(serializers.ModelSerializer):
    filled = serializers.SerializerMethodField()
    remaining_openings = serializers.SerializerMethodField()
    is_taken = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = [
            'id', 'company_name', 'name', 'address', 'date', 'start_time', 'end_time',
            'base_pay', 'bonus_pay', 'total_pay', 'total_openings',
            'filled', 'remaining_openings', 'is_taken'
        ]

    def get_filled(self, obj):
        return ShiftAssignment.objects.filter(shift=obj).exclude(status='cancelled').count()

    def get_remaining_openings(self, obj):
        return max(obj.total_openings - self.get_filled(obj), 0)

    def get_is_taken(self, obj):
        user = self.context['request'].user
        return ShiftAssignment.objects.filter(shift=obj, employee=user).exclude(status='cancelled').exists()
