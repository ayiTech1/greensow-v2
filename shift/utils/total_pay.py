def calculate_and_save_total_pay(shift):
    shift.total_pay = (shift.base_pay or 0) + (shift.bonus_pay or 0)
    shift.save()
    return shift
