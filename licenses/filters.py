import django_filters
from .models import License

class LicenseFilter(django_filters.FilterSet):
    account_id = django_filters.CharFilter(lookup_expr='icontains')
    broker_server = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    account_trade_mode = django_filters.ChoiceFilter(choices=License.ACCOUNT_TRADE_MODES)
    expires_at = django_filters.DateFromToRangeFilter()
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = License
        fields = ['account_id', 'broker_server', 'is_active', 'account_trade_mode']