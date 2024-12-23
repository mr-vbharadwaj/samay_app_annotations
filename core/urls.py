from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('create-annotation/<int:image_id>/', views.create_annotation, name='create_annotation'),
    path('api/save-annotation/<int:image_id>/', views.api_save_annotation, name='api_save_annotation'),
    path('view-annotations/', views.view_annotations, name='view_annotations'),
]

