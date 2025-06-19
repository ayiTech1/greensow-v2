from rest_framework import serializers
from accounts.models.rating import Rating
from accounts.models.profile import EmployeeProfile, EmployerProfile

class RatingSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=EmployeeProfile.objects.all(), required=False, source='employee'
    )
    employer_id = serializers.PrimaryKeyRelatedField(
        queryset=EmployerProfile.objects.all(), required=False, source='employer'
    )

    class Meta:
        model = Rating
        fields = ['id', 'score', 'comment', 'employee_id', 'employer_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        employee = data.get('employee')
        employer = data.get('employer')

        if not employee and not employer:
            raise serializers.ValidationError("Must rate either an employee or an employer.")
        if employee and employer:
            raise serializers.ValidationError("Cannot rate both employee and employer at the same time.")
        return data

    def create(self, validated_data):
        rater = self.context['request'].user
        employee = validated_data.get('employee')
        employer = validated_data.get('employer')
        score = validated_data['score']
        comment = validated_data.get('comment', '')

        if employee:
            return Rating.objects.rate_employee(rater, employee, score, comment)
        return Rating.objects.rate_employer(rater, employer, score, comment)
