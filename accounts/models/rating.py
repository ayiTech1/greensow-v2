from django.db import models
from accounts.models.user import User
from accounts.models.profile import EmployeeProfile, EmployerProfile
from accounts.models.managers.rating import RatingManager

class Rating(models.Model):
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='received_ratings')
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='received_ratings')
    score = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RatingManager()

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['rater', 'employee'], name='unique_rating_employee'),
            models.UniqueConstraint(fields=['rater', 'employer'], name='unique_rating_employer'),
        ]


    def __str__(self):
        target = self.employee or self.employer
        return f"Rating for {target} by {self.rater.email} - {self.score}"

    @property
    def average_rating(self):
        ratings = self.received_ratings.all()
        return round(sum(r.score for r in ratings) / ratings.count(), 2) if ratings.exists() else 0.0

    @property
    def rating_count(self):
        return self.received_ratings.count()
