from django.urls import path
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
