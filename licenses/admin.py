from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import connection
from django.db.utils import ProgrammingError
from .models import Client, License

def table_exists(table_name):
    """Check if a database table exists"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, [table_name])
            return cursor.fetchone()[0]
    except:
        # Fallback for SQLite
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                return bool(cursor.fetchone())
        except:
            return False

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'country', 'email', 'phone', 'license_count_safe', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'country']
    readonly_fields = ['created_at', 'updated_at']
    
    def license_count_safe(self, obj):
        """Safe license count that handles missing tables"""
        try:
            if not table_exists('licenses_license'):
                return "Setup pending"
            
            count = obj.licenses.count()
            if count > 0:
                url = reverse('admin:licenses_license_changelist') + f'?client__id__exact={obj.id}'
                return format_html('<a href="{}">{} licenses</a>', url, count)
            return "0 licenses"
        except ProgrammingError:
            return "Setup pending"
        except Exception as e:
            return f"Error: {str(e)[:20]}..."
    
    license_count_safe.short_description = "Licenses"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = [
        'license_key_short', 'client_name_safe', 'status_badge_safe', 
        'account_trade_mode_display_safe', 'expires_at', 'usage_count', 'created_at'
    ]
    list_filter = ['account_trade_mode', 'is_active', 'created_at', 'expires_at']
    search_fields = ['license_key', 'client__first_name', 'client__last_name']
    readonly_fields = [
        'license_key', 'system_hash', 'account_hash', 'account_hash_history', 'broker_server',
        'first_used_at', 'last_used_at', 'usage_count', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('License Information', {
            'fields': ('license_key', 'client', 'trading_configuration')
        }),
        ('Trading Configuration', {
            'fields': ('account_trade_mode', 'expires_at', 'is_active')
        }),
        ('Account Binding (Auto-filled on first use)', {
            'fields': ('system_hash', 'broker_server'),
            'description': 'System hash is the primary account identifier'
        }),
        ('Account Login Tracking (Auto-filled and tracked)', {
            'fields': ('account_hash', 'account_hash_history'),
            'classes': ('collapse',),
            'description': 'Account hash tracks login changes with history'
        }),
        ('Usage Statistics', {
            'fields': ('first_used_at', 'last_used_at', 'usage_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def license_key_short(self, obj):
        return f"{obj.license_key[:12]}..."
    license_key_short.short_description = "License Key"
    
    def client_name_safe(self, obj):
        try:
            return obj.client.full_name if obj.client else "No Client"
        except:
            return "Client Error"
    client_name_safe.short_description = "Client"
    
    def account_trade_mode_display_safe(self, obj):
        try:
            return obj.get_account_trade_mode_display()
        except:
            return "Mode Error"
    account_trade_mode_display_safe.short_description = "Trade Mode"
    
    def status_badge_safe(self, obj):
        try:
            status = obj.status
            color_map = {
                "Active": "green",
                "Expired": "red", 
                "Inactive": "gray",
                "Not Bound": "orange",
                "Bound - No Login": "blue"
            }
            color = color_map.get(status, "gray")
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, status
            )
        except:
            return format_html('<span style="color: red;">Error</span>')
    status_badge_safe.short_description = "Status"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
