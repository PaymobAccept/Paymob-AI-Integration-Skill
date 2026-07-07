# Sandbox Test Credentials

Source: https://developers.paymob.com/paymob-docs/need-help/faq/test-credentials (last updated by Paymob: June 1, 2026)

Use these **only** with Test-mode keys and Test-mode Integration IDs. Never use real card numbers in sandbox, and never use these numbers against Live keys.

⚠️ Sandbox test transactions/intentions are stored for **30 days** — complete a full test flow within that window.

## Test cards — Mastercard

**Card 1**
- Card number: `5123456789012346`
- Cardholder name: `Test Account`
- Expiry month: `01`
- Expiry year: `39`
- CVV: `123`

**Card 2**
- Card number: `5123450000000008`
- Cardholder name: `Test Account`
- Expiry month: `01`
- Expiry year: `39`
- CVV: `123`

## Test cards — Visa

- Card number: `4111111111111111`
- Cardholder name: `Test Account`
- Expiry month: `01`
- Expiry year: `39`
- CVV: `123`

## Test mobile wallet

- Wallet number: `01010101010`
- MPIN code: `123456`
- OTP: `123456`

## Using them

1. Make sure the Integration ID used in the Intention request is the **Test** version of the relevant payment method (Cards or Wallets), and that the Secret Key used is also Test mode — mismatched modes cause a 404 on intention creation (see `intention-api.md`).
2. Go through the real checkout flow (Unified Checkout redirect) and enter the test card / wallet details above as if you were the customer.
3. Confirm:
   - The checkout reaches a success state.
   - Your `notification_url` receives a POST callback (log the raw payload the first time).
   - Your HMAC verification (see `hmac-verification.md`) computes a match against the `hmac` query param.
   - Your order/database state updates correctly and idempotently.
4. If you need to test 3D Secure or wallet OTP flows, the same test cards/numbers above are used — the sandbox will walk through the same UI prompts (3DS challenge, OTP entry) using the listed OTP/MPIN values.
5. Paymob's public docs do not list separate "decline" test card numbers as of this writing — if the merchant specifically needs to test declined/failed transaction handling, recommend they ask their Paymob account manager or support@paymob.com for decline-simulation guidance rather than guessing, since using the wrong details on success-only test cards may just retry rather than decline.
6. Once the full flow (intention → checkout → test payment → verified callback → order update) passes, the merchant can switch the Dashboard to Live mode and swap only the keys/Integration IDs to their live equivalents — no code changes should be needed if env vars were used correctly.
