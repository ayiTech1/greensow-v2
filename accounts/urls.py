from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views.auth.manager_app_auth import ManagerAuthViewSet
from accounts.views.auth.manager_social_auth import ManagerSocialAuthViewSet
from accounts.views.auth.mfa_auth import MultifactorAuthenticationViewSet
from accounts.views.auth.reset_password import ResetPasswordViewSet
from accounts.views.auth.user_social_auth import UserSocialAuthViewSet
from accounts.views.auth.users_app_auth import UserAuthViewSet
from accounts.views.manager.manage_profile import ManagerEmployeeProfileManageViewSet, ManagerEmployerProfileManageViewSet
from accounts.views.manager.status_profile import ManagerEmployeeProfileStatusViewSet, ManagerEmployerProfileStatusViewSet
from accounts.views.notifications import NotificationViewSet
from accounts.views.rating import RatingViewSet
from accounts.views.users.employees.manage_profile import EmployeeProfileManageViewSet
from accounts.views.users.employees.status_profile import EmployeeProfileStatusViewSet
from accounts.views.users.employers.manage_profile import EmployerProfileManageViewSet
from accounts.views.users.employers.status_profile import EmployerProfileStatusViewSet

router = DefaultRouter()
router.register(r'manager/auth', ManagerAuthViewSet, basename='manager-auth')
router.register(r'manager/social', ManagerSocialAuthViewSet, basename='manager-social-auth')
router.register(r'users/auth', UserAuthViewSet, basename='users-auth')
router.register(r'users/social', UserSocialAuthViewSet, basename='user-social-auth')
router.register(r'mfa', MultifactorAuthenticationViewSet, basename='mfa-auth')
router.register(r'reset-password', ResetPasswordViewSet, basename='reset-password')
router.register(r'manager/employer-profiles', ManagerEmployerProfileManageViewSet, basename='manager-employer-profiles')
router.register(r'manager/employee-profiles', ManagerEmployeeProfileManageViewSet, basename='manager-employee-profiles')
router.register(r'manager/employer-status', ManagerEmployerProfileStatusViewSet, basename='manager-employer-status')
router.register(r'manager/employee-status', ManagerEmployeeProfileStatusViewSet, basename='manager-employee-status')
router.register(r'employees/profile', EmployeeProfileManageViewSet, basename='employee-profile')
router.register(r'employees/profile-status', EmployeeProfileStatusViewSet, basename='employee-profile-status')
router.register(r'employers/profile', EmployerProfileManageViewSet, basename='employer-profile')
router.register(r'employers/profile-status', EmployerProfileStatusViewSet, basename='employer-profile')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'rating', RatingViewSet, basename='rating')


urlpatterns = [
    path('', include(router.urls)),
]