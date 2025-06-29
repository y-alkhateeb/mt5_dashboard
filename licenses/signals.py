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
        # Get or create a default configuration (shared among licenses)
        default_config, config_created = TradingConfiguration.objects.get_or_create(
            name='Default Configuration',
            defaults={
                'description': 'Default trading configuration for new licenses',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '08:45',
                'inp_SessionEnd': '10:00',
                'is_active': True,
            }
        )
        
        # Assign the shared configuration to the license
        instance.trading_configuration = default_config
        instance.save(update_fields=['trading_configuration'])
        
        if config_created:
            logger.info("Created default shared trading configuration")
        logger.info(f"Assigned default configuration to license {instance.license_key[:8]}...")