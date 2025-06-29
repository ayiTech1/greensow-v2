from rest_framework import serializers
from shift.models import Shift






class ManagerDeleteShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'  

    def validate(self, attrs):
        instance = self.instance
        if not instance:
            raise serializers.ValidationError("Shift does not exist.")
        if instance.status == 'posted':
            raise serializers.ValidationError("Posted shifts cannot be deleted.")
        return attrs

    def delete(self):
        instance = self.instance
        instance.delete()
        return instance
