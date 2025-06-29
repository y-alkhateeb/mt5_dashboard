from django.core.management.base import BaseCommand
from configurations.models import TradingConfiguration

class Command(BaseCommand):
    help = 'Create default trading configurations'
    
    def handle(self, *args, **options):
        # Create default configurations
        configs = [
            {
                'name': 'US30 Standard',
                'description': 'Standard US30 trading configuration',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '08:45',
                'inp_SessionEnd': '10:00',
            },
            {
                'name': 'EURUSD Conservative',
                'description': 'Conservative EURUSD trading configuration',
                'inp_AllowedSymbol': 'EURUSD',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '09:00',
                'inp_SessionEnd': '17:00',
                'inp_FibLevel_1_05': 1.02,  # More conservative
                'inp_FibLevel_Neg_05': -0.02,
            },
            {
                'name': 'XAUUSD Aggressive',
                'description': 'Aggressive Gold trading configuration',
                'inp_AllowedSymbol': 'XAUUSD',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '07:00',
                'inp_SessionEnd': '16:00',
                'inp_FibLevel_1_05': 1.08,  # More aggressive
                'inp_FibLevel_Neg_05': -0.08,
            }
        ]
        
        for config_data in configs:
            config, created = TradingConfiguration.objects.get_or_create(
                name=config_data['name'],
                defaults=config_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created configuration: {config.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Configuration already exists: {config.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Total configurations: {TradingConfiguration.objects.count()}')
        )
