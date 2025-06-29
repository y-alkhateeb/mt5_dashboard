from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import License
from configurations.models import TradingConfiguration
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=License)
def ensure_license_has_configuration(sender, instance, created, **kwargs):
    """Ensure license has a trading configuration assigned"""
    if created and not instance.trading_configuration:
        # Get or create a default configuration
        default_config, config_created = TradingConfiguration.objects.get_or_create(
            name='Default Configuration',
            defaults={
                'description': 'Default trading configuration auto-created',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
            }
        )
        
        instance.trading_configuration = default_config
        instance.save(update_fields=['trading_configuration'])
        
        if config_created:
            logger.info(f"Created default configuration")
        logger.info(f"Assigned default configuration to license {instance.license_key[:8]}...")
