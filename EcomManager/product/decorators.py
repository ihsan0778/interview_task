from functools import wraps
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy

def admin_required(function=None, error_message="You do not have permission to access this page."):
    """
    Decorator for views that checks that the user is an admin.
    """
    def check_admin(user):
        return user.is_active and user.is_superuser

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not check_admin(request.user):
                return HttpResponseForbidden(error_message)
            return view_func(request, *args, **kwargs)
        
        return wrapped_view

    if function:
        return decorator(function)
    return decorator

def staff_or_admin_required(function=None, error_message="You do not have permission to access this page."):
    def check_staff_or_admin(user):
        return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == 'staff')

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not check_staff_or_admin(request.user):
                return HttpResponseForbidden(error_message)
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator

def admin_or_agent_permissionrequired(function=None, error_message="You do not have permission to access this page."):
    def check_staff_or_admin(user):
        return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == 'end_user')

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not check_staff_or_admin(request.user):
                return HttpResponseForbidden(error_message)
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator
