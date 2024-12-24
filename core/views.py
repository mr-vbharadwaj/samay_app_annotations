# views.py

import cv2
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
from .keypoint_prediction import load_model, predict_keypoints, correct_keypoints
import logging

logger = logging.getLogger(__name__)

# Load the model once when the server starts
try:
    model = load_model(settings.MODEL_WEIGHTS_PATH)
    logger.info(f"Model loaded successfully from {settings.MODEL_WEIGHTS_PATH}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

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
    image_path = os.path.join(settings.MEDIA_ROOT, image.file.name)
    
    # Initialize default response data
    context = {
        'image': image,
        'keypoints': [],
        'bbox': [],
        'bbox_n': [],
        'error_message': None,
        'image_dimensions': None
    }
    
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        if model is None:
            raise RuntimeError("Model not loaded. Please check model configuration.")
        
        # Read image for dimensions
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Failed to read image file")
            
        context['image_dimensions'] = {
            'width': img.shape[1],
            'height': img.shape[0]
        }
        
        # Get predictions
        keypoints, bbox, bbox_n = predict_keypoints(model, image_path)
        if keypoints and len(keypoints) > 0:
            corrected_keypoints = correct_keypoints(keypoints[0], img)
            context.update({
                'keypoints': corrected_keypoints,
                'bbox': bbox,
                'bbox_n': bbox_n
            })
        else:
            context['error_message'] = "No keypoints detected in the image"
            
    except Exception as e:
        logger.error(f"Annotation creation failed: {e}")
        context['error_message'] = f"Failed to process image: {str(e)}"
    
    return render(request, 'core/create_annotation.html', context)

@require_POST
@annotator_required
def api_save_annotation(request, image_id):
    try:
        image = get_object_or_404(Image, id=image_id)
        data = json.loads(request.body)
        annotation_data = data.get('annotation_data')

        if not annotation_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No annotation data provided'
            }, status=400)

        # Validate annotation data structure
        if not isinstance(annotation_data, list):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid annotation data format'
            }, status=400)

        # Create annotation object
        annotation = Annotation.objects.create(
            image=image,
            annotator=request.user,
            data=annotation_data,
            file=f"pending_verifications/{image.id}_annotation.png"
        )

        # Ensure directories exist
        annotations_dir = os.path.join(settings.MEDIA_ROOT, 'pending_verifications')
        os.makedirs(annotations_dir, exist_ok=True)

        # Save annotation data as JSON
        json_path = os.path.join(annotations_dir, f"{image.id}_annotation.json")
        with open(json_path, 'w') as f:
            json.dump(annotation_data, f)

        # Create visualization
        try:
            output_image_path = os.path.join(annotations_dir, f"{image.id}_annotation.png")
            original_image_path = os.path.join(settings.MEDIA_ROOT, image.file.name)
            
            with PILImage.open(original_image_path) as img:
                draw = ImageDraw.Draw(img)
                
                # Draw skeleton lines first
                skeletonConnections = [
                    [0, 1], [0, 2], [1, 3], [2, 4], [5, 7], [7, 9],
                    [6, 8], [8, 10], [11, 13], [13, 15], [12, 14], [14, 16],
                    [17, 18], [18, 21], [19, 21], [19, 20], [20, 11], [20, 12],
                    [15, 24], [16, 25], [9, 22], [10, 23]
                ]
                
                for [start_idx, end_idx] in skeletonConnections:
                    if start_idx < len(annotation_data) and end_idx < len(annotation_data):
                        start_point = annotation_data[start_idx]
                        end_point = annotation_data[end_idx]
                        draw.line(
                            [
                                (start_point['x'], start_point['y']),
                                (end_point['x'], end_point['y'])
                            ],
                            fill='blue',
                            width=2
                        )
                
                # Draw keypoints
                for idx, point in enumerate(annotation_data):
                    x, y = point['x'], point['y']
                    radius = 5
                    draw.ellipse(
                        (x - radius, y - radius, x + radius, y + radius),
                        fill='red'
                    )
                    # Add keypoint number
                    draw.text(
                        (x + radius + 2, y - radius - 2),
                        str(idx + 1),
                        fill='black'
                    )
                
                img.save(output_image_path)
        
        except Exception as e:
            logger.error(f"Failed to create visualization: {e}")
            # Continue without visualization
            pass

        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action=f"Created annotation {annotation.id} for image {image.id}"
        )

        return JsonResponse({
            'status': 'success',
            'annotation_id': annotation.id
        })

    except Exception as e:
        logger.error(f"Failed to save annotation: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

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