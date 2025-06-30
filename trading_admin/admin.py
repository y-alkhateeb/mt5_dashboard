from django.contrib import admin
from django.contrib.admin import AdminSite

class TradingAdminSite(AdminSite):
    """Custom admin site with customized text"""
    
    # Change the main title
    site_title = 'Trading Bot Administration'
    site_header = 'Administration'  # This changes "Django administration" to "Administration"
    index_title = 'Trading Bot Admin Dashboard'
    
    # Optional: Add custom CSS or additional customization
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'site_url': '/dashboard/',  # Link to your custom dashboard
            'has_permission': True,
            'available_apps': context.get('available_apps', []),

        })
        return context

# Replace the default admin site
admin.site = TradingAdminSite()
admin.site.__class__ = TradingAdminSite

# Alternative simple approach - just modify the existing admin site
admin.site.site_header = 'Administration'
admin.site.site_title = 'Trading Bot Administration'
admin.site.index_title = 'Trading Bot Admin Dashboard'
admin.site.enable_nav_sidebar = True  # Enable the navigation sidebar
