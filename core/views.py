from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import User, Image
from .forms import LoginForm, ImageUploadForm
import json
import os

# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard view
@login_required
def dashboard(request):
    images = Image.objects.all()
    return render(request, 'core/dashboard.html', {'images': images})

# Upload image view
@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.uploaded_by = request.user
            image.save()
            return redirect('dashboard')
    else:
        form = ImageUploadForm()
    return render(request, 'core/upload_image.html', {'form': form})

# Keypoint annotation page view
@login_required
def create_annotation(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    return render(request, 'core/create_annotation.html', {'image': image})

# API to save annotation data
@require_POST
@login_required
def api_save_annotation(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    data = json.loads(request.body)
    annotation_data = data.get('annotation_data')

    # Save annotation to a text file
    annotations_dir = os.path.join(settings.MEDIA_ROOT, 'annotations')
    os.makedirs(annotations_dir, exist_ok=True)
    file_name = f"{image.file.name.split('/')[-1].split('.')[0]}.json"  # Save as .json
    file_path = os.path.join(annotations_dir, file_name)

    # Write the annotation data to a JSON file
    with open(file_path, 'w') as f:
        json.dump(annotation_data, f)

    return JsonResponse({'status': 'success'})

# View annotations page
@login_required
def view_annotations(request):
    annotations_dir = os.path.join(settings.MEDIA_ROOT, 'annotations')
    annotations = []
    for file_name in os.listdir(annotations_dir):
        if file_name.endswith('.json'):  # Updated to check for .json files
            image_name = file_name.split('.')[0] + '.jpg'  # Assuming images are JPGs
            annotations.append({
                'image_name': image_name,
                'annotation_file': file_name,
            })
    return render(request, 'core/view_annotations.html', {'annotations': annotations})
