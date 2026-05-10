# app/paypal_client.py
import asyncio
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from .config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE

if PAYPAL_MODE == "sandbox":
    environment = SandboxEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
else:
    environment = LiveEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)

client = PayPalHttpClient(environment)

async def create_paypal_order(order_total: float, currency: str = "EUR"):
    request = OrdersCreateRequest()
    request.prefer("return=representation")
    request.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": f"{order_total:.2f}"
            }
        }],
        "application_context": {
            "return_url": "http://127.0.0.1:8000/payment-success",
            "cancel_url": "http://127.0.0.1:8000/payment-cancel"
        }
    })
    # Le SDK n'est pas asynchrone, on l'exécute dans un thread séparé
    response = await asyncio.to_thread(client.execute, request)
    return response.result

async def capture_paypal_order(paypal_order_id: str):
    request = OrdersCaptureRequest(paypal_order_id)
    request.prefer("return=representation")
    response = await asyncio.to_thread(client.execute, request)
    return response.result