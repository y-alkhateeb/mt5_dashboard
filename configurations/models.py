# File: configurations/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TradingConfiguration(models.Model):
    license = models.OneToOneField(
        'licenses.License',
        on_delete=models.CASCADE,
        related_name='configuration'
    )
    
    # ═══ Symbol Validation ═══
    inp_AllowedSymbol = models.CharField(
        max_length=20,
        default="US30",
        help_text="Allowed Symbol (overridden by license)"
    )
    inp_StrictSymbolCheck = models.BooleanField(
        default=True,
        help_text="Enable Strict Symbol Validation (overridden by license)"
    )
    
    # ═══ Session Configuration ═══
    inp_SessionStart = models.CharField(
        max_length=5,
        default="08:45",
        help_text="Session Start Time (overridden by license)"
    )
    inp_SessionEnd = models.CharField(
        max_length=5,
        default="10:00",
        help_text="Session End Time (overridden by license)"
    )
    
    # ═══ Enhanced Fibonacci Levels ═══
    inp_FibLevel_1_1 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.325,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 1.1 (overridden by license)"
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
        help_text="Primary Order Pending Timeout (overridden by license)"
    )
    inp_PrimaryPositionTimeout = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Primary Position Timeout"
    )
    inp_HedgingPendingTimeout = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Hedging Order Pending Timeout"
    )
    inp_HedgingPositionTimeout = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Hedging Position Timeout"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trading Configuration'
        verbose_name_plural = 'Trading Configurations'
    
    def __str__(self):
        return f"Config for {self.license.client.full_name} ({self.license.license_key[:8]}...)"
