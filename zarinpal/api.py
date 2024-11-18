import requests
import logging
from .error_handling import (
    ZarinPalError,
    ValidationException,
    TerminalException,
    PaymentRequestException,
    PaymentVerifyException,
    MyPaymentException,
)

class ZarinPalPayment:
    REQUEST_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"
    VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"
    START_PAYMENT_URL = "https://www.zarinpal.com/pg/StartPay/{}"
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, merchant_id: str, amount: int):
        self.merchant_id = merchant_id
        self.amount = amount

    def _make_request(self, url, data):
        try:
            response = requests.post(url, json=data, headers=self.HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.critical(f"Request to {url} failed: {e}, Data Sent: {data}")
            raise MyPaymentException(f"Request failed: {e}")

    def _handle_zarinpal_errors(self, response_data):
        errors = response_data.get("errors", {})
        if errors:
            error_code = errors.get("code", -1)
            message = errors.get("message", "Unknown error")
            raise ZarinPalError(error_code, message)

    def request_payment(
        self, callback_url: str, description: str, mobile: str = None, email: str = None
    ) -> dict:
        data = {
            "merchant_id": self.merchant_id,
            "amount": int(self.amount),  # Ensure the amount is an integer
            "callback_url": callback_url,
            "description": description,
        }

        if mobile or email:
            data["metadata"] = {}
            if mobile:
                data["metadata"]["mobile"] = mobile
            if email:
                data["metadata"]["email"] = email

        try:
            response_data = self._make_request(self.REQUEST_URL, data)
            self._handle_zarinpal_errors(response_data)
            authority = response_data["data"]["authority"]
            payment_url = self._redirect_to_payment_gateway(authority)
            return {
                "success": True,
                "data": {"authority": authority, "payment_url": payment_url},
                "error": None,
                "response_data": response_data,
            }
        except ZarinPalError as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
            }

    def _redirect_to_payment_gateway(self, authority: str) -> str:
        return self.START_PAYMENT_URL.format(authority)

    def verify_payment(self, authority: str) -> dict:
        data = {
            "merchant_id": self.merchant_id,
            "amount": int(self.amount),
            "authority": authority,
        }

        try:
            response_data = self._make_request(self.VERIFY_URL, data)
            self._handle_zarinpal_errors(response_data)
            return {"success": True, "data": response_data["data"]}
        except ZarinPalError as e:
            return {"success": False, "error": str(e)}
