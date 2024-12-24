from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from .models import User, Image, Annotation, Verification, AuditLog
from .forms import LoginForm, ImageUploadForm, CustomUserCreationForm
from .decorators import viewer_required, annotator_required, verifier_required, admin_required
import json
import os
from PIL import Image as PILImage, ImageDraw

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

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@admin_required
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'core/admin_dashboard.html', {'users': users})

@annotator_required
def annotator_dashboard(request):
    images = Image.objects.all()
    return render(request, 'core/annotator_dashboard.html', {'images': images})

@verifier_required
def verifier_dashboard(request):
    pending_verifications = Annotation.objects.filter(verification__isnull=True)
    return render(request, 'core/verifier_dashboard.html', {'pending_verifications': pending_verifications})

@viewer_required
def viewer_dashboard(request):
    verified_annotations = Annotation.objects.filter(verification__status='approved')
    
    for annotation in verified_annotations:
        if not annotation.file:
            print(f"Annotation {annotation.id} has no associated file.")
    
    return render(request, 'core/viewer_dashboard.html', {'verified_annotations': verified_annotations})

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

@annotator_required
def create_annotation(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    return render(request, 'core/create_annotation.html', {'image': image})

@require_POST
@annotator_required
def api_save_annotation(request, image_id):
    try:
        image = get_object_or_404(Image, id=image_id)
        data = json.loads(request.body)
        annotation_data = data.get('annotation_data')

        if not annotation_data:
            return JsonResponse({'status': 'error', 'message': 'No annotation data provided'}, status=400)

        annotation = Annotation.objects.create(
            image=image,
            annotator=request.user,
            data=annotation_data,
            file=f"pending_verifications/{image.id}_annotation.png" 
        )

        # Save annotation data to a JSON file
        annotations_dir = os.path.join(settings.MEDIA_ROOT, 'pending_verifications')
        os.makedirs(annotations_dir, exist_ok=True)
        file_name = f"{image.id}_annotation.txt"
        file_path = os.path.join(annotations_dir, file_name)

        with open(file_path, 'w') as f:
            json.dump(annotation_data, f)

        # Draw keypoints on the image
        output_image_path = os.path.join(annotations_dir, f"{image.id}_annotation.png")
        original_image_path = os.path.join(settings.MEDIA_ROOT, image.file.name)
        with PILImage.open(original_image_path) as img:
            draw = ImageDraw.Draw(img)
            for point in annotation_data:
                x, y = point['x'], point['y']
                radius = 5
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill="red")
            img.save(output_image_path)

        # AuditLog.objects.create(user=request.user, action=f"Created annotation for image {image.id}")

        return JsonResponse({'status': 'success', 'annotation_id': annotation.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@viewer_required
def view_annotations(request):
    annotations = Annotation.objects.filter(verification__status='approved')
    return render(request, 'core/view_annotations.html', {'annotations': annotations})

@annotator_required
@require_http_methods(["GET", "POST"])
def edit_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        updated_annotation_data = data.get('annotation_data')
        
        if not updated_annotation_data:
            return JsonResponse({'status': 'error', 'message': 'No annotation data provided'}, status=400)
        
        annotation.data = updated_annotation_data
        annotation.save()
        
        # Update the annotation image
        annotations_dir = os.path.join(settings.MEDIA_ROOT, 'pending_verifications')
        output_image_path = os.path.join(annotations_dir, f"{annotation.image.id}_annotation.png")
        original_image_path = os.path.join(settings.MEDIA_ROOT, annotation.image.file.name)
        
        with PILImage.open(original_image_path) as img:
            draw = ImageDraw.Draw(img)
            for point in updated_annotation_data:
                x, y = point['x'], point['y']
                radius = 5
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill="red")
            img.save(output_image_path)
        
        AuditLog.objects.create(user=request.user, action=f"Edited annotation {annotation.id}")
        
        return JsonResponse({'status': 'success', 'message': 'Annotation updated successfully'})
    
    return render(request, 'core/edit_annotation.html', {'annotation': annotation})

@verifier_required
@require_http_methods(["GET", "POST"])
def verify_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, id=annotation_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        feedback = request.POST.get('feedback', '')
        
        verification, created = Verification.objects.get_or_create(
            annotation=annotation,
            defaults={'verifier': request.user, 'status': status, 'feedback': feedback}
        )
        
        if not created:
            verification.status = status
            verification.feedback = feedback
            verification.save()
        
        if status == 'approved':
            # Move the annotation to verified_annotations
            src_path = os.path.join(settings.MEDIA_ROOT, 'pending_verifications', f"{annotation.image.id}_annotation.png")
            dst_dir = os.path.join(settings.MEDIA_ROOT, 'verified_annotations')
            os.makedirs(dst_dir, exist_ok=True)
            dst_path = os.path.join(dst_dir, f"{annotation.image.id}_annotation.png")
            os.rename(src_path, dst_path)
        
        AuditLog.objects.create(user=request.user, action=f"Verified annotation {annotation.id} as {status}")
        
        return redirect('verifier_dashboard')
    
    return render(request, 'core/verify_annotation.html', {'annotation': annotation})

@admin_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            AuditLog.objects.create(user=request.user, action=f"Created user {user.username}")
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/create_user.html', {'form': form})

