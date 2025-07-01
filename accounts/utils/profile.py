from accounts.models import EmployerProfile
from accounts.models.profile import EmployeeProfile

def get_employer_profile(user):
    return EmployerProfile.objects.filter(user=user).first()


def get_employee_profile(user):
        return EmployeeProfile.objects.filter(user=user).first()


