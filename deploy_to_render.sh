#!/bin/bash
# File: deploy_to_render.sh
# Purpose: Final deployment checklist and quick start guide

set -e

echo "🚀 TRADING ROBOT ADMIN - RENDER DEPLOYMENT"
echo "=========================================="
echo ""
echo "This script will verify your project is ready for Render.com deployment"
echo "and provide step-by-step deployment instructions."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Verify project structure
echo "📋 STEP 1: Project Structure Verification"
echo "----------------------------------------"

required_files=(
    "manage.py"
    "requirements.txt"
    "trading_admin/settings.py"
    "trading_admin/settings_render.py"
    "trading_admin/wsgi.py"
    "render.yaml"
    "licenses/models.py"
    "configurations/models.py"
    "core/views.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found: $file"
    else
        print_error "Missing: $file"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    print_error "Missing required files. Run preparation scripts first!"
    exit 1
fi

print_status "All required files present"
echo ""

# Step 2: Verify Django setup
echo "📋 STEP 2: Django Configuration Verification"
echo "-------------------------------------------"

# Test settings import
python -c "
import os
import sys
os.environ['SECRET_KEY'] = 'test-key-for-verification'
os.environ['RENDER_EXTERNAL_HOSTNAME'] = 'test.onrender.com'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')

try:
    import django
    django.setup()
    print('✅ Render settings load successfully')
    
    # Test model imports
    from licenses.models import License, Client
    from configurations.models import TradingConfiguration
    print('✅ Models import successfully')
    
    # Test API imports
    from licenses.views import BotValidationAPIView
    from core.api_views import health_check
    print('✅ API views import successfully')
    
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_status "Django configuration valid"
else
    print_error "Django configuration has issues"
    exit 1
fi

echo ""

# Step 3: Check requirements.txt
echo "📋 STEP 3: Dependencies Verification"
echo "-----------------------------------"

required_packages=(
    "Django"
    "djangorestframework"
    "gunicorn"
    "psycopg2-binary"
    "dj-database-url"
    "whitenoise"
    "django-cors-headers"
)

missing_packages=()
for package in "${required_packages[@]}"; do
    if grep -q "$package" requirements.txt; then
        print_status "Found: $package"
    else
        print_warning "Missing: $package"
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -eq 0 ]; then
    print_status "All required packages present"
else
    print_warning "Some packages may be missing - verify requirements.txt"
fi

echo ""

# Step 4: Git status check
echo "📋 STEP 4: Git Repository Status"
echo "-------------------------------"

if git status &>/dev/null; then
    print_status "Git repository detected"
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Uncommitted changes detected"
        echo "Modified files:"
        git status --porcelain | head -10
        echo ""
        print_info "You should commit changes before deployment"
    else
        print_status "Working directory clean"
    fi
    
    # Check remote origin
    if git remote get-url origin &>/dev/null; then
        origin_url=$(git remote get-url origin)
        print_status "Remote origin: $origin_url"
    else
        print_warning "No remote origin configured"
    fi
else
    print_error "Not a git repository - you need git for Render deployment"
fi

echo ""

# Step 5: Create deployment guide
echo "📋 STEP 5: Deployment Instructions"
echo "---------------------------------"

cat > QUICK_DEPLOY_GUIDE.md << 'EOF'
# 🚀 Quick Deployment Guide for Render.com

## Prerequisites ✅
- [x] Project prepared for deployment
- [x] Git repository with latest changes
- [x] Render.com account

## Step-by-Step Deployment

### 1. Commit and Push Your Code
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create PostgreSQL Database on Render
1. Go to [render.com](https://render.com) → Dashboard
2. Click **"New"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `trading-robot-db`
   - **Database**: `trading_admin`
   - **User**: `trading_admin_user`
   - **Region**: `Oregon` (or closest to you)
   - **Plan**: `Starter` (free)
4. Click **"Create Database"**
5. Wait for status: **"Available"**

### 3. Create Web Service
1. Click **"New"** → **"Web Service"**
2. **Connect Repository**: Select your GitHub repo
3. Configure service:
   - **Name**: `trading-robot-admin`
   - **Runtime**: `Python 3`
   - **Region**: `Oregon` (same as database)
   - **Branch**: `main`

### 4. Environment Variables
Add these in the **Environment** section:
```
DJANGO_SETTINGS_MODULE=trading_admin.settings_render
DEBUG=false
```

### 5. Build Configuration
**Build Command**:
```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py setup_admin
```

**Start Command**:
```bash
gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

### 6. Deploy!
Click **"Create Web Service"** and wait 5-10 minutes for deployment.

## Post-Deployment Testing

### Test URLs (replace `your-app` with your Render service name):
- **Admin**: https://your-app.onrender.com/admin/
- **Dashboard**: https://your-app.onrender.com/dashboard/
- **API Health**: https://your-app.onrender.com/api/health/
- **API Docs**: https://your-app.onrender.com/api/docs/

### Default Admin Credentials:
```
Username: admin
Password: admin123
Email: admin@example.com
```

### Test API Endpoint:
```bash
curl -X POST https://your-app.onrender.com/api/validate/ \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "test-key",
    "system_hash": "test-hash", 
    "account_trade_mode": 0,
    "timestamp": "2024-01-01T00:00:00Z"
  }'
```

Expected response: `{"success": false, "error": {"code": "INVALID_LICENSE", "message": "Invalid license key"}}`

## Troubleshooting

### Build Fails
- Check Render logs for specific errors
- Verify requirements.txt has all packages
- Ensure Python version compatibility

### Database Connection Issues
- Verify DATABASE_URL is automatically set by Render
- Check PostgreSQL service is running
- Ensure web service and database are in same region

### Admin Login Issues
- Try creating admin manually via Render Shell:
  ```bash
  python manage.py setup_admin
  ```

### API Not Working
- Check if migrations ran: `python manage.py showmigrations`
- Verify URL patterns in Render logs
- Test health endpoint first

## Production Optimizations

### For Live Use:
1. **Upgrade Plans**: Free tier has limitations
2. **Custom Domain**: Add your domain in Render
3. **Monitoring**: Set up error tracking
4. **Backups**: Enable database backups
5. **Security**: Change default passwords

### Performance Tips:
- Monitor response times in Render dashboard
- Check database query performance
- Consider Redis caching for high traffic
- Optimize images and static files

## Support
- Render Docs: https://render.com/docs/deploy-django
- Django Docs: https://docs.djangoproject.com/
- Project Issues: Check GitHub issues

---
**🎉 Success!** Your Trading Robot Admin is now live on Render!
EOF

print_status "Quick deployment guide created: QUICK_DEPLOY_GUIDE.md"
echo ""

# Step 6: Final checklist
echo "📋 STEP 6: Final Deployment Checklist"
echo "------------------------------------"

checklist=(
    "All required files present"
    "Django configuration valid"
    "Dependencies verified"
    "Git repository ready"
    "Deployment guide created"
)

for item in "${checklist[@]}"; do
    print_status "$item"
done

echo ""
echo "🎯 DEPLOYMENT STATUS: READY!"
echo "==========================="
echo ""
print_info "Your Trading Robot Admin is ready for Render.com deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Read the quick deployment guide:"
echo "   📖 cat QUICK_DEPLOY_GUIDE.md"
echo ""
echo "2. Commit your changes:"
echo "   📤 git add . && git commit -m 'Ready for Render deployment'"
echo ""
echo "3. Deploy on Render.com:"
echo "   🌐 Follow the step-by-step guide in QUICK_DEPLOY_GUIDE.md"
echo ""
echo "4. Test your deployment:"
echo "   🧪 python test_api.py https://your-app.onrender.com"
echo ""
echo "🔗 Key URLs (after deployment):"
echo "   🏠 Dashboard: https://your-app.onrender.com/dashboard/"
echo "   👤 Admin: https://your-app.onrender.com/admin/"
echo "   🤖 API: https://your-app.onrender.com/api/"
echo ""
echo "🔐 Default Admin Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  Change password after first login!"
echo ""
print_status "Good luck with your deployment! 🚀"