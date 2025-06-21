from rest_framework import serializers
from .models import Client, License

class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'country', 'email', 'phone', 'full_name']

class LicenseSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    is_account_bound = serializers.ReadOnlyField()
    has_login_info = serializers.ReadOnlyField()
    account_hash_changes_count = serializers.ReadOnlyField()
    account_hash_history = serializers.SerializerMethodField()
    client = ClientSerializer(read_only=True)
    
    class Meta:
        model = License
        fields = [
            'id', 'license_key', 'client', 'system_hash', 'account_hash',
            'account_trade_mode', 'broker_server', 'expires_at', 'is_active',
            'status', 'is_expired', 'is_valid', 'is_account_bound', 'has_login_info',
            'account_hash_changes_count', 'account_hash_history',
            'first_used_at', 'last_used_at', 'usage_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'license_key', 'system_hash', 'account_hash', 'broker_server',
            'account_hash_history', 'first_used_at', 'last_used_at', 'usage_count', 
            'created_at', 'updated_at'
        ]
    
    def get_account_hash_history(self, obj):
        return obj.get_account_hash_history()

class BotValidationRequestSerializer(serializers.Serializer):
    """Serializer for bot validation request"""
    license_key = serializers.CharField(max_length=64, help_text="The license key provided to client")
    system_hash = serializers.CharField(max_length=128, help_text="Primary trading account identifier")
    account_trade_mode = serializers.ChoiceField(
        choices=License.ACCOUNT_TRADE_MODES,
        help_text="Account trade mode: 0=Demo, 1=Restricted, 2=Live"
    )
    broker_server = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text="Broker server address")
    timestamp = serializers.DateTimeField(help_text="Request timestamp")
    
    # Account login hash (optional - for tracking login changes)
    account_hash = serializers.CharField(max_length=128, required=False, allow_blank=True, help_text="Hashed account login ID")

class BotValidationResponseSerializer(serializers.Serializer):
    """Serializer for bot validation response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    license_key = serializers.CharField(required=False)
    client_name = serializers.CharField(required=False)
    
    # If successful
    configuration = serializers.DictField(required=False)
    expires_at = serializers.DateTimeField(required=False)
    account_trade_mode = serializers.IntegerField(required=False)
    first_time_use = serializers.BooleanField(required=False)
    account_login_changed = serializers.BooleanField(required=False)
    
    # Usage info
    usage_count = serializers.IntegerField(required=False)
    last_used_at = serializers.DateTimeField(required=False)

class BasicLicenseSerializer(serializers.ModelSerializer):
    """
    Basic license serializer for admin API - excludes sensitive information
    """
    status = serializers.ReadOnlyField()
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    
    class Meta:
        model = License
        fields = [
            'id',
            'license_key', 
            'client_name',
            'account_trade_mode',
            'expires_at',
            'is_active',
            'status',
            'created_at'
        ]
        read_only_fields = ['license_key', 'created_at']