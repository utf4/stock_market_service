from django.urls import path
from stock.views import signup, get_stock_info

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('stocks/<symbol>/', get_stock_info, name='get_stock_info'),
]