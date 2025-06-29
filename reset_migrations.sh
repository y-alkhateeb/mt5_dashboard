#!/bin/bash
# File: reset_migrations.sh

set -e  # Exit on any error

echo "🔄 Resetting Django migrations and database..."
echo "=============================================="

# Step 1: Remove migration files
echo "🗑️ Step 1: Removing old migration files..."

# Remove license app migrations (keep __init__.py)
if [ -d "licenses/migrations" ]; then
    find licenses/migrations/ -name "*.py" -not -name "__init__.py" -delete
    echo "   ✅ Removed licenses migrations"
fi

# Remove configurations app migrations (keep __init__.py)
if [ -d "configurations/migrations" ]; then
    find configurations/migrations/ -name "*.py" -not -name "__init__.py" -delete
    echo "   ✅ Removed configurations migrations"
fi

# Remove core app migrations (keep __init__.py)
if [ -d "core/migrations" ]; then
    find core/migrations/ -name "*.py" -not -name "__init__.py" -delete
    echo "   ✅ Removed core migrations"
fi

# Step 2: Remove database
echo "🗑️ Step 2: Removing old database..."
if [ -f "db.sqlite3" ]; then
    rm -f db.sqlite3
    echo "   ✅ Removed db.sqlite3"
fi

# Step 3: Remove migration-related data files
echo "🗑️ Step 3: Cleaning up migration data..."
if [ -f "railway_migration_data.json" ]; then
    rm -f railway_migration_data.json
    echo "   ✅ Removed railway_migration_data.json"
fi

if [ -f "migrate_to_railway.py" ]; then
    rm -f migrate_to_railway.py
    echo "   ✅ Removed migrate_to_railway.py"
fi

# Step 4: Remove Python cache
echo "🧹 Step 4: Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo "   ✅ Cleaned Python cache"

# Step 5: Create logs directory
echo "📁 Step 5: Creating logs directory..."
mkdir -p logs
echo "   ✅ Created logs directory"

echo ""
echo "✅ Migration reset completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update your model files with the fixed versions"
echo "2. Run: python manage.py makemigrations"
echo "3. Run: python manage.py migrate"
echo "4. Run: python manage.py createsuperuser"
echo "5. Run: python manage.py create_sample_data"
echo ""
echo "🚀 You're ready to start fresh!"