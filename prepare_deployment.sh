#!/bin/bash
# File: prepare_deployment.sh

set -e  # Exit on any error

echo "🚀 Preparing deployment package for SmarterASP.net..."
echo "=================================================="

# Step 1: Cleanup
echo "🧹 Step 1: Cleaning temporary files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name ".DS_Store" -delete
rm -f *.log
rm -f db.sqlite3
rm -rf staticfiles/
rm -rf deployment/
rm -f *.zip

echo "✅ Cleanup completed"

# Step 2: Validate required files
echo "🔍 Step 2: Validating required files..."
required_files=(
    "trading_admin/settings_smarterasp.py"
    "app.py"
    "web.config"
    "requirements-smarterasp.txt"
    "manage.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files:"
    printf '%s\n' "${missing_files[@]}"
    echo ""
    echo "Please create these files first!"
    echo "See the deployment guide for file contents."
    exit 1
fi

echo "✅ All required files present"

# Step 3: Create deployment directory
echo "📦 Step 3: Creating deployment package..."
mkdir -p deployment

# Step 4: Copy files with exclusions
echo "📋 Copying files (excluding development files)..."
rsync -av \
  --exclude='.git/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='*.pyd' \
  --exclude='venv/' \
  --exclude='env/' \
  --exclude='.env' \
  --exclude='*.log' \
  --exclude='.DS_Store' \
  --exclude='Thumbs.db' \
  --exclude='.vscode/' \
  --exclude='.idea/' \
  --exclude='deployment/' \
  --exclude='db.sqlite3' \
  --exclude='staticfiles/' \
  --exclude='docker-compose.yml' \
  --exclude='Dockerfile' \
  --exclude='nginx*.conf' \
  --exclude='explore_db.py' \
  --exclude='reset.txt' \
  --exclude='*.zip' \
  --exclude='migrations/' \
  ./ deployment/

# Step 5: Create zip file
echo "🗜️ Step 4: Creating zip file..."
cd deployment
zip -r ../trading-robot-admin-smarterasp-$(date +%Y%m%d_%H%M).zip . -q
cd ..

# Step 6: Cleanup deployment folder
rm -rf deployment/

# Step 7: Show results
ZIPFILE="trading-robot-admin-smarterasp-$(date +%Y%m%d_%H%M).zip"
FILESIZE=$(du -h "$ZIPFILE" | cut -f1)

echo ""
echo "🎉 Deployment package ready!"
echo "=============================="
echo "📁 File: $ZIPFILE"
echo "📊 Size: $FILESIZE"
echo ""
echo "📋 Next steps:"
echo "1. Upload this zip to SmarterASP.net File Manager"
echo "2. Extract in your domain folder"
echo "3. Create .env file with database credentials"
echo "4. Run Django migrations"
echo ""
echo "✅ Deployment package creation completed!"