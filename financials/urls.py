from django.urls import path
from .views import financial_ratios_view,financial_statement_view, income_statement_view,add_watched_stock, watched_stocks_list, edit_watched_stock,delete_watched_stock,delete_watched_stock

urlpatterns = [
    path('financial-statement/', financial_statement_view, name='financial-statement'),
    path('income-statement/<str:ticker_symbol>/', income_statement_view, name='income-statement'),
    path('add-watched-stock/', add_watched_stock, name='add_watched_stock'),
    path('watched-stocks/', watched_stocks_list, name='watched_stocks_list'),
    path('edit-watched-stock/<int:pk>/', edit_watched_stock, name='edit_watched_stock'),
    path('delete-watched-stock/<int:pk>/', delete_watched_stock, name='delete_watched_stock'),
    path('delete-watched-stock/<int:stock_id>/', delete_watched_stock, name='delete_watched_stock'),
    path('financial-ratios/', financial_ratios_view, name='financial_ratios'),


]