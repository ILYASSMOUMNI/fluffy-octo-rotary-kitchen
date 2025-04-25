from django.shortcuts import redirect
from django.conf import settings

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.email != settings.ADMIN_EMAIL:
            return redirect('login')  # or your custom unauthorized page
        return view_func(request, *args, **kwargs)
    return _wrapped_view
