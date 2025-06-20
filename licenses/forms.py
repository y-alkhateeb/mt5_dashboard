from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, Div, HTML
from crispy_forms.bootstrap import FormActions
from .models import License

class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = [
            'account_id', 'account_hash', 'account_trade_mode',
            'broker_server', 'expires_at', 'is_active'
        ]
        widgets = {
            'account_hash': forms.PasswordInput(attrs={
                'placeholder': 'Enter account hash for security'
            }),
            'expires_at': AdminDateWidget(),
            'broker_server': forms.TextInput(attrs={
                'placeholder': 'e.g., broker.example.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'License Information',
                Row(
                    Column('account_id', css_class='form-group col-md-6 mb-3'),
                    Column('account_trade_mode', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('account_hash', css_class='form-group col-md-8 mb-3'),
                    Column('is_active', css_class='form-group col-md-4 mb-3'),
                ),
                Row(
                    Column('broker_server', css_class='form-group col-md-6 mb-3'),
                    Column('expires_at', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            FormActions(
                Submit('submit', 'Save License', css_class='btn btn-primary'),
                HTML('<a href="{% url "admin:licenses_license_changelist" %}" class="btn btn-secondary">Cancel</a>')
            )
        )
        
        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'is_active':
                field.widget.attrs.update({'class': 'form-check-input'})