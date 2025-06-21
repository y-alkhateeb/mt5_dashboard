#!/bin/bash
# File: prepare_railway_deployment.sh

set -e  # Exit on any error

echo "🚂 Preparing project for Railway deployment..."
echo "=============================================="

# Step 1: Remove SmarterASP.net specific files
echo "🗑️ Step 1: Removing SmarterASP.net specific files..."

# Files to remove
files_to_remove=(
    "app.py"
    "web.config"
    "prepare_deployment.sh"
    "requirements-smarterasp.txt"
    "trading_admin/settings_smarterasp.py"
    "deployment_exclude.txt"
    ".dockerignore"
    "Dockerfile"
    "docker-compose.yml"
)

for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        echo "   Removing: $file"
        rm -f "$file"
    fi
done

# Remove deployment directory if it exists
if [ -d "deployment" ]; then
    echo "   Removing: deployment/"
    rm -rf deployment/
fi

echo "✅ SmarterASP.net files removed"

# Step 2: Clean development files
echo "🧹 Step 2: Cleaning development files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
rm -f *.log 2>/dev/null || true
rm -f db.sqlite3 2>/dev/null || true
rm -rf staticfiles/ 2>/dev/null || true

echo "✅ Development files cleaned"

# Step 3: Validate Railway files
echo "🔍 Step 3: Validating Railway files..."
required_files=(
    "railway.json"
    "requirements.txt"
    "trading_admin/settings_railway.py"
    "manage.py"
    ".railwayignore"
    "railway_migration_data.json"
    "migrate_to_railway.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required Railway files:"
    printf '%s\n' "${missing_files[@]}"
    echo ""
    echo "Please ensure all Railway files are present!"
    exit 1
fi

echo "✅ All Railway files present"

# Step 4: Update .gitignore for Railway
echo "📝 Step 4: Updating .gitignore for Railway..."
cat >> .gitignore << 'EOF'

# Railway specific
.railway/
railway.toml

# SmarterASP.net files (removed)
app.py
web.config
prepare_deployment.sh
requirements-smarterasp.txt
trading_admin/settings_smarterasp.py
web.config.backup
EOF

echo "✅ .gitignore updated"

# Step 5: Create Railway deployment checklist
echo "📋 Step 5: Creating deployment checklist..."
cat > RAILWAY_DEPLOYMENT.md << 'EOF'
# Railway Deployment Checklist

## Pre-deployment Steps
- [x] Remove SmarterASP.net files
- [x] Update settings for Railway
- [x] Configure railway.json
- [x] Update requirements.txt
- [x] Clean development files

## Railway Setup Steps
1. **Connect Repository**
   - Link your GitHub repository to Railway
   
2. **Environment Variables**
   Set these in Railway dashboard:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-railway-domain.up.railway.app
   ```

3. **Database Migration**
   After first deployment, run:
   ```bash
   railway run python migrate_to_railway.py
   ```

4. **Create Superuser**
   ```bash
   railway run python manage.py createsuperuser
   ```

## Files Structure (Railway Ready)
```
trading_admin/
├── core/
├── licenses/
├── configurations/
├── trading_admin/
│   ├── settings.py          # Base settings
│   ├── settings_railway.py  # Railway production settings
│   ├── urls.py
│   └── wsgi.py
├── manage.py                # Updated for Railway
├── requirements.txt         # Railway dependencies
├── railway.json            # Railway configuration
├── .railwayignore          # Deployment exclusions
├── railway_migration_data.json
├── migrate_to_railway.py
└── README.md
```

## Post-deployment
- Access admin at: https://your-app.up.railway.app/admin/
- Test API endpoints
- Verify license management functionality
EOF

echo "✅ Deployment checklist created"

# Step 6: Show summary
echo ""
echo "🎉 Railway deployment preparation completed!"
echo "============================================="
echo ""
echo "📁 Files removed:"
echo "   - app.py (SmarterASP.net WSGI)"
echo "   - web.config (IIS configuration)"
echo "   - prepare_deployment.sh (old deployment script)"
echo "   - requirements-smarterasp.txt (SmarterASP.net deps)"
echo "   - settings_smarterasp.py (SmarterASP.net settings)"
echo ""
echo "📁 Files updated/ready:"
echo "   ✅ railway.json (with start command)"
echo "   ✅ requirements.txt (Railway dependencies)"
echo "   ✅ settings_railway.py (fixed Railway settings)"
echo "   ✅ manage.py (defaults to Railway settings)"
echo "   ✅ .railwayignore (deployment exclusions)"
echo ""
echo "📋 Next steps:"
echo "1. Review RAILWAY_DEPLOYMENT.md"
echo "2. Push changes to your repository"
echo "3. Connect repository to Railway"
echo "4. Set environment variables in Railway"
echo "5. Deploy and run migration script"
echo ""
echo "🚂 Ready for Railway deployment!"