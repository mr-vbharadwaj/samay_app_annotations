from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Image, Annotation, Verification, Batch

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='testpass123', role='annotator')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.role, 'annotator')

class ImageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.image = Image.objects.create(file='test_image.jpg', uploaded_by=self.user)

    def test_image_creation(self):
        self.assertEqual(self.image.uploaded_by, self.user)
        self.assertTrue(self.image.uploaded_at)

class AnnotationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.image = Image.objects.create(file='test_image.jpg', uploaded_by=self.user)
        self.annotation = Annotation.objects.create(
            image=self.image,
            annotator=self.user,
            data={'keypoints': [[100, 100], [200, 200]]}
        )

    def test_annotation_creation(self):
        self.assertEqual(self.annotation.image, self.image)
        self.assertEqual(self.annotation.annotator, self.user)
        self.assertEqual(self.annotation.data, {'keypoints': [[100, 100], [200, 200]]})

class VerificationModelTest(TestCase):
    def setUp(self):
        self.annotator = User.objects.create_user(username='annotator', password='testpass123')
        self.verifier = User.objects.create_user(username='verifier', password='testpass123')
        self.image = Image.objects.create(file='test_image.jpg', uploaded_by=self.annotator)
        self.annotation = Annotation.objects.create(
            image=self.image,
            annotator=self.annotator,
            data={'keypoints': [[100, 100], [200, 200]]}
        )
        self.verification = Verification.objects.create(
            annotation=self.annotation,
            verifier=self.verifier,
            status='approved',
            feedback='Good annotation'
        )

    def test_verification_creation(self):
        self.assertEqual(self.verification.annotation, self.annotation)
        self.assertEqual(self.verification.verifier, self.verifier)
        self.assertEqual(self.verification.status, 'approved')
        self.assertEqual(self.verification.feedback, 'Good annotation')

class BatchModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.image1 = Image.objects.create(file='test_image1.jpg', uploaded_by=self.user)
        self.image2 = Image.objects.create(file='test_image2.jpg', uploaded_by=self.user)
        self.batch = Batch.objects.create(
            name='Test Batch',
            created_by=self.user,
            description='Test batch description'
        )
        self.batch.images.add(self.image1, self.image2)

    def test_batch_creation(self):
        self.assertEqual(self.batch.name, 'Test Batch')
        self.assertEqual(self.batch.created_by, self.user)
        self.assertEqual(self.batch.description, 'Test batch description')
        self.assertEqual(self.batch.images.count(), 2)
        self.assertIn(self.image1, self.batch.images.all())
        self.assertIn(self.image2, self.batch.images.all())

