# File: licenses/urls.py

from django.urls import path
from .views import BotValidationAPIView, APIInfoView

urlpatterns = [
    # Main validation endpoint for trading robots
    path('validate/', BotValidationAPIView.as_view(), name='bot-validate'),
    
    # API information
    path('info/', APIInfoView.as_view(), name='api-info'),
]

# Available endpoints:
# POST /api/validate/  - Bot license validation
# GET  /api/info/      - API information