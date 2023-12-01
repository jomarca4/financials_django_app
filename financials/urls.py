from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import home,financial_ratios_view, income_statement_view,add_watched_stock, watched_stocks_list, edit_watched_stock,delete_watched_stock,delete_watched_stock

urlpatterns = [
    path('income-statement/<str:ticker_symbol>/', income_statement_view, name='income-statement'),
    path('add-watched-stock/', add_watched_stock, name='add_watched_stock'),
    path('watched-stocks/', watched_stocks_list, name='watched_stocks_list'),
    path('edit-watched-stock/<int:pk>/', edit_watched_stock, name='edit_watched_stock'),
    path('delete-watched-stock/<int:pk>/', delete_watched_stock, name='delete_watched_stock'),
    path('delete-watched-stock/<int:stock_id>/', delete_watched_stock, name='delete_watched_stock'),
    path('financial-ratios/', financial_ratios_view, name='financial_ratios'),
    path('', home, name='home'),  # Set this as the root URL
    path('login/', LoginView.as_view(template_name='financials/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),



]