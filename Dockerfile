# Dockerfile for Trading Robot Admin - Render.com Optimized
# Multi-stage build for smaller image size and better security

# ============================================================================
# Build Stage - Install dependencies and prepare application
# ============================================================================
FROM python:3.11.9-slim as builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Production Stage - Minimal runtime image
# ============================================================================
FROM python:3.11.9-slim as production

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=trading_admin.settings_render \
    PORT=10000

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django django

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs staticfiles media && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Collect static files (run during build for better performance)
RUN python manage.py collectstatic --noinput --settings=trading_admin.settings_render

# Expose port (Render uses $PORT environment variable)
EXPOSE $PORT

# ============================================================================
# Entrypoint Script for Database Setup and App Start
# ============================================================================
# Create entrypoint script
USER root
RUN cat > /app/docker-entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting Trading Robot Admin on Render.com"
echo "=============================================="

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    python << 'PYTHON'
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL not found")
    sys.exit(1)

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
        print("✅ Database connection successful")
        break
    except psycopg2.OperationalError as e:
        attempt += 1
        print(f"⏳ Database not ready, attempt {attempt}/{max_attempts}")
        if attempt >= max_attempts:
            print("❌ Database connection failed after maximum attempts")
            sys.exit(1)
        time.sleep(2)
PYTHON
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
    python << 'PYTHON'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from licenses.models import License
from configurations.models import TradingConfiguration

if License.objects.count() == 0 and TradingConfiguration.objects.count() == 0:
    print("📊 Creating sample data...")
    from django.core.management import call_command
    call_command('create_sample_data', '--clients', '3')
    print("✅ Sample data created")
else:
    print("✅ Data already exists, skipping sample data creation")
PYTHON
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

# Main execution
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

# Run main function
main "$@"
EOF

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh && \
    chown django:django /app/docker-entrypoint.sh

# Switch back to django user
USER django

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-10000}/api/health/', timeout=30)" || exit 1

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]