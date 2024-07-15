from django.urls import path
from .views import change_password, change_user_details, registerPage, transfer_balance, loginPage, logoutPage, generate_referral_link, register_with_referral

urlpatterns = [
    path('', loginPage, name='loginPage'),
    path('register/', registerPage, name='registerPage'),
    path('logout/', logoutPage, name='logoutPage'),
    path('change_password/', change_password, name='change_password'),
    path('change_user_details/', change_user_details, name='change_user_details'),
    path('transfer-balance/', transfer_balance, name='transfer_balance'),
    path('generate-referral/', generate_referral_link, name='generate_referral_link'),
    path('register-referral/', register_with_referral, name='register_with_referral'),
]
