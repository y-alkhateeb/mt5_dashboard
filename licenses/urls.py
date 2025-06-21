# File: licenses/urls.py

from django.urls import path
from .views import BotValidationAPIView

urlpatterns = [
    # Only validation endpoint for trading robots
    path('validate/', BotValidationAPIView.as_view(), name='bot-validate'),
]

# Available endpoint:
# POST /api/validate/ - Bot license validation (public)