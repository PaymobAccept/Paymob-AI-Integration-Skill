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

## Methods with no sandbox test path

⚠️ **These methods cannot be tested in sandbox at all.** No test credentials exist for them, and a payment cannot be completed end-to-end in Test mode. (Confirmed with Paymob, August 2026.)

- **Kiosk** — Aman, Masary
- **BNPL** — Valu, Souhoola, Tabby, Tamara, Sympl, and the other providers

What that means in practice:

- Do **not** substitute a test card for one of these methods and record it as validated — that exercises the card rail, not theirs.
- **A green sandbox run does not cover them.** If the merchant is enabling kiosk or BNPL, tell them *before* they plan go-live, not after: cards and wallets validate in sandbox as normal, but these have to be verified with their Paymob account manager or `support@paymob.com`. The Phase 3 exit criteria in `SKILL.md` ("only flip to Live after a full successful test run") is not achievable for these methods, so don't present a passing sandbox suite as clearing them.

**Not confirmed either way — don't assume:** Apple Pay, Google Pay, and bank installments. (`README.md` notes bank installments are "Live IDs only," which points the same way, but confirm with `support@paymob.com` before telling a merchant whether they can test it.) Don't infer a sandbox path for any of these from the card/wallet sections above.

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
