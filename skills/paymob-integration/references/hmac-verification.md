# HMAC Callback Verification

Source: https://developers.paymob.com/paymob-docs/developers/webhook-callbacks-and-hmac/hmac

## Why this matters

Anyone can POST a fake payload to your `notification_url`. The `hmac` query parameter on every callback request is how you prove the data actually came from Paymob and wasn't tampered with in transit. **Never update order/payment state from a callback whose HMAC doesn't match.** This is the single most important security control in the integration — do not skip it or treat it as optional, even for a quick prototype.

## Where the HMAC secret comes from

Dashboard → Settings → API Keys → HMAC Secret field. This is a separate secret from the API Key / Secret Key / Public Key (though all four live in the same Settings → API Keys section). Store it as `PAYMOB_HMAC_SECRET`.

## Calculation algorithm (Transaction Processed Callback)

1. Paymob POSTs the transaction object to your `notification_url`, with `?hmac=<value>` on the URL as a query parameter.
2. The transaction data lives at `obj` in the POST body (i.e. `body.obj`).
3. From `obj`, pull exactly these fields/keys, **in this exact order** (this is the documented concatenation order — note it is NOT simple alphabetical order of the literal key names below, it is the order Paymob specifies):

```
amount_cents
created_at
currency
error_occured
has_parent_transaction
id
integration_id
is_3d_secure
is_auth
is_capture
is_refunded
is_standalone_payment
is_voided
order.id            (nested: obj.order.id)
owner
pending
source_data.pan         (nested: obj.source_data.pan)
source_data.sub_type    (nested: obj.source_data.sub_type)
source_data.type        (nested: obj.source_data.type)
success
```

4. Convert each value to its string representation (booleans become the literal strings `true`/`false`; numbers become their plain string form) and **concatenate them with no separator** in the order above.
5. Compute `HMAC-SHA512(concatenated_string, hmac_secret)`.
6. Convert the result to lowercase hex.
7. Compare to the `hmac` query parameter from the callback URL. If they match exactly, the callback is authentic — proceed to update order state. If not, reject/ignore the callback (return 200 to avoid retries if your framework requires it, but do not act on the data).

### Worked example (from Paymob docs)

Given a sample transaction with `amount_cents=100`, `created_at=2020-03-25T18:39:44.719228`, `currency=EGP`, `error_occured=false`, `has_parent_transaction=false`, `id=2556706`, `integration_id=6741`, `is_3d_secure=true`, `is_auth=false`, `is_capture=false`, `is_refunded=false`, `is_standalone_payment=true`, `is_voided=false`, `order.id=4778239`, `owner=4705`, `pending=false`, `source_data.pan=2346`, `source_data.sub_type=MasterCard`, `source_data.type=card`, `success=true`:

Concatenated string:
```
1002020-03-25T18:39:44.719228EGPfalsefalse25567066741truefalsefalsefalsetruefalse47782394705false2346MasterCardcardtrue
```

Resulting HMAC (SHA-512, hex, lowercase) — using the merchant's own HMAC secret as the key — should equal what Paymob sends. (The exact hash output is merchant-secret-dependent; the point of this example is to validate your concatenation logic produces the same string before you trust your hash function output.)

## Implementation notes for the coding agent

- Build the concatenation purely from the **raw values as received** — don't reformat dates, don't round numbers, don't add/remove whitespace.
- Watch out for `obj.order.id` vs a top-level `id` — both `id` and `order.id` appear in the list as separate fields; don't conflate them.
- If a field is missing/null in a given callback type, check the live payload structure rather than assuming — different callback types (Transaction Processed vs Card Token) have different field lists and orders. This file covers the standard **Transaction Processed callback**. If the merchant also needs card-token callbacks (for "pay with saved card"), fetch the current field order from `https://developers.paymob.com/paymob-docs/developers/webhook-callbacks-and-hmac/hmac/hmac-for-card-tokens` before implementing, since the field set differs (it includes things like `card_subtype`, `email`, masked PAN, etc.) and getting the order wrong silently breaks verification.
- Always log the raw callback body once during development/testing so you can confirm your field extraction matches reality for this specific merchant's payment methods — wallets and cards can return slightly different nested shapes.
- Respond `200 OK` to Paymob promptly (process asynchronously if your business logic is slow) — webhook senders typically retry on non-2xx or timeout, which can cause duplicate processing if you're not idempotent on `order.id` / `special_reference`.

## Idempotency

Use `special_reference` (your own order ID, returned as `merchant_order_id`) or Paymob's `order.id` as your idempotency key — guard against processing the same successful callback twice if Paymob retries delivery.
