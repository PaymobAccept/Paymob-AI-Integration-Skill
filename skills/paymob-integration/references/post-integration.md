# Post-Integration — Go Live, Operate, Diagnose, and Get Support

The integration phases end at "first test payment passed". This file covers everything **after** that: getting approved for live, running the integration day to day, diagnosing problems with Paymob's own tools, and escalating to Paymob support with a ticket that gets resolved on the first reply.

Sources: Paymob Integration Wizard (`https://wizard.paymob.com/`), Paymob developer docs — *Integration Checklist* (`https://developers.paymob.com/paymob-docs/getting-started/integration-checklist.md`) and *New Dashboard* (`https://developers.paymob.com/paymob-docs/getting-started/new-dashboard.md`). Checked 2026-09. The wizard and dashboard change without notice. If a button or menu named here is gone, say so. Don't invent a replacement path.

The **live action safety** rules in `SKILL.md` apply to every account action below: refunds, voids, captures, settlements, payment links, integrations, and support tickets created through the MCP server.

---

## 1. Go-live readiness

### Paymob's side: the approval path

Paymob's documented path to live has nine sequential stages. The merchant can't skip one, and the agent should not imply that code alone gets them live:

1. **Account creation**: dashboard and test environment access.
2. **Paperwork validation**: business and legal documents reviewed.
3. **Contract finalization**: commercial terms agreed and signed.
4. **Risk approvals**: the risk team assesses the business model and activity.
5. **Integration cycle**: the merchant integrates in the test environment.
6. **Test and validation**: test transactions confirm the flow works.
7. **Technical approval**: Paymob reviews the integration against technical and security requirements.
8. **Live credentials**: production keys and Integration IDs are issued.
9. **Going live**: real customer payments start.

Stages 2–4 and 7–8 are Paymob's. The agent's job is to make stages 5–6 pass cleanly and to hand stage 7 a clean integration.

### Submitting go-live documents from the wizard

On `https://wizard.paymob.com/`, a connected merchant can use **Send your go-live documents**:

- It accepts up to **8 files** (PDF, JPG, or PNG, up to **4 MB each**) and emails Paymob support with the wizard's **setup summary**.
- The wizard states plainly that it **does not collect signatures and this is not live approval**. Don't tell the merchant that uploading here makes them live.
- **Send without documents** sends the setup summary alone. It suits a merchant whose paperwork already went through onboarding who wants Paymob to review the technical setup.

### The wizard's "Switch to live"

**Switch to live** moves the wizard's own tools to live credentials. The merchant must tick *"I understand live mode charges real money. Test cards will not work."* It only works once Paymob has approved the account (`merchant_info.is_live`). If the switch is unavailable, the account is still in stages 2–8 above. The fix is to follow up with Paymob, not to change code.

### Merchant-side go-live checklist (custom builds)

Run this before the merchant flips to live. `/paymob-go-live-check` automates the code half.

| # | Check | How to verify |
|---|---|---|
| 1 | Secrets only in server env vars; nothing committed; only `pk_*` in the frontend | Grep the repo and the built frontend bundle for `sk_`, the HMAC secret variable name, and the API key variable name |
| 2 | **Live** Secret Key paired with **Live** Integration IDs, and the matching regional base URL | The mode mismatch fails as a 404 on intention create |
| 3 | `notification_url` is the production HTTPS endpoint, not hooks.paymob.com, a tunnel, or localhost | Read config for every environment |
| 4 | Callback URL also set per integration in **Dashboard → Settings → Payment Integrations** (plugins and Payment Links rely on this) | Dashboard |
| 5 | HMAC verified (SHA-512, exact field order, timing-safe) **before** any state change | `/paymob-check-hmac` |
| 6 | Idempotency: unique `obj.id`, compare-and-set order state, transactional outbox | `/paymob-check-hmac` item 6 |
| 7 | The order amount is computed **server-side** from the merchant's order record, never taken from the browser | Read the checkout route |
| 8 | Transaction Inquiry fallback for stuck-pending orders, plus a reconciliation job | `transaction-inquiry.md` |
| 9 | The refund/void path matches the enabled methods (kiosk and BNPL don't refund) | `advanced-features.md` payment-methods table |
| 10 | Logs contain no secrets, no full PAN or CVV, and no OTPs; callback bodies are logged only while debugging | Read the logger config |
| 11 | Plugins and Shopify apps have **Test Mode off** and live keys and live Integration IDs entered | Plugin settings |
| 12 | A support contact and a runbook exist (who checks stuck orders, who files tickets) | Section 5 |

After go-live, watch the **first real transaction per payment method**: the Integration ID, the callback shape, and HMAC (see Phase 3, step 7 in `SKILL.md`).

---

## 2. Day-to-day operations (Paymob Dashboard)

Dashboard: `https://accept.paymob.com/portal2/en/login` (Egypt; other regions sign in through their own portal). The new dashboard's main areas are **Home, Transactions, Orders, Quick Links, Settings**.

| Task | Where | Notes |
|---|---|---|
| Find a transaction | **Transactions**. Filter by time period, status (Success / Pending / Declined), currency, payment method, Transaction ID, Order ID, Terminal ID, card fingerprint | The detail view shows transaction and order info, payment method, breakdown, and customer |
| Refund / Void / Capture by hand | **Transactions** → select the transaction → action (available according to its status) | The same live-write rules apply when the agent does it through the API or MCP. Confirm the exact transaction, amount, and currency first |
| Find an order | **Orders**. Filter by status (Paid / Unpaid), Order ID, **Merchant Order ID** (your `special_reference`), phone, last 4 digits | "Delete Order" only **hides** the order from the dashboard; it is not removed from Paymob |
| Manage payment links | **Quick Links**. Filter Paid / Unpaid / Canceled; **Cancel** or **Share** | Cancel unpaid links that should no longer be payable |
| Keys and HMAC secret | **Settings → API Keys** (Secret Key, Public Key, API Key, HMAC Secret) | |
| Integration IDs and callback URLs | **Settings → Payment Integrations**. Switch Live/Test to see each mode's IDs; update callback URLs per integration | |
| Team access | **Settings → Users & Permissions**. Predefined roles: **Admin, Owner, Developer, Finance, Operations, Sales**; custom roles and permissions allowed | Least privilege: developers don't need refund rights in live; remove leavers promptly |

### Refunds in operations

- Prefer refunding from the merchant's **own admin**, calling the refund API. That keeps the merchant's order state and Paymob in sync. A refund made only in the Paymob Dashboard leaves the merchant's database saying "paid" unless reconciliation picks it up.
- Partial refunds pass `amount_cents` less than the original. Track the running refunded total per transaction and never exceed the captured amount.
- After any refund or void, re-read the transaction (Transaction Inquiry or MCP `get_filtered_transactions`) and report the resulting `is_refunded` / `is_voided` state. A 200 response alone doesn't prove the result.

### Balances, transfers, and settlements

- Read-only: MCP `get_merchant_balances`, `get_merchant_transfers`, `get_filtered_transfers`, and `export_transactions`. These are safe for reconciliation and dashboards.
- `request_instant_settlement` **moves money** to the merchant's bank. It needs explicit confirmation of account, mode, amount, and currency every time, and is never automated.
- Settlement schedules, fees, and reserve terms are **contractual** and not in the public docs. Don't state them; send the merchant to their Paymob account manager or support.

### Disputes and chargebacks

Paymob's public developer docs don't document a dispute API or self-serve dispute flow, so disputes go through Paymob support or operations. The agent can help the merchant:

- Assemble an evidence pack: Paymob transaction ID (`obj.id`), Paymob order ID, merchant order ID, amount and currency, timestamp, `is_3d_secure`, customer communication, proof of delivery or service, and the public refund policy URL.
- Reply before the deadline given in Paymob's notice. Don't guess deadlines.
- **Ask Paymob before refunding a transaction that is under dispute.** Refunding and then losing the dispute can debit the merchant twice.

---

## 3. Monitoring and reconciliation

Set these up once the integration is live:

| Signal | Why | Alert when |
|---|---|---|
| HMAC-rejected callbacks | A spike means a rotated or wrong HMAC secret, a new payment method with a different callback shape, or spoofing attempts | Any sustained increase over baseline |
| Orders pending past the expected window | A missed callback, or a kiosk payment not yet made | Older than the method's normal window (kiosk can take days) |
| Intention-create errors (401/404/400) | Key or Integration ID revoked, mode mismatch, or a validation change | Any 401/404 in live |
| Callback-to-order latency | A slow or failing outbox worker | Above your fulfilment SLA |
| Daily reconciliation diff | Paymob's successful transactions vs orders the merchant marked paid | Any non-zero diff |

**Reconciliation job:** once a day, list the previous day's Paymob transactions (Transaction Inquiry, `references/transaction-inquiry.md`; or MCP `export_transactions` / `get_filtered_transactions` by hand) and compare them with the merchant's paid orders by `merchant_order_id`. Fix discrepancies through the same idempotent code path the webhook uses. Never mark an order paid through a separate side path.

The wizard's **Check transactions** shows only the **last 14 days of test-mode** activity. It is a sandbox sanity check, not a live monitoring tool.

---

## 4. Diagnose with Paymob's tools

Match the symptom to the tool. These are human-facing web tools: give the merchant the link and exact steps. Don't try to script them.

| Symptom | Tool | What to do |
|---|---|---|
| HMAC mismatch | **HMAC Signature Troubleshooter** (wizard) | Paste the HMAC hex value, the full webhook payload JSON, and the HMAC secret. Diagnosis runs **entirely in the browser**; nothing is sent to a server. Point the merchant to it rather than asking them to paste the secret into chat |
| Callback not arriving, or unsure what Paymob sends | **hooks.paymob.com** | Use the Hook URL as a **test** intention's `notification_url`, with the page kept open (it keeps no history) |
| "My request shape is wrong", or 400/401/404 on intention create | **Code Lab** (wizard) | Generates the Intention request for Node.js, Python, PHP, Java, or .NET with the merchant's region and settings, **runs it against the sandbox**, and includes a plain-English **Code Walkthrough**, a ready HMAC webhook handler, and auto-generated unit tests (success, 401, 404, 406, network error). Compare its working request with the merchant's failing one |
| Needs a runnable API baseline outside the app | **Export to Postman** (wizard) | Downloads a collection pre-filled with region and settings. Import it, then set the Secret Key in the collection variables (never commit that collection with the key in it) |
| Customer confused by checkout, or choosing redirect vs embedded | **Virtual Showroom** (wizard) | Shows how customers experience **Unified Checkout** vs **Pixel** on a sample storefront |
| WordPress/WooCommerce store: payments failing or misconfigured | **Store Check** (`https://wizard.paymob.com/store-doctor/`) | See below |
| Missing Integration ID for a method (test) | Wizard → **Connect Paymob account** → **Create Integration** | Types: Card (VPC), Mobile Wallet, valU (BNPL), Cash Collection. Enter currency, an optional name, and an HTTPS callback URL. **Wizard-created integrations are always test mode**; live Integration IDs come from Paymob |
| Keys wrong or stale in local code | Wizard → **Retrieve keys** → **Push to Code Lab** | Keys stay in the browser session. The wizard stores secrets for the session only and saves other values in the browser, so on a shared computer clear it afterwards |
| Quick question, code explanation, or security review (Arabic or English, voice or text) | **Mobe** (wizard AI assistant, "Ask Mobe") | Good first stop before a ticket |

### Store Check (Store Doctor)

URL: `https://wizard.paymob.com/store-doctor/`. The flow is three steps: **Connect store → Scan → Findings and fixes**.

- **Public scan** (no login): checks the storefront's HTTPS certificate, Paymob plugin status, callback URL response, and whether a refund policy is linked, then shows a pass/fail checklist. The page notes that WooCommerce isn't required to run it.
- **Connected check** (WordPress): diagnoses gateway settings and orders in depth. Install the **Paymob Wizard Connector** (`https://wizard.paymob.com/store-doctor/downloads/paymob-wizard-connector.zip`) with wp-admin → **Plugins → Add New → Upload Plugin**, activate it, then open Store Check from the **Paymob Wizard** menu in WordPress, or sign in on the wizard with the store URL and WordPress username. The page warns: **"Do not use your WordPress login password."**
- The Connector is a diagnostic helper, **not** the Paymob payment plugin.
- **When to run it:** after first configuration, after **every** plugin, WooCommerce, or theme update, after changing the domain or SSL certificate, and whenever card payments start failing.

---

## 5. Get support: channels and a ticket that gets resolved

### Pick the channel

| Need | Channel |
|---|---|
| Docs question, code explanation, "how do I…" | **Mobe** on `https://wizard.paymob.com/` (instant) |
| Integration Q&A others may have hit | Community forum, `https://community.paymob.com/` |
| Needs Paymob staff: account, transaction, settlement, dispute, go-live status, production incident | **Contact Support** form on the wizard (**Submit Ticket**: Your Name, Email Address, Subject, Message; protected by a security check), or email `support@paymob.com` |
| Terminal or payment issue, from inside the agent, with the MCP server connected | MCP `create_support_ticket` (see below) |
| Go-live paperwork | Wizard → **Send your go-live documents** (section 1) |
| Contract terms, fees, settlement schedule | The merchant's Paymob account manager |
| Feedback on the wizard itself | Wizard feedback form (1–5 rating, optional email) |

The wizard form doesn't show categories or SLAs. Don't promise a response time.

### Draft the ticket (the agent's job)

Draft the ticket for the merchant to send. Fill in what's known from the codebase, logs, and conversation; ask for the rest. Use `/paymob-support-ticket`.

```
Subject: [<Region> · <Test|Live>] <symptom in one line> — <Paymob txn/order ID if any>

Account
- Merchant/account email: <…>        Region: <Egypt|UAE|KSA|Oman>        Mode: <Test|Live>
- Integration path: <Unified Checkout | Pixel | Mobile SDK (platform + SDK version) | Plugin (name + version) | Shopify app | Payment Links>
- Integration ID(s) involved: <…>      Payment method: <card | wallet | Apple Pay | …>

What happened
- Expected: <…>
- Actual: <exact error text / HTTP status / callback behaviour>
- First seen: <date time + timezone>   Frequency: <every time | intermittent | one order>
- Scope: <one customer | all customers | one method>   Business impact: <e.g. "all card checkouts failing since 14:10">

Identifiers (for each affected payment)
- Paymob transaction ID (obj.id): <…>   Paymob order ID: <…>   Merchant order ID (special_reference): <…>
- Amount + currency: <…>   Timestamp: <…>

Evidence (redacted)
- Request: <method + path + body with secrets removed>
- Response: <status + body>
- Callback payload (if relevant): <JSON with PII masked>

Already tried
- <e.g. HMAC Signature Troubleshooter: match/mismatch · Store Check findings · Code Lab sandbox request works/fails · keys re-checked for mode>
```

**Redaction is mandatory.** Never put these in a ticket, chat, or file: the Secret Key, API Key, HMAC Secret, auth tokens, full card numbers, CVV, OTPs or MPINs, or customer passwords. Mask customer phone and email (for example `+2010••••7890`) unless Paymob needs them to find the payment; the transaction ID is usually enough. A Public Key (`pk_*`) and Integration IDs are fine to include.

### Filing through the MCP server

If the Paymob MCP server is connected and the merchant wants the agent to file the ticket:

1. Show the full ticket text and the account and mode it will be filed under, then get explicit confirmation. Filing a ticket is a write.
2. Call `create_support_ticket` once. On a timeout or unclear reply, don't retry blindly. Tell the merchant it may already have been filed, and let them check their email or support history first.
3. Report the ticket reference the tool returns, and suggest the merchant keep it for follow-ups.

Otherwise, hand the merchant the drafted text and the Contact Support link. The wizard form is behind a security check and is meant for the human to submit.

---

## 6. Changes after launch

- **Rotating credentials**: rotate immediately if a Secret Key, API Key, or HMAC Secret was exposed (committed, logged, or pasted). Rotate from **Settings → API Keys** where the dashboard allows it; otherwise ask Paymob support. Deploy the new value to every environment. For the HMAC Secret, briefly accept either the old or the new secret during cutover so in-flight callbacks aren't rejected, then remove the old one.
- **New payment method**: get its Integration ID (test first), add it to `payment_methods`, check refund support, and watch its **first live callback** for shape and HMAC.
- **Plugin, app, or SDK updates**: read the changelog, update in staging with test mode on, run a test payment, re-run Store Check (WordPress), then update production. Pin mobile SDK versions and don't auto-upgrade in CI.
- **Domain or callback URL change**: update `notification_url` / `redirection_url` in code **and** the per-integration callback URLs in **Settings → Payment Integrations**, then run a test payment.
- **Staff changes**: review **Users & Permissions**, remove leavers, and rotate any key they had access to.
