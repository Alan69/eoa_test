from django.urls import path
from .views import AuthenticateGmailView, OAuth2CallbackView, FetchEmailsView, AddBalanceView

urlpatterns = [
    path('authenticate-gmail/', AuthenticateGmailView.as_view(), name='authenticate_gmail'),
    path('oauth2callback/', OAuth2CallbackView.as_view(), name='oauth2callback'),
    path('fetch-emails/', FetchEmailsView.as_view(), name='fetch_emails'),
    path('add-balance/', AddBalanceView.as_view(), name='add_balance'),
]
