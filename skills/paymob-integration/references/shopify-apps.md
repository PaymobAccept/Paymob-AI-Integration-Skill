# Paymob on Shopify — App-Based Integration

If the merchant's store runs on **Shopify**, do not build a custom Intention API integration (no code, no API keys to wire up manually). Paymob ships as installable **Shopify apps** — the integration work is choosing the right app(s), installing them, and configuring settings inside Shopify admin. Each app's installation flow also handles Paymob merchant onboarding itself.

## Available apps

| App | Type | Covers | Region | Install link |
|---|---|---|---|---|
| **Paymob - Native Card Checkout** | On-site (embedded) | Cards only — no BNPL, no installments, no wallets | Egypt, UAE, KSA, Oman | `https://accounts.shopify.com/store-login?no_redirect=true&redirect=%2Fadmin%2Fsettings%2Fpayments%2Falternative-providers%2F26640385` |
| **Paymob Accept** | Off-site (redirect) | All Paymob payment methods (cards, wallets, BNPL, Kiosk, etc.) via Unified Checkout | Egypt, UAE, KSA, Oman | `https://accounts.shopify.com/store-login?no_redirect=true&redirect=%2Fadmin%2Fsettings%2Fpayments%2Falternative-providers%2F1059519` |
| **Sympl** | Off-site (redirect), standalone BNPL | Sympl installment payments only | Egypt only | `https://accounts.shopify.com/store-login?no_redirect=true&redirect=%2Fadmin%2Fsettings%2Fpayments%2Falternative-providers%2F11993089` |
| **valU** | Off-site (redirect), standalone BNPL | valU installment payments only | Egypt only | `https://accounts.shopify.com/store-login?no_redirect=true&redirect=%2Fadmin%2Fsettings%2Fpayments%2Falternative-providers%2F13631489` |

## Choosing which app(s) to recommend

Ask the merchant what they need, then map it:

1. **"I just want card payments, embedded in my checkout (customer never leaves my site)"** → **Paymob - Native Card Checkout** only. Note the tradeoff up front: this app handles cards only — no wallets, no BNPL/installments. If the merchant wants those too, they'll need to add Paymob Accept (off-site) alongside it, or accept the cards-only limitation.
2. **"I want to offer all of Paymob's methods (cards, wallets, BNPL, Kiosk) without managing separate integrations"** → **Paymob Accept** (off-site). Customers are redirected to Paymob's Unified Checkout, which surfaces every method enabled on the merchant's Paymob account.
3. **"I specifically want Sympl or valU installments available on Shopify, in Egypt"** → these are **separate, standalone apps**, not features toggled inside Paymob Accept. Install **Sympl** and/or **valU** directly. A merchant can run these alongside Paymob - Native Card Checkout or Paymob Accept — Shopify supports multiple alternative payment providers active at once, so layering Sympl/valU on top of either card option is normal, not a conflict.
4. **Merchant is outside Egypt and asks for Sympl/valU** → not available; these two apps are Egypt-only. Cards, wallets, and other BNPL options (e.g. Tabby/Tamara, if enabled on the merchant's Paymob account) are still reachable through Paymob Accept in UAE/KSA/Oman.

## What the AI agent actually does here

Since this is app installation, not code integration, your job is to:

1. Confirm which app(s) fit the merchant's needs (above).
2. Give them the exact install link(s) — these go through Shopify's own login/redirect flow straight to the alternative-payment-providers settings page for that specific app, so just hand the merchant the link; there's nothing to build.
3. Tell them: installing the app starts the **Paymob merchant onboarding flow as part of the install process** — they do not need to separately complete the standalone web onboarding flow (the `onboarding.paymob.com` link) when going the Shopify route. The app's own setup screens collect the business/verification info needed.
4. After installation, remind them to check in **Shopify Admin → Settings → Payments** that the new provider shows as active, and to verify it's in the correct mode (test vs live, if the app exposes that toggle) before going live.
5. There is no HMAC verification, callback handling, or Intention API code for the merchant to write in this path — Shopify and the Paymob app handle the payment flow and order status updates internally. Do not write custom webhook/HMAC code for a Shopify store going through these apps — only suggest custom Intention API code (Phase 2 in the main skill) if the merchant explicitly wants a fully custom backend instead of these apps (uncommon for a standard Shopify store).
6. If the merchant wants to combine more than one app (e.g. Paymob Accept + valU + Sympl), just walk them through installing each — there's no extra glue code required between them; Shopify lists each as an independent payment option at checkout.

## When to still use the rest of this skill on a Shopify store

The custom-code phases (Phase 2 Intention API, HMAC verification, Transaction Inquiry) are only relevant if the merchant is explicitly building a **custom checkout experience outside Shopify's native checkout** (e.g. a headless storefront calling Shopify's Storefront API with a fully custom payment step) and intentionally bypassing these apps. Confirm that's really their situation before reaching for custom API code on a Shopify project — it's rare and adds real maintenance burden compared to the apps above.
