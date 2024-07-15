from django.shortcuts import render
import requests
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json
from accounts.models import User
import datetime
import os
import re
import base64
from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from .models import FetchedEmailData


def post_order(request):
    url = 'https://qazdrivekaspi.kz/api/orders'
    today_date = datetime.datetime.now().date
    start_date = datetime.datetime.now() + datetime.timedelta(30)
    customer = request.user.first_name + " " + request.user.last_name
    customer_id = request.user.id

    data={
    "full_name": customer,
    # "tariff": product,
    "sum": sum,
    "user_id": customer_id,
    "course": "ПДД"
    }
    
    # response = requests.post(url, json=data)
    
    # if (response.status_code != 204
    #         and 'content-type' in response.headers
    #         and 'application/json' in response.headers['content-type']):
    #     parsed = response.json()

    #     currunt_user = User.objects.filter(id = request.user.id).first()
        
    # else:
    #     print('conditions not met')
    currunt_user = User.objects.filter(id = request.user.id).first()
    # if request.user.tarif_expire_date == today_date:
    # if request.user.pddtest_pass == None:
    # if parsed['data']['id'] == None:
        # currunt_user.payment_id = parsed['data']['id']
        # currunt_user.payment_id = 69
        # currunt_user.tarif_name = product
        # currunt_user.tarif_expire_date = start_date
        # currunt_user.save()
    return render(request, 'payments/post_order.html')
    # else:
    #     messages.success(request, 'У вас есть активный тариф')
    #     return redirect('index')

#для проверки оплаты
def check_order(request):
    kaspi_id = request.user.payment_id
    url = f'https://qazdrivekaspi.kz/api/orders/{kaspi_id}'
    response = requests.get(url)
    is_payed = False
    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()

        if parsed['data']['txn_id'] == None:
            is_payed = False
        else:
            is_payed = True
    else:
        print('conditions not met')
    
    if is_payed == True:
        return HttpResponse("Оплачено")
    else:
        return HttpResponse("Не оплачено")
    
# get balance from gmail
# If modifying these SCOPES, delete the file token.json.

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
MY_GMAIL = 'synaqtest1@gmail.com'
SENDER_EMAIL = 'kaspi.payments@kaspibank.kz'

def authenticate_gmail(request):
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'token.json')
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, settings.GMAIL_SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GMAIL_CREDENTIALS_PATH, settings.GMAIL_SCOPES)
            flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            request.session['state'] = state
            return HttpResponseRedirect(authorization_url)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def oauth2callback(request):
    state = request.session.get('state')
    flow = InstalledAppFlow.from_client_secrets_file(
        settings.GMAIL_CREDENTIALS_PATH, settings.GMAIL_SCOPES, state=state)
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    token_path = os.path.join(settings.BASE_DIR, 'token.json')
    with open(token_path, 'w') as token:
        token.write(creds.to_json())

    return HttpResponseRedirect(reverse('fetch_emails'))

def get_messages(service):
    try:
        results = service.users().messages().list(userId='me', q='from:' + SENDER_EMAIL).execute()
        messages = results.get('messages', [])

        parsed_messages = []
        if messages:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                msg_str = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
                parsed_message = parse_message(msg_str)
                if parsed_message:
                    parsed_messages.append(parsed_message)

        return parsed_messages
    except Exception as e:
        return []

def parse_message(message):
    fio_match = re.search(r'ФИО учащегося: (.+)', message)
    jsn_iin_match = re.search(r'ЖСН\|ИИН = (\d+)', message)
    payment_amount_match = re.search(r'Платеж на сумму: (\d+\.\d{2})', message)
    payment_id_match = re.search(r'Идентификатор платежа: (\d+)', message)

    if fio_match and jsn_iin_match and payment_amount_match and payment_id_match:
        return {
            'fio_student': fio_match.group(1),
            'jsn_iin': jsn_iin_match.group(1),
            'payment_amount': payment_amount_match.group(1),
            'payment_id': payment_id_match.group(1)
        }
    return None

@csrf_exempt
def fetch_emails(request):
    service = authenticate_gmail(request)
    if isinstance(service, HttpResponseRedirect):
        return service  # Redirect to OAuth2 authorization URL
    parsed_messages = get_messages(service)

    
    for parsed_message in parsed_messages:
            fio_student = parsed_message.get('fio_student')
            jsn_iin = parsed_message.get('jsn_iin')
            payment_amount = parsed_message.get('payment_amount')
            payment_id = parsed_message.get('payment_id')
            
            # Check if payment_id already exists
            if FetchedEmailData.objects.filter(payment_id_match=payment_id).exists():
                continue  # Skip saving if payment_id already exists
            
            # Save the new entry
            fetched_email = FetchedEmailData(
                fio_student=fio_student,
                jsn_iin=jsn_iin,
                payment_amount=payment_amount,
                payment_id_match=payment_id  # Assuming payment_id is stored in parsed_message
            )
            fetched_email.save()

    return JsonResponse(parsed_messages, safe=False)

@csrf_exempt
def add_balance(request):
    try:
        # Get user's payment_id from request.user
        payment_id = request.user.payment_id
        
        # Check if there is a matching FetchedEmailData entry
        fetched_email = get_object_or_404(FetchedEmailData, payment_id_match=payment_id)
        
        # Retrieve jsn_iin and payment_amount from fetched_email
        jsn_iin = fetched_email.jsn_iin
        payment_amount = fetched_email.payment_amount
        
        # Update user balance
        user = request.user
        user.balance += Decimal(payment_amount)
        user.save()
        
        # Delete the fetched email entry
        fetched_email.delete()

        return JsonResponse({'success': f'Balance of {payment_amount} added to user {jsn_iin}. Fetched email data deleted.'})

    except Exception as e:
        return JsonResponse({'error': f'Error adding balance: {e}'}, status=500)

def kaspi_info_view(request):
    return render(request, 'payments/kaspi_info.html')