from django import forms
from .models import Image, KeypointAnnotation, Comment

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file']

class KeypointAnnotationForm(forms.ModelForm):
    class Meta:
        model = KeypointAnnotation
        fields = ['points', 'confidence', 'bbox', 'annotation_notes']
        widgets = {
            'points': forms.HiddenInput(),
            'confidence': forms.HiddenInput(),
            'bbox': forms.HiddenInput(),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

