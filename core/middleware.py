# from django.shortcuts import redirect
# from django.urls import reverse

# class RoleBasedRedirectMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated and request.path == '/':
#             if request.user.user_type == 'viewer':
#                 return redirect(reverse('view_annotations'))
#             elif request.user.user_type == 'annotator':
#                 return redirect(reverse('annotator_dashboard'))
#             elif request.user.user_type == 'verifier':
#                 return redirect(reverse('verifier_dashboard'))

#         response = self.get_response(request)
#         return response


import json
from .models import AuditLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=request.method,
                url=request.path,
                data=json.dumps(request.POST)
            )

        return response
