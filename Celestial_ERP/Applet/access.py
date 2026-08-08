from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required, permission_required


def module_permission_required(permission: str):
    def decorator(view_func):
        return login_required(permission_required(permission, raise_exception=True)(view_func))

    return decorator


def all_permissions_required(*permissions: str):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            for permission in permissions:
                if not request.user.has_perm(permission):
                    from django.core.exceptions import PermissionDenied

                    raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
