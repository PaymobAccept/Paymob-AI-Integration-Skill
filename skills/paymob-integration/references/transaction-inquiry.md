# Transaction Inquiry API (Reconciliation / Polling)

Source: Paymob Transaction Inquiry API section (Authentication Request, Retrieve Transaction With Order ID / Transaction ID / Merchant Order ID) — `https://developers.paymob.com/paymob-docs/...` (legacy/management API, works alongside Intention-based payments since every Intention payment still produces an underlying Order + Transaction record).

## What this is for

The Intention API + HMAC-verified callback (see `intention-api.md` and `hmac-verification.md`) is the **primary** way the merchant's backend learns a payment's outcome. The Inquiry API is a **secondary, pull-based** check — you call it, instead of waiting for Paymob to call you. Use it as a safety net, not as your main flow.

### When the merchant system should call it

1. **Callback didn't arrive within an expected window.** If your `notification_url` hasn't received a callback within a few minutes of the customer reaching a success/fail screen on Paymob's checkout (network blip, firewall blocking the webhook, server downtime during deploy), proactively inquire about the transaction/order instead of leaving it stuck in "pending" forever.
2. **Reconciliation jobs.** A scheduled job (e.g. hourly/daily) that cross-checks your "pending" or "awaiting payment" orders against Paymob's records, to catch any callback that was missed or a duplicate that slipped past idempotency checks.
3. **Customer support / dispute lookups.** A support agent or admin panel needs to pull current status/details for one order without digging through raw webhook logs.
4. **Before manually adjusting an order's status.** Always re-confirm the live status via Inquiry before, e.g., manually marking an order paid — don't trust a stale local DB state.

### When NOT to use it

- Don't poll Inquiry instead of implementing the callback — it adds latency and API load, and the docs explicitly position Inquiry as a fallback/search tool, not the primary status channel.
- Don't use Inquiry results to skip HMAC verification on callbacks — they're two independent checks, not a substitute for each other.

## Authentication (separate from the Intention API's Secret Key)

This API uses the older Auth-Token flow, not the `Authorization: Token <SECRET_KEY>` header used by the Intention API.

```
POST {base_url}/api/auth/tokens
Content-Type: application/json

{ "api_key": "<API_KEY>" }
```

Response:
```json
{ "token": "<AUTH_TOKEN>" }
```

- `api_key` is the **API Key** from Dashboard → Settings → API Keys (different from the Secret/Public keys used for Intentions).
- The returned `token` is short-lived — generate a fresh one per inquiry session rather than caching it long-term.

## Retrieve a transaction by Transaction ID

```
GET {base_url}/api/acceptance/transactions/{transaction_id}?token={AUTH_TOKEN}
```
Returns the full transaction object — same shape as what arrives in the `obj` of a callback (amount_cents, success, pending, order, source_data, etc.).

## Retrieve an order by Order ID

```
GET {base_url}/api/ecommerce/orders/{order_id}?token={AUTH_TOKEN}
```
Returns the order object, including its nested `transactions` array — useful when you only stored Paymob's `intention_order_id` / `order.id` and want every transaction attempt tied to it.

## List/paginate orders or transactions

```
GET {base_url}/api/ecommerce/orders?page={page}&token={AUTH_TOKEN}
GET {base_url}/api/acceptance/transactions?page={page}&token={AUTH_TOKEN}
```

## Retrieve by your own Merchant Order ID (special_reference)

Paymob's Transaction Inquiry API also supports searching by **your own** order identifier (the `special_reference` you sent when creating the Intention, returned as `merchant_order_id`) — this is the most useful lookup for a merchant system, since you don't have to store Paymob's internal IDs at all to check status. The exact path/query-param form can vary slightly by region/account — **before hardcoding it, pull the current request example from the merchant's API Explorer or Postman collection for their region** (Dashboard → Developers → API explorer, or the Postman collection linked from the dashboard) rather than guessing, since this is the one inquiry variant whose exact URL shape isn't consistently documented across regions.

## Implementation notes

- Base URL is the same regional base used for the Intention API (`accept.paymob.com`, `oman.paymob.com`, `ksa.paymob.com`, or `uae.paymob.com`).
- Match Test/Live: an Inquiry auth token generated with a Test API Key will only see Test-mode transactions, and vice versa.
- Rate-limit yourself: don't reconciliation-poll in a tight loop — a periodic job (e.g. every few minutes for "still pending" orders, falling off after some max age) is enough.
- Treat the Inquiry response the same way you treat a verified callback: read `success`/`pending`/`is_voided`/`is_refunded` to determine real state, and update your order using the same idempotent logic keyed on `order.id` / `special_reference`.
