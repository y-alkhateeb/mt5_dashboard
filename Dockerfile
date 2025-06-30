# Dockerfile for Trading Robot Admin - Pure Docker Deployment
# Optimized for Render.com

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
    curl \
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
    curl \
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
RUN mkdir -p logs staticfiles media

# Set permissions for the app directory
# Note: The chmod for docker-entrypoint.sh has been removed.
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose port (Render uses $PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/api/health/ || exit 1

# CMD to start the application server
ENTRYPOINT ["entrypoint.sh"]
# Gunicorn is now started directly.
CMD ["gunicorn", "trading_admin.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers", "3""]