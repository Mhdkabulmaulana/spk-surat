from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):

            # Superuser selalu diizinkan
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Cek apakah user mempunyai salah satu group
            if request.user.groups.filter(
                name__in=group_names
            ).exists():
                return view_func(request, *args, **kwargs)

            # Tidak punya hak akses
            raise PermissionDenied

        return wrapper

    return decorator