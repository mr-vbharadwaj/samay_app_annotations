from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse

def login_required(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return function(request, *args, **kwargs)
    return wrapper

def role_required(role):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login'))
            if request.user.user_type != role:
                return redirect(reverse('dashboard'))
            return function(request, *args, **kwargs)
        return wrapper
    return decorator

viewer_required = role_required('viewer')
annotator_required = role_required('annotator')
verifier_required = role_required('verifier')
admin_required = role_required('admin')

