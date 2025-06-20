from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TradingConfiguration(models.Model):
    license = models.OneToOneField(
        'licenses.License',  # ✅ String reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='configuration'
    )
    
    # ═══ Symbol Validation ═══
    allowed_symbol = models.CharField(
        max_length=20,
        default="EURUSD",
        help_text="Allowed trading symbol"
    )
    strict_symbol_check = models.BooleanField(
        default=True,
        help_text="Enable strict symbol validation"
    )
    
    # ═══ Session Configuration ═══
    inp_session_start = models.TimeField(
        default="08:45",
        help_text="Trading session start time (HH:MM)"
    )
    inp_session_end = models.TimeField(
        default="10:00",
        help_text="Trading session end time (HH:MM)"
    )
    
    # ═══ Enhanced Fibonacci Levels ═══
    inp_fib_level_1_1 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.10000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_1_05 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_1_0 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.00000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_primary_buy_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.95000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_primary_sell_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_hedge_buy = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.90000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_hedge_sell = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.10000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_hedge_buy_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.85000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_hedge_sell_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.15000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_0_0 = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.00000,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)]
    )
    inp_fib_level_neg_05 = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.05000,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)]
    )
    inp_fib_level_neg_1 = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.10000,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)]
    )
    inp_fib_level_hedge_buy_tp = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.20000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    inp_fib_level_hedge_sell_tp = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.80000,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    
    # ═══ Timeout Configuration (Minutes) ═══
    inp_primary_pending_timeout = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Primary pending order timeout in minutes"
    )
    inp_primary_position_timeout = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Primary position timeout in minutes"
    )
    inp_hedging_pending_timeout = models.PositiveIntegerField(
        default=45,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Hedging pending order timeout in minutes"
    )
    inp_hedging_position_timeout = models.PositiveIntegerField(
        default=90,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text="Hedging position timeout in minutes"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trading Configuration'
        verbose_name_plural = 'Trading Configurations'
    
    def __str__(self):
        return f"Config for {self.license.client.full_name} ({self.license.license_key[:8]}...)"
