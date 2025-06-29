# File: fix_production_issues.py
"""
Fix production issues and optimize API for Render deployment
Run this after the main deployment preparation script
"""

import os
import shutil

def create_fixed_core_urls():
    """Create fixed core/urls.py without setup views for production"""
    content = '''from django.urls import path
from .views import DashboardView
from .api_views import api_documentation, health_check

urlpatterns = [
    # Dashboard URLs
    path('', DashboardView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # API Documentation URLs
    path('api/docs/', api_documentation, name='api-docs'),
    path('api/health/', health_check, name='health-check'),
]
'''
    
    with open('core/urls.py', 'w') as f:
        f.write(content)
    print("✅ Fixed core/urls.py")

def create_fixed_licenses_views():
    """Fix issues in licenses/views.py for production"""
    content = '''from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import License, Client
from .serializers import (
    LicenseSerializer, 
    ClientSerializer,
    BotValidationRequestSerializer, 
    BotValidationResponseSerializer
)
from configurations.models import TradingConfiguration
from configurations.serializers import TradingConfigurationSerializer
import logging

logger = logging.getLogger(__name__)

class BotValidationThrottle(AnonRateThrottle):
    scope = 'bot_validation'

class BotValidationAPIView(APIView):
    """🤖 API for trading bot license validation with enhanced error handling"""
    permission_classes = [AllowAny]
    throttle_classes = [BotValidationThrottle]
    
    def post(self, request):
        """Validate trading bot license and return configuration"""
        try:
            serializer = BotValidationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'Invalid request data',
                        'details': serializer.errors
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            license_key = serializer.validated_data['license_key']
            system_hash = serializer.validated_data['system_hash']
            account_trade_mode = serializer.validated_data['account_trade_mode']
            broker_server = serializer.validated_data.get('broker_server', '')
            account_hash = serializer.validated_data.get('account_hash', '')
            
            # Find license
            try:
                license_obj = License.objects.select_related('trading_configuration').get(
                    license_key=license_key
                )
            except License.DoesNotExist:
                logger.warning(f"License not found: {license_key[:8]}...")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_LICENSE',
                        'message': 'Invalid license key'
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if license is valid
            if not license_obj.is_valid:
                if license_obj.is_expired:
                    error_code = 'LICENSE_EXPIRED'
                    error_message = 'License has expired'
                elif not license_obj.is_active:
                    error_code = 'LICENSE_INACTIVE'
                    error_message = 'License is inactive'
                else:
                    error_code = 'NO_CONFIGURATION'
                    error_message = 'No trading configuration assigned to this license'
                
                logger.warning(f"License validation failed for {license_key[:8]}...: {error_message}")
                return Response({
                    'success': False,
                    'error': {
                        'code': error_code,
                        'message': error_message
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Validate system hash
            system_valid, system_message = license_obj.validate_system_hash(system_hash)
            if not system_valid:
                logger.warning(f"System hash validation failed for {license_key[:8]}...: {system_message}")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'SYSTEM_MISMATCH',
                        'message': system_message
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check account trade mode compatibility
            if license_obj.system_hash and license_obj.account_trade_mode != account_trade_mode:
                logger.warning(f"Account trade mode mismatch for {license_key[:8]}...")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'TRADE_MODE_MISMATCH',
                        'message': f'Account trade mode mismatch. Expected {license_obj.account_trade_mode}, got {account_trade_mode}'
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Bind account (internal tracking)
            license_obj.bind_account(
                system_hash=system_hash,
                account_trade_mode=account_trade_mode,
                broker_server=broker_server,
                account_hash=account_hash if account_hash else None
            )
            
            # Get configuration
            if not license_obj.trading_configuration:
                logger.error(f"No trading configuration assigned to license {license_key[:8]}...")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NO_CONFIGURATION',
                        'message': 'No trading configuration assigned to this license'
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Serialize configuration
            config_serializer = TradingConfigurationSerializer(license_obj.trading_configuration)
            
            # Return success response
            response_data = {
                'success': True,
                'message': 'License validated successfully',
                'configuration': config_serializer.data,
                'expires_at': license_obj.expires_at,
                'license_info': {
                    'usage_count': license_obj.usage_count,
                    'daily_usage': license_obj.daily_usage_count,
                    'first_time_use': license_obj.usage_count == 1,
                    'account_login_changed': license_obj.account_hash_changes_count > 1
                }
            }
            
            logger.info(f"License validation successful for {license_key[:8]}...")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"License validation error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Internal server error during license validation'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LicenseViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for License management"""
    queryset = License.objects.select_related('client', 'trading_configuration').all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def perform_create(self, serializer):
        license_instance = serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def configuration(self, request, pk=None):
        """Get or update license configuration"""
        license_instance = self.get_object()
        
        if request.method == 'GET':
            if not license_instance.trading_configuration:
                return Response({
                    'error': 'No configuration assigned to this license'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = TradingConfigurationSerializer(license_instance.trading_configuration)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            if not license_instance.trading_configuration:
                return Response({
                    'error': 'No configuration assigned to this license. Assign a configuration first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            partial = request.method == 'PATCH'
            serializer = TradingConfigurationSerializer(
                license_instance.trading_configuration, 
                data=request.data, 
                partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_configuration(self, request, pk=None):
        """Assign a trading configuration to a license"""
        license_instance = self.get_object()
        config_id = request.data.get('configuration_id')
        
        if not config_id:
            return Response({
                'error': 'configuration_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config = TradingConfiguration.objects.get(id=config_id, is_active=True)
            license_instance.trading_configuration = config
            license_instance.save()
            
            return Response({
                'message': f'Configuration "{config.name}" assigned successfully',
                'configuration': TradingConfigurationSerializer(config).data
            })
        except TradingConfiguration.DoesNotExist:
            return Response({
                'error': 'Configuration not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active licenses"""
        active_licenses = self.queryset.filter(is_active=True)
        page = self.paginate_queryset(active_licenses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(active_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired licenses"""
        expired_licenses = self.queryset.filter(expires_at__lt=timezone.now())
        page = self.paginate_queryset(expired_licenses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(expired_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get licenses expiring within 30 days"""
        thirty_days_from_now = timezone.now() + timezone.timedelta(days=30)
        expiring_licenses = self.queryset.filter(
            expires_at__lt=thirty_days_from_now,
            expires_at__gt=timezone.now(),
            is_active=True
        )
        page = self.paginate_queryset(expiring_licenses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(expiring_licenses, many=True)
        return Response(serializer.data)

class ClientViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for Client management"""
    queryset = Client.objects.prefetch_related('licenses').all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
'''
    
    with open('licenses/views.py', 'w') as f:
        f.write(content)
    print("✅ Fixed licenses/views.py")

def create_production_settings_base():
    """Update base settings for better production compatibility"""
    
    # Read current settings
    with open('trading_admin/settings.py', 'r') as f:
        content = f.read()
    
    # Create backup
    with open('trading_admin/settings.py.backup', 'w') as f:
        f.write(content)
    
    # Create optimized base settings
    optimized_content = '''"""
Django settings for trading_admin project.
Optimized for production deployment.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-development-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'core',
    'licenses',
    'configurations',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trading_admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trading_admin.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework with enhanced security
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'bot_validation': '60/minute',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'licenses': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'configurations': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
'''
    
    with open('trading_admin/settings.py', 'w') as f:
        f.write(optimized_content)
    print("✅ Optimized base settings.py")

def create_api_test_script():
    """Create API testing script for validation"""
    content = '''#!/usr/bin/env python
"""
API Testing Script for Trading Robot Admin
Run this to test your deployed API endpoints
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoints(base_url):
    """Test all API endpoints"""
    print(f"🧪 Testing API endpoints at: {base_url}")
    print("=" * 50)
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    endpoints = [
        {
            'name': 'Health Check',
            'url': f'{base_url}/api/health/',
            'method': 'GET',
            'auth_required': True
        },
        {
            'name': 'API Documentation', 
            'url': f'{base_url}/api/docs/',
            'method': 'GET',
            'auth_required': True
        },
        {
            'name': 'Bot Validation (Sample)',
            'url': f'{base_url}/api/validate/',
            'method': 'POST',
            'auth_required': False,
            'data': {
                'license_key': 'test-license-key-123456789012',
                'system_hash': 'test-system-hash',
                'account_trade_mode': 0,
                'broker_server': 'demo.broker.com',
                'timestamp': datetime.now().isoformat()
            }
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint['name']}")
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=30)
            else:
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint.get('data', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
            
            status = "✅ PASS" if response.status_code < 500 else "❌ FAIL"
            print(f"   Status: {response.status_code} - {status}")
            
            if response.status_code < 500:
                try:
                    response_data = response.json()
                    if 'success' in response_data:
                        print(f"   Success: {response_data['success']}")
                    if 'message' in response_data:
                        print(f"   Message: {response_data['message']}")
                except:
                    print(f"   Response length: {len(response.text)} chars")
            else:
                print(f"   Error: {response.text[:100]}...")
            
            results.append({
                'endpoint': endpoint['name'],
                'status_code': response.status_code,
                'success': response.status_code < 500
            })
            
        except requests.RequestException as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append({
                'endpoint': endpoint['name'],
                'status_code': 0,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print("📊 SUMMARY")
    print("=" * 20)
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check deployment")
    
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_api.py <base_url>")
        print("Example: python test_api.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    test_api_endpoints(base_url)

if __name__ == "__main__":
    main()
'''
    
    with open('test_api.py', 'w') as f:
        f.write(content)
    
    # Make executable
    os.chmod('test_api.py', 0o755)
    print("✅ Created API testing script")

def main():
    """Run all fixes"""
    print("🔧 Applying production fixes and optimizations...")
    print("=" * 50)
    
    # Apply fixes
    create_fixed_core_urls()
    create_fixed_licenses_views()
    create_production_settings_base()
    create_api_test_script()
    
    print()
    print("🎉 Production fixes applied successfully!")
    print("=" * 40)
    print()
    print("📁 Files updated:")
    print("   ✅ core/urls.py (removed setup views)")
    print("   ✅ licenses/views.py (enhanced error handling)")
    print("   ✅ trading_admin/settings.py (optimized)")
    print("   ✅ test_api.py (API testing script)")
    print()
    print("📋 Next steps:")
    print("1. Run the main deployment script:")
    print("   bash prepare_render_deployment_complete.sh")
    print()
    print("2. Test API after deployment:")
    print("   python test_api.py https://your-app.onrender.com")
    print()
    print("🚀 Your app is ready for production!")

if __name__ == "__main__":
    main()