from django.contrib.auth import logout,authenticate, update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserCreationForm, CustomPasswordChangeForm, UserChangeForm, UserChangeFormCustom, BalanceTransferForm
from django.contrib import messages
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('test_list') 
    else: 
        form = UserCreationForm()
        if request.method=='POST':
            form = UserCreationForm(request.POST)
            if form.is_valid() :
                user=form.save()
                return redirect('test_list')
        context={
            'form':form,
        }
        return render(request,'accounts/auth.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('test_list')
    else:
       if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
       context={}
       return render(request,'accounts/login.html',context)
 
def logoutPage(request):
    logout(request)
    return redirect('loginPage')

def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Ваш пароль был успешно изменен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

def change_user_details(request):
    if request.method == 'POST':
        form = UserChangeFormCustom(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваши данные были успешно изменены!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
    else:
        form = UserChangeFormCustom(instance=request.user)
    return render(request, 'accounts/change_user_details.html', {'form': form})


def is_principal_or_teacher(user):
    return user.is_principal or user.is_teacher

@login_required
# @user_passes_test(is_principal_or_teacher)
def transfer_balance(request):
    if not request.user.is_principal and not request.user.is_teacher:
        messages.error(request, "You do not have permission to transfer balance.")
        return redirect('some_view_name')

    if request.method == 'POST':
        form = BalanceTransferForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username']
            amount = form.cleaned_data['amount']

            try:
                recipient = User.objects.get(username=recipient_username)
                request.user.transfer_balance(recipient, amount)
                messages.success(request, f'Successfully transferred {amount} to {recipient.get_full_name()}')
                return redirect('some_view_name')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = BalanceTransferForm()

    return render(request, 'transfer_balance.html', {'form': form})

@login_required
def generate_referral_link(request):
    user = request.user
    if not user.referral_link:
        user.generate_referral_link()
    return redirect('profile')

def register_with_referral(request):
    ref_token = request.GET.get('ref')
    if ref_token:
        referring_user = get_object_or_404(User, referral_link=f'/register-referral?ref={ref_token}')
        # Perform registration logic
        # Example: create a new user, credit bonus to referring_user
        referring_user.referral_bonus += 50  # Example bonus amount
        referring_user.save()
        messages.success(request, 'Registered successfully with referral bonus!')
    else:
        # Handle case where no referral link is found
        messages.error(request, 'Invalid referral link.')

    return redirect('test_list')

# from twilio.rest import Client
# from django.conf import settings

# def send_verification_code(phone_number, verification_code):
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#     message = client.messages.create(
#         body=f"Your verification code is {verification_code}",
#         from_=settings.TWILIO_PHONE_NUMBER,
#         to=phone_number
#     )
#     return message.sid

# def verify_phone(request, user_id):
#     user = User.objects.get(pk=user_id)
#     if request.method == 'POST':
#         code = request.POST.get('verification_code')
#         sms_verification = SMSVerification.objects.get(user=user)
#         if sms_verification.verification_code == code:
#             sms_verification.verified = True
#             sms_verification.save()
#             login(request, user)
#             return redirect('home')
#         else:
#             error = "Invalid verification code"
#             return render(request, 'verify_phone.html', {'error': error})
#     return render(request, 'verify_phone.html', {'user_id': user_id})