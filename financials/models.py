from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

from django.utils import timezone
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
    date = models.DateField(db_index=True)
    open_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    close_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    high_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    low_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    market_cap = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    dividend_amount = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)

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



class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    total_value = models.FloatField(default=0)
    creation_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'portfolio'
        indexes = [
            models.Index(fields=['user'], name='idx_portfolio_user'),
        ]

class AssetHolding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    market_data = models.ForeignKey(market_data, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_price = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'asset_holdings'
        indexes = [
            models.Index(fields=['portfolio'], name='idx_asset_holdings_portfolio'),
            models.Index(fields=['market_data'], name='idx_asset_holdings_market_data'),
        ]

#BLOG


class Section(models.Model):
    title = models.CharField(max_length=200)
    parent_section = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subsections')

    def __str__(self):
        return self.title

    @property
    def is_subsection(self):
        return self.parent_section is not None

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()  # instead of models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
    first_paragraph = models.TextField(help_text="Enter the first paragraph of the post", default="Default text")
    img_url = models.URLField(max_length=1024, blank=True, null=True, help_text="URL of the image hosted on a third-party service")


    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
