#!/bin/bash
# File: quick_fix_migrations.sh

set -e  # Exit on any error

echo "🔧 Quick Fix for Missing Database Tables"
echo "======================================="

# Step 1: Check current status
echo "📊 Step 1: Checking current database status..."
python diagnostic_check.py 2>/dev/null || echo "Diagnostic script not available, continuing..."

# Step 2: Create migrations for all apps
echo ""
echo "🔨 Step 2: Creating migrations..."

echo "   Creating licenses migrations..."
python manage.py makemigrations licenses --verbosity=2

echo "   Creating configurations migrations..."
python manage.py makemigrations configurations --verbosity=2

echo "   Creating core migrations..."
python manage.py makemigrations core --verbosity=2

# Step 3: Show migration status
echo ""
echo "📋 Step 3: Checking migration status..."
python manage.py showmigrations

# Step 4: Apply migrations
echo ""
echo "🚀 Step 4: Applying migrations..."
python manage.py migrate --verbosity=2

# Step 5: Verify tables exist
echo ""
echo "✅ Step 5: Verifying database tables..."
python manage.py dbshell << 'EOF'
.tables
.quit
EOF

# Step 6: Test admin access
echo ""
echo "🧪 Step 6: Testing admin interface..."
python manage.py check

echo ""
echo "✅ Fix completed! Try accessing the admin interface now."
echo "   📱 Admin URL: http://localhost:8000/admin/"
echo "   🏠 Dashboard URL: http://localhost:8000/dashboard/"