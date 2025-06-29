from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
import json

def generate_license_key():
    """Generate a unique license key"""
    return str(uuid.uuid4()).replace('-', '')

def default_account_hash_history():
    """Return empty list for account hash history"""
    return []

class Client(models.Model):
    """Client information for license management"""
    first_name = models.CharField(max_length=50, help_text="Client's first name")
    last_name = models.CharField(max_length=50, help_text="Client's last name")
    country = models.CharField(max_length=100, help_text="Client's country")
    email = models.EmailField(blank=True, null=True, help_text="Client's email address (optional)")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Client's phone number (optional)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_clients')
    
    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ['first_name', 'last_name', 'country']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['country']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.country})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class License(models.Model):
    """Trading license with system hash as primary identifier"""
    ACCOUNT_TRADE_MODES = [
        (0, 'Demo Account'),
        (1, 'Restricted Account'),
        (2, 'Live Account'),
    ]
    
    # License Information
    license_key = models.CharField(
        max_length=64, 
        unique=True, 
        default=generate_license_key,
        help_text="Unique license key for the trading robot"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='licenses',
        help_text="Client who owns this license"
    )
    
    # Trading Configuration Assignment (ForeignKey allows sharing)
    trading_configuration = models.ForeignKey(
        'configurations.TradingConfiguration',
        on_delete=models.PROTECT,  # Prevent deletion of configs in use
        related_name='licenses',
        help_text="Trading configuration for this license",
        null=True,  # Temporary null for migration
        blank=True
    )
    
    # PRIMARY IDENTIFIER: System Hash (Trading Account Identifier)
    system_hash = models.CharField(
        max_length=128,
        blank=True, null=True,
        unique=True,  # This is the main unique identifier
        help_text="Primary trading account identifier (set on first use)"
    )
    
    # SECONDARY: Account Login Hash (For tracking login changes)
    account_hash = models.CharField(
        max_length=128,
        blank=True, null=True,
        help_text="Hashed account login ID (for tracking account login changes)"
    )
    
    # Account Hash History (JSON field to store previous account hashes)
    account_hash_history = models.JSONField(
        default=default_account_hash_history, 
        blank=True,
        help_text="History of account hash changes with timestamps"
    )
    
    # Other Information
    broker_server = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Broker server address (set on first use)"
    )
    
    # License Settings
    account_trade_mode = models.IntegerField(
        choices=ACCOUNT_TRADE_MODES,
        default=0,
        help_text="Trading mode: Demo, Restricted, or Live"
    )
    expires_at = models.DateTimeField(
        help_text="License expiration date and time"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the license is currently active"
    )
    
    # Usage tracking
    first_used_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the license was first used by trading bot"
    )
    last_used_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the license was last used by trading bot"
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this license has been used"
    )
    
    # Enhanced Usage Analytics
    daily_usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of uses today (resets daily)"
    )
    last_reset_date = models.DateField(
        auto_now_add=True,
        help_text="Last date when daily usage was reset"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_licenses'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['license_key']),
            models.Index(fields=['system_hash']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['account_trade_mode']),
            models.Index(fields=['last_used_at']),
        ]
    
    def __str__(self):
        config_name = self.trading_configuration.name if self.trading_configuration else "No Config"
        if self.system_hash:
            account_info = f"Account: {self.system_hash[:8]}..."
            login_info = f" | Login: {self.account_hash[:8]}..." if self.account_hash else " | No Login"
            return f"License {self.license_key[:8]}... - {self.client.full_name} ({config_name}) ({account_info}{login_info})"
        else:
            return f"License {self.license_key[:8]}... - {self.client.full_name} ({config_name}) (Not Bound)"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_expiring_soon(self):
        """Check if license expires within 30 days"""
        return timezone.now() + timedelta(days=30) > self.expires_at
    
    @property
    def status(self):
        """Enhanced status with more granular states"""
        if not self.is_active:
            return "Inactive"
        elif self.is_expired:
            return "Expired"
        elif not self.system_hash:
            return "Not Bound"
        elif not self.account_hash:
            return "Bound - No Login"
        elif self.is_expiring_soon:
            return "Expiring Soon"
        else:
            return "Active"
    
    @property
    def is_valid(self):
        """Check if license is valid for trading"""
        return self.is_active and not self.is_expired and self.trading_configuration is not None
    
    @property
    def is_account_bound(self):
        """Check if license is bound to a trading account (system_hash)"""
        return bool(self.system_hash)
    
    @property
    def has_login_info(self):
        """Check if license has account login information"""
        return bool(self.account_hash)
    
    @property
    def account_hash_changes_count(self):
        """Get number of times account hash was changed"""
        return len(self.account_hash_history)
    
    def reset_daily_usage_if_needed(self):
        """Reset daily usage count if it's a new day"""
        today = timezone.now().date()
        if self.last_reset_date < today:
            self.daily_usage_count = 0
            self.last_reset_date = today
            self.save(update_fields=['daily_usage_count', 'last_reset_date'])
    
    def bind_account(self, system_hash, account_trade_mode, broker_server=None, account_hash=None):
        """Bind license to a trading account on first use"""
        now = timezone.now()
        
        # Reset daily usage if needed
        self.reset_daily_usage_if_needed()
        
        if not self.first_used_at:
            self.first_used_at = now
            self.system_hash = system_hash
            self.account_trade_mode = account_trade_mode
            if broker_server:
                self.broker_server = broker_server
            if account_hash:
                self.account_hash = account_hash
                # Add to history
                self.account_hash_history.append({
                    'account_hash': account_hash,
                    'timestamp': now.isoformat(),
                    'action': 'initial_set'
                })
        else:
            # Update account hash if it changed
            if account_hash and account_hash != self.account_hash:
                # Save old hash to history
                if self.account_hash:
                    self.account_hash_history.append({
                        'account_hash': self.account_hash,
                        'timestamp': now.isoformat(),
                        'action': 'replaced'
                    })
                
                # Set new hash
                self.account_hash = account_hash
                self.account_hash_history.append({
                    'account_hash': account_hash,
                    'timestamp': now.isoformat(),
                    'action': 'updated'
                })
        
        self.last_used_at = now
        self.usage_count += 1
        self.daily_usage_count += 1
        self.save()
    
    def validate_system_hash(self, system_hash):
        """Validate if the system hash matches the bound account"""
        if not self.system_hash:
            return True, "First time use - will bind account"
        elif self.system_hash == system_hash:
            return True, "Account authorized"
        else:
            return False, "Account not authorized - license bound to different trading account"
    
    def get_account_hash_history(self):
        """Get formatted account hash history"""
        history = []
        for entry in self.account_hash_history:
            history.append({
                'account_hash': entry['account_hash'][:8] + '...' if entry['account_hash'] else None,
                'timestamp': entry['timestamp'],
                'action': entry['action']
            })
        return history
    
    def save(self, *args, **kwargs):
        # Set default expiration if not provided
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)