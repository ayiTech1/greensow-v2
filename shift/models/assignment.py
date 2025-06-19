from shift.stores.constant import SHIFT_ASSIGNMENT
from django.db import models
from django.db.models import Q, CheckConstraint
from django.utils.translation import gettext_lazy as _
from accounts.models.user import User
from shift.models.shift import Shift


class ShiftAssignment(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='assignments', help_text=_("The shift to which this assignment belongs"), verbose_name=_("Shift"))
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_assignments', help_text=_("Employee assigned to this shift"), verbose_name=_("Employee"))
    status = models.CharField(max_length=20, choices=SHIFT_ASSIGNMENT, default='taken', db_index=True, help_text=_("Current status of the shift assignment"), verbose_name=_("Assignment Status"))
    filled_openings = models.PositiveIntegerField(default=0, help_text=_("Number of filled openings by this assignment"), verbose_name=_("Filled Openings"))
    actual_start_time = models.TimeField(null=True, blank=True, help_text=_("Actual time the employee started the shift"), verbose_name=_("Actual Start Time"))
    actual_end_time = models.TimeField(null=True, blank=True, help_text=_("Actual time the employee ended the shift"), verbose_name=_("Actual End Time"))
    notify_time_start = models.BooleanField(default=False, help_text=_("Whether a shift reminder has been sent"), verbose_name=_("Reminder Sent"))
    completed_notes = models.TextField(blank=True, null=True, help_text=_("Notes entered upon completion of the shift"), verbose_name=_("Completion Notes"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, help_text=_("Timestamp when the record was created"),verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Timestamp when the record was last updated"),verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Shift Assignment")
        verbose_name_plural = _("Shift Assignments")
        constraints = [
            CheckConstraint(check=Q(actual_start_time__lte=models.F('actual_end_time')), name='check_actual_start_end'),
        ]
