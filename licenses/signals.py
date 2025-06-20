from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import License

@receiver(post_save, sender=License)
def create_license_configuration(sender, instance, created, **kwargs):
    """Automatically create a default configuration when a license is created"""
    if created:
        from configurations.models import TradingConfiguration
        config, config_created = TradingConfiguration.objects.get_or_create(license=instance)
        if config_created:
            print(f"✅ Auto-created configuration for license {instance.license_key[:8]}...")