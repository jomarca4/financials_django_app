from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models  # Import models
from django.db.models import Max

from collections import defaultdict
from itertools import groupby
from operator import attrgetter
# Create your views here.
from .models import financial_ratios, financial_statement_items, quarters, WatchedStock, companies, FinancialStatementLabel,financial_statements
from .forms import WatchedStockForm  # Make sure this import is correct

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