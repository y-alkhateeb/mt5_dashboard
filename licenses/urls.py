from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BotValidationAPIView, LicenseViewSet, ClientViewSet

# Router for admin API endpoints
router = DefaultRouter()
router.register(r'licenses', LicenseViewSet)
router.register(r'clients', ClientViewSet)

urlpatterns = [
    # Bot validation endpoint (public)
    path('validate/', BotValidationAPIView.as_view(), name='bot-validate'),
    
    # Admin API endpoints (authenticated)
    path('admin/', include(router.urls)),
]