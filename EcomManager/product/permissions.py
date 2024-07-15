from rest_framework import permissions

class IsAdminPermission(permissions.BasePermission):
    """
    Custom permission to allow admin users to perform any action.
    """
    def has_permission(self, request, view):
        
        print(4546)
        if request.user.role == 'admin':
            return True
        else:
            False


class IsStaffPermission(permissions.BasePermission):
    """
    Custom permission to allow staff users to approve or reject products.
    """
    def has_permission(self, request, view, obj):
        print(4546544)
        if request.user.role == 'staff':
            return True
        else:
            False


class IsAgentPermission(permissions.BasePermission):
    """
    Custom permission to allow agents to manage product history.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'agent' and obj.status in ['rejected', 'approved']
