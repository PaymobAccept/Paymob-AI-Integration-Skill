# Testing Guide — prompt for a test payment, show the right test details

This file tells the agent **when** to stop and ask for a test payment, **which** test details to show, and **how** to test each integration type. The test card and wallet numbers themselves live only in `test-credentials.md` — read that file and copy from it. Never list test numbers from memory.

## 1. The test checkpoint

Run this checkpoint once the integration is set up — after the code is written (custom builds), after the plugin or app is configured (Shopify / WooCommerce / other plugins), or after the first Payment Link is created. Don't skip it and don't bury it in a long summary.

1. Ask the user directly: **"Ready to run a test payment?"**
2. Confirm test mode is on for their integration type (section 3).
3. Show **only** the test details for the payment methods they enabled (section 2), copied from `test-credentials.md`.
4. Tell them what a passing test looks like for their integration type (section 3), then wait for the result.
5. If it fails, go to Troubleshooting in `SKILL.md`, or use `/paymob-explain-error` / `/paymob-check-hmac` where available.

Always carry over the two caveats from `test-credentials.md`: sandbox data expires after **30 days**, and Paymob publishes no decline-simulation cards.

## 2. Which test details to show

| Enabled method | What to show |
|---|---|
| Cards | The Mastercard and Visa test cards from `test-credentials.md` |
| Mobile wallets | The test wallet number, MPIN, and OTP from `test-credentials.md` |
| Kiosk, BNPL (Valu, Souhoola, Tabby, Tamara, Sympl, …) | The **no sandbox test path** message from `test-credentials.md`. Say the card test covers the shared integration code, and list the first-live-transaction checks from Phase 3 step 7 in `SKILL.md`. Don't substitute a test card and call the method tested. |
| Apple Pay, Google Pay, bank installments | Say sandbox support isn't confirmed in this skill, and point to `support@paymob.com` or the live docs. Don't invent a test path. |

If the merchant enabled several methods, show each matching block — and nothing for methods they didn't enable.

## 3. How to test each integration type

### Custom web — Unified Checkout (redirect) or Pixel (embedded)

- **Test mode:** Test Secret Key + Test Public Key + **Test** Integration IDs (mismatched modes → 404 on intention creation).
- **Webhook URL:** `notification_url` must be public HTTPS. To just see the callback, use `https://hooks.paymob.com` (the user opens it and pastes back their Hook URL). To test the merchant's own handler, use a tunnel or deployed preview URL. Details: *Making `notification_url` reachable* in `intention-api.md`.
- **Run:** create an intention → open Unified Checkout (or render Pixel) → pay with the test details from section 2.
- **Passes when:** the merchant's handler receives the POST callback, the HMAC verifies, and the order updates once (a replayed callback changes nothing). Seeing the callback on hooks.paymob.com alone is not a pass.
- Also run a Transaction Inquiry lookup for the test transaction (`transaction-inquiry.md`).

### Mobile SDK (iOS / Android / Flutter / React Native)

- Same test mode, webhook URL, and pass criteria as custom web — the backend is identical.
- Pay inside the SDK's native checkout, on a real device and a simulator/emulator if possible.
- Assert on the **backend callback**, not the SDK's in-app result.

### Shopify (Paymob apps)

- **Test mode:** turn on the **test mode** button in the Paymob app's settings in Shopify admin, with test credentials.
- **Run:** place an order on the storefront, choose Paymob at checkout, and pay with the test details from section 2.
- **Passes when:** the order shows as paid in Shopify admin and the transaction appears in the Paymob dashboard (Test mode).
- **Before going live:** turn test mode **off**. Leaving it on means real customers can't pay.

### WooCommerce and other official plugins (Magento 2, Odoo, OpenCart, PrestaShop, …)

- **Test mode:** in the Paymob plugin's settings, choose the **Test Mode** state and enter the **Test** API Key, Secret Key, Public Key, and **Test** Integration IDs. (In Paymob's plugins, Test Mode is the unpublished state; "Enabled" / Live uses the live keys and charges real money.)
- **Run:** place an order on the store and pay with the test details from section 2.
- **Passes when:** the order status changes to paid/processing in the store admin and the transaction appears in the Paymob dashboard (Test mode).
- **WooCommerce — run Store Check (optional, recommended):** on `https://wizard.paymob.com/`, open Store Check. A public scan needs only the store's address. For a deeper check of gateway settings and orders, install the **Paymob Wizard Connector** plugin from `https://wizard.paymob.com/store-doctor/downloads/paymob-wizard-connector.zip` (wp-admin → Plugins → Add New → Upload Plugin). The connector is a separate diagnostic helper, **not** the Paymob payment plugin. See `live-resources.md` section 3.
- **Before going live:** switch the plugin to the live state and enter live keys and live Integration IDs.

### Payment Links (no code)

- **Test mode:** create the link with the Dashboard in **Test** mode and a Test Integration ID, or use the Integration Wizard's sandbox **Payment Links** creator (`https://wizard.paymob.com/`).
- **Run:** open the link and pay with the test details from section 2. The wizard's **"Pay with test card"** button runs the same check in one step.
- **Passes when:** the link shows as paid and the transaction appears in the Dashboard (Test mode).
- For links created through the API, see the QuickLink APIs in the developer docs (`live-resources.md`), and test the webhook exactly as for custom web.

## 4. After a passing test

Switch to live using the step for the integration type above (live keys and Integration IDs, plugin live state, Shopify test mode off). For custom builds nothing else changes — same code, same base URL. Then offer the next steps from **What this skill can help with** in `SKILL.md`.
