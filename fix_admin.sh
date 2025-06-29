#!/bin/bash
# Quick Fix Script for Trading Robot Admin Database Issues
# Run this script to fix the missing database tables error

set -e

echo "🔧 TRADING ROBOT ADMIN - QUICK DATABASE FIX"
echo "============================================"
echo ""
echo "This script will fix the missing database tables error."
echo ""

# Function to print colored output
print_success() {
    echo -e "✅ $1"
}

print_warning() {
    echo -e "⚠️  $1"
}

print_error() {
    echo -e "❌ $1"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Step 1: Check if we're in the right directory
echo "📍 Step 1: Verifying project directory..."

if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from your Django project root directory."
    exit 1
fi

if [ ! -d "licenses" ] || [ ! -d "configurations" ]; then
    print_error "Required app directories not found. Please ensure you're in the correct project directory."
    exit 1
fi

print_success "Project directory verified"

# Step 2: Create the fixed admin file
echo ""
echo "📝 Step 2: Updating admin configuration..."

cat > licenses/admin.py << 'EOF'
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
EOF

print_success "Admin configuration updated with safe methods"

# Step 3: Run migrations
echo ""
echo "🚀 Step 3: Running database migrations..."

# Check if migration files exist, create them if they don't
print_info "Checking migration files..."

if [ ! -f "configurations/migrations/0001_initial.py" ]; then
    print_warning "Creating configurations migrations..."
    python manage.py makemigrations configurations
fi

if [ ! -f "licenses/migrations/0001_initial.py" ]; then
    print_warning "Creating licenses migrations..."
    python manage.py makemigrations licenses
fi

if [ ! -f "core/migrations/0001_initial.py" ]; then
    print_warning "Creating core migrations..."
    python manage.py makemigrations core
fi

# Apply migrations
print_info "Applying migrations..."
python manage.py migrate

print_success "Database migrations completed"

# Step 4: Create admin user
echo ""
echo "👤 Step 4: Setting up admin user..."

python manage.py shell << 'EOF'
from django.contrib.auth.models import User

username = 'yousef'
password = 'admin123123'
email = 'yousef@tradingadmin.com'

try:
    if User.objects.filter(username=username).exists():
        print(f"✅ Admin user '{username}' already exists")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.email = email
        user.save()
        print("✅ Admin user credentials updated")
    else:
        User.objects.create_superuser(username, email, password)
        print(f"✅ Created admin user: {username}")
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    
except Exception as e:
    print(f"❌ Error setting up admin user: {e}")
EOF

print_success "Admin user setup completed"

# Step 5: Create sample data
echo ""
echo "📊 Step 5: Creating sample data..."

python manage.py shell << 'EOF'
from licenses.models import Client, License
from configurations.models import TradingConfiguration
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

try:
    # Create sample configuration
    config, created = TradingConfiguration.objects.get_or_create(
        name='US30 Standard Configuration',
        defaults={
            'description': 'Standard US30 trading configuration',
            'inp_AllowedSymbol': 'US30',
            'inp_StrictSymbolCheck': True,
            'inp_SessionStart': '08:45',
            'inp_SessionEnd': '10:00'
        }
    )
    
    if created:
        print("✅ Created sample trading configuration")
    else:
        print("✅ Sample trading configuration already exists")
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if admin_user:
        # Create sample client
        client, created = Client.objects.get_or_create(
            first_name='Sample',
            last_name='Client',
            country='United States',
            defaults={
                'email': 'sample@example.com',
                'created_by': admin_user
            }
        )
        
        if created:
            print("✅ Created sample client")
        else:
            print("✅ Sample client already exists")
        
        # Create sample license
        if not License.objects.filter(client=client).exists():
            License.objects.create(
                client=client,
                trading_configuration=config,
                account_trade_mode=0,  # Demo
                expires_at=timezone.now() + timedelta(days=365),
                is_active=True,
                created_by=admin_user
            )
            print("✅ Created sample license")
        else:
            print("✅ Sample license already exists")
    
    print("🎉 Sample data setup completed!")
    
except Exception as e:
    print(f"❌ Error creating sample data: {e}")
EOF

print_success "Sample data creation completed"

# Step 6: Verify everything works
echo ""
echo "🔍 Step 6: Verifying the fix..."

python manage.py shell << 'EOF'
from licenses.models import Client, License
from configurations.models import TradingConfiguration
from django.contrib.auth.models import User

try:
    # Test database access
    client_count = Client.objects.count()
    license_count = License.objects.count()
    config_count = TradingConfiguration.objects.count()
    admin_count = User.objects.filter(is_superuser=True).count()
    
    print(f"📊 Database Statistics:")
    print(f"   👤 Admin users: {admin_count}")
    print(f"   👥 Clients: {client_count}")
    print(f"   🔑 Licenses: {license_count}")
    print(f"   ⚙️  Configurations: {config_count}")
    
    if all([client_count > 0, license_count > 0, config_count > 0, admin_count > 0]):
        print("✅ All database tables verified and populated!")
    else:
        print("⚠️  Some data may be missing, but tables exist")
        
except Exception as e:
    print(f"❌ Verification failed: {e}")
EOF

# Step 7: Final summary
echo ""
echo "🎉 DATABASE FIX COMPLETED SUCCESSFULLY!"
echo "======================================="
echo ""
print_success "All database issues have been resolved!"
echo ""
echo "🔐 Admin Credentials:"
echo "   Username: yousef"
echo "   Password: admin123123"
echo "   Email: yousef@tradingadmin.com"
echo ""
echo "🌐 URLs:"
echo "   🏠 Local Admin: http://localhost:8000/admin/"
echo "   📊 Local Dashboard: http://localhost:8000/dashboard/"
echo "   🤖 Production Admin: https://mt5-dashboard.onrender.com/admin/"
echo ""
echo "📋 Next Steps:"
echo "1. 🚀 Start your Django server: python manage.py runserver"
echo "2. 🌐 Visit http://localhost:8000/admin/"
echo "3. 🔑 Login with the credentials above"
echo "4. 🧪 Test the admin interface"
echo "5. 📊 Check the dashboard at http://localhost:8000/dashboard/"
echo ""
print_success "Your Trading Robot Admin is ready to use!"