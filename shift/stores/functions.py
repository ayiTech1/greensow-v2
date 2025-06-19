from shift.models import Shift
from rest_framework import status


def get_shift_summary_grouped(status_label):
    shifts = Shift.objects.filter(status=status_label).order_by('-created_at')

    if not shifts.exists():
        return {
            "total_count": 0,
            "summary": [],
            "message": f"No {status_label} shifts available."
        }

    seen = set()
    summary = []

    for shift in shifts:
        key = (shift.company_name or "", shift.name or "", shift.address or "", shift.date, shift.start_time)
        if key not in seen:
            seen.add(key)
            summary.append({
                "shift_id": shift.id,
                "company_name": key[0],
                "shift_name": key[1],
                "location": key[2],
                "date": key[3],
                "start_time": key[4],
            })

    return {
        "total_count": shifts.count(),
        "summary": summary
    }


def get_shift_detail(shift_id, status_label):
    try:
        shift = Shift.objects.get(id=shift_id, status=status_label)
        return shift, None
    except Shift.DoesNotExist:
        return None, {
            "message": f"{status_label.capitalize()} shift not found.",
            "status": status.HTTP_404_NOT_FOUND
        }


# Wrapper functions for explicit calls

def get_approved_shift_summary_grouped():
    return get_shift_summary_grouped('approved')

def get_pending_shift_summary_grouped():
    return get_shift_summary_grouped('pending')

def get_rejected_shift_summary_grouped():
    return get_shift_summary_grouped('rejected')


def get_approved_shift_detail(shift_id):
    return get_shift_detail(shift_id, 'approved')

def get_pending_shift_detail(shift_id):
    return get_shift_detail(shift_id, 'pending')

def get_rejected_shift_detail(shift_id):
    return get_shift_detail(shift_id, 'rejected')


def apply_shift_update(instance, validated_data):
    base_pay = validated_data.get('base_pay', instance.base_pay)
    bonus_pay = validated_data.get('bonus_pay', instance.bonus_pay)

    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    instance.total_pay = base_pay + bonus_pay
    instance.save()

    return instance

def calculate_and_save_total_pay(shift):
    shift.total_pay = shift.base_pay + shift.bonus_pay
    shift.save()
    return shift