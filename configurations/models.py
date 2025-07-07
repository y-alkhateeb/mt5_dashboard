from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TradingConfiguration(models.Model):
    """
    Simplified Trading Configuration - Removed Fibonacci and Session Configuration
    """
    
    # Configuration Identity
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Configuration name (e.g., 'Standard Config', 'Aggressive Setup')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this trading configuration"
    )
    
    # ═══ Symbol Validation ═══
    allowed_symbol = models.CharField(
        max_length=20,
        default="US30",
        help_text="Allowed Symbol for trading"
    )
    strict_symbol_check = models.BooleanField(
        default=True,
        help_text="Enable Strict Symbol Validation"
    )
    
    # ═══ Timeout Configuration (Minutes) ═══
    primary_pending_timeout = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Primary Order Pending Timeout (minutes)"
    )
    primary_position_timeout = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Primary Position Timeout (minutes)"
    )
    hedging_pending_timeout = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Hedging Order Pending Timeout (minutes)"
    )
    hedging_position_timeout = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Hedging Position Timeout (minutes)"
    )
    
    # Configuration Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this configuration is active and can be assigned to licenses"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trading Configuration'
        verbose_name_plural = 'Trading Configurations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.allowed_symbol})"
    
    @property
    def license_count(self):
        """Get number of licenses using this configuration"""
        return self.licenses.count()
    
    # Compatibility properties for API (minimal required fields only)
    @property
    def inp_AllowedSymbol(self):
        return self.allowed_symbol
    
    @property
    def inp_StrictSymbolCheck(self):
        return self.strict_symbol_check