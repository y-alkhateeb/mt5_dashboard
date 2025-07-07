# File: configurations/forms.py
# Simplified form without Fibonacci and Session configuration

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML
from crispy_forms.bootstrap import FormActions
from .models import TradingConfiguration

class TradingConfigurationForm(forms.ModelForm):
    """
    Simplified form for Trading Configuration - Symbol and Timeouts only
    """
    
    class Meta:
        model = TradingConfiguration
        exclude = ['created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field widgets
        self.fields['allowed_symbol'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g., US30, EURUSD, XAUUSD'
        })
        
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description of this trading configuration...'
        })
        
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '📝 Configuration Details',
                Row(
                    Column('name', css_class='form-group col-md-8 mb-3'),
                    Column('is_active', css_class='form-group col-md-4 mb-3'),
                ),
                'description',
                css_class='border p-3 mb-4 rounded bg-light'
            ),
            
            Fieldset(
                '🎯 Symbol Configuration',
                Row(
                    Column('allowed_symbol', css_class='form-group col-md-8 mb-3'),
                    Column('strict_symbol_check', css_class='form-group col-md-4 mb-3'),
                ),
                HTML('<small class="text-muted">Configure which symbols the robot can trade</small>'),
                css_class='border p-3 mb-4 rounded bg-primary-light'
            ),
        
            
            FormActions(
                Submit('submit', '💾 Save Configuration', css_class='btn btn-primary btn-lg'),
                HTML('<a href="javascript:history.back()" class="btn btn-secondary btn-lg ms-2">↩️ Cancel</a>')
            )
        )