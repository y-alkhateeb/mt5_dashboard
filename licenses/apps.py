from django.apps import AppConfig

class LicensesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'licenses'
    
    def ready(self):
        import licenses.signals  # Import signals when app is ready