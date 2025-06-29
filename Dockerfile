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

# Create necessary directories and copy entrypoint
RUN mkdir -p logs staticfiles media

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# Set permissions
RUN chown -R django:django /app && \
    chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER django

# Collect static files (run during build for better performance)
RUN python manage.py collectstatic --noinput --settings=trading_admin.settings_render

# Expose port (Render uses $PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-10000}/api/health/', timeout=30)" || exit 1

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
