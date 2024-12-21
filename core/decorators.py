from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def annotator_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.user_type == 'annotator':
            return function(request, *args, **kwargs)
        messages.error(request, 'You must be an annotator to access this page.')
        return redirect('dashboard')
    return wrap

def verifier_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.user_type == 'verifier':
            return function(request, *args, **kwargs)
        messages.error(request, 'You must be a verifier to access this page.')
        return redirect('dashboard')
    return wrap