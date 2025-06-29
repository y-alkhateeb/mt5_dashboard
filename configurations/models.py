from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class TradingConfiguration(models.Model):
    """
    Independent Trading Configuration that can be shared across multiple licenses
    """
    
    # Configuration Identity
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Configuration name (e.g., 'US30 Standard', 'EURUSD Aggressive')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this trading configuration"
    )
    
    # ═══ Symbol Validation ═══
    inp_AllowedSymbol = models.CharField(
        max_length=20,
        default="US30",
        help_text="Allowed Symbol for trading"
    )
    inp_StrictSymbolCheck = models.BooleanField(
        default=True,
        help_text="Enable Strict Symbol Validation"
    )
    
    # ═══ Session Configuration ═══
    inp_SessionStart = models.CharField(
        max_length=5,
        default="08:45",
        help_text="Session Start Time (HH:MM format)"
    )
    inp_SessionEnd = models.CharField(
        max_length=5,
        default="10:00",
        help_text="Session End Time (HH:MM format)"
    )
    
    # ═══ Enhanced Fibonacci Levels ═══
    inp_FibLevel_1_1 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.325,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 1.1"
    )
    inp_FibLevel_1_05 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 1.05 (Buy Entry)"
    )
    inp_FibLevel_1_0 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 1.0 (Session High)"
    )
    inp_FibLevel_PrimaryBuySL = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Primary Buy Stop Loss Level"
    )
    inp_FibLevel_PrimarySellSL = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Primary Sell Stop Loss Level"
    )
    inp_FibLevel_HedgeBuy = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Buy Entry Level"
    )
    inp_FibLevel_HedgeSell = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Sell Entry Level"
    )
    inp_FibLevel_HedgeBuySL = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Buy Stop Loss Level"
    )
    inp_FibLevel_HedgeSellSL = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Sell Stop Loss Level"
    )
    inp_FibLevel_0_0 = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 0.0 (Session Low)"
    )
    inp_FibLevel_Neg_05 = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level -0.05 (Sell Entry)"
    )
    inp_FibLevel_Neg_1 = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.325,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level -0.325 (Sell TP)"
    )
    inp_FibLevel_HedgeBuyTP = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.3,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Buy Take Profit Level"
    )
    inp_FibLevel_HedgeSellTP = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.3,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Sell Take Profit Level"
    )
    
    # ═══ Timeout Configuration (Minutes) ═══
    inp_PrimaryPendingTimeout = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Primary Order Pending Timeout (minutes)"
    )
    inp_PrimaryPositionTimeout = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Primary Position Timeout (minutes)"
    )
    inp_HedgingPendingTimeout = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Hedging Order Pending Timeout (minutes)"
    )
    inp_HedgingPositionTimeout = models.PositiveIntegerField(
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
        return f"{self.name} ({self.inp_AllowedSymbol})"
    
    @property
    def license_count(self):
        """Get number of licenses using this configuration"""
        return self.licenses.count()
    
    def clean(self):
        """Validate session times"""
        super().clean()
        if not self._is_valid_time_format(self.inp_SessionStart):
            raise ValidationError({'inp_SessionStart': 'Please enter time in HH:MM format'})
        if not self._is_valid_time_format(self.inp_SessionEnd):
            raise ValidationError({'inp_SessionEnd': 'Please enter time in HH:MM format'})
    
    def _is_valid_time_format(self, time_str):
        """Check if time string is in HH:MM format"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False
