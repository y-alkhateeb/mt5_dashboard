from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div, Tab, TabHolder
from crispy_forms.bootstrap import FormActions
from .models import TradingConfiguration

class TradingConfigurationForm(forms.ModelForm):
    class Meta:
        model = TradingConfiguration
        exclude = ['license', 'created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Symbol & Session',
                    Fieldset(
                        'Symbol Validation',
                        Row(
                            Column('allowed_symbol', css_class='form-group col-md-8 mb-3'),
                            Column('strict_symbol_check', css_class='form-group col-md-4 mb-3'),
                        ),
                        css_class='border p-3 mb-4 rounded'
                    ),
                    Fieldset(
                        'Session Configuration',
                        Row(
                            Column('inp_session_start', css_class='form-group col-md-6 mb-3'),
                            Column('inp_session_end', css_class='form-group col-md-6 mb-3'),
                        ),
                        css_class='border p-3 mb-4 rounded'
                    ),
                ),
                Tab('Fibonacci Levels',
                    Fieldset(
                        'Primary Fibonacci Levels',
                        Row(
                            Column('inp_fib_level_1_1', css_class='form-group col-md-4 mb-3'),
                            Column('inp_fib_level_1_05', css_class='form-group col-md-4 mb-3'),
                            Column('inp_fib_level_1_0', css_class='form-group col-md-4 mb-3'),
                        ),
                        css_class='border p-3 mb-4 rounded'
                    ),
                    Fieldset(
                        'Stop Loss Levels',
                        Row(
                            Column('inp_fib_level_primary_buy_sl', css_class='form-group col-md-6 mb-3'),
                            Column('inp_fib_level_primary_sell_sl', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('inp_fib_level_hedge_buy_sl', css_class='form-group col-md-6 mb-3'),
                            Column('inp_fib_level_hedge_sell_sl', css_class='form-group col-md-6 mb-3'),
                        ),
                        css_class='border p-3 mb-4 rounded'
                    ),
                    Fieldset(
                        'Hedge & Take Profit Levels',
                        Row(
                            Column('inp_fib_level_hedge_buy', css_class='form-group col-md-6 mb-3'),
                            Column('inp_fib_level_hedge_sell', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('inp_fib_level_hedge_buy_tp', css_class='form-group col-md-6 mb-3'),
                            Column('inp_fib_level_hedge_sell_tp', css_class='form-group col-md-6 mb-3'),
                        ),
                        css_class='border p-3 mb-4 rounded'
                    ),
                ),
                Tab('Timeouts',
                    Fieldset(
                        'Timeout Configuration (Minutes)',
                        Row(
                            Column('inp_primary_pending_timeout', css_class='form-group col-md-6 mb-3'),
                            Column('inp_primary_position_timeout', css_class='form-group col-md-6 mb-3'),
                        ),
                        Row(
                            Column('inp_hedging_pending_timeout', css_class='form-group col-md-6 mb-3'),
                            Column('inp_hedging_position_timeout', css_class='form-group col-md-6 mb-3'),
                        ),
                        css_class='border p-3 mb-4 rounded'
                    ),
                ),
            ),
            FormActions(
                Submit('submit', 'Save Configuration', css_class='btn btn-primary'),
                HTML('<a href="javascript:history.back()" class="btn btn-secondary">Cancel</a>')
            )
        )