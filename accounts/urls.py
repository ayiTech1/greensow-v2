from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views.auth import AuthViewSet
from accounts.views.profile import EmployerProfileViewSet,  EmployeeProfileViewSet
from accounts.views.notifications import NotificationViewSet
from accounts.views.managers import EmployeeManagerDashboardViewSet, EmployerManagerDashboardViewSet
from accounts.views.rating import RatingViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'employer-profile', EmployerProfileViewSet, basename='employer-profile')
router.register(r'employee-profile', EmployeeProfileViewSet, basename='employee-profile')
router.register(r'ratings', RatingViewSet, basename='employer-rating')
router.register(r'notification', NotificationViewSet, basename='notification')
router.register(r'employers-manager-dashboard', EmployerManagerDashboardViewSet, basename='employer-manager-dashboard')
router.register(r'employees-manager-dashboard', EmployeeManagerDashboardViewSet, basename='employee-manager-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
