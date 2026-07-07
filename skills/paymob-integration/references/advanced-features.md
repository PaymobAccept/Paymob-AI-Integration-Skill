# Advanced Features — Subscriptions, Saved Cards, Auth/Capture, Refund/Void, Split, Convenience Fees

All endpoints below use the regional base URL from `intention-api.md` and, unless noted, the header `Authorization: Token <SECRET_KEY>` (the literal word `Token`, not `Bearer`). Amounts are in **cents** (10000 = 100.00 EGP). Verify exact current shapes against the live docs (`live-resources.md`) before going live — some of these features must be enabled on the merchant's account by Paymob first.

---

## Refund / Void / Capture (post-payment operations)

These act on a completed transaction by its `transaction_id` (from the verified callback).

```http
POST {base_url}/api/acceptance/void_refund/refund
Authorization: Token {SECRET_KEY}
Content-Type: application/json

{ "transaction_id": 12345, "amount_cents": 10000 }
```

```http
POST {base_url}/api/acceptance/void_refund/void
Authorization: Token {SECRET_KEY}
Content-Type: application/json

{ "transaction_id": 12345 }
```

```http
POST {base_url}/api/acceptance/capture
Authorization: Token {SECRET_KEY}
Content-Type: application/json

{ "transaction_id": 12345, "amount_cents": 10000 }
```

- **Refund** — returns funds after settlement (full or partial via `amount_cents`). Availability varies by method (cards: yes; wallets: yes; most BNPL/kiosk: no — see the payment-methods notes in `intention-api.md`).
- **Void** — cancels an authorization/transaction before settlement (card only).
- **Capture** — captures a previously authorized (Auth/Capture) transaction.

```javascript
// Node.js — refund/void/capture share the same auth header
const axios = require('axios');
const api = axios.create({
  baseURL: process.env.PAYMOB_BASE_URL,            // e.g. https://accept.paymob.com
  headers: { Authorization: `Token ${process.env.PAYMOB_SECRET_KEY}` },
});

const refund  = (transactionId, amountCents) =>
  api.post('/api/acceptance/void_refund/refund', { transaction_id: transactionId, amount_cents: amountCents }).then(r => r.data);
const voidTxn = (transactionId) =>
  api.post('/api/acceptance/void_refund/void', { transaction_id: transactionId }).then(r => r.data);
const capture = (transactionId, amountCents) =>
  api.post('/api/acceptance/capture', { transaction_id: transactionId, amount_cents: amountCents }).then(r => r.data);
```

---

## Auth / Capture (two-step: authorize now, capture later)

Reserve funds at checkout, capture (or void) them later — useful for order-fulfillment-on-ship models.

1. Create the Intention with the auth flag set, then check out as normal:

```json
{
  "amount": 10000,
  "currency": "EGP",
  "payment_methods": [123456],
  "is_auth": true,
  "billing_data": { "phone_number": "+201234567890", "first_name": "John", "last_name": "Doe", "email": "john@example.com" },
  "special_reference": "order_123",
  "notification_url": "https://yoursite.com/api/paymob/callback",
  "redirection_url": "https://yoursite.com/checkout/result"
}
```

2. The callback arrives with `is_auth: true` and the funds held. Later, capture:

```http
POST {base_url}/api/acceptance/capture
Authorization: Token {SECRET_KEY}
{ "transaction_id": 12345, "amount_cents": 10000 }
```

   …or release the hold with the **void** endpoint above.

> Some accounts use `payment_type: "AUTH"` instead of `is_auth: true` on the Intention. Confirm which your merchant's account expects against the live docs.

---

## Saved Cards — CIT then MIT

### CIT (Customer-Initiated Transaction) — tokenize on first payment

The first payment must be customer-initiated. Ask Paymob/the dashboard to enable card tokenization for the Integration ID, and request tokenization on the Intention (commonly via `extras.save_card` — confirm the current flag name in the live docs):

```json
{
  "amount": 10000,
  "currency": "EGP",
  "payment_methods": [123456],
  "billing_data": { "phone_number": "+201234567890", "first_name": "John", "last_name": "Doe", "email": "john@example.com" },
  "customer": { "first_name": "John", "last_name": "Doe", "email": "john@example.com" },
  "special_reference": "order_123",
  "notification_url": "https://yoursite.com/webhook",
  "redirection_url": "https://yoursite.com/complete",
  "extras": { "save_card": true }
}
```

After a successful tokenization, Paymob sends a **Card Token callback** — verify it with the **Card Token HMAC** (different field set/order from the transaction HMAC) before storing the token:

**Card Token HMAC** — 8 fields, SHA-512, concatenated in this exact order, no separator:
```
card_subtype, created_at, email, id, masked_pan, merchant_id, order_id, token
```

```javascript
// Node.js — Card Token HMAC verification
const crypto = require('crypto');
function verifyCardTokenHmac(data, receivedHmac, secret) {
  const fields = [
    data.card_subtype, data.created_at, data.email, data.id,
    data.masked_pan, data.merchant_id, data.order_id, data.token,
  ];
  const computed = crypto.createHmac('sha512', secret)
    .update(fields.map(String).join('')).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(computed), Buffer.from(receivedHmac));
}
```

Store **only** `token` and `masked_pan` (and the customer linkage). Never store raw card data. Verify the token-callback `email` matches your customer record.

### MIT (Merchant-Initiated Transaction) — charge the saved token later

1. Create an Intention as normal (gives you a `client_secret`).
2. Instead of redirecting the customer, charge the stored token directly:

```http
POST {base_url}/api/acceptance/payments/pay
Authorization: Token {SECRET_KEY}
Content-Type: application/json

{
  "source": { "identifier": "SAVED_CARD_TOKEN", "subtype": "TOKEN" },
  "payment_token": "INTENTION_CLIENT_SECRET"
}
```

3. A `success: true` response (and the subsequent callback) means the card was charged with no customer interaction. MIT charges must comply with PCI/scheme rules — these are off-session payments the customer has pre-authorized.

You can also let the customer pick a previously saved card inside Unified Checkout / the SDK by passing the saved `card_tokens` on the Intention (CIT one-click) — confirm the current field name in the live docs.

---

## Subscriptions (recurring billing)

Subscriptions are available to selected merchants — Paymob must enable the feature on the account.

### Auth note
Subscription **plan management** uses a Bearer auth token (from the API-Key auth endpoint); attaching a subscription to a payment uses the normal `Authorization: Token <SECRET_KEY>` on the Intention.

```http
POST {base_url}/api/auth/tokens
Content-Type: application/json
{ "api_key": "<API_KEY>" }
# -> { "token": "<AUTH_TOKEN>" }
```

### Create a plan

```http
POST {base_url}/api/acceptance/subscription_plans
Authorization: Bearer {AUTH_TOKEN}
Content-Type: application/json

{ "name": "Monthly Pro", "amount_cents": 50000, "currency": "EGP",
  "frequency": 30, "reminder_days": 2, "retrial_days": 1 }
```

- Valid `frequency` values (days): **7, 15, 30, 60, 90, 180, 360**.
- The plan response returns a plan `id`.

### Start a subscription via the Intention

Attach the plan to a normal Intention (the first charge is CIT through checkout; subsequent charges are MIT auto-debits). Confirm the current attachment field name against the live docs — accounts use either `subscription_plan_id` on the Intention or a `recurring` object:

```json
{
  "amount": 50000,
  "currency": "EGP",
  "payment_methods": [123456],
  "subscription_plan_id": 789,
  "billing_data": { "phone_number": "+201234567890", "first_name": "John", "last_name": "Doe", "email": "john@example.com" },
  "special_reference": "sub_order_123",
  "notification_url": "https://yoursite.com/webhook",
  "redirection_url": "https://yoursite.com/complete"
}
```

### Subscription callbacks (Subscription HMAC)

Subscription events POST to your `notification_url`. The HMAC string is **not** the 20-field transaction concatenation — it is:

```
"{trigger_type}for{subscription_data.id}"
# e.g. "Subscription Createdfor12345"
```

and the `hmac` is in the **request body**, not the query string.

```python
# Python — Subscription HMAC verification
import hashlib, hmac
def verify_subscription_hmac(body: dict, secret: str) -> bool:
    s = f"{body['trigger_type']}for{body['subscription_data']['id']}"
    computed = hmac.new(secret.encode(), s.encode(), hashlib.sha512).hexdigest()
    return hmac.compare_digest(computed, body['hmac'])
```

### Manage

```http
GET  {base_url}/api/acceptance/subscriptions/{subscription_id}              # status
POST {base_url}/api/acceptance/subscriptions/{subscription_id}/cancel       # cancel
Authorization: Token {SECRET_KEY}
```

Store `subscription_data.id` for future management. For patterns like free trials, see the Paymob community forum (`live-resources.md`).

---

## Split features

- **Split Amount** — distribute one payment's revenue among marketplace sub-accounts at payment time (marketplace/platform model). Configured on the Intention; requires the feature enabled on the account.
- **Split Payment** — let one customer pay a single order across up to ~3 cards.

Exact request fields evolve — pull the current spec from the live docs before implementing.

---

## Convenience fees

Add a fee on top of the order, configurable as **percentage**, **fixed**, or **combined**, and can be card-specific (debit vs credit, BIN range, domestic vs international) or wallet-specific. Enabled/configured per account; confirm the current Intention field shape in the live docs.

---

## Reminders

- Verify the correct HMAC type per callback: **transaction** (20 fields, query param), **card token** (8 fields, query param), **subscription** (string formula, request body). Wrong type/order silently breaks verification — see `hmac-verification.md`.
- Always SHA-512, always timing-safe compare, never log secrets.
- Treat every callback as the source of truth only **after** HMAC passes, and process idempotently on `order.id` / `special_reference`.
