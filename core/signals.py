from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Annotation, AuditLog

@receiver(post_save, sender=Annotation)
def create_audit_log(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance.annotator,
            action=f"Created annotation for image {instance.image.id}",
            url=f"/annotation/{instance.id}/"
        )
    else:
        AuditLog.objects.create(
            user=instance.annotator,
            action=f"Updated annotation for image {instance.image.id}",
            url=f"/annotation/{instance.id}/"
        )

