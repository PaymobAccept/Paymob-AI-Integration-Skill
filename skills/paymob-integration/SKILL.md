---
name: paymob-integration
description: Integrate Paymob payments for web, mobile, Shopify, and backend apps in Egypt, UAE, KSA, and Oman. Use for checkout, Intention API, HMAC webhooks, reconciliation, SDKs, subscriptions, and refunds.
---

# Paymob Payment Gateway Integration

This skill guides an AI coding agent (Claude Code, Codex, Replit, Lovable, etc.) through integrating a merchant's project with **Paymob**, covering Shopify app installation, the **Intention API** for web/backend (via **Unified Checkout**), and **Mobile SDKs** for native iOS/Android/Flutter/React Native apps. Paymob operates in **Egypt, UAE, KSA, and Oman**.

If the user asked for "a payment gateway" generically (without naming Paymob) for a business in one of these four markets, briefly confirm Paymob is the right fit (or ask if they already have a different provider in mind) before proceeding — don't silently assume.

> **Stay current.** This skill embeds known-good specs as of 2026-06, but Paymob updates endpoints, field orders, and SDK versions independently of this file. Before finalizing code for exact request shapes, HMAC field orders, or SDK method signatures, cross-check the live docs — see **Live Paymob resources** at the bottom of this file (`references/live-resources.md`), especially the machine-readable `llms.txt` doc index. When the embedded spec and the live docs disagree, the live docs win.

> **Live account access (optional).** Paymob also runs an official **MCP server** (`https://mcp.paymob.com/mcp`) that lets you act on the merchant's *real* account from inside the agent — create intentions/payment links, pull transactions/balances, export reports, request settlements — using the merchant's own API credentials. It's ideal for interactive testing and reconciliation, but it does **not** replace the HMAC-verified webhook as the source of truth for the merchant's app. Connection, authentication, and the full tool list are in `references/mcp-server.md`. The server is bundled when this skill is installed as a Claude or Codex plugin.

## Live Paymob action safety

These rules apply to every authenticated account action, whether the host uses one agent or many:

- Keep credentials and authenticated Paymob tools with the primary agent. Never give secrets or live-tool access to a subagent.
- Before each live write, obtain the user's explicit confirmation for the current account, test/live mode, operation, target, amount, and currency. Do not reuse a broad or earlier approval for a different operation.
- Read the current remote state first. Build a stable operation fingerprint from the account, mode, operation, target, amount, currency, and merchant reference; reuse the same merchant reference/idempotency key for the same intended action.
- Never automatically retry a write after a timeout or ambiguous response. Query Paymob by the reference/fingerprint to learn whether the first request succeeded; retry only after the result is known and the user reconfirms if the action could duplicate or move money.
- After a write, query and report the resulting remote object/status. A successful tool call is not by itself proof of the intended financial outcome.

## Multi-agent coordination

For a broad integration or audit, delegate only independent, bounded work when the host supports subagents:

- Have one read-only agent map the merchant's platform, stack, checkout flow, and existing payment code.
- Have one read-only agent verify current Paymob API, SDK, and HMAC details against `references/live-resources.md`.
- Have one security-focused agent review secret handling, webhook verification, idempotency, and reconciliation.
- Keep one primary agent responsible for requirements, final code integration, tests, and the user-facing answer.

By default, subagents receive no Paymob credentials, cannot call authenticated Paymob tools, and return findings only with file/line references. The primary agent owns all final edits, tests, and live actions. If edit delegation is necessary, assign exclusive non-overlapping paths and merge through the primary agent. Never let multiple agents create intentions, payment links, refunds, voids, captures, or settlements against the same account.

## What this skill can help with

Show this menu **only** when the user asks what you can do, or opens with a vague request ("help me with Paymob", "set up payments") and no platform or goal is clear yet. Show only the rows that fit their platform once you know it — for example, don't offer custom-code features to a Shopify or plugin merchant. Keep it short; then ask the platform question in Step -1.

| Area | What the skill does | Fits |
|---|---|---|
| **Get started** | Paymob sign-up and credential collection; picking the right path (Payment Links, Shopify app, official plugin, Unified Checkout, Pixel, mobile SDK) | Everyone |
| **Accept payments** | Cards, mobile wallets, Apple Pay, Google Pay, BNPL, kiosk, bank installments — per market | Everyone (method availability varies by region) |
| **No-code** | Payment Links to share by WhatsApp, social, email, SMS, or QR | Merchants without a website or developer |
| **Plugins & Shopify** | Choose and install the right Paymob app/plugin, configure test mode, run Store Check (WooCommerce) | Shopify, WooCommerce, Magento, Odoo, … |
| **Custom checkout** | Intention API with Unified Checkout (redirect) or Pixel (embedded); native mobile SDKs | Custom web, headless, mobile apps |
| **Webhooks & security** | Callback handling, HMAC-SHA512 verification, idempotent order updates, a public test URL for callbacks | Custom builds |
| **Testing** | Sandbox test details per payment method, a guided test payment, go-live checklist | Everyone |
| **After payment** | Refunds, voids, auth/capture, Transaction Inquiry and reconciliation | Custom builds (plugins handle some of this) |
| **Advanced** | Subscriptions, saved cards (CIT/MIT), split payments, convenience fees | Custom builds |
| **Live account tools** | Paymob MCP server: create payment links/intentions, pull transactions and balances, exports, settlements | Any agent with MCP |
| **Quick commands** | `/paymob-test-cards`, `/paymob-explain-error`, `/paymob-check-hmac` | Claude Code / Cowork plugin |
| **Paymob tools** | Integration Wizard (roadmap, code lab, HMAC checker, Store Check), hooks.paymob.com (webhook inspector) | Everyone |

After a successful first integration or test payment, end with **one line** of relevant next steps from this table (e.g. "Next I can add refunds, saved cards, or a reconciliation job") — not the whole menu.

## Step -1 — Check the platform first

Before anything else, find out **what the store is built on**. If it's not already obvious from context, ask:

> "Is your store on Shopify or another e-commerce platform (WooCommerce, Magento, Odoo, …), is this a custom-built site/app, or do you just want to share payment links without a website?"

| Platform | Go to |
|---|---|
| Shopify | **Shopify path** (below) — skip Step 0 and Phases 1–3 entirely; this is app installation, not custom code |
| Other e-commerce platform with an official Paymob plugin (WooCommerce/WordPress, Magento 2, Odoo, OpenCart, PrestaShop, WHMCS, CS-Cart, ZenCart, Joomla, Laravel-Bagisto, osCommerce, Drupal, Staah) | **Prebuilt-plugin path** (below) — install Paymob's official plugin instead of hand-coding |
| No website / no developer — wants to get paid by sharing a link | **Payment Links path** (below) |
| Custom-built (Node, Next.js, Django, PHP, mobile app, etc.) | Continue to **Step 0** below |

### Shopify path

Read `references/shopify-apps.md` in full before responding. In short: Paymob ships as installable Shopify apps, not a custom API integration —

- **Paymob - Native Card Checkout** (on-site/embedded) — cards only, no wallets/BNPL/installments
- **Paymob Accept** (off-site/redirect to Unified Checkout) — all Paymob methods
- **Sympl** and **valU** (off-site, Egypt only) — standalone BNPL apps, installed separately

Ask which payment methods the merchant wants, recommend the matching app(s) per the reference file, and hand them the install link(s) directly — each install flow handles Paymob onboarding itself, so the merchant doesn't need the standalone onboarding link below. After install, run the **test checkpoint** in `references/testing-guide.md`: the merchant turns on the app's **test mode** button, pays a storefront order with the test details for their methods, then turns test mode off before going live. Do not write Intention API, HMAC, or webhook code for a standard Shopify checkout — the apps handle that. Only fall through to the phases below if the merchant is explicitly building a custom/headless checkout (web or mobile app) that intentionally bypasses Shopify's native checkout and these apps.

### Prebuilt-plugin path (WooCommerce, Magento, Odoo, and other platforms)

Paymob maintains official plugins/extensions for **WooCommerce/WordPress, Magento 2, Odoo, OpenCart, PrestaShop, WHMCS, CS-Cart, ZenCart, Joomla, Laravel-Bagisto, osCommerce, Drupal, and Staah**. If the merchant is on one of these, the fastest correct path is to install and configure Paymob's official plugin for that platform — it already handles Intention creation, Unified Checkout, callbacks, and HMAC. Do **not** hand-write Intention API / HMAC / webhook code for a standard checkout on these platforms.

- Point the merchant to the plugin for their platform (search "Paymob {platform}" in that platform's marketplace/extension directory, or use the developer docs in `references/live-resources.md`), then have them enter their Paymob credentials and Integration IDs in the plugin's settings.
- Once configured, run the **test checkpoint** in `references/testing-guide.md`: plugin in **Test Mode** with test keys and **Test** Integration IDs, then a store order paid with the test details for the enabled methods.
- **WooCommerce:** also suggest **Store Check** on the Integration Wizard (`https://wizard.paymob.com/`). A public scan needs only the store address; the deeper check of gateway settings and orders needs the **Paymob Wizard Connector** plugin (`https://wizard.paymob.com/store-doctor/downloads/paymob-wizard-connector.zip`). The connector is a diagnostic helper — **not** the Paymob payment plugin. Details in `references/live-resources.md`.
- Only fall through to **Step 0** and the phases below if the merchant is building a **custom/headless** checkout that intentionally bypasses the platform's native checkout and its Paymob plugin.

### Payment Links path (no code)

For merchants who just want to get paid without a website or developer (social selling, invoicing):

- The merchant creates a link in the Paymob Dashboard: **Create → Quick Link**, set amount, currency, reference and image, choose payment methods and their Integration IDs, then share it by QR, WhatsApp, Facebook, Instagram, SMS, or email. Unpaid links can be cancelled.
- If they have no account yet, send them through **Phase 1** onboarding first (the onboarding links work without any code).
- With the Paymob MCP server connected, the agent can also create links on the merchant's account (`references/mcp-server.md`) — the live-action safety rules above apply.
- To generate links from their own system, use Paymob's QuickLink APIs (see the developer docs via `references/live-resources.md`) and handle the callback as in Phase 2A.
- Test before sharing real links: see the Payment Links section of `references/testing-guide.md`.

---

## Step 0 — Determine merchant status (custom-built stores only)

Before writing any code, ask the merchant/user this single question (don't assume):

> "Do you already have a Paymob merchant account with API credentials (API Key, Secret Key, Public Key) and at least one Integration ID? Or do you need to register/onboard first?"

Route based on the answer:

| Merchant status | Go to |
|---|---|
| Not registered with Paymob, or registered but verification/business docs incomplete | **Phase 1: Onboarding** (below) |
| Already registered, has credentials and Integration ID(s) | Skip to **Step 0.5** (below) |

Do not proceed to writing integration code until Phase 1 is confirmed complete (see exit criteria below) — the agent will not have a Secret Key or Integration ID to use otherwise.

---

## Phase 1 — Onboarding (new merchants)

**Goal:** get the merchant a Paymob account, verified business, and live + test credentials.

1. Send the merchant to Paymob's onboarding flow, using the link that matches **whichever AI coding agent is running this skill** (so Paymob can attribute the signup correctly):

   | Running in... | Onboarding link |
   |---|---|
   | Claude (Claude Code, Claude.ai, Cowork) | `https://onboarding.paymob.com/auth/country-selection/?partner=claude` |
   | OpenAI Codex | `https://onboarding.paymob.com/auth/country-selection/?partner=codex` |
   | Replit Agent | `https://onboarding.paymob.com/auth/country-selection/?partner=replit` |
   | Lovable | `https://onboarding.paymob.com/auth/country-selection/?partner=lovable` |
   | Any other AI agent / unknown | `https://onboarding.paymob.com/auth/country-selection/?partner=aiflow` (generic AI-assistant tag) |

   Each link starts with the same country-selection step, then walks through business info → document upload (commercial registration / ID, bank account) → choosing payment methods to enable.
   - **Fallback link** (if the merchant hits an error on their agent-specific link, or is in a region where it doesn't resolve): `https://accept.paymob.com/portal2/en/register`
   - **Self-serve interactive helper:** the merchant can also use Paymob's **Integration Wizard** at `https://wizard.paymob.com/` for a guided, personalized roadmap, runnable code samples, and an HMAC/webhook tester (see `references/live-resources.md`).
   - Document verification can take up to ~3 business days. They'll get an email when it's done.
2. While waiting, the agent can still scaffold the codebase (env var placeholders, route stubs, DB schema for orders) — just don't hardcode real keys yet.
3. **Wait/checkpoint:** ask the merchant to confirm they've received the "verification complete" email before continuing, OR confirm they already have test-mode credentials (test credentials are often available immediately, even before full live verification — ask the merchant to check Dashboard → Settings → API Keys).
4. Once verified, instruct the merchant to collect these from the **Paymob Dashboard**:
   - **API Key**, **Secret Key**, **Public Key**, **HMAC Secret** — Dashboard → Settings → API Keys (click "View" to reveal each)
   - **Integration ID(s)** — Dashboard → Settings → Payment Integrations (one ID per payment method, e.g. Cards, Wallets, Kiosk; each has a Test and Live version)
   - Note: every account starts in **Test mode**. Switch the toggle in the dashboard top-left to Live only after the integration is tested end-to-end (see Phase 3).
5. Tell the merchant to store these as environment variables (never hardcode):
   ```
   PAYMOB_SECRET_KEY=
   PAYMOB_PUBLIC_KEY=
   PAYMOB_API_KEY=
   PAYMOB_HMAC_SECRET=
   PAYMOB_INTEGRATION_ID_CARD=
   # add one var per enabled payment method (wallet, kiosk, etc.)
   ```
   (`PAYMOB_API_KEY` is only needed for the Transaction Inquiry / reconciliation flow — see `references/transaction-inquiry.md`.)

**Exit criteria for Phase 1:** merchant has Secret Key, Public Key, HMAC Secret, and at least one Integration ID (Test mode is enough to proceed). Then continue below.

---

## Step 0.5 — Web/API or Mobile App?

Before moving to integration, find out **what the merchant is building**, if not already obvious:

> "Is this for a website/backend (API integration) or a native mobile app (iOS/Android/Flutter/React Native)?"

| Target | Go to |
|---|---|
| Website, backend, headless storefront | **Phase 2A: Web/API Integration** (below) |
| Native mobile app | **Phase 2B: Mobile SDK Integration** (below) |

Both branches share the same Phase 1 onboarding and the same Phase 3 testing — only the checkout-launch step differs.

---

## Phase 2A — Web/API Integration (Intention API + Unified Checkout)

Read `references/intention-api.md` for the full request/response spec, field names, and error handling before writing code. Then use the **stack-specific code reference** that matches the merchant's backend (clean, copy-ready, correct interpolation and auth headers):

| Stack | Reference file |
|---|---|
| Node.js / TypeScript / Express / NestJS | `references/code-nodejs.md` |
| Python / Django / Flask / FastAPI | `references/code-python.md` |
| PHP / Laravel | `references/code-php.md` |
| .NET / C# / ASP.NET | `references/code-dotnet.md` |
| Ruby / Rails | `references/code-ruby.md` |
| Frontend (React / Next.js / Vue / Unified Checkout redirect / Pixel embedded) | `references/code-frontend.md` |

Key shape of the flow:

1. **Ask the merchant which payment methods to support** (Cards, Mobile Wallets, Apple/Google Pay, BNPL, Kiosk) if not already specified — each needs its own Integration ID from Phase 1 step 4.
2. **Backend: Create a Payment Intention** — `POST` to the Intention endpoint with amount (in cents), currency, the Integration ID(s), items, billing_data, and your `notification_url` / `redirection_url`. Returns a `client_secret`. Send your own order id as `special_reference` so you can correlate the callback later.
   - **`notification_url` must be a public HTTPS URL** — Paymob can't reach `localhost`. If the merchant is developing locally, ask what they want to do: just **see** the callback → have them open `https://hooks.paymob.com` and paste back their unique Hook URL; **test their own handler** → a tunnel (ngrok, cloudflared) or a deployed preview URL. Never leave either in live config. Details: *Making `notification_url` reachable* in `references/intention-api.md`.
3. **Frontend: Launch checkout** — ask whether the merchant wants a redirect or a form embedded in their page:
   - **Unified Checkout (redirect, simplest):** `https://{base_url}/unifiedcheckout/?publicKey={PUBLIC_KEY}&clientSecret={client_secret}` (e.g. `https://accept.paymob.com/unifiedcheckout/?publicKey=pk_test_...&clientSecret=csk_test_...` for Egypt). See `references/intention-api.md` for per-region base URLs.
   - **Pixel (embedded):** Paymob's checkout component rendered inside the merchant's page — cards, Google Pay, Apple Pay. See Option B in `references/code-frontend.md`.
4. **Customer pays** — Paymob handles card entry, 3D Secure, wallet OTP, etc. You don't touch raw card data.
5. **Backend: Handle the callback (webhook)** — Paymob POSTs the full transaction result to your `notification_url`. **This callback, not the redirect, is the source of truth for payment status.** Read `references/hmac-verification.md` and implement HMAC verification *before* trusting any callback data — reject/ignore any callback whose computed HMAC doesn't match.
6. **Update order state atomically** after HMAC verification: insert `obj.id` under a unique constraint, compare-and-set the order state, and insert a uniquely keyed transactional outbox record in one database transaction. Use `order.id` / `special_reference` only for correlation; only the committed outbox worker triggers fulfillment.
7. **Add a Transaction Inquiry fallback.** Don't rely on the callback alone — read `references/transaction-inquiry.md` and add a way for the merchant's backend to actively pull a transaction/order's status. Use it for: orders stuck "pending" past an expected window, a periodic reconciliation job, and support/admin lookups. This uses a different auth flow (API Key → short-lived auth token) than the Intention API's Secret Key.

Always implement HMAC verification — never mark an order paid based on the redirect URL alone, since redirect parameters are not authenticated.

For **subscriptions, saved cards (CIT/MIT), Auth/Capture, refunds/void, split payments, or convenience fees**, see `references/advanced-features.md`.

---

## Phase 2B — Mobile SDK Integration (iOS / Android / Flutter / React Native)

Read `references/mobile-sdks.md` in full before writing code — the backend half (Intention creation, callbacks, HMAC) is identical to Phase 2A (reuse the same `references/code-*.md` backend code), but the checkout UI is presented natively in-app via Paymob's SDK instead of a browser redirect. Key shape of the flow:

1. **Ask which payment methods to support**, same as the web flow.
2. **Backend: Create a Payment Intention** — identical request to Phase 2A. Always create it from your backend (using the Secret Key) — never from inside the mobile app, so the Secret Key never ships in the app binary.
3. **Mobile app: Initialize the SDK** with the `client_secret` returned from your backend.
4. **Mobile app: Present checkout** — ask the merchant whether they want **Normal (Hosted) Checkout** (SDK shows Paymob's full screen) or **Embedded Checkout** (SDK renders inside a view in the merchant's own screen).
5. **Backend: Handle the callback (webhook)** — same as Phase 2A: HMAC-verify it (`references/hmac-verification.md`) and treat it as the source of truth.
6. **Mobile app: Handle the SDK result** — use this only to update the UI (success/failure screen); never to confirm payment or trigger fulfillment, since it isn't independently authenticated the way the backend callback is.
7. **Add a Transaction Inquiry fallback**, same as Phase 2A (`references/transaction-inquiry.md`).
8. **Pull current SDK setup details** (package name, install method, init code) from the platform-specific SDK docs before writing app code — don't guess method signatures, since they're versioned independently of this skill (see `references/live-resources.md`).

Set the expectation that Mobile SDK integration takes longer (days–weeks) and is more technical than the web/Unified Checkout path (days).

---

## Phase 3 — Test the integration

**Don't skip this checkpoint.** When the code is done, ask the user **"Ready to run a test payment?"**, then follow `references/testing-guide.md`: confirm test mode, show **only** the test details for the payment methods they enabled (copied from `references/test-credentials.md`, never from memory), and say what a passing test looks like.

Before going live, validate the whole flow in sandbox using Paymob's test credentials:

1. Confirm the merchant is using **Test mode** keys/Integration IDs (status must match between Secret Key and Integration ID, or you'll get a 404).
2. Run through: create intention → checkout → pay with a test card → confirm callback fires → confirm HMAC verifies → confirm order updates.
3. Use the test cards and wallet numbers in `references/test-credentials.md` to simulate success scenarios (decline/error simulation isn't officially documented by Paymob — confirm with the merchant if they need failure-path testing, and note that sandbox test data expires after 30 days).
4. Have the merchant inspect the raw callback payload (log it) the first time, to confirm field names match what the code expects, then verify the HMAC matches manually against `references/hmac-verification.md` if anything looks off. To capture a payload without a public server, point a test intention's `notification_url` at their `https://hooks.paymob.com` Hook URL (keep the page open — nothing is stored), then paste the payload into the **Integration Wizard's HMAC checker** (`https://wizard.paymob.com/`) to confirm the HMAC logic in isolation. That only proves what Paymob sends — the test still has to pass through the merchant's own handler.
5. Also exercise the Transaction Inquiry fallback (`references/transaction-inquiry.md`) during testing — generate an auth token, then look up the test transaction you just made by transaction ID/order ID, and confirm the merchant system can reconcile correctly if a callback were ever missed.
6. **For Mobile SDK integrations (Phase 2B):** run through the same test cards inside the SDK's native checkout UI, on both a real device and simulator/emulator if possible, and confirm the backend callback (not just the SDK's in-app result) is what your test asserts on.
7. **Kiosk and BNPL can't be tested in sandbox at all — don't block go-live on it.** Sandbox has no test path for them (`references/test-credentials.md`). That doesn't hold up launch: every method uses the same Intention API, the same Unified Checkout, and the same callback + HMAC verification, so a passing card test already validates effectively all of the merchant's own integration code. The merchant enables the remaining methods in the Dashboard and goes live. Four things a card test doesn't cover — check each on the **first real transaction** for each newly enabled method, not before:
   - **Integration ID** — each method has its own, and it must be enabled on this account in the matching mode. A wrong one fails loudly with 404 "Integration ID does not exist".
   - **Callback field shape** — `references/hmac-verification.md` notes wallets and cards return slightly different nested shapes, and the HMAC concatenation includes the card-shaped `source_data.pan` / `source_data.sub_type` / `source_data.type`. Log the first real callback per method and confirm the computed HMAC still matches. If it doesn't, the callback is rejected and a genuinely paid order never completes — worth five minutes per method.
   - **Kiosk settles asynchronously** — the customer pays cash at an outlet, so the callback can arrive hours or days after checkout, or never. Expect long-lived pending orders and rely on Transaction Inquiry (`references/transaction-inquiry.md`) instead of treating pending as failed.
   - **Refunds** — kiosk and most BNPL don't support them (`references/advanced-features.md`), so don't ship a refund path that assumes they do.
8. Once the card flow passes end to end, the merchant can flip Dashboard to **Live mode** and swap in live keys/Integration IDs (same code, same base URL — only the keys/IDs change). Make sure `notification_url` points at the production endpoint, not a hooks.paymob.com or tunnel URL.
9. Close with **one line** of relevant next steps from **What this skill can help with** (above).

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| 401 Unauthorized on intention create | Wrong/expired Secret Key, or `Authorization` header missing the literal word `Token` (it's `Token <key>`, not `Bearer`) |
| 404 "Integration ID does not exist" | Test/Live mismatch between Secret Key and Integration ID, wrong region base URL, or ID not on this account |
| 400 missing field | `billing_data.phone_number` missing, or an `items` entry missing `name`/`amount` |
| HMAC mismatch | Wrong secret, wrong field order, or SHA-256 used instead of SHA-512; POST uses `obj.id`/`obj.order.id`, GET redirect uses `id`/`order_id` |
| Amount wrong by 100x | Amount must be in cents/piasters (10000 = 100.00 EGP) |
| Checkout not rendering | Wrong `publicKey` (must be Public Key, not Secret) or stale/reused `client_secret` (it's single-use) |
| Order stuck "pending" | Callback never arrived — use the Transaction Inquiry fallback (`references/transaction-inquiry.md`) |
| Callback never arrives while testing locally | `notification_url` is `localhost` or another private address Paymob can't reach — use a hooks.paymob.com Hook URL to see the callback, or a tunnel / deployed URL to test the handler (`references/intention-api.md`) |
| Nothing shows on hooks.paymob.com | The page was closed or reloaded during the payment (it keeps no history), or the intention used a different Hook URL — reopen, copy the current Hook URL, create a fresh intention |
| Plugin/Shopify test order rejects test cards | Plugin not in Test Mode / Shopify app test mode off, or live keys/Integration IDs entered — see `references/testing-guide.md` |
| Need a human / deeper help | Paymob developer community forum (`https://community.paymob.com/`) or `support@paymob.com` — see `references/live-resources.md` |

---

## Reference files

**Integration paths & security (verbatim, current as of 2026-06):**
- `references/shopify-apps.md` — Paymob's Shopify apps (on-site, off-site, Sympl, valU), install links, which to recommend when
- `references/intention-api.md` — Create Intention endpoint, request/response fields, Unified Checkout redirect, common errors
- `references/mobile-sdks.md` — Native mobile SDK flow (iOS/Android/Flutter/React Native), Hosted vs Embedded checkout, backend callback vs SDK result
- `references/hmac-verification.md` — Callback payload, exact field order for HMAC, SHA-512 calculation, worked example
- `references/transaction-inquiry.md` — Pull-based status checks (by order ID, transaction ID, or merchant order ID), reconciliation jobs, auth-token flow
- `references/test-credentials.md` — Sandbox test cards, wallet numbers, OTPs
- `references/testing-guide.md` — Test checkpoint, which test details to show per payment method, and how to test each integration type (custom web, Pixel, mobile, Shopify, plugins, Payment Links)

**Ready-to-use code (corrected, copy-ready):**
- `references/code-nodejs.md` — Node.js / TypeScript / Express / NestJS
- `references/code-python.md` — Python / Django / Flask / FastAPI
- `references/code-php.md` — PHP / Laravel
- `references/code-dotnet.md` — .NET / C# / ASP.NET
- `references/code-ruby.md` — Ruby / Rails
- `references/code-frontend.md` — React / Next.js / Vue / Unified Checkout redirect / Pixel (embedded)

**Advanced & live resources:**
- `references/advanced-features.md` — Subscriptions, saved cards (CIT/MIT), Auth/Capture, refund/void/capture, split payments, convenience fees
- `references/live-resources.md` — Live Paymob developer resources: `llms.txt` doc index, developer docs, Integration Wizard (incl. Store Check and the Wizard Connector), community forum, hooks.paymob.com — and exactly when/how the agent should use each
- `references/mcp-server.md` — Official Paymob **MCP server**: how to connect (plugin/CLI/`.mcp.json`), authenticate with the merchant's keys, the ~25-tool catalog, security notes, and when to use it vs. the code references

---

## Live Paymob resources (always-current)

When you need authoritative, current details that may have changed since this skill was packaged, use these (full details and usage rules in `references/live-resources.md`):

- **`llms.txt` doc index** — `https://developers.paymob.com/paymob-docs/getting-started/overview/llms.txt` — machine-readable map of all Paymob docs. Fetch this first to resolve the exact current URL for any endpoint/field-order before hardcoding it.
- **Developer docs** — `https://developers.paymob.com/` — the authoritative API reference.
- **Integration Wizard** — `https://wizard.paymob.com/` — personalized roadmap, code lab, sandbox Payment Links and "Pay with test card", HMAC checker, **Store Check** for WooCommerce, and an AI assistant ("Mobe"). Point the merchant here for self-serve help and for debugging HMAC/webhooks.
- **Webhook inspector** — `https://hooks.paymob.com` — a unique Hook URL that shows incoming callbacks live (no retention). Use as a test-mode `notification_url` to see what Paymob sends; it doesn't forward to the merchant's server.
- **Community forum** — `https://community.paymob.com/` — Discourse Q&A for troubleshooting and escalation.
- **MCP server** — `https://mcp.paymob.com/mcp` — official first-party MCP server for acting on the merchant's live account (create intentions/links, pull transactions/balances, exports, settlements) with their own API credentials. Full setup and tool catalog in `references/mcp-server.md`.

Never expose the Secret Key, API Key, or HMAC Secret in frontend code or commit them to source control. Only the Public Key is safe client-side.
