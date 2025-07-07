# Dockerfile for Trading Robot Admin - Fixed Migration Issues
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

# Copy application code
COPY . .

# Remove problematic migration files and generate fresh ones
RUN rm -f configurations/migrations/0002_*.py && \
    rm -f configurations/migrations/0003_*.py && \
    rm -f configurations/migrations/0004_*.py

# Set Django settings for migration generation
ENV DJANGO_SETTINGS_MODULE=trading_admin.settings

# Generate fresh migrations for the updated models
RUN python manage.py makemigrations configurations --name remove_fibonacci_session_fields || echo "Migration generation skipped"

# Production Stage
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

# Copy application code with fresh migrations
COPY --from=builder /app /app

# Create necessary directories and set permissions
RUN mkdir -p logs staticfiles media && \
    chmod +x entrypoint.sh && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/api/health/ || exit 1

# Start the application
ENTRYPOINT ["./entrypoint.sh"]