# File: configurations/forms.py

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div, Tab, TabHolder
from crispy_forms.bootstrap import FormActions
from .models import TradingConfiguration

class TradingConfigurationForm(forms.ModelForm):
    """
    Enhanced form for Trading Configuration with MT5-specific field layout
    """
    
    class Meta:
        model = TradingConfiguration
        exclude = ['license', 'created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field widgets and help text
        self.fields['inp_AllowedSymbol'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g., US30, EURUSD, XAUUSD'
        })
        
        self.fields['inp_SessionStart'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'HH:MM (e.g., 08:45)'
        })
        
        self.fields['inp_SessionEnd'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'HH:MM (e.g., 10:00)'
        })
        
        # Add step attribute to decimal fields for better UX
        decimal_fields = [
            'inp_FibLevel_1_1', 'inp_FibLevel_1_05', 'inp_FibLevel_1_0',
            'inp_FibLevel_PrimaryBuySL', 'inp_FibLevel_PrimarySellSL',
            'inp_FibLevel_HedgeBuy', 'inp_FibLevel_HedgeSell',
            'inp_FibLevel_HedgeBuySL', 'inp_FibLevel_HedgeSellSL',
            'inp_FibLevel_0_0', 'inp_FibLevel_Neg_05', 'inp_FibLevel_Neg_1',
            'inp_FibLevel_HedgeBuyTP', 'inp_FibLevel_HedgeSellTP'
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
                            Column('inp_AllowedSymbol', css_class='form-group col-md-8 mb-3'),
                            Column('inp_StrictSymbolCheck', css_class='form-group col-md-4 mb-3'),
                        ),
                        HTML('<small class="text-muted">Configure which symbols the robot can trade</small>'),
                        css_class='border p-3 mb-4 rounded bg-light'
                    ),
                    Fieldset(
                        '═══ Session Configuration ═══',
                        Row(
                            Column('inp_SessionStart', css_class='form-group col-md-6 mb-3'),
                            Column('inp_SessionEnd', css_class='form-group col-md-6 mb-3'),
                        ),
                        HTML('<small class="text-muted">Set trading session times in HH:MM format</small>'),
                        css_class='border p-3 mb-4 rounded bg-light'
                    ),
                ),
                
                Tab('📐 Fibonacci Levels',
                    Fieldset(
                        '═══ Primary Fibonacci Levels ═══',
                        Row(
                            Column('inp_FibLevel_1_1', css_class='form-group col-md-4 mb-3'),
                            Column('inp_FibLevel_1_05', css_class='form-group col-md-4 mb-3'),
                            Column('inp_FibLevel_1_0', css_class='form-group col-md-4 mb-3'),
                        ),
                        HTML('<small class="text-muted">Main Fibonacci retracement levels</small>'),
                        css_class='border p-3 mb-4 rounded bg-light'
                    ),
                    
                    Fieldset(
                        '═══ Stop Loss Levels ═══',
                        Row(
                            Column('inp_FibLevel_PrimaryBuySL', css_class='form-group col-md-6 mb-3'),
                            Column('inp_FibLevel_PrimarySellSL', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('inp_FibLevel_HedgeBuySL', css_class='form-group col-md-6 mb-3'),
                            Column('inp_FibLevel_HedgeSellSL', css_class='form-group col-md-6 mb-3'),
                        ),
                        HTML('<small class="text-muted">Configure stop loss levels for risk management</small>'),
                        css_class='border p-3 mb-4 rounded bg-warning-light'
                    ),
                    
                    Fieldset(
                        '═══ Additional Levels ═══',
                        Row(
                            Column('inp_FibLevel_0_0', css_class='form-group col-md-4 mb-3'),
                            Column('inp_FibLevel_Neg_05', css_class='form-group col-md-4 mb-3'),
                            Column('inp_FibLevel_Neg_1', css_class='form-group col-md-4 mb-3'),
                        ),
                        Row(
                            Column('inp_FibLevel_HedgeBuy', css_class='form-group col-md-6 mb-3'),
                            Column('inp_FibLevel_HedgeSell', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('inp_FibLevel_HedgeBuyTP', css_class='form-group col-md-6 mb-3'),
                            Column('inp_FibLevel_HedgeSellTP', css_class='form-group col-md-6 mb-3'),
                        ),
                        HTML('<small class="text-muted">Hedging and take profit levels</small>'),
                        css_class='border p-3 mb-4 rounded bg-success-light'
                    ),
                ),
                
                Tab('⏱️ Timeouts',
                    Fieldset(
                        '═══ Timeout Configuration (Minutes) ═══',
                        Row(
                            Column('inp_PrimaryPendingTimeout', css_class='form-group col-md-6 mb-3'),
                            Column('inp_PrimaryPositionTimeout', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('inp_HedgingPendingTimeout', css_class='form-group col-md-6 mb-3'),
                            Column('inp_HedgingPositionTimeout', css_class='form-group col-md-6 mb-3'),
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
        
    def clean_inp_SessionStart(self):
        """Validate session start time format"""
        value = self.cleaned_data['inp_SessionStart']
        if not self._is_valid_time_format(value):
            raise forms.ValidationError('Please enter time in HH:MM format (e.g., 08:45)')
        return value
    
    def clean_inp_SessionEnd(self):
        """Validate session end time format"""
        value = self.cleaned_data['inp_SessionEnd']
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