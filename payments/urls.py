from django.urls import  path
from .views import *

urlpatterns = [
    path('post_order/', post_order, name ="post_order"),
    path('check_order/', check_order, name="check_order"),
    path('fetch-emails/', fetch_emails, name='fetch_emails'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('add_balance/', add_balance, name='add_balance'),
    path('kaspi-info/', kaspi_info_view, name='kaspi_info'),
]