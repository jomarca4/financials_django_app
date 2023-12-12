from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models  # Import models
from django.db.models import Max, Subquery, OuterRef
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
import random
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
import time
from collections import defaultdict
from itertools import groupby
from operator import attrgetter
# Create your views here.
from .models import Post, Section,market_data,Portfolio, AssetHolding,financial_ratios, financial_statement_items, quarters, WatchedStock, companies, FinancialStatementLabel,financial_statements
from .forms import WatchedStockForm, AssetHoldingForm  
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.db.models import Sum
from datetime import datetime       
from django.conf import settings 
import requests       
from datetime import datetime


def home(request):
    # You can add any context data you want to pass to the template here
    return render(request, 'financials/home.html')



def income_statement_view(request, ticker_symbol):
    try:
        company = companies.objects.get(ticker_symbol=ticker_symbol)

        # Fetch the latest three quarters with financial statement data
        latest_three_quarters = quarters.objects.filter(
            company=company,
            financial_statements__type='income_statement'
        ).order_by('-year', '-quarter_number').distinct()[:9]

        context = {'company': company, 'quarters_data': []}

        for quarter in latest_three_quarters:
            financial_statement = financial_statements.objects.get(
                quarter=quarter, 
                type='income_statement'
            )

            # Fetch labels with depth = 100
            depth_labels = FinancialStatementLabel.objects.filter(depth=100)
            label_map = {label.name: label.mapped_label for label in depth_labels}

            # Fetch financial statement items that match the labels
            items = financial_statement_items.objects.filter(
                financial_statement=financial_statement,
                account_label__in=label_map.keys()
            )

            # Sort items by rankings
            label_rankings = {label.name: label.ranking for label in FinancialStatementLabel.objects.all()}
            sorted_items = sorted(items, key=lambda item: label_rankings.get(item.account_label, 0))

            # Prepare data for template
            context['quarters_data'].append({
                'year': quarter.year,
                'quarter_number': quarter.quarter_number,
                'items': [{'item': item, 'mapped_label': label_map.get(item.account_label, '')} for item in sorted_items]
            })
    except (companies.DoesNotExist, quarters.DoesNotExist, financial_statements.DoesNotExist, financial_statement_items.DoesNotExist):
        context = {'items': None, 'company': None}

    return render(request, 'financials/income_statement.html', context)

@login_required
def add_watched_stock(request):
    if request.method == 'POST':
        form = WatchedStockForm(request.POST)
        if form.is_valid():
            watched_stock = form.save(commit=False)
            watched_stock.user = request.user
            watched_stock.save()
            return redirect('watched_stocks_list')  # Redirect to a success page or list view
    else:
        form = WatchedStockForm()

    return render(request, 'financials/add_watched_stock.html', {'form': form})

@login_required
def watched_stocks_list(request):
    watched_stocks = WatchedStock.objects.filter(user=request.user)  # Fetch watched stocks for the logged-in user
    # Your Financial Modeling Prep API Key
    for stock in watched_stocks:
        # API endpoint to get the current stock price
         # Accessing the ticker symbol from the related Company model
        ticker_symbol = stock.company.ticker_symbol
        #print(ticker_symbol)
        url = f'https://financialmodelingprep.com/api/v3/quote/{ticker_symbol}?apikey={settings.FMP_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                # Assuming the response contains a list and we need the first item
                current_price = data[0].get('price')
                stock.current_price = current_price  # Add the current price to the stock object
            else:
                stock.current_price = None  # Handle the case where no data is returned

    return render(request, 'financials/watched_stocks_list.html', {'watched_stocks': watched_stocks})

def edit_watched_stock(request, pk):
    stock = get_object_or_404(WatchedStock, pk=pk, user=request.user)  # Ensure the stock belongs to the user


    # If this is a POST request, process the form data
    if request.method == 'POST':
        form = WatchedStockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('watched_stocks_list')  # Redirect to the list of watched stocks
    else:
        # If this is a GET request, initialize the form with the stock's current data
        form = WatchedStockForm(instance=stock)

    return render(request, 'financials/edit_watched_stock.html', {'form': form})

def delete_watched_stock(request, pk):
    stock = get_object_or_404(WatchedStock, pk=pk, user=request.user)
    if request.method == 'POST':
        stock.delete()
        return redirect('watched_stocks_list')
    else:
            # Show confirmation page or something similar
        return render(request, 'financials/confirm_delete.html', {'stock': stock})
    # Render a confirmation page or handle the deletion directly
    # ...


def financial_ratios_view(request):
    company_id = request.GET.get('company_id')
    ratios = None
    company_list = companies.objects.all().order_by('ticker_symbol')  # Fetch all companies

    if company_id:
        # Fetch ratios and sort them by name and then by quarter
        ratios = financial_ratios.objects.filter(quarter__company_id=company_id).select_related('quarter').order_by('ratio_name', 'quarter__year', 'quarter__quarter_number')

        # Get unique quarters
        unique_quarters = sorted(set((ratio.quarter.year, ratio.quarter.quarter_number) for ratio in ratios), reverse=True)

        # Initialize the structure for template data
        ratios_for_template = defaultdict(lambda: ['N/A'] * len(unique_quarters))

        # Fill the structure with data
        for ratio in ratios:
            quarter_index = unique_quarters.index((ratio.quarter.year, ratio.quarter.quarter_number))
            ratios_for_template[ratio.ratio_name][quarter_index] = ratio.ratio_value

        context = {
            'companies': company_list,
            'ratios_grouped': dict(ratios_for_template),
            'unique_quarters': unique_quarters
        }
    else:
        context = {
            'companies': company_list,
            'ratios_grouped': None,
            'unique_quarters': None
        }

    return render(request, 'financials/financial_ratios.html', context)


class PortfolioListView(LoginRequiredMixin,ListView):
    model = Portfolio
    template_name = 'financials/portfolio_list.html'

    def get_queryset(self):
        # Filter portfolios to show only those belonging to the current user
        return Portfolio.objects.filter(user=self.request.user)

class PortfolioDetailView(LoginRequiredMixin, DetailView):
    model = Portfolio
    template_name = 'financials/portfolio_detail.html'

    def get_current_price_from_api(self, ticker_symbol):
        cache_key = f'current_price_{ticker_symbol}'
        cached_price = cache.get(cache_key)

        if not cached_price:
            response = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker_symbol}?apikey={settings.FMP_KEY}')  # Replace with actual API URL
            if response.status_code == 200:
                current_price = response.json()[0]['price']
                print(current_price)  # Adjust according to API response
                cache.set(cache_key, current_price, 24 * 60 * 60)  # Cache for 24 hours
                return Decimal(current_price)
            else:
                return Decimal('0.0')  # Default value in case of API failure
        else:
            return Decimal(cached_price)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio = self.object
        asset_holdings = portfolio.assetholding_set.all()  # Assuming a related_name 'assetholdings'

        total_stocks = 0
        market_value = Decimal('0.0')
        total_purchase_price = Decimal('0.0')
        current_year = datetime.now().year
        asset_holdings_with_details = []

        for holding in asset_holdings:
            #print(holding.companies.ticker_symbol)
            company_ticker = holding.market_data.company.ticker_symbol
            recent_close = self.get_current_price_from_api(company_ticker)

            # Calculate YTD dividend amount
            ytd_dividends = market_data.objects.filter(
                company_id=holding.market_data.company.id, 
                date__year=current_year
            ).aggregate(Sum('dividend_amount'))['dividend_amount__sum'] or Decimal('0.0')
            ytd_dividend_yield = (ytd_dividends / recent_close) * 100 if recent_close else Decimal('0.0')

            holding_market_value = recent_close * Decimal(holding.quantity)
            holding_purchase_price = Decimal(holding.purchase_price) * Decimal(holding.quantity)
            holding_gain = holding_market_value - holding_purchase_price

            # YTD Market Gain calculations
            start_of_year_data = market_data.objects.filter(
                company_id=holding.market_data.company.id, 
                date__gte=datetime(current_year, 1, 1)
            ).order_by('date').first()
            start_of_year_price = start_of_year_data.close_price if start_of_year_data else Decimal('0.0')
            ytd_market_gain = (recent_close - start_of_year_price) * Decimal(holding.quantity)
            ytd_percentage_gain = ((recent_close - start_of_year_price) / start_of_year_price) * 100 if start_of_year_price else Decimal('0.0')

            # Add stock name and gain to the details for each holding
            stock_name = holding.market_data.company.name if holding.market_data.company.name and holding.market_data.company else "Unknown"
            asset_holdings_with_details.append({
                'holding': holding,
                'recent_close': recent_close,
                'stock_name': stock_name,
                'holding_gain': holding_gain,
                'ytd_dividends': ytd_dividends,
                'ytd_market_gain': ytd_market_gain,
                'ytd_dividend_yield': ytd_dividend_yield,
                'ytd_percentage_gain': ytd_percentage_gain
            })

            total_stocks += holding.quantity
            market_value += holding_market_value
            total_purchase_price += holding_purchase_price

        gain_loss = market_value - total_purchase_price
        percentage_gain_loss = (gain_loss / total_purchase_price) * 100 if total_purchase_price else Decimal('0.0')

        context.update({
            'total_stocks': total_stocks,
            'market_value': market_value,
            'gain_loss': gain_loss,
            'percentage_gain_loss': percentage_gain_loss,
            'asset_holdings_with_details': asset_holdings_with_details,
        })

        return context

class PortfolioCreateView(LoginRequiredMixin,CreateView):
    model = Portfolio
    fields = ['name', 'total_value']
    template_name = 'financials/portfolio_form.html'
    success_url = reverse_lazy('portfolio_list')  # Use the name of the URL pattern

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assuming portfolios are user-specific
        return super().form_valid(form)

class PortfolioDeleteView(LoginRequiredMixin, DeleteView):
    model = Portfolio
    template_name = 'financials/portfolio_confirm_delete.html'  # Confirmation template
    success_url = reverse_lazy('portfolio_list')  # Redirect after delete



class AssetHoldingUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetHolding
    fields = ['quantity', 'purchase_price']  # specify the fields you want to be editable
    template_name = 'financials/asset_holding_form.html'  # a form template for editing

    def get_success_url(self):
        # Redirect back to the portfolio detail page after editing
        return reverse_lazy('portfolio_detail', kwargs={'pk': self.object.portfolio.pk})

class AssetHoldingDeleteView(LoginRequiredMixin, DeleteView):
    model = AssetHolding
    template_name = 'financials/asset_holding_confirm_delete.html'  # Confirmation template
    success_url = reverse_lazy('portfolio_list')  # Redirect after delete

class AssetHoldingCreateView(LoginRequiredMixin, CreateView):
    model = AssetHolding
    form_class = AssetHoldingForm
    template_name = 'financials/asset_holding_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.portfolio = get_object_or_404(Portfolio, pk=self.kwargs['portfolio_id'], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Get the ticker symbol from the form
        ticker_symbol = form.cleaned_data['ticker_symbol']
 #       Fetch company data from API and handle API failure
        response = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker_symbol}?apikey={settings.FMP_KEY}')
        if response.status_code != 200:
        # Handle API failure (e.g., return an error message or redirect)
            pass

        company_data = response.json()[0]
        # Get or create the company
        #print(company_data['cik'])
        if company_data['cik'] == None:
            company_data['cik'] = random.randint(10**6, 10**7 - 1)            #print('cik')
        if company_data['city'] == None:
            company_data['city'] = 'Valencia'
        company, created = companies.objects.get_or_create(
            ticker_symbol=ticker_symbol,
            defaults={
                'name': company_data['companyName'],
                'cik': company_data.get('cik'),
                'location': company_data['city'],
                'exchange': company_data['exchangeShortName'],
                'industry': company_data['industry'],
            }
        )
            # Fetch or create market data for the company
        response_market_data = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{ticker_symbol}?apikey={settings.FMP_KEY}')
        if response_market_data.status_code != 200:
            form.add_error(None, "Failed to fetch market data")
            return self.form_invalid(form)

        market_data_api = response_market_data.json()[0]
        market_data_entry, md_created = market_data.objects.update_or_create(
        company=company,
        date=datetime.today(),
        defaults={
            'open_price': market_data_api['open'],
            'close_price': market_data_api['price'],
            'high_price': market_data_api['dayHigh'],
            'low_price': market_data_api['dayLow'],
            'volume': market_data_api['volume'],
            'market_cap': market_data_api['marketCap'],
            }
            )

        # Create the AssetHolding instance
        asset_holding = form.save(commit=False)
        asset_holding.market_data = market_data_entry
        asset_holding.portfolio = self.portfolio
        asset_holding.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('portfolio_detail', kwargs={'pk': self.portfolio.pk})



#BLOG
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'financials/post_list.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)    
    return render(request, 'financials/post_detail.html', {'post': post})

def section_posts(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    return render(request, 'financials/section_posts.html', {'section': section})

def about(request):
    return render(request, 'financials/about.html')

@login_required
def earnings_estimates_view(request):
    ticker = request.GET.get('ticker', '')  # Get the ticker symbol from the GET request
    estimates = []
    if ticker:
        try:
            url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?apikey={settings.FMP_KEY}"
            response = requests.get(url)
            response.raise_for_status()  # This will raise an exception for HTTP errors
            all_estimates = response.json()
            # Filter out past dates
            current_date = datetime.now().date()
            estimates = [estimate for estimate in all_estimates if datetime.strptime(estimate['date'], "%Y-%m-%d").date() > current_date]
            #print(estimates)
        except requests.exceptions.RequestException as e:
            estimates = None
            print(e)  # Handle logging appropriately in your project

    return render(request, 'financials/earnings_estimates.html', {'estimates': estimates, 'ticker': ticker})

