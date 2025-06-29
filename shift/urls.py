from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shift.views.managers.shift_manage_view import ShiftManageViewSet
from shift.views.managers.shift_assignment_view import ShiftAssignmentViewSet
from shift.views.managers.shift_status_view import ShiftStatusViewSet
from shift.views.employers.shift_manage_view import EmployersShiftManageViewSet
from shift.views.employers.shift_assignment_view import EmployersShiftAssignmentViewSet
from shift.views.employers.shift_status_view import EmployerShiftStatusViewSet
from shift.views.employees.shift_assignment_view import EmployeeShiftAssignmentViewSet
from shift.views.employees.shift_status_view import EmployeeShiftStatusViewSet



router = DefaultRouter()
router.register(r'manager/shifts-manage', ShiftManageViewSet, basename='manager-shift')
router.register(r'manager/shift-assignments', ShiftAssignmentViewSet, basename='manager-shift-assignment')
router.register(r'manager/shift-status', ShiftStatusViewSet, basename='manager-shift-status')
router.register(r'employer/shifts-manage', EmployersShiftManageViewSet, basename='employer-shift-manage')
router.register(r'employer/shift-assignments',EmployersShiftAssignmentViewSet, basename='employer-shift-assignment')
router.register(r'employer/shifts-status', EmployerShiftStatusViewSet, basename='employer-shift-status')
router.register(r'employee/shifts-assignment', EmployeeShiftAssignmentViewSet, basename='employee-shift-assignment') 
router.register(r'employee/shift-status', EmployeeShiftStatusViewSet, basename='employee-shift-status')  


urlpatterns = [
    path('', include(router.urls)),
]
