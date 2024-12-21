from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from .models import Image, KeypointAnnotation
from .forms import ImageUploadForm, KeypointAnnotationForm, CommentForm

import json

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    elif hasattr(request.user, 'annotator'):
        return redirect('annotator_dashboard')
    elif hasattr(request.user, 'verifier'):
        return redirect('verifier_dashboard')
    else:
        return redirect('view_annotations')

@login_required
def annotator_dashboard(request):
    pending_images = Image.objects.filter(status='unlabeled')
    return render(request, 'core/annotator_dashboard.html', {
        'pending_images': pending_images
    })

@login_required
def create_annotation(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    
    if request.method == 'POST':
        form = KeypointAnnotationForm(request.POST)
        if form.is_valid():
            annotation = form.save(commit=False)
            annotation.image = image
            annotation.annotator = request.user
            annotation.save()
            
            image.status = 'annotated'
            image.save()
            
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    
    return render(request, 'core/create_annotations.html', {
        'image': image
    })

@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('annotator_dashboard')
    else:
        form = ImageUploadForm()
    return render(request, 'core/upload_image.html', {'form': form})

@login_required
def verifier_dashboard(request):
    pending_annotations = KeypointAnnotation.objects.filter(status='pending')
    return render(request, 'core/verifier_dashboard.html', {
        'pending_annotations': pending_annotations
    })

@login_required
def view_annotations(request):
    verified_annotations = KeypointAnnotation.objects.filter(status='verified')
    return render(request, 'core/view_annotations.html', {
        'verified_annotations': verified_annotations
    })

@login_required
def verify_annotation(request, annotation_id):
    annotation = get_object_or_404(KeypointAnnotation, id=annotation_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        comments = request.POST.get('comments')
        
        annotation.status = status
        annotation.comments = comments
        annotation.save()
        
        if status == 'verified':
            annotation.image.status = 'verified'
            annotation.image.save()
        
        return redirect('verifier_dashboard')
    
    return render(request, 'core/verify_annotation.html', {'annotation': annotation})

@login_required
def add_comment(request, annotation_id):
    annotation = get_object_or_404(KeypointAnnotation, id=annotation_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.annotation = annotation
            comment.author = request.user
            comment.save()
            return redirect('verify_annotation', annotation_id=annotation_id)
    else:
        form = CommentForm()
    return render(request, 'core/add_comment.html', {'form': form, 'annotation': annotation})



def logout_view(request):
    logout(request)
    return redirect('login')

