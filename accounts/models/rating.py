# accounts/models/rating.py

from django.db import models
from accounts.managers.rating import RatingManager
from accounts.models.profile import EmployeeProfile, EmployerProfile
from shift.models.assignment import ShiftAssignment  

class Rating(models.Model):
    rater = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, null=True, blank=True)
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, null=True, blank=True)
    shift_assignment = models.ForeignKey(ShiftAssignment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RatingManager()

    class Meta:
        unique_together = ('rater', 'shift_assignment')
