from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def setup_admin(request):
    """
    One-time setup endpoint to create admin user
    Should be removed after first use for security
    """
    try:
        # Check if admin already exists
        if User.objects.filter(username='admin').exists():
            return JsonResponse({
                'success': False,
                'message': 'Admin user already exists',
                'action': 'Login at /admin/ with existing credentials'
            })
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Admin user created successfully!',
            'credentials': {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@example.com'
            },
            'login_url': '/admin/',
            'warning': 'Please change the password after first login!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating admin user: {str(e)}'
        })

@require_http_methods(["GET"])  
def setup_status(request):
    """Check if admin user exists"""
    admin_exists = User.objects.filter(username='admin').exists()
    user_count = User.objects.count()
    
    return JsonResponse({
        'admin_exists': admin_exists,
        'total_users': user_count,
        'setup_needed': not admin_exists,
        'setup_url': '/setup/admin/' if not admin_exists else None
    })
