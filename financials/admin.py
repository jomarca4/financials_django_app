from django.contrib import admin

# Register your models here.
from .models import companies, quarters, financial_statements, market_data, financial_statement_items,financial_ratios,analyst_estimates

admin.site.register(companies)
admin.site.register(quarters)
admin.site.register(market_data)
admin.site.register(financial_statements)
admin.site.register(financial_statement_items)
# Register other models similarly