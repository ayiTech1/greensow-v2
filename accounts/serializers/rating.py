from rest_framework import serializers
from accounts.models.rating import Rating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'score', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        shift_assignment = self.context['shift_assignment']
        rater = self.context['request'].user

        # check if rating already exists
        if Rating.objects.filter(rater=rater, shift_assignment=shift_assignment).exists():
            raise serializers.ValidationError("You have already rated this shift assignment.")

        if shift_assignment.status != 'completed':
            raise serializers.ValidationError("You can only rate completed shift assignments.")

        return data

    def create(self, validated_data):
        rater = self.context['request'].user
        shift_assignment = self.context['shift_assignment']

        if rater.is_employer:
            employee = shift_assignment.employee.employee_profile
            employer = None
        else:
            employer = shift_assignment.shift.employer.employer_profile
            employee = None

        return Rating.objects.create(
            rater=rater,
            employee=employee,
            employer=employer,
            shift_assignment=shift_assignment,
            score=validated_data['score'],
            comment=validated_data.get('comment', '')
        )
