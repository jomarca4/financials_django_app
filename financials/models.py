from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class companies(models.Model):
    name = models.TextField()
    ticker_symbol = models.TextField(unique=True)
    cik = models.IntegerField(unique=True)
    location = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    exchange = models.TextField(null=True)  # Exchange can be null
    industry = models.TextField(null=True)  # Industry can be null

    def __str__(self):
        return self.ticker_symbol
    class Meta:
        db_table = 'companies'



class quarters(models.Model):
    year = models.IntegerField()
    quarter_number = models.IntegerField()
    company = models.ForeignKey(companies, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quarters'

class financial_statements(models.Model):
    STATEMENT_TYPE_CHOICES = [
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
        ('cash_flow', 'Cash Flow'),
        # Add other types as needed
    ]
    type = models.TextField(choices=STATEMENT_TYPE_CHOICES)
    date = models.DateField()
    currency = models.TextField()
    quarter = models.ForeignKey(quarters, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'financial_statements'

class financial_statement_items(models.Model):
    account_label = models.TextField()
    value = models.DecimalField(max_digits=19, decimal_places=4)
    unit_of_measurement = models.TextField()
    financial_statement = models.ForeignKey(financial_statements, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'financial_statement_items'

class financial_ratios(models.Model):
    quarter = models.ForeignKey(quarters, on_delete=models.CASCADE)
    ratio_name = models.TextField()
    ratio_value = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        unique_together = [['quarter', 'ratio_name']]
        db_table = 'financial_ratios'

class market_data(models.Model):
    company = models.ForeignKey(companies, on_delete=models.CASCADE)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    close_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    high_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    low_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    market_cap = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)

    class Meta:
        unique_together = ('company', 'date')
        db_table = 'market_data'

class analyst_estimates(models.Model):
    company = models.ForeignKey(companies, on_delete=models.CASCADE)
    analyst_name = models.TextField()
    estimate_date = models.DateField()
    estimate_type = models.TextField()
    estimate_value = models.DecimalField(max_digits=19, decimal_places=4)
    class Meta:
        db_table = 'analyst_estimates'


class FinancialStatementLabel(models.Model):
    name = models.TextField()
    label = models.TextField()
    depth = models.IntegerField()
    financial_statement_type = models.TextField()
    mapped_label = models.TextField(blank=True, null=True)
    ranking = models.IntegerField(default=0)  # Default to 0 or any other suitable default

    class Meta:
        db_table = 'financial_statement_labels'  # Ensure this matches your existing table name
        ordering = ['ranking']  # This will make items ordered by ranking by default


class WatchedStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(companies, on_delete=models.CASCADE)
    price_target = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watched_stocks'