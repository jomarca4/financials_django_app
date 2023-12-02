from django import forms
from .models import WatchedStock,AssetHolding
from django_select2.forms import Select2Widget

class WatchedStockForm(forms.ModelForm):
    class Meta:
        model = WatchedStock
        fields = ['company', 'price_target', 'notes','current_price']
        widgets = {
            'company': Select2Widget
        }


#to add assets to a portfolio
class AssetHoldingForm(forms.ModelForm):
    ticker_symbol = forms.CharField(max_length=10)  # Adjust max_length as needed

    class Meta:
        model = AssetHolding
        fields = ['ticker_symbol', 'quantity', 'purchase_price']

    def clean_ticker_symbol(self):
        ticker_symbol = self.cleaned_data.get('ticker_symbol')
        # Logic to validate or transform the ticker symbol if needed
        return ticker_symbol