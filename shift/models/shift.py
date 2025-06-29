from django.db import models
from django.db.models import Q, CheckConstraint, F
from django.utils.translation import gettext_lazy as _
from accounts.models.user import User

SHIFT = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('posted', 'Posted')
]


class Shift(models.Model):
    employer = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_shifts',
        verbose_name=_("Employer"),
        help_text=_("Employer who created the shift")
    )

    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='managed_shifts',
        verbose_name=_("Manager"),
        help_text=_("Manager assigned to oversee the shift")
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("Shift Name"),
        help_text=_("Title or name of the shift")
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of the shift")
    )

    address = models.TextField(
        verbose_name=_("Location"),
        help_text=_("Location address of the shift")
    )

    latitude = models.FloatField(
        null=True, blank=True,
        verbose_name=_("Latitude"),
        help_text=_("Latitude coordinate of the shift location")
    )

    longitude = models.FloatField(
        null=True, blank=True,
        verbose_name=_("Longitude"),
        help_text=_("Longitude coordinate of the shift location")
    )

    company_name = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Company Name"),
        help_text=_("Name of the company offering the shift")
    )

    date = models.DateField(
        db_index=True,
        verbose_name=_("Shift Date"),
        help_text=_("Date when the shift occurs")
    )

    start_time = models.TimeField(
        db_index=True,
        verbose_name=_("Start Time"),
        help_text=_("Time when the shift starts")
    )

    end_time = models.TimeField(
        db_index=True,
        verbose_name=_("End Time"),
        help_text=_("Time when the shift ends")
    )

    base_pay = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        verbose_name=_("Base Pay"),
        help_text=_("Base pay offered for the shift")
    )

    bonus_pay = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        verbose_name=_("Bonus Pay"),
        help_text=_("Additional bonus pay for the shift")
    )

    total_pay = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        verbose_name=_("Total Pay"),
        help_text=_("Total pay (base + bonus)")
    )

    total_openings = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Total Openings"),
        help_text=_("Total number of openings available for this shift")
    )

    status = models.CharField(
        max_length=20,
        choices=SHIFT,
        default='pending',
        db_index=True,
        verbose_name=_("Status"),
        help_text=_("Approval status of the shift")
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Whether the shift is currently active")
    )

    requirements = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Requirements"),
        help_text=_("List of requirements for the shift (in JSON format)")
    )

    prohibited_items = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Prohibited Items"),
        help_text=_("List of prohibited items during the shift (in JSON format)")
    )

    image_url = models.URLField(
        blank=True, null=True,
        verbose_name=_("Image URL"),
        help_text=_("Optional image related to the shift")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when the record was created")
    )

    class Meta:
        verbose_name = _("Shift")
        verbose_name_plural = _("Shifts")
        constraints = [
            CheckConstraint(check=Q(start_time__lt=F('end_time')), name='check_start_before_end'),
        ]

    def __str__(self):
        return f"{self.name} - {self.date} ({self.start_time} to {self.end_time})"
