from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('annotator', 'Annotator'),
        ('verifier', 'Verifier'),
        ('viewer', 'Viewer'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=ROLES,
        default='user',
    )
    role = models.CharField(max_length=20, choices=ROLES, default='viewer')

class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images', default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Annotation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='annotations')
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotations')
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

class Batch(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_batches')
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ManyToManyField(Image, related_name='batches')
    description = models.TextField(blank=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    data = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
