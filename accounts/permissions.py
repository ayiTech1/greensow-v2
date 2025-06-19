from rest_framework.permissions import BasePermission

class IsManagerOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_manager

class IsEmployerOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_employer

class IsEmployeeOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_employee

class CanViewEmployeeProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_manager or request.user.is_employer)

class CanViewEmployerProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_manager or request.user.is_employer)