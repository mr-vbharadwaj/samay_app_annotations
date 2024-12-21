"""
URL configuration for annotations_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('view-annotations/', views.view_annotations, name='view_annotations'),
    path('annotator/', views.annotator_dashboard, name='annotator_dashboard'),
    path('annotator/create/<int:image_id>/', views.create_annotation, name='create_annotation'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('verifier/', views.verifier_dashboard, name='verifier_dashboard'),
    path('verifier/verify/<int:annotation_id>/', views.verify_annotation, name='verify_annotation'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
