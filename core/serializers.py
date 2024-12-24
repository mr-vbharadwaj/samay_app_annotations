from rest_framework import serializers
from .models import User, Image, Annotation, Verification, Batch

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'file', 'uploaded_by', 'uploaded_at']

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ['id', 'file', 'image', 'annotator', 'data', 'created_at', 'updated_at', 'verifier']

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ['id', 'annotation', 'verifier', 'status', 'feedback', 'verified_at']

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'name', 'created_by', 'created_at', 'images', 'description']

