# Paymob — Python (Django / Flask / FastAPI)

Clean, correct reference (Intention API + Unified Checkout + HMAC-verified webhook). Read `intention-api.md` and `hmac-verification.md` alongside this.

## Environment

```env
PAYMOB_BASE_URL=https://accept.paymob.com
PAYMOB_SECRET_KEY=sk_test_xxxxxxxx
PAYMOB_PUBLIC_KEY=pk_test_xxxxxxxx
PAYMOB_HMAC_SECRET=your_hmac_secret
PAYMOB_INTEGRATION_ID_CARD=123456
APP_URL=https://yoursite.com
```

```bash
pip install requests python-dotenv
```

## Client (`paymob.py`)

```python
import os, hashlib, hmac
import requests


class PaymobClient:
    def __init__(self):
        self.base = os.environ.get("PAYMOB_BASE_URL", "https://accept.paymob.com").rstrip("/")
        self.secret = os.environ["PAYMOB_SECRET_KEY"]
        self.public = os.environ["PAYMOB_PUBLIC_KEY"]
        self.hmac_secret = os.environ["PAYMOB_HMAC_SECRET"]
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Token {self.secret}",   # literal "Token", not "Bearer"
            "Content-Type": "application/json",
        })

    def create_intention(self, *, amount_cents, currency, payment_methods,
                         special_reference, customer, items=None) -> dict:
        payload = {
            "amount": amount_cents,
            "currency": currency,
            "payment_methods": payment_methods,
            "items": items or [],
            "special_reference": special_reference,
            "billing_data": {
                "first_name": customer["first_name"],
                "last_name": customer["last_name"],
                "email": customer["email"],
                "phone_number": customer["phone"],     # REQUIRED
                "apartment": "NA", "floor": "NA", "street": "NA", "building": "NA",
                "shipping_method": "NA", "postal_code": "NA", "city": "NA",
                "state": "NA", "country": "EGY",
            },
            "customer": {
                "first_name": customer["first_name"],
                "last_name": customer["last_name"],
                "email": customer["email"],
            },
            "notification_url": f"{os.environ['APP_URL']}/api/paymob/webhook",
            "redirection_url": f"{os.environ['APP_URL']}/payment/complete",
        }
        r = self.s.post(f"{self.base}/v1/intention/", json=payload)
        r.raise_for_status()
        d = r.json()
        return {"id": d["id"], "client_secret": d["client_secret"]}

    def checkout_url(self, client_secret: str) -> str:
        return f"{self.base}/unifiedcheckout/?publicKey={self.public}&clientSecret={client_secret}"

    def verify_transaction_post_hmac(self, obj: dict, received_hmac: str) -> bool:
        fields = [
            obj["amount_cents"], obj["created_at"], obj["currency"], obj["error_occured"],
            obj["has_parent_transaction"], obj["id"], obj["integration_id"], obj["is_3d_secure"],
            obj["is_auth"], obj["is_capture"], obj["is_refunded"], obj["is_standalone_payment"],
            obj["is_voided"], obj["order"]["id"], obj["owner"], obj["pending"],
            obj["source_data"]["pan"], obj["source_data"]["sub_type"],
            obj["source_data"]["type"], obj["success"],
        ]
        concat = "".join(_paymob_str(f) for f in fields)
        computed = hmac.new(self.hmac_secret.encode(), concat.encode(), hashlib.sha512).hexdigest()
        return hmac.compare_digest(computed, received_hmac or "")

    def refund(self, transaction_id: int, amount_cents: int) -> dict:
        return self._post("/api/acceptance/void_refund/refund",
                          {"transaction_id": transaction_id, "amount_cents": amount_cents})

    def void(self, transaction_id: int) -> dict:
        return self._post("/api/acceptance/void_refund/void", {"transaction_id": transaction_id})

    def capture(self, transaction_id: int, amount_cents: int) -> dict:
        return self._post("/api/acceptance/capture",
                          {"transaction_id": transaction_id, "amount_cents": amount_cents})

    def _post(self, path, body):
        r = self.s.post(f"{self.base}{path}", json=body); r.raise_for_status(); return r.json()


def _paymob_str(v) -> str:
    # Python's str(True) is "True"; Paymob expects JSON-style "true"/"false"
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)
```

> **Note the boolean fix:** Paymob concatenates booleans as lowercase `true`/`false`. Naive `str(True)` yields `"True"` and silently breaks HMAC. `_paymob_str` handles it.

## Django view

```python
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .paymob import PaymobClient

paymob = PaymobClient()

@csrf_exempt
def create_checkout(request):
    data = json.loads(request.body)
    intention = paymob.create_intention(
        amount_cents=round(float(data["amount"]) * 100),
        currency="EGP",
        payment_methods=[int(os.environ["PAYMOB_INTEGRATION_ID_CARD"])],
        special_reference=str(data["order_id"]),
        customer={"first_name": data.get("first_name", "NA"),
                  "last_name": data.get("last_name", "NA"),
                  "email": data["email"], "phone": data["phone"]},
        items=[],
    )
    return JsonResponse({"checkout_url": paymob.checkout_url(intention["client_secret"])})

@csrf_exempt
def paymob_webhook(request):
    body = json.loads(request.body)
    obj = body.get("obj", {})
    received = request.GET.get("hmac", "")
    if not paymob.verify_transaction_post_hmac(obj, received):
        return JsonResponse({"error": "Invalid HMAC"}, status=401)
    if obj.get("success") and not obj.get("pending"):
        ...  # mark_order_paid(obj["order"]["id"]) idempotently, then fulfill
    return JsonResponse({"received": True})
```

## Flask / FastAPI

Identical client; only the request plumbing differs:

```python
# Flask
received = request.args.get("hmac", ""); body = request.get_json()
# FastAPI
received = request.query_params.get("hmac", ""); body = await request.json()
```

In both, pull `obj = body["obj"]`, call `paymob.verify_transaction_post_hmac(obj, received)`, then act on `obj["success"]` idempotently.

## Gotchas

- `Authorization: Token <secret>` (not Bearer). Amount in **cents**. `billing_data.phone_number` required.
- Concatenate booleans as `true`/`false` (see `_paymob_str`).
- Verify HMAC before trusting `success`; never trust redirect params. `client_secret` is single-use.
