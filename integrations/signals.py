from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Integration, AgoraIntegration
from .services import AgoraService

@receiver(post_save, sender=AgoraIntegration)
def handle_agora_integration_save(sender, instance, created, **kwargs):
    """Handle Agora integration save events"""
    # Clear the cache when an integration is updated
    AgoraService.clear_cache()
    
    # If this integration is enabled, disable other Agora integrations
    if instance.is_enabled:
        AgoraIntegration.objects.exclude(pk=instance.pk).update(
            is_enabled=False,
            status='inactive'
        )

@receiver(post_delete, sender=AgoraIntegration)
def handle_agora_integration_delete(sender, instance, **kwargs):
    """Handle Agora integration deletion"""
    # Clear the cache when an integration is deleted
    AgoraService.clear_cache() 