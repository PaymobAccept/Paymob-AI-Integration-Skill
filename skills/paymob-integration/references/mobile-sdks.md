# Mobile SDK Integration (iOS / Android / Flutter / React Native)

Source: https://developers.paymob.com/paymob-docs/integration-paths/mobile-sdks (last updated by Paymob: June 1, 2026)

## When to use this path instead of Unified Checkout

Use Paymob's **Mobile SDKs** when the merchant is building a **native mobile app** (iOS, Android, Flutter, or React Native) and wants a checkout experience that feels native — no browser, no WebView redirect. If the merchant instead just needs a payment step inside a mobile *web* view or a hybrid app that's fine being redirected to a browser-based checkout, the regular Unified Checkout flow (`intention-api.md`) works there too and is simpler — only reach for the SDK when a truly native UI is required.

## How this differs from the Web/API flow

The **backend half is identical** — same Intention creation call, same merchant onboarding, same HMAC-verified callback as the source of truth. The only thing that changes is **how the checkout UI is presented to the customer**: instead of redirecting a browser to the Unified Checkout URL, the mobile app hands the `client_secret` to Paymob's native SDK, which renders the payment UI in-app.

## Integration flow

1. **Backend: Create a Payment Intention** — identical to the web flow. `POST` to the Intention endpoint (see `intention-api.md` for the full request shape: amount in cents, currency, `payment_methods` Integration ID(s), `items`, `billing_data`, etc.). The response's `client_secret` is what gets passed to the mobile app — never create the Intention from inside the mobile app itself; it must come from your backend, authenticated with the Secret Key, so the Secret Key never ships inside the app binary.

2. **Mobile app: Initialize the SDK** — using the `client_secret` received from your backend, initialize the Paymob Mobile SDK (iOS, Android, Flutter, or React Native, depending on the merchant's stack). No sensitive payment data is handled by the app itself at this stage — this keeps the app outside PCI scope.

3. **Mobile app: Present the checkout UI** — the SDK presents one of two UI modes:
   - **Normal (Hosted) Checkout** — the SDK shows Paymob's full checkout screen as a separate native screen.
   - **Embedded Checkout** — the SDK renders the checkout UI inside a view you configure within your own app screen.
   Ask the merchant which they want; both handle card entry, 3D Secure, and other authentication inside the SDK — the merchant's app code never touches raw card data either way.

4. **Backend: Handle the callback** — exactly like the web flow. Paymob POSTs the transaction result to your `notification_url`. **This backend callback is the source of truth** — verify its HMAC (see `hmac-verification.md`) before updating order state.

5. **Mobile app: Handle the SDK result** — separately, the SDK itself returns a status to the app once the payment attempt finishes. **Use this only to update the UI** (show a success/failure screen to the customer) — never to confirm the payment or trigger fulfillment. Only the verified backend callback should drive actual order/business logic. Treat the SDK result the same way you'd treat the web flow's `redirection_url` query params: useful for UX, not authoritative.

6. **(Optional) Transaction Inquiry fallback** — same as the web flow; if a backend callback doesn't arrive in a reasonable window, pull status directly (see `transaction-inquiry.md`).

## Platform-specific SDK setup

Paymob provides native SDKs for **iOS, Android, Flutter, and React Native**. The exact installation step (CocoaPods/SPM for iOS, Gradle dependency for Android, pub package for Flutter, npm package for React Native) and initialization API calls are platform-specific — pull the current SDK package name, version, and init code sample from `https://developers.paymob.com/paymob-docs/developers/mobile-sdks/overview` and the platform-specific sub-pages before writing app code, rather than guessing package names or method signatures, since SDK APIs are versioned and can change independently of this skill.

## Notes for the coding agent

- Time-to-launch and technical level for Mobile SDKs is the highest of Paymob's integration options (days–weeks, per Paymob's own integration-options comparison) — set that expectation with the merchant up front, especially compared to Unified Checkout (days) or e-commerce plugins (hours).
- Onboarding (Phase 1 in the main skill) is unchanged — same dashboard, same credentials (API Key, Secret Key, Public Key, HMAC Secret from Settings → API Keys; Integration IDs from Settings → Payment Integrations).
- Testing (Phase 3, `test-credentials.md`) is unchanged — use the same sandbox test cards inside the SDK's checkout UI during QA.
- Always confirm test vs live mode matches between the Secret Key used to create the Intention and the Integration ID(s) selected — same 404 risk as the web flow.
