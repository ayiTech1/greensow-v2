from celery import shared_task
from django.utils import timezone
from datetime import datetime

from shift.models import ShiftAssignment


@shared_task
def auto_start_shifts():
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    assignments = ShiftAssignment.objects.filter(
        shift__date=today,
        shift__start_time__lte=current_time,
        status='taken'
    )

    for assignment in assignments:
        assignment.status = 'ongoing'
        assignment.actual_start_time = current_time
        assignment.save()
    return f"{assignments.count()} shifts auto-started."


@shared_task
def auto_complete_shifts():
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    assignments = ShiftAssignment.objects.filter(
        shift__date=today,
        shift__end_time__lte=current_time,
        status='ongoing'
    )

    for assignment in assignments:
        assignment.status = 'completed'
        assignment.actual_end_time = current_time
        assignment.save()
    return f"{assignments.count()} shifts auto-completed."
