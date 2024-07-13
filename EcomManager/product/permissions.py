# product/permissions.py
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow admin users to perform any action.
    """
    def has_permission(self, request, view):
        # Allow read-only access for non-admin users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow admin users to perform any action
        return request.user.role == 'admin'

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow staff users to approve or reject products.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for non-staff users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow staff users to approve or reject products
        return request.user.role == 'staff'

class IsAgentOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow agents to manage product history.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for non-agents
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow agents to manage product history if rejected by staff or admin
        return (request.user.role == 'agent' and obj.status in ['rejected', 'approved'])
