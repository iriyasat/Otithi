import requests
import json
from datetime import datetime
from config import Config

class BKashPayment:
    def __init__(self):
        self.api_key = Config.BKASH_API_KEY
        self.api_secret = Config.BKASH_API_SECRET
        self.base_url = Config.BKASH_API_URL
        self.merchant_id = Config.BKASH_MERCHANT_ID

    def create_payment(self, amount, currency, booking_id):
        """
        Create a bKash payment request
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'merchant_id': self.merchant_id,
                'amount': amount,
                'currency': currency,
                'intent': 'sale',
                'merchant_order_id': f'booking_{booking_id}',
                'callback_url': f'{Config.BASE_URL}/api/payments/bkash/callback'
            }

            response = requests.post(
                f'{self.base_url}/checkout/create',
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Failed to create bKash payment'}

        except Exception as e:
            return {'error': str(e)}

    def verify_payment(self, payment_id):
        """
        Verify a bKash payment
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f'{self.base_url}/checkout/execute/{payment_id}',
                headers=headers
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Failed to verify bKash payment'}

        except Exception as e:
            return {'error': str(e)}

class PaymentGateway:
    def __init__(self):
        self.bkash = BKashPayment()

    def create_payment(self, payment_method, amount, currency, booking_id):
        if payment_method == 'bkash':
            return self.bkash.create_payment(amount, currency, booking_id)
        else:
            return {'error': 'Unsupported payment method'}

    def verify_payment(self, payment_method, payment_id):
        if payment_method == 'bkash':
            return self.bkash.verify_payment(payment_id)
        else:
            return {'error': 'Unsupported payment method'} 