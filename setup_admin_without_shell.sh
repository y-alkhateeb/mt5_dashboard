#!/bin/bash
# File: setup_admin_without_shell.sh
# Purpose: Set up admin creation without requiring Render shell access

set -e

echo "🔧 Setting up admin creation (no shell required)..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run from Django project root."
    exit 1
fi

echo "✅ Django project detected"

# Create directories if they don't exist
mkdir -p core/management/commands/

# Create __init__.py files
touch core/management/__init__.py
touch core/management/commands/__init__.py

echo "📁 Directory structure created"

# Method 1: Create simple admin command
echo "📝 Creating simple admin management command..."
cat > core/management/commands/createadmin.py << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create admin user if it does not exist'
    
    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists')
            )
            return
        
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user created successfully!')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'🚀 Login at: /admin/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin: {e}')
            )
EOF

echo "✅ Management command created"

# Method 2: Create setup endpoint
echo "📝 Creating one-time setup endpoint..."
cat > core/setup_views.py << 'EOF'
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def setup_admin(request):
    """
    One-time setup endpoint to create admin user
    Should be removed after first use for security
    """
    try:
        # Check if admin already exists
        if User.objects.filter(username='admin').exists():
            return JsonResponse({
                'success': False,
                'message': 'Admin user already exists',
                'action': 'Login at /admin/ with existing credentials'
            })
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Admin user created successfully!',
            'credentials': {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@example.com'
            },
            'login_url': '/admin/',
            'warning': 'Please change the password after first login!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating admin user: {str(e)}'
        })

@require_http_methods(["GET"])  
def setup_status(request):
    """Check if admin user exists"""
    admin_exists = User.objects.filter(username='admin').exists()
    user_count = User.objects.count()
    
    return JsonResponse({
        'admin_exists': admin_exists,
        'total_users': user_count,
        'setup_needed': not admin_exists,
        'setup_url': '/setup/admin/' if not admin_exists else None
    })
EOF

echo "✅ Setup endpoint created"

# Method 3: Update URLs
echo "📝 Updating core/urls.py..."
if [ -f "core/urls.py" ]; then
    # Backup original
    cp core/urls.py core/urls.py.backup
    
    cat > core/urls.py << 'EOF'
from django.urls import path
from .views import DashboardView
from .api_views import api_documentation, health_check
from .setup_views import setup_admin, setup_status

urlpatterns = [
    # Dashboard URLs
    path('', DashboardView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # API Documentation URLs
    path('api/docs/', api_documentation, name='api-docs'),
    path('api/health/', health_check, name='health-check'),
    
    # Setup URLs (temporary - remove after first use)
    path('setup/status/', setup_status, name='setup-status'),
    path('setup/admin/', setup_admin, name='setup-admin'),
]
EOF
    echo "✅ URLs updated"
else
    echo "⚠️  core/urls.py not found, skipping URL update"
fi

# Method 4: Update render.yaml for auto-creation
echo "📝 Creating render.yaml with auto-admin creation..."
cat > render.yaml << 'EOF'
services:
  # Web Service (Django App)
  - type: web
    name: trading-robot-admin
    runtime: python3
    buildCommand: |
      pip install --upgrade pip --root-user-action=ignore &&
      pip install -r requirements.txt --root-user-action=ignore &&
      python manage.py collectstatic --noinput &&
      python manage.py migrate --noinput &&
      python manage.py createadmin
    startCommand: |
      gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --max-requests 1000 --max-requests-jitter 50
    plan: starter
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.5
      - key: DJANGO_SETTINGS_MODULE
        value: trading_admin.settings_render
      - key: DEBUG
        value: false
      - key: WEB_CONCURRENCY
        value: 3
    healthCheckPath: /api/health/
    
  # PostgreSQL Database
  - type: pgsql
    name: trading-robot-db
    databaseName: trading_admin
    user: trading_admin_user
    plan: starter
EOF

echo "✅ render.yaml updated"

# Show summary
echo ""
echo "🎉 Setup complete! Choose your preferred method:"
echo ""
echo "════════════════════════════════════════════════"
echo "🚀 METHOD 1: Auto-Create During Deployment (EASIEST)"
echo "════════════════════════════════════════════════"
echo "1. Commit and push:"
echo "   git add ."
echo "   git commit -m 'Add admin auto-creation'"
echo "   git push origin main"
echo ""
echo "2. Redeploy in Render dashboard"
echo "3. Admin will be created automatically!"
echo ""
echo "════════════════════════════════════════════════"
echo "🌐 METHOD 2: One-Time Setup Endpoint (QUICK)"
echo "════════════════════════════════════════════════"
echo "1. Deploy the changes above"
echo "2. Visit: https://your-app.onrender.com/setup/status/"
echo "3. If setup needed, POST to: https://your-app.onrender.com/setup/admin/"
echo "4. Or use curl:"
echo "   curl -X POST https://your-app.onrender.com/setup/admin/"
echo ""
echo "════════════════════════════════════════════════"
echo "📊 METHOD 3: Use Existing Sample Data Command"
echo "════════════════════════════════════════════════"
echo "Update render.yaml buildCommand to:"
echo "python manage.py create_sample_data --clean --clients 3"
echo ""
echo "🔐 Default Admin Credentials (All Methods):"
echo "   Username: admin"
echo "   Password: admin123"
echo "   Email: admin@example.com"
echo "   URL: https://your-app.onrender.com/admin/"
echo ""
echo "⚠️  IMPORTANT: Change password after first login!"
echo ""
echo "🎯 RECOMMENDED: Use Method 1 (auto-create during deployment)"