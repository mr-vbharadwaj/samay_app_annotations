from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_image, name='upload_image'),
    path('create_annotation/<int:image_id>/', views.create_annotation, name='create_annotation'),
    path('api/save_annotation/<int:image_id>/', views.api_save_annotation, name='api_save_annotation'),
    path('view_annotations/', views.view_annotations, name='view_annotations'),
    path('edit_annotation/<int:annotation_id>/', views.edit_annotation, name='edit_annotation'),
    path('verify_annotation/<int:annotation_id>/', views.verify_annotation, name='verify_annotation'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('annotator_dashboard/', views.annotator_dashboard, name='annotator_dashboard'),
    path('verifier_dashboard/', views.verifier_dashboard, name='verifier_dashboard'),
    path('viewer_dashboard/', views.viewer_dashboard, name='viewer_dashboard'),
    path('create_user/', views.create_user, name='create_user'),
]

