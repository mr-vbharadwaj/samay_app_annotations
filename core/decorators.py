from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('dashboard')
        return wrapper
    return decorator

admin_required = role_required(['admin'])
annotator_required = role_required(['annotator'])
verifier_required = role_required(['verifier'])
viewer_required = role_required(['viewer'])

