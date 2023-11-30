from django import forms
from .models import WatchedStock
from django_select2.forms import Select2Widget

class WatchedStockForm(forms.ModelForm):
    class Meta:
        model = WatchedStock
        fields = ['company', 'price_target', 'notes','current_price']
        widgets = {
            'company': Select2Widget
        }