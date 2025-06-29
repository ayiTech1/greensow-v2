from rest_framework import serializers
from shift.models import Shift

class ShiftSerializer(serializers.ModelSerializer):
    shift_id = serializers.IntegerField(source='id')

    class Meta:
        model = Shift
        fields = ('shift_id', 'company_name', 'name', 'address', 'date', 'start_time', 'status')



class ShiftDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'  
        read_only_fields = ['id', 'manager', 'created_at', 'updated_at', 'status']
