# File: configurations/forms.py
# Fixed for PostgreSQL field names

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div, Tab, TabHolder
from crispy_forms.bootstrap import FormActions
from .models import TradingConfiguration

class TradingConfigurationForm(forms.ModelForm):
    """
    Enhanced form for Trading Configuration with MT5-specific field layout
    Updated for PostgreSQL compatibility
    """
    
    class Meta:
        model = TradingConfiguration
        exclude = ['created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field widgets and help text
        self.fields['allowed_symbol'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g., US30, EURUSD, XAUUSD'
        })
        
        self.fields['session_start'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'HH:MM (e.g., 08:45)'
        })
        
        self.fields['session_end'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'HH:MM (e.g., 10:00)'
        })
        
        # Add step attribute to decimal fields for better UX
        decimal_fields = [
            'fib_primary_buy_tp', 'fib_primary_buy_entry', 'fib_session_high',
            'fib_primary_buy_sl', 'fib_primary_sell_sl',
            'fib_level_hedge_buy', 'fib_level_hedge_sell',
            'fib_level_hedge_buy_sl', 'fib_level_hedge_sell_sl',
            'fib_session_low', 'fib_primary_sell_entry', 'fib_primary_sell_tp',
            'fib_hedge_buy_tp', 'fib_hedge_sell_tp'
        ]
        
        for field_name in decimal_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control',
                    'step': '0.00001'
                })
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('🎯 Symbol & Session',
                    Fieldset(
                        '═══ Symbol Validation ═══',
                        Row(
                            Column('allowed_symbol', css_class='form-group col-md-8 mb-3'),
                            Column('strict_symbol_check', css_class='form-group col-md-4 mb-3'),
                        ),
                        HTML('<small class="text-muted">Configure which symbols the robot can trade</small>'),
                        css_class='border p-3 mb-4 rounded bg-light'
                    ),
                    Fieldset(
                        '═══ Session Configuration ═══',
                        Row(
                            Column('session_start', css_class='form-group col-md-6 mb-3'),
                            Column('session_end', css_class='form-group col-md-6 mb-3'),
                        ),
                        HTML('<small class="text-muted">Set trading session times in HH:MM format</small>'),
                        css_class='border p-3 mb-4 rounded bg-light'
                    ),
                ),

                Tab('📐 Trade Levels',
                    Fieldset(
                        '═══ Primary Buy Entry / TP / SL ═══',
                        Row(
                            Column('fib_primary_buy_entry', css_class='form-group col-md-4 mb-3'),
                            Column('fib_primary_buy_tp', css_class='form-group col-md-4 mb-3'),
                            Column('fib_primary_buy_sl', css_class='form-group col-md-4 mb-3'),
                        ),
                        HTML('<small class="text-muted">Configure buy levels for primary trades</small>'),
                        css_class='border p-3 mb-4 rounded bg-primary-light'
                    ),

                    Fieldset(
                        '═══ Primary Sell Entry / TP / SL ═══',
                        Row(
                            Column('fib_primary_sell_entry', css_class='form-group col-md-4 mb-3'),
                            Column('fib_primary_sell_tp', css_class='form-group col-md-4 mb-3'),
                            Column('fib_primary_sell_sl', css_class='form-group col-md-4 mb-3'),
                        ),
                        HTML('<small class="text-muted">Configure sell levels for primary trades</small>'),
                        css_class='border p-3 mb-4 rounded bg-danger-light'
                    ),

                    Fieldset(
                        '═══ Hedging Configuration ═══',
                        Row(
                            Column('fib_level_hedge_buy', css_class='form-group col-md-6 mb-3'),
                            Column('fib_level_hedge_sell', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('fib_hedge_buy_tp', css_class='form-group col-md-6 mb-3'),
                            Column('fib_hedge_sell_tp', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('fib_level_hedge_buy_sl', css_class='form-group col-md-6 mb-3'),
                            Column('fib_level_hedge_sell_sl', css_class='form-group col-md-6 mb-3'),
                        ),
                        HTML('<small class="text-muted">Hedging entry, SL, and TP levels</small>'),
                        css_class='border p-3 mb-4 rounded bg-success-light'
                    ),

                    Fieldset(
                        '═══ Additional Session Levels ═══',
                        Row(
                            Column('fib_session_high', css_class='form-group col-md-6 mb-3'),
                            Column('fib_session_low', css_class='form-group col-md-6 mb-3'),
                        ),
                        HTML('<small class="text-muted">High and low session-based levels</small>'),
                        css_class='border p-3 mb-4 rounded bg-light'
                    ),
                ),

                Tab('⏱️ Timeouts',
                    Fieldset(
                        '═══ Timeout Configuration (Minutes) ═══',
                        Row(
                            Column('primary_pending_timeout', css_class='form-group col-md-6 mb-3'),
                            Column('primary_position_timeout', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('hedging_pending_timeout', css_class='form-group col-md-6 mb-3'),
                            Column('hedging_position_timeout', css_class='form-group col-md-6 mb-3'),
                        ),
                        HTML('''
                            <div class="alert alert-info mt-3">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>Timeout Guidelines:</strong>
                                <ul class="mb-0">
                                    <li>Primary Pending: Time to wait for order execution</li>
                                    <li>Primary Position: Time to hold primary positions</li>
                                    <li>Hedging Pending: Time to wait for hedge order execution</li>
                                    <li>Hedging Position: Time to hold hedging positions</li>
                                </ul>
                            </div>
                        '''),
                        css_class='border p-3 mb-4 rounded bg-info-light'
                    ),
                ),
            ),
            
            FormActions(
                Submit('submit', '💾 Save Configuration', css_class='btn btn-primary btn-lg'),
                HTML('<a href="javascript:history.back()" class="btn btn-secondary btn-lg ms-2">↩️ Cancel</a>')
            )
        )
        
    def clean_session_start(self):
        """Validate session start time format"""
        value = self.cleaned_data['session_start']
        if not self._is_valid_time_format(value):
            raise forms.ValidationError('Please enter time in HH:MM format (e.g., 08:45)')
        return value
    
    def clean_session_end(self):
        """Validate session end time format"""
        value = self.cleaned_data['session_end']
        if not self._is_valid_time_format(value):
            raise forms.ValidationError('Please enter time in HH:MM format (e.g., 17:30)')
        return value
    
    def _is_valid_time_format(self, time_str):
        """Check if time string is in HH:MM format"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False