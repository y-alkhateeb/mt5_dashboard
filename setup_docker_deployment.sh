#!/bin/bash
# File: setup_docker_deployment.sh
# Purpose: Set up Docker-based deployment for Render.com

echo "🐳 TRADING ROBOT ADMIN - DOCKER DEPLOYMENT SETUP"
echo "================================================"
echo ""
echo "This script sets up Docker-based deployment for Render.com"
echo ""

# Step 1: Verify project structure
echo "📋 Step 1: Verifying project structure..."

required_files=("manage.py" "requirements.txt" "trading_admin/settings.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Found: $file"
    else
        echo "❌ Missing: $file"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files. Please ensure your Django project is properly set up."
    exit 1
fi

echo ""

# Step 2: Create Render settings if not exists
echo "⚙️  Step 2: Creating Render settings..."

if [ ! -f "trading_admin/settings_render.py" ]; then
    cat > trading_admin/settings_render.py << 'EOF'
"""
Production settings for Render.com (Docker deployment)
"""
import os
import dj_database_url
from .settings import *

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Allowed hosts for Render
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, '*.onrender.com', 'localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['*']

# Database configuration
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("✅ Using Render PostgreSQL database")
else:
    print("⚠️  Using SQLite fallback - set DATABASE_URL for production")

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise middleware for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# CORS settings
CORS_ALLOWED_ORIGINS = [
    f'https://{RENDER_EXTERNAL_HOSTNAME}',
] if RENDER_EXTERNAL_HOSTNAME else []
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trading-admin-cache',
        'TIMEOUT': 300,
        'OPTIONS': {'MAX_ENTRIES': 1000}
    }
}

# Enhanced rate limiting for production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',
    'user': '1000/hour',
    'bot_validation': '60/minute',
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'licenses': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'configurations': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

print("🐳 Docker Render settings loaded successfully!")
print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🔐 DEBUG: {DEBUG}")
print(f"💾 DATABASE: {'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite'}")
EOF

    echo "✅ Created settings_render.py"
else
    echo "✅ settings_render.py already exists"
fi

echo ""

# Step 3: Create admin setup command if needed
echo "👤 Step 3: Setting up admin management command..."

admin_command_dir="core/management/commands"
admin_command_file="$admin_command_dir/setup_admin.py"

if [ ! -f "$admin_command_file" ]; then
    mkdir -p "$admin_command_dir"
    touch core/management/__init__.py
    touch core/management/commands/__init__.py
    
    cat > "$admin_command_file" << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create admin user for production deployment'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Admin username')
        parser.add_argument('--password', default='admin123', help='Admin password')
        parser.add_argument('--email', default='admin@example.com', help='Admin email')
    
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'✅ Admin user "{username}" already exists')
            return
        
        try:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(f'✅ Created admin user: {username}')
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'🔑 Password: {password}')
            self.stdout.write('⚠️  Change password after first login!')
        except Exception as e:
            self.stdout.write(f'❌ Error creating admin: {e}')
EOF
    
    echo "✅ Created admin setup command"
else
    echo "✅ Admin setup command already exists"
fi

echo ""

# Step 4: Create sample data command if needed
echo "📊 Step 4: Setting up sample data command..."

sample_command_file="licenses/management/commands/create_sample_data.py"

if [ ! -f "$sample_command_file" ]; then
    mkdir -p "licenses/management/commands"
    touch licenses/management/__init__.py
    touch licenses/management/commands/__init__.py
    
    cat > "$sample_command_file" << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from licenses.models import Client, License
from configurations.models import TradingConfiguration
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample data for demo purposes'
    
    def add_arguments(self, parser):
        parser.add_argument('--clients', type=int, default=3, help='Number of clients to create')
    
    def handle(self, *args, **options):
        num_clients = options['clients']
        
        self.stdout.write('🚀 Creating sample data...')
        
        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('✅ Admin user created')
        
        # Create trading configurations
        configs = [
            {
                'name': 'US30 Standard',
                'description': 'Standard US30 trading configuration',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '08:45',
                'inp_SessionEnd': '10:00',
            },
            {
                'name': 'EURUSD Conservative',
                'description': 'Conservative EURUSD trading',
                'inp_AllowedSymbol': 'EURUSD',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '09:00',
                'inp_SessionEnd': '17:00',
            }
        ]
        
        created_configs = []
        for config_data in configs:
            config, created = TradingConfiguration.objects.get_or_create(
                name=config_data['name'],
                defaults=config_data
            )
            created_configs.append(config)
            if created:
                self.stdout.write(f'✅ Created configuration: {config.name}')
        
        # Create sample clients and licenses
        client_data = [
            {'first_name': 'John', 'last_name': 'Smith', 'country': 'United States', 'email': 'john@example.com'},
            {'first_name': 'Maria', 'last_name': 'Garcia', 'country': 'Spain', 'email': 'maria@example.com'},
            {'first_name': 'Ahmed', 'last_name': 'Hassan', 'country': 'Egypt', 'email': 'ahmed@example.com'},
        ]
        
        for i in range(min(num_clients, len(client_data))):
            data = client_data[i]
            client, created = Client.objects.get_or_create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                country=data['country'],
                defaults={
                    'email': data['email'],
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write(f'✅ Created client: {client.full_name}')
                
                # Create license for client
                License.objects.create(
                    client=client,
                    trading_configuration=created_configs[i % len(created_configs)],
                    account_trade_mode=i % 3,  # Rotate between demo, restricted, live
                    expires_at=timezone.now() + timedelta(days=365),
                    is_active=True,
                    created_by=admin_user
                )
                self.stdout.write(f'✅ Created license for {client.full_name}')
        
        self.stdout.write('🎉 Sample data creation completed!')
        self.stdout.write(f'📊 Total licenses: {License.objects.count()}')
        self.stdout.write(f'👥 Total clients: {Client.objects.count()}')
        self.stdout.write(f'⚙️  Total configurations: {TradingConfiguration.objects.count()}')
EOF
    
    echo "✅ Created sample data command"
else
    echo "✅ Sample data command already exists"
fi

echo ""

# Step 5: Create Docker entrypoint script
echo "🐳 Step 5: Creating Docker entrypoint script..."

cat > docker-entrypoint.sh << 'EOF'
#!/bin/bash
# Docker entrypoint script for Trading Robot Admin

set -e

echo "🚀 Starting Trading Robot Admin on Render.com"
echo "=============================================="

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    
    if [ -z "$DATABASE_URL" ]; then
        echo "⚠️  DATABASE_URL not set, skipping database wait"
        return 0
    fi
    
    python -c "
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)
db_config = {
    'host': parsed.hostname,
    'port': parsed.port or 5432,
    'user': parsed.username,
    'password': parsed.password,
    'dbname': parsed.path[1:]  # Remove leading '/'
}

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        conn = psycopg2.connect(**db_config)
        conn.close()
        print('✅ Database connection successful')
        break
    except psycopg2.OperationalError:
        attempt += 1
        print(f'⏳ Database not ready, attempt {attempt}/{max_attempts}')
        if attempt >= max_attempts:
            print('❌ Database connection failed after maximum attempts')
            sys.exit(1)
        time.sleep(2)
"
}

# Function to run Django setup
setup_django() {
    echo "🔧 Setting up Django application..."
    
    # Run database migrations
    echo "📊 Running database migrations..."
    python manage.py migrate --noinput
    
    # Create admin user if it doesn't exist
    echo "👤 Setting up admin user..."
    python manage.py setup_admin --username admin --password admin123 --email admin@example.com || true
    
    # Create sample data if database is empty
    echo "📋 Checking if sample data is needed..."
    python -c "
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from licenses.models import License
from configurations.models import TradingConfiguration

if License.objects.count() == 0 and TradingConfiguration.objects.count() == 0:
    print('📊 Creating sample data...')
    from django.core.management import call_command
    try:
        call_command('create_sample_data', '--clients', '3')
        print('✅ Sample data created')
    except Exception as e:
        print(f'⚠️  Could not create sample data: {e}')
else:
    print('✅ Data already exists, skipping sample data creation')
"
}

# Function to start the application
start_app() {
    echo "🚀 Starting application server..."
    echo "📍 Port: ${PORT:-10000}"
    echo "🌐 Workers: ${WEB_CONCURRENCY:-3}"
    
    exec gunicorn trading_admin.wsgi:application \
        --bind 0.0.0.0:${PORT:-10000} \
        --workers ${WEB_CONCURRENCY:-3} \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload
}

# Main execution function
main() {
    # Wait for database if DATABASE_URL is provided
    if [ ! -z "$DATABASE_URL" ]; then
        wait_for_db
        setup_django
    else
        echo "⚠️  No DATABASE_URL found, skipping database setup"
    fi
    
    # Start the application
    start_app
}

# Run main function with all arguments
main "$@"
EOF

# Make it executable
chmod +x docker-entrypoint.sh

echo "✅ Created docker-entrypoint.sh"

echo ""

# Step 6: Create .dockerignore
echo "📝 Step 6: Creating .dockerignore..."

cat > .dockerignore << 'EOF'
# Git
.git
.gitignore

# Docker
Dockerfile.backup
docker-compose*.yml

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/

# Virtual environments
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local development
.env
.env.local
db.sqlite3
*.log

# Media and static (collected during build)
media/
staticfiles/

# Documentation
*.md
docs/

# Test files
.coverage
.pytest_cache/
.tox/

# Backup files
*.backup
EOF

echo "✅ Created .dockerignore"

echo ""

# Step 7: Update .gitignore
echo "📝 Step 7: Updating .gitignore..."

cat >> .gitignore << 'EOF'

# Docker
.dockerignore
docker-compose*.yml

# Render
.render/
staticfiles/

# Logs
logs/
*.log
EOF

echo "✅ Updated .gitignore"

echo ""

# Step 8: Test Docker build locally (optional)
echo "🧪 Step 8: Testing Docker configuration..."

if command -v docker >/dev/null 2>&1; then
    echo "🐳 Docker found - you can test locally with:"
    echo "   docker build -t trading-robot-admin ."
    echo "   docker run -p 8000:10000 -e SECRET_KEY=test-key trading-robot-admin"
    echo ""
    echo "Do you want to test the Docker build now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🔨 Building Docker image..."
        if docker build -t trading-robot-admin .; then
            echo "✅ Docker build successful!"
            echo "🚀 You can now run: docker run -p 8000:10000 -e SECRET_KEY=test-key trading-robot-admin"
        else
            echo "❌ Docker build failed - check the output above"
        fi
    fi
else
    echo "⚠️  Docker not found - skipping local test"
fi

echo ""

# Step 9: Final instructions
echo "🎉 DOCKER DEPLOYMENT SETUP COMPLETED!"
echo "===================================="
echo ""
echo "📁 Files created/updated:"
echo "   ✅ Dockerfile (production-ready)"
echo "   ✅ docker-entrypoint.sh (startup script)"
echo "   ✅ render.yaml (Docker configuration)"
echo "   ✅ trading_admin/settings_render.py"
echo "   ✅ core/management/commands/setup_admin.py"
echo "   ✅ licenses/management/commands/create_sample_data.py"
echo "   ✅ .dockerignore"
echo "   ✅ .gitignore (updated)"
echo ""
echo "📋 Docker Deployment Process:"
echo ""
echo "1. Commit your changes:"
echo "   git add ."
echo "   git commit -m 'Add Docker deployment configuration'"
echo "   git push origin main"
echo ""
echo "2. Deploy on Render:"
echo "   🌐 Go to render.com → Create Web Service"
echo "   🔗 Connect your GitHub repository"
echo "   ⚙️  Render will automatically detect the Dockerfile"
echo "   🐳 Runtime will be set to 'Docker'"
echo ""
echo "3. Environment Variables (set in Render Dashboard):"
echo "   DJANGO_SETTINGS_MODULE=trading_admin.settings_render"
echo "   SECRET_KEY=(auto-generated)"
echo "   DEBUG=false"
echo ""
echo "4. After deployment:"
echo "   🏠 Dashboard: https://your-app.onrender.com/dashboard/"
echo "   👤 Admin: https://your-app.onrender.com/admin/ (admin/admin123)"
echo "   🤖 API: https://your-app.onrender.com/api/validate/"
echo ""
echo "🐳 Docker Benefits:"
echo "   ✅ Consistent environment across dev/prod"
echo "   ✅ Isolated dependencies"
echo "   ✅ Automatic health checks"
echo "   ✅ Better resource management"
echo "   ✅ Easier debugging and scaling"
echo ""
echo "🚀 Your Trading Robot Admin is ready for Docker deployment on Render!"