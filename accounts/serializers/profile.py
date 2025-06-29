
from rest_framework import serializers
from accounts.models.profile import EmployeeProfile, EmployerProfile

class EmployerProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=100)
    industry = serializers.CharField(max_length=100, required=False, allow_blank=True)
    average_rating = serializers.DecimalField(read_only=True, max_digits=4, decimal_places=2)
    total_ratings = serializers.IntegerField(read_only=True)


    class Meta:
        model = EmployerProfile
        fields = '__all__'
        read_only_fields = ['user', 'status', 'last_submitted', 'created_at', 'updated_at']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    average_rating = serializers.DecimalField(read_only=True, max_digits=4, decimal_places=2)
    total_ratings = serializers.IntegerField(read_only=True)
    class Meta:
        model = EmployeeProfile
        fields = '__all__'
        read_only_fields = ['user', 'status', 'last_submitted', 'created_at', 'updated_at']
