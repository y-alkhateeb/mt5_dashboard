from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TradingConfigurationViewSet

router = DefaultRouter()
router.register(r'configurations', TradingConfigurationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
