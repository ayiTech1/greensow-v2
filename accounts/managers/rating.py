
from accounts import models


class RatingManager(models.Manager):
    def rate_employee(self, rater, employee, score, shift_assignment, comment=""):
        if self.filter(rater=rater, shift_assignment=shift_assignment).exists():
            raise ValueError("You have already rated this shift assignment.")
        rating = self.create(
            rater=rater,
            employee=employee,
            shift_assignment=shift_assignment,
            score=score,
            comment=comment
        )
        profile = employee.employee_profile
        self._update_average(profile, score)
        return rating

    def rate_employer(self, rater, employer, score, shift_assignment, comment=""):
        if self.filter(rater=rater, shift_assignment=shift_assignment).exists():
            raise ValueError("You have already rated this shift assignment.")
        rating = self.create(
            rater=rater,
            employer=employer,
            shift_assignment=shift_assignment,
            score=score,
            comment=comment
        )
        profile = employer.employer_profile
        self._update_average(profile, score)
        return rating

    def _update_average(self, profile, new_score):
        total = profile.total_ratings
        current_avg = profile.average_rating or 0
        new_total = total + 1
        new_avg = ((current_avg * total) + new_score) / new_total
        profile.average_rating = round(new_avg, 2)
        profile.total_ratings = new_total
        profile.save()
