from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class TradingConfiguration(models.Model):
    """
    Trading Configuration with PostgreSQL-compatible field names
    All field names are now lowercase/snake_case for PostgreSQL compatibility
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
    allowed_symbol = models.CharField(
        max_length=20,
        default="US30",
        help_text="Allowed Symbol for trading"
    )
    strict_symbol_check = models.BooleanField(
        default=True,
        help_text="Enable Strict Symbol Validation"
    )
    
    # ═══ Session Configuration ═══
    session_start = models.CharField(
        max_length=5,
        default="08:45",
        help_text="Session Start Time (HH:MM format)"
    )
    session_end = models.CharField(
        max_length=5,
        default="10:00",
        help_text="Session End Time (HH:MM format)"
    )
    
    # ═══ Enhanced Fibonacci Levels ═══
    fib_level_1_1 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.325,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 1.1"
    )
    fib_level_1_05 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 1.05 (Buy Entry)"
    )
    fib_level_1_0 = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 1.0 (Session High)"
    )
    fib_level_primary_buy_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Primary Buy Stop Loss Level"
    )
    fib_level_primary_sell_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Primary Sell Stop Loss Level"
    )
    fib_level_hedge_buy = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Buy Entry Level"
    )
    fib_level_hedge_sell = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Sell Entry Level"
    )
    fib_level_hedge_buy_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Buy Stop Loss Level"
    )
    fib_level_hedge_sell_sl = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Sell Stop Loss Level"
    )
    fib_level_0_0 = models.DecimalField(
        max_digits=8, decimal_places=5, default=0.0,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level 0.0 (Session Low)"
    )
    fib_level_neg_05 = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.05,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level -0.05 (Sell Entry)"
    )
    fib_level_neg_1 = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.325,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Fibonacci Level -0.325 (Sell TP)"
    )
    fib_level_hedge_buy_tp = models.DecimalField(
        max_digits=8, decimal_places=5, default=1.3,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Buy Take Profit Level"
    )
    fib_level_hedge_sell_tp = models.DecimalField(
        max_digits=8, decimal_places=5, default=-0.3,
        validators=[MinValueValidator(-5.0), MaxValueValidator(5.0)],
        help_text="Hedging Sell Take Profit Level"
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
    
    def clean(self):
        """Validate session times"""
        super().clean()
        if not self._is_valid_time_format(self.session_start):
            raise ValidationError({'session_start': 'Please enter time in HH:MM format'})
        if not self._is_valid_time_format(self.session_end):
            raise ValidationError({'session_end': 'Please enter time in HH:MM format'})
    
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
    
    # Compatibility properties for backward compatibility with API
    @property
    def inp_AllowedSymbol(self):
        return self.allowed_symbol
    
    @property
    def inp_StrictSymbolCheck(self):
        return self.strict_symbol_check
    
    @property
    def inp_SessionStart(self):
        return self.session_start
    
    @property
    def inp_SessionEnd(self):
        return self.session_end
    
    @property
    def inp_FibLevel_1_1(self):
        return self.fib_level_1_1
    
    @property
    def inp_FibLevel_1_05(self):
        return self.fib_level_1_05
    
    @property
    def inp_FibLevel_1_0(self):
        return self.fib_level_1_0
    
    @property
    def inp_FibLevel_PrimaryBuySL(self):
        return self.fib_level_primary_buy_sl
    
    @property
    def inp_FibLevel_PrimarySellSL(self):
        return self.fib_level_primary_sell_sl
    
    @property
    def inp_FibLevel_HedgeBuy(self):
        return self.fib_level_hedge_buy
    
    @property
    def inp_FibLevel_HedgeSell(self):
        return self.fib_level_hedge_sell
    
    @property
    def inp_FibLevel_HedgeBuySL(self):
        return self.fib_level_hedge_buy_sl
    
    @property
    def inp_FibLevel_HedgeSellSL(self):
        return self.fib_level_hedge_sell_sl
    
    @property
    def inp_FibLevel_0_0(self):
        return self.fib_level_0_0
    
    @property
    def inp_FibLevel_Neg_05(self):
        return self.fib_level_neg_05
    
    @property
    def inp_FibLevel_Neg_1(self):
        return self.fib_level_neg_1
    
    @property
    def inp_FibLevel_HedgeBuyTP(self):
        return self.fib_level_hedge_buy_tp
    
    @property
    def inp_FibLevel_HedgeSellTP(self):
        return self.fib_level_hedge_sell_tp
    
    @property
    def inp_PrimaryPendingTimeout(self):
        return self.primary_pending_timeout
    
    @property
    def inp_PrimaryPositionTimeout(self):
        return self.primary_position_timeout
    
    @property
    def inp_HedgingPendingTimeout(self):
        return self.hedging_pending_timeout
    
    @property
    def inp_HedgingPositionTimeout(self):
        return self.hedging_position_timeout