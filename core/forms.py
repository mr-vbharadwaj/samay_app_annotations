from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Image

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file'})
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('user_type',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].widget = forms.Select(choices=User.ROLES)

