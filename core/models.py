from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('annotator', 'Annotator'),
        ('verifier', 'Verifier'),
        ('viewer', 'Viewer'),
    )
    user_type = models.CharField(max_length=20, choices=ROLES, default='viewer')
    role = models.CharField(max_length=20, choices=ROLES)
    def save(self, *args, **kwargs):
        if not self.role:  # If role is not set, set it to user_type
            self.role = self.user_type
        super().save(*args, **kwargs)

class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Annotation(models.Model):
    file = models.ImageField(upload_to='pending_verifications/')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='annotations')
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotations')
    data = models.JSONField()  # This will store the keypoint data
    version = models.PositiveIntegerField(default=1)  # Tracks annotation version
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verifier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_verifications')
    feedback = models.TextField(blank=True)

class Verification(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    annotation = models.OneToOneField(Annotation, on_delete=models.CASCADE, related_name='verification')
    verifier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    verified_at = models.DateTimeField(auto_now=True)
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
