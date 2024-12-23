from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Image, Annotation, Verification, Batch

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)

class LoginForm(AuthenticationForm):
    pass

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file']

class AnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ['data']
        widgets = {
            'data': forms.Textarea(attrs={'rows': 4}),
        }

class VerificationForm(forms.ModelForm):
    class Meta:
        model = Verification
        fields = ['status', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name', 'description']

