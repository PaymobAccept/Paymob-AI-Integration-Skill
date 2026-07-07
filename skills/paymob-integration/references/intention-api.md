# Intention API Reference

Source: https://developers.paymob.com/paymob-docs/developers/intention-apis/create-intention

## Regional base URLs

Test and live modes share the same base URL per region — the mode is controlled entirely by which keys/Integration IDs you use, not the URL.

- Egypt: `https://accept.paymob.com/`
- Oman: `https://oman.paymob.com/`
- Saudi Arabia: `https://ksa.paymob.com/`
- UAE: `https://uae.paymob.com/`

The Intention creation endpoint is `POST /v1/intention/` on the relevant base URL (confirm exact path in the merchant's Postman collection/API explorer for their region, since path casing can vary slightly by region).

## Create Intention

### Auth
Header: `Authorization: Token <SECRET_KEY>` (note the literal word "Token", not "Bearer").
`Content-Type: application/json`

### Request body fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `amount` | number | yes | Total transaction amount **in cents** (e.g. 10000 = 100.00 EGP) |
| `currency` | string | yes | Must match the currency configured on the Integration ID used |
| `payment_methods` | array | yes | Integration ID(s) as integers, or method names as strings (e.g. `"card"`). Test/Live status of these IDs must match the Secret Key's status |
| `items` | array | no | Each item needs at minimum `name` and `amount`; omitting either causes a 400 |
| `billing_data` | object | yes (in practice) | Must include `phone_number` — missing it causes a 400. Also typically: `first_name`, `last_name`, `email`, `street`, `building`, `floor`, `apartment`, `city`, `country` (3-letter ISO), `state` |
| `extras` | object | no | Arbitrary custom merchant data; echoed back in callbacks under the payment `claims` object |
| `special_reference` | string | no | Your own internal order ID — returned in the transaction callback as `merchant_order_id`. Use this to correlate orders |
| `expiration` | number | no | Intention expiry in seconds |
| `notification_url` | string | no | Your webhook endpoint — receives the POST callback with full transaction details. **Card Integration IDs only** |
| `redirection_url` | string | no | Where the customer is redirected after payment, with transaction details as query params. **Card and Wallet methods only**. Not authenticated — don't trust it for order state |

### Example request

```json
{
  "amount": 10000,
  "currency": "EGP",
  "payment_methods": [4569876],
  "items": [
    { "name": "Product 1", "amount": 10000, "description": "Demo item", "quantity": 1 }
  ],
  "billing_data": {
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+201234567890",
    "email": "customer@example.com",
    "street": "Example Street",
    "building": "4",
    "floor": "5",
    "apartment": "123",
    "city": "Cairo",
    "country": "EGY",
    "state": "Cairo"
  },
  "extras": { "merchant_order_id": "order_123" },
  "special_reference": "order_123",
  "notification_url": "https://yourapp.com/api/paymob/callback",
  "redirection_url": "https://yourapp.com/checkout/result"
}
```

### Key response fields

- `id` — Intention ID, also usable to correlate the transaction
- `intention_order_id` — Paymob Order ID, returned again in the transaction callback
- `client_secret` — the critical value: used to launch the Unified Checkout redirect
- `payment_methods` — array confirming which methods are live on this intention
- `status` — e.g. `"intended"` initially
- `confirmed` — boolean

### Launching checkout

Redirect the customer to Paymob's **Unified Checkout** (Paymob-hosted payment page) using this URL structure, built from the `client_secret` returned above and the merchant's **Public Key**:

```
https://{base_url}/unifiedcheckout/?publicKey={PUBLIC_KEY}&clientSecret={client_secret}
```

Example for an Egypt merchant:
```
https://accept.paymob.com/unifiedcheckout/?publicKey=pk_test_abc123&clientSecret=csk_test_a1b2c3d4e5
```

- Swap `accept.paymob.com` for the merchant's regional base URL (`oman.paymob.com`, `ksa.paymob.com`, `uae.paymob.com`).
- `publicKey` must be the **Public Key**, not the Secret Key — the Public Key is safe to expose client-side; the Secret Key is never sent to the browser.
- `clientSecret` is single-use — a new Intention (and therefore a new `client_secret`) is required for each payment attempt.
- The customer completes card entry, 3D Secure, or wallet OTP entirely on this Paymob-hosted page; your frontend never touches raw card data.
- Confirm this exact path against the merchant's current API explorer/Postman collection before going live, since hosted-checkout paths can be updated by Paymob independently of the Intention API version.

### Common errors

**404 — bad/mismatched Integration ID**
```json
{ "detail": "Integration ID/Name does not exist in our system. You can find the list of Integration ID's/Names from Merchant Dashboard under Developers → Payment Integrations Tab" }
```
(Note: this is Paymob's literal API error text; in the current dashboard, Integration IDs are actually found under **Settings → Payment Integrations**.)
Checklist to fix: (1) Integration ID's Test/Live status must match the Secret Key's status, (2) ID belongs to this merchant account and is an online integration, (3) ID is fully configured — if not, merchant should contact support@paymob.com.

**400 — missing item fields**
```json
{ "items": { "name": ["This field is required."] } }
```
Fix: every object in `items` needs both `name` and `amount`.

**400 — missing phone number**
```json
{ "billing_data": { "phone_number": ["This field is required."] } }
```
Fix: always populate `billing_data.phone_number`.

## After payment: callbacks are the source of truth

Paymob sends a `notification_url` POST with full transaction details once the payment is processed (success or fail), and separately redirects the customer via `redirection_url`. **Always treat the callback as authoritative and verify its HMAC before updating order state** (see `hmac-verification.md`) — the redirect is for UX only and its query params are not signed/verifiable the same way.
