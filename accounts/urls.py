from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views.auth import AuthViewSet
from accounts.views.employers import EmployerProfileViewSet, EmployerRatingViewSet
from accounts.views.employees import EmployeeProfileViewSet, EmployeeRatingViewSet 
from accounts.views.notifications import NotificationViewSet
from accounts.views.managers import EmployeeManagerDashboardViewSet, EmployerManagerDashboardViewSet
from django.urls import re_path
from accounts.stores.consumers import ProfileConsumer

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'employer-profile', EmployerProfileViewSet, basename='employer-profile')
router.register(r'employer-ratings', EmployerRatingViewSet, basename='employer-rating')
router.register(r'employee-profile', EmployeeProfileViewSet, basename='employee-profile')
router.register(r'employee-ratings', EmployeeRatingViewSet, basename='employee-rating')
router.register(r'notification', NotificationViewSet, basename='notification')
router.register(r'employers-manager-dashboard', EmployerManagerDashboardViewSet, basename='employer-manager-dashboard')
router.register(r'employees-manager-dashboard', EmployeeManagerDashboardViewSet, basename='employee-manager-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]

websocket_urlpatterns = [
    re_path(r'ws/profiles/$', ProfileConsumer.as_asgi()),
]
