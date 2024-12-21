from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    USER_TYPES = (
        ('viewer', 'Viewer'),
        ('annotator', 'Annotator'),
        ('verifier', 'Verifier'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=500)

# class Image(models.Model):
#     dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
#     file_path = models.CharField(max_length=500)
#     machine_label = models.TextField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=[
#         ('unlabeled', 'Unlabeled'),
#         ('machine_labeled', 'Machine Labeled'),
#         ('annotated', 'Annotated'),
#         ('verified', 'Verified')
#     ])

# class Annotation(models.Model):
#     image = models.ForeignKey(Image, on_delete=models.CASCADE)
#     annotator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='annotations')
#     verifier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verifications', null=True)
#     annotation_data = models.TextField()
#     annotator_comment = models.TextField(null=True, blank=True)
#     verifier_comment = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     status = models.CharField(max_length=20, choices=[
#         ('pending', 'Pending Verification'),
#         ('verified', 'Verified'),
#         ('rejected', 'Rejected')
#     ])
#     annotated_image = models.ImageField(upload_to='annotated_images/', null=True, blank=True)
#     verified_image = models.ImageField(upload_to='verified_images/', null=True, blank=True)


class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('unlabeled', 'Unlabeled'),
        ('machine_labeled', 'Machine Labeled'),
        ('annotated', 'Annotated'),
        ('verified', 'Verified')
    ], default='unlabeled')

    def __str__(self):
        return f"Image {self.id}"

class KeypointAnnotation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotations')
    points = models.JSONField()  # Stores keypoint coordinates
    confidence = models.JSONField()  # Stores confidence values
    bbox = models.JSONField()  # Stores bounding box coordinates
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], default='pending')
    annotation_notes = models.TextField(blank=True, null=True)  # Renamed from 'comments'
    
    def __str__(self):
        return f"Annotation for Image {self.image.id}"

class Comment(models.Model):
    annotation = models.ForeignKey(KeypointAnnotation, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Annotation {self.annotation.id}"

