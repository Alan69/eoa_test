from rest_framework import status, views, reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.conf import settings
from decimal import Decimal
import os
import re
import base64
from .models import FetchedEmailData
from accounts.models import User

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

MY_GMAIL = 'synaqtest1@gmail.com'
SENDER_EMAIL = 'kaspi.payments@kaspibank.kz'


class AuthenticateGmailView(views.APIView):
    def get(self, request):
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
                return Response({"authorization_url": authorization_url}, status=status.HTTP_302_FOUND)

            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)


class OAuth2CallbackView(views.APIView):
    def get(self, request):
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

        return Response({"message": "Token fetched successfully"}, status=status.HTTP_200_OK)


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


class FetchEmailsView(views.APIView):
    def get(self, request):
        # Authenticate and build the Gmail service object
        service = AuthenticateGmailView().get(request)
        if isinstance(service, Response) and service.status_code == status.HTTP_302_FOUND:
            return service  # Redirect to OAuth2 authorization URL

        # Now use the service object to fetch the messages
        parsed_messages = get_messages(service)

        # Process the messages and save to the database
        for parsed_message in parsed_messages:
            fio_student = parsed_message.get('fio_student')
            jsn_iin = parsed_message.get('jsn_iin')
            payment_amount = parsed_message.get('payment_amount')
            payment_id = parsed_message.get('payment_id')

            if FetchedEmailData.objects.filter(payment_id_match=payment_id).exists():
                continue  # Skip saving if payment_id already exists

            FetchedEmailData.objects.create(
                fio_student=fio_student,
                jsn_iin=jsn_iin,
                payment_amount=payment_amount,
                payment_id_match=payment_id
            )

        return Response(parsed_messages, status=status.HTTP_200_OK)


class AddBalanceView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            payment_id = request.user.payment_id
            fetched_email = get_object_or_404(FetchedEmailData, payment_id_match=payment_id)

            user = request.user
            user.balance += Decimal(fetched_email.payment_amount)
            user.save()

            fetched_email.delete()

            return Response(
                {'success': f'Balance of {fetched_email.payment_amount} added to user {fetched_email.jsn_iin}. Fetched email data deleted.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': f'Error adding balance: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
