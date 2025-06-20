from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count
from django.utils import timezone
from licenses.models import License

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # License statistics
        total_licenses = License.objects.count()
        active_licenses = License.objects.filter(is_active=True).count()
        expired_licenses = License.objects.filter(expires_at__lt=timezone.now()).count()
        
        # Recent licenses
        recent_licenses = License.objects.order_by('-created_at')[:5]
        
        # Trade mode distribution
        trade_mode_stats = License.objects.values('account_trade_mode').annotate(
            count=Count('account_trade_mode')
        )
        
        context.update({
            'total_licenses': total_licenses,
            'active_licenses': active_licenses,
            'expired_licenses': expired_licenses,
            'recent_licenses': recent_licenses,
            'trade_mode_stats': list(trade_mode_stats),
        })
        
        return context
