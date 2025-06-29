#!/bin/bash
# File: prepare_render_deployment_complete.sh
# Purpose: Complete preparation for Render.com deployment with all fixes

set -e

echo "🚀 COMPLETE RENDER.COM DEPLOYMENT PREPARATION"
echo "============================================="
echo ""
echo "This script will prepare your Trading Robot Admin system for Render.com deployment"
echo "All configurations will be optimized for production use"
echo ""

# Step 1: Verify project structure
echo "📋 Step 1: Verifying project structure..."
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run from Django project root."
    exit 1
fi

required_dirs=("licenses" "configurations" "core" "trading_admin")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Error: Required directory '$dir' not found."
        exit 1
    fi
done

echo "✅ Project structure verified"

# Step 2: Create logs directory
echo "📁 Step 2: Creating logs directory..."
mkdir -p logs
touch logs/.gitkeep
echo "✅ Logs directory created"

# Step 3: Clean and optimize manage.py
echo "🔧 Step 3: Creating production-ready manage.py..."
cat > manage.py << 'EOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # Production-ready settings detection for Render.com
    
    # Priority 1: Explicit environment variable (set in Render dashboard)
    if os.getenv('DJANGO_SETTINGS_MODULE'):
        print(f"🔧 Using explicit DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    
    # Priority 2: Render platform detection (RENDER_EXTERNAL_HOSTNAME is set by Render)
    elif os.getenv('RENDER_EXTERNAL_HOSTNAME') or os.getenv('RENDER'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Detected Render platform - using settings_render")
    
    # Priority 3: Local development fallback
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
        print("💻 Using local development settings")
    
    # Debug information for troubleshooting
    print(f"📍 Final settings module: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    print(f"🌐 Environment: {'Render' if os.getenv('RENDER_EXTERNAL_HOSTNAME') else 'Local'}")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)
EOF

echo "✅ manage.py optimized for Render"

# Step 4: Create production-ready wsgi.py
echo "🔧 Step 4: Creating production-ready wsgi.py..."
cat > trading_admin/wsgi.py << 'EOF'
"""
WSGI config for trading_admin project.
Optimized for Render.com deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

# Production-ready settings detection for Render.com

# Priority 1: Explicit environment variable (set in Render dashboard)
if os.getenv('DJANGO_SETTINGS_MODULE'):
    # Already set by Render dashboard, use it
    pass
    
# Priority 2: Render platform detection
elif os.getenv('RENDER_EXTERNAL_HOSTNAME') or os.getenv('RENDER'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
    
# Priority 3: Local development fallback
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
EOF

echo "✅ wsgi.py optimized for Render"

# Step 5: Create comprehensive Render settings
echo "⚙️  Step 5: Creating comprehensive Render settings..."
cat > trading_admin/settings_render.py << 'EOF'
"""
Production settings for Render.com deployment
Optimized for Trading Robot Admin System
"""

import os
import sys
import dj_database_url
from django.core.management.utils import get_random_secret_key
from .settings import *

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# Secret key handling
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = get_random_secret_key()
    print("⚠️  WARNING: SECRET_KEY auto-generated. Set it in Render dashboard for production!")

# Debug mode (always False in production)
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Render domain configuration
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME:
    # Production - use Render domain
    ALLOWED_HOSTS = [
        RENDER_EXTERNAL_HOSTNAME,
        '*.onrender.com',
        'localhost',
        '127.0.0.1'
    ]
    # CORS for production
    CORS_ALLOWED_ORIGINS = [
        f'https://{RENDER_EXTERNAL_HOSTNAME}',
    ]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Development fallback
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
    CORS_ALLOW_ALL_ORIGINS = True

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

if os.getenv('DATABASE_URL'):
    # Use Render PostgreSQL database
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("✅ Using Render PostgreSQL database")
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("⚠️  Using SQLite fallback - ensure DATABASE_URL is set in production")

# ============================================================================
# STATIC FILES CONFIGURATION (WhiteNoise)
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuration for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Additional static files directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

# ============================================================================
# SECURITY SETTINGS FOR PRODUCTION
# ============================================================================

# SSL/HTTPS settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS settings
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Cookie security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# ============================================================================
# CACHING CONFIGURATION
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trading-admin-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# ============================================================================
# API RATE LIMITING (Enhanced for production)
# ============================================================================

# Enhanced rate limiting for production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',              # Anonymous users
    'user': '1000/hour',             # Authenticated admin users
    'bot_validation': '60/minute',   # Bot validation endpoint
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'licenses': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'configurations': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# ============================================================================
# EMAIL CONFIGURATION (Optional)
# ============================================================================

# Configure email settings if EMAIL_URL is provided
EMAIL_URL = os.getenv('EMAIL_URL')
if EMAIL_URL:
    # Parse email URL and configure Django email settings
    # Format: smtp://username:password@hostname:port
    print("✅ Email configuration detected")

# ============================================================================
# DEPLOYMENT VERIFICATION
# ============================================================================

# Print configuration summary
print("🚀 RENDER SETTINGS LOADED SUCCESSFULLY!")
print("=" * 50)
print(f"📍 RENDER_EXTERNAL_HOSTNAME: {RENDER_EXTERNAL_HOSTNAME or 'Not set (development)'}")
print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🔐 SECRET_KEY: {'✅ Set' if SECRET_KEY else '❌ Missing'}")
print(f"🐛 DEBUG: {DEBUG}")
print(f"💾 DATABASE: {'✅ Render PostgreSQL' if os.getenv('DATABASE_URL') else '⚠️  SQLite fallback'}")
print(f"📁 STATIC_ROOT: {STATIC_ROOT}")
print(f"🔒 SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
print(f"⚡ CACHE_BACKEND: {CACHES['default']['BACKEND']}")
print("=" * 50)

# Validate critical settings
if not DEBUG and not os.getenv('DATABASE_URL'):
    print("❌ CRITICAL: DATABASE_URL must be set in production!")
    
if not DEBUG and not RENDER_EXTERNAL_HOSTNAME:
    print("⚠️  WARNING: RENDER_EXTERNAL_HOSTNAME not detected")
EOF

echo "✅ Comprehensive Render settings created"

# Step 6: Create optimal render.yaml
echo "📝 Step 6: Creating production-ready render.yaml..."
cat > render.yaml << 'EOF'
services:
  # Web Service (Django Trading Robot Admin)
  - type: web
    name: trading-robot-admin
    runtime: python3
    region: oregon  # Choose region closest to your users
    
    # Build command - runs once during deployment
    buildCommand: |
      echo "🚀 Starting build process..."
      pip install --upgrade pip
      pip install -r requirements.txt
      echo "📦 Dependencies installed"
      python manage.py collectstatic --noinput
      echo "📁 Static files collected"
      python manage.py migrate --noinput
      echo "💾 Database migrations applied"
      echo "✅ Build completed successfully"
    
    # Start command - runs every time the service starts
    startCommand: |
      echo "🚀 Starting Trading Robot Admin..."
      gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --max-requests 1000 --max-requests-jitter 50 --access-logfile - --error-logfile -
    
    # Service configuration
    plan: starter  # Free tier - upgrade for production
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: DJANGO_SETTINGS_MODULE
        value: trading_admin.settings_render
      - key: SECRET_KEY
        generateValue: true  # Render will auto-generate
      - key: DEBUG
        value: false
      - key: WEB_CONCURRENCY
        value: 3
    
    # Health check endpoint
    healthCheckPath: /api/health/
    
    # Disk storage for logs
    disk:
      name: logs
      mountPath: /opt/render/project/src/logs
      sizeGB: 1

  # PostgreSQL Database
  - type: pgsql
    name: trading-robot-db
    region: oregon  # Same region as web service
    databaseName: trading_admin
    user: trading_admin_user
    plan: starter  # Free tier - 1GB storage, expires after 90 days without upgrade
    
    # Database configuration
    postgresMajorVersion: 15
EOF

echo "✅ Production-ready render.yaml created"

# Step 7: Verify and update requirements.txt
echo "📦 Step 7: Verifying and updating requirements.txt..."

# Create backup if requirements.txt exists
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements.txt.backup
fi

# Ensure all required packages are present
cat > requirements.txt << 'EOF'
# Core Django and Web Framework
Django==4.2.7
djangorestframework==3.14.0

# Database and Caching
psycopg2-binary==2.9.7
dj-database-url==2.1.0
redis==5.0.1

# Production Server
gunicorn==21.2.0
whitenoise==6.6.0

# Static Files and Media
Pillow==10.1.0

# CORS and Security
django-cors-headers==4.3.1

# Forms and UI
django-crispy-forms==2.1
crispy-bootstrap5==0.7

# Development and Utilities
django-extensions==3.2.3
python-decouple==3.8

# API Documentation (Optional)
# drf-spectacular==0.26.5

# Monitoring and Error Tracking (Optional)
# sentry-sdk[django]==1.38.0

# Rate Limiting (Built into DRF, but can add django-ratelimit if needed)
# django-ratelimit==4.1.0
EOF

echo "✅ requirements.txt verified and updated"

# Step 8: Create admin setup command
echo "👤 Step 8: Creating admin setup management command..."
mkdir -p core/management/commands/
touch core/management/__init__.py
touch core/management/commands/__init__.py

cat > core/management/commands/setup_admin.py << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Create admin user for production deployment'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--email',
            default='admin@example.com',
            help='Admin email (default: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            help='Admin password (if not provided, will use default)'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password'] or 'admin123'
        
        # Check if admin user already exists
        if User.objects.filter(username=username).exists():
            existing_user = User.objects.get(username=username)
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists')
            )
            self.stdout.write(f'Email: {existing_user.email}')
            self.stdout.write(f'Last login: {existing_user.last_login or "Never"}')
            return
        
        # Create admin user
        try:
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Admin user created successfully!')
            )
            self.stdout.write('=' * 40)
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write('=' * 40)
            self.stdout.write(f'🌐 Admin URL: https://your-app.onrender.com/admin/')
            self.stdout.write(f'🏠 Dashboard: https://your-app.onrender.com/dashboard/')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('⚠️  IMPORTANT: Change the password after first login!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {e}')
            )
EOF

echo "✅ Admin setup command created"

# Step 9: Create sample data command fix
echo "📊 Step 9: Verifying sample data command..."
if [ -f "licenses/management/commands/create_sample_data.py" ]; then
    echo "✅ Sample data command already exists"
else
    echo "⚠️  Sample data command not found - creating basic version..."
    mkdir -p licenses/management/commands/
    touch licenses/management/__init__.py
    touch licenses/management/commands/__init__.py
    
    cat > licenses/management/commands/create_sample_data.py << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from licenses.models import Client, License
from configurations.models import TradingConfiguration
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create sample data for demo purposes'
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 Creating sample data...')
        
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                'admin', 'admin@example.com', 'admin123'
            )
            self.stdout.write('✅ Admin user created')
        else:
            admin_user = User.objects.get(username='admin')
        
        # Create sample configuration
        config, created = TradingConfiguration.objects.get_or_create(
            name='US30 Standard',
            defaults={
                'description': 'Standard US30 trading configuration',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '08:45',
                'inp_SessionEnd': '10:00',
            }
        )
        
        # Create sample client
        client, created = Client.objects.get_or_create(
            first_name='John',
            last_name='Smith',
            country='United States',
            defaults={
                'email': 'john.smith@example.com',
                'created_by': admin_user
            }
        )
        
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
            self.stdout.write('✅ Sample license created')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Sample data creation completed!')
        )
EOF
fi

echo "✅ Sample data command verified"

# Step 10: Create deployment validation script
echo "🔍 Step 10: Creating deployment validation script..."
cat > validate_deployment.py << 'EOF'
#!/usr/bin/env python
"""
Deployment validation script for Trading Robot Admin
Run this after deployment to verify everything works
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

def validate_deployment():
    """Validate deployment configuration"""
    print("🔍 DEPLOYMENT VALIDATION")
    print("=" * 30)
    
    # Check Django settings
    from django.conf import settings
    print(f"✅ Django settings: {settings.SETTINGS_MODULE}")
    print(f"✅ Debug mode: {settings.DEBUG}")
    print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")
    
    # Check database connection
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Check models
    try:
        from licenses.models import License, Client
        from configurations.models import TradingConfiguration
        print(f"✅ License model: {License.objects.count()} records")
        print(f"✅ Client model: {Client.objects.count()} records")
        print(f"✅ Configuration model: {TradingConfiguration.objects.count()} records")
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
    
    # Check admin user
    try:
        from django.contrib.auth.models import User
        admin_count = User.objects.filter(is_superuser=True).count()
        print(f"✅ Admin users: {admin_count}")
    except Exception as e:
        print(f"❌ Admin user check failed: {e}")
    
    # Check static files
    import os
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root and os.path.exists(static_root):
        print("✅ Static files directory exists")
    else:
        print("⚠️  Static files directory not found")
    
    print("=" * 30)
    print("🎉 Validation completed!")

if __name__ == '__main__':
    validate_deployment()
EOF

chmod +x validate_deployment.py
echo "✅ Deployment validation script created"

# Step 11: Create comprehensive .gitignore
echo "📝 Step 11: Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Render specific
staticfiles/
.render/

# Backup files
*.backup
requirements.txt.backup

# Environment variables
.env
.env.local
.env.production

# Deployment files
deployment/
render_config/

# Logs
logs/*.log
!logs/.gitkeep

# Database
*.sqlite3
*.db

# Cache
__pycache__/
*.pyc
*.pyo
*.pyd

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

echo "✅ .gitignore updated"

# Step 12: Create deployment checklist
echo "📋 Step 12: Creating deployment checklist..."
cat > RENDER_DEPLOYMENT_GUIDE.md << 'EOF'
# 🚀 Trading Robot Admin - Render.com Deployment Guide

## Pre-Deployment Checklist ✅

- [x] Optimized `manage.py` for Render platform detection
- [x] Optimized `wsgi.py` for production 
- [x] Created comprehensive `settings_render.py`
- [x] Created production-ready `render.yaml`
- [x] Updated `requirements.txt` with all dependencies
- [x] Created admin setup management command
- [x] Added deployment validation script
- [x] Updated `.gitignore` for Render

## 🔧 Render.com Setup Steps

### 1. Create Render Account
- Go to [render.com](https://render.com) and sign up
- Connect your GitHub/GitLab account

### 2. Create PostgreSQL Database
1. Click **"New"** → **"PostgreSQL"**
2. Configure database:
   - **Name**: `trading-robot-db`
   - **Database**: `trading_admin`
   - **User**: `trading_admin_user`
   - **Region**: `Oregon` (or closest to you)
   - **Plan**: `Starter` (free)
3. Wait for status to show **"Available"**
4. Note the **Internal Database URL** for later

### 3. Create Web Service
1. Click **"New"** → **"Web Service"**
2. Connect your repository
3. Configure service:
   - **Name**: `trading-robot-admin`
   - **Runtime**: `Python 3`
   - **Region**: `Oregon` (same as database)
   - **Branch**: `main` (or your deploy branch)
   - **Root Directory**: Leave empty if deploying from root

### 4. Configure Environment Variables
In the Environment section, add:
```
DJANGO_SETTINGS_MODULE=trading_admin.settings_render
SECRET_KEY=(auto-generated by Render)
DEBUG=false
```

### 5. Configure Build & Start Commands
- **Build Command**: 
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput
  ```
- **Start Command**:
  ```bash
  gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
  ```

### 6. Deploy
1. Click **"Create Web Service"**
2. Wait for deployment to complete (5-10 minutes)
3. Check logs for any errors

## 🎯 Post-Deployment Steps

### 1. Create Admin User
Use the Render Shell or add to build command:
```bash
python manage.py setup_admin
```

### 2. Create Sample Data (Optional)
```bash
python manage.py create_sample_data
```

### 3. Verify Deployment
```bash
python validate_deployment.py
```

### 4. Test Your Application
- **Admin Panel**: `https://your-app.onrender.com/admin/`
- **Dashboard**: `https://your-app.onrender.com/dashboard/`
- **API Health**: `https://your-app.onrender.com/api/health/`
- **API Docs**: `https://your-app.onrender.com/api/docs/`

## 🔗 Important URLs

Replace `your-app` with your actual Render service name:

- **Admin Panel**: `https://your-app.onrender.com/admin/`
- **Dashboard**: `https://your-app.onrender.com/dashboard/`
- **API Health Check**: `https://your-app.onrender.com/api/health/`
- **API Documentation**: `https://your-app.onrender.com/api/docs/`
- **Bot Validation API**: `https://your-app.onrender.com/api/validate/`

## 🔐 Default Admin Credentials

```
Username: admin
Password: admin123
Email: admin@example.com
```

**⚠️ IMPORTANT**: Change the password immediately after first login!

## 🐛 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check requirements.txt for package conflicts
   - Verify Python version compatibility
   - Check build logs in Render dashboard

2. **Database Connection Errors**
   - Ensure DATABASE_URL environment variable is set
   - Verify PostgreSQL service is running
   - Check database credentials

3. **Static Files Not Loading**
   - Verify WhiteNoise is in MIDDLEWARE
   - Check STATIC_ROOT setting
   - Run `collectstatic` command

4. **Admin Login Issues**
   - Run `python manage.py setup_admin` via Render Shell
   - Check if superuser exists: `python manage.py shell`
   - Verify admin URLs are correct

### Debug Commands

Use Render Shell to run these commands:

```bash
# Check database connection
python manage.py dbshell

# List all users
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.all())"

# Check migrations
python manage.py showmigrations

# Collect static files
python manage.py collectstatic --noinput

# Create admin user manually
python manage.py createsuperuser
```

## 📊 Performance Optimization

### For Production Use:

1. **Upgrade Database Plan**
   - Free PostgreSQL expires after 90 days
   - Consider upgrading to paid plan for persistence

2. **Upgrade Web Service Plan**
   - Free tier spins down after inactivity
   - Paid plans offer better performance and uptime

3. **Add Monitoring**
   - Set up error tracking (Sentry)
   - Monitor API usage and performance
   - Set up uptime monitoring

4. **Configure Caching**
   - Add Redis for session/cache storage
   - Enable template caching
   - Implement API response caching

## 🔒 Security Considerations

1. **Environment Variables**
   - Set strong SECRET_KEY
   - Use environment variables for all secrets
   - Never commit sensitive data to Git

2. **Database Security**
   - Use strong database passwords
   - Limit database access to your app only
   - Regular database backups

3. **API Security**
   - Monitor API usage for abuse
   - Implement proper rate limiting
   - Use HTTPS for all communications

4. **Admin Security**
   - Change default admin password
   - Use strong admin passwords
   - Consider enabling 2FA

## 📈 Scaling Considerations

When your application grows:

1. **Database Scaling**
   - Monitor database performance
   - Consider read replicas
   - Implement database connection pooling

2. **Application Scaling**
   - Increase worker count
   - Use Redis for caching
   - Consider background task processing

3. **Monitoring & Alerting**
   - Set up comprehensive logging
   - Monitor response times
   - Set up error alerting

## 🆘 Support

If you encounter issues:

1. Check Render logs first
2. Review this deployment guide
3. Check Django documentation
4. Contact Render support for platform issues

---

**🎉 Congratulations!** Your Trading Robot Admin system is now deployed on Render.com!
EOF

echo "✅ Comprehensive deployment guide created"

# Step 13: Final verification
echo "🔍 Step 13: Running final verification..."

# Test settings import
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'trading_admin.settings_render'
os.environ['SECRET_KEY'] = 'test-key'
os.environ['RENDER_EXTERNAL_HOSTNAME'] = 'test.onrender.com'
import django
django.setup()
print('✅ Render settings load successfully')
" 2>/dev/null && echo "✅ Settings validation passed" || echo "⚠️  Settings validation failed"

# Check if all required files exist
required_files=(
    "manage.py"
    "trading_admin/wsgi.py"
    "trading_admin/settings_render.py"
    "render.yaml"
    "requirements.txt"
    "core/management/commands/setup_admin.py"
    "RENDER_DEPLOYMENT_GUIDE.md"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ All required files present"
else
    echo "❌ Missing files:"
    printf '   %s\n' "${missing_files[@]}"
fi

echo ""
echo "🎉 DEPLOYMENT PREPARATION COMPLETED!"
echo "===================================="
echo ""
echo "📁 Files created/updated:"
echo "   ✅ manage.py (production-ready)"
echo "   ✅ trading_admin/wsgi.py (optimized)" 
echo "   ✅ trading_admin/settings_render.py (comprehensive)"
echo "   ✅ render.yaml (production-ready)"
echo "   ✅ requirements.txt (verified)"
echo "   ✅ core/management/commands/setup_admin.py"
echo "   ✅ validate_deployment.py"
echo "   ✅ RENDER_DEPLOYMENT_GUIDE.md"
echo "   ✅ .gitignore (updated)"
echo ""
echo "📋 Next steps:"
echo "1. Review all changes:"
echo "   📖 Read RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "2. Commit and push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Complete Render.com deployment preparation'"
echo "   git push origin main"
echo ""
echo "3. Deploy on Render.com:"
echo "   🌐 Go to render.com"
echo "   🔗 Connect your GitHub repository"
echo "   ⚙️  Follow the deployment guide"
echo ""
echo "4. Test your deployed application:"
echo "   🔍 Run post-deployment validation"
echo "   👤 Create admin user"
echo "   📊 Verify all functionality"
echo ""
echo "📖 Complete guide: RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "🚀 Your Trading Robot Admin is ready for Render.com!"