# Payment Methods & Feature Advisor

Two jobs: the **catalog** of what Paymob can accept in each region, and the rules for **when to raise an extra method** with a merchant who didn't ask for one.

For *which integration surface and payment model* to build, see `choose-integration.md`. For request shapes and code, see `intention-api.md` and `advanced-features.md`.

Availability, refundability, and enablement are account- and contract-specific. The tables below follow Paymob's live payment-method docs (checked 2026-10); confirm anything you are about to ship against `live-resources.md`, and confirm per-account enablement with the merchant's dashboard or account manager. Never quote fees, rates, settlement timing, or reserves — those are contractual (`post-integration.md` §5).

---

## 1. Card networks by region

| Region | Networks |
|---|---|
| EGY | Visa, Mastercard, Amex (conditional — needs coordination with the merchant's account manager) |
| KSA | Visa, Mastercard, Amex, MADA |
| UAE | Visa, Mastercard, Amex, Jaywan |
| OMN | Visa, Mastercard, Amex, OmanNet |

## 2. Card transaction types

One card Integration ID, several ways to charge it. Which one you use is a **payment-model** decision — see `choose-integration.md`.

| Type | What it is | Void | Refund | Capture |
|---|---|---|---|---|
| **Normal 3DS** | The customer authenticates during checkout (bank OTP). The default. | Yes | Full / partial | — |
| **MOTO** | Mail Order / Telephone Order. Card not present, used for back-to-back requests without customer interaction. Passes both OTP and CVV. | Yes | Full / partial | — |
| **Card on File** | A card stored after a first customer-initiated payment, charged again later. Passes OTP only. | Yes | Full / partial | — |
| **Auth/Cap** | Reserve funds now, capture (or void) later. | Yes | Full / partial | Full / partial |
| **Verification** | Checks a card's details and available balance **without** reserving or transferring funds. Used to confirm a card is valid before a later MOTO or Verification charge. | — | — | — |

MOTO and Verification are enabled per account by Paymob and are not self-serve. Paymob does not publish their enablement path or request shape — have the merchant confirm both with their account manager, and do not infer fields. Read the MOTO card in `choose-integration.md` for the PCI and chargeback consequences before proposing it.

### 3D Secure — what it is and what you do about it

3DS is the card schemes' authentication step (Verified by Visa, Mastercard Identity Check). The issuing bank, not Paymob and not the merchant, decides whether to challenge the cardholder — usually an OTP or an in-app approval — or to let the payment through **frictionlessly** on its own risk scoring. The scheme rule that matters commercially: when a payment is authenticated through 3DS, chargeback liability for fraud generally shifts from the merchant to the issuer. That is the single biggest reason **not** to reach for MOTO when a normal checkout would do.

**There is nothing to implement.** Paymob hosts the card entry and runs the 3DS flow inside Unified Checkout, Pixel, and the mobile SDKs. The merchant's code never sees a PAN, never renders an OTP field, and never calls a 3DS endpoint. Paymob does not publish a 3DS configuration surface — so do not promise a merchant you can turn challenges off, tune the risk rules, or request exemptions, and do not build anything that tries to.

What it does change in the merchant's integration is **timing and failure modes**:

- **The customer can be gone for a while.** A challenge can take a minute or more, and the customer may be redirected to their bank's page or app. Never treat a slow checkout as a failed one.
- **An abandoned challenge produces no callback at all.** The customer closes the tab at the OTP screen and nothing POSTs to `notification_url`. The order sits pending forever unless something reconciles it — this is exactly what `transaction-inquiry.md` is for. Expect this to be a normal share of traffic, not an edge case.
- **A failed challenge is a declined payment**, and arrives as an ordinary unsuccessful callback. HMAC-verify it like any other (`hmac-verification.md`); don't special-case it.
- **"OTP never arrived" is the merchant's most common support ticket, and it isn't theirs to fix.** The OTP is sent by the cardholder's bank. The merchant can't resend it, can't see it, and must never ask a customer for it — nor may it ever reach a support ticket (`post-integration.md` §5). The customer retries, or contacts their bank.

MOTO and Card-on-File do not run a 3DS challenge, which is why liability sits with the merchant on those. Saved-card MIT charges are off-session and pre-authorized by the customer during the original 3DS-authenticated CIT.

## 3. Methods by region

| Method | Regions | Refund | Sandbox | Integration IDs | Channels |
|---|---|---|---|---|---|
| **Cards** | EGY, KSA, UAE, OMN | Full / partial | Yes | Test + Live | APIs, SDKs, Plugins, Links |
| **Mobile Wallets** (Vodafone Cash, Orange Cash, e& money, We Pay, bank wallets) | EGY | Full / partial | Yes | Test + Live | APIs, SDKs, Plugins, Links |
| **StcPay** | KSA | Yes (no void) | Confirm | Confirm | Confirm per account |
| **BNPL** (15 providers — §4) | EGY, KSA, UAE | Per provider — §4 | **No** | Live (confirm per provider) | Varies — §4 |
| **Apple Pay** | EGY, KSA, UAE, OMN | Full / partial | **No** — Live IDs only | Live only | APIs, SDKs, Plugins, Links |
| **Google Pay** | KSA, UAE | Full / partial | **No** — Live IDs only | Live only | APIs, SDKs, Plugins, Links |
| **Samsung Pay** | UAE | Full / partial (+ capture) | **No** — Live IDs only | Live only | APIs |
| **Bank Installments** | EGY | Full / partial | **No** — Live IDs only | Live only | APIs, Plugins, Links |
| **Kiosk** (cash at an outlet) | EGY | **No refunds** | **No** | Test + Live | APIs, Plugins, Links |

Notes that change what you build:

- **Apple Pay setup differs by surface.** Mobile SDK needs Apple Pay certificates; Pixel (embedded) via the APIs, and the WooCommerce plugin, need **domain verification as well as** certificates. Budget for it — it is not a dashboard toggle.
- **Google Pay is KSA and UAE.** Earlier versions of this skill listed Oman too; the live docs do not. Confirm via `live-resources.md` before telling a merchant otherwise.
- **Samsung Pay is API-only.** No SDK, plugin, or Payment Links path.
- **Kiosk settles asynchronously.** The customer pays cash later, so the callback can arrive hours or days after checkout, or never. Expect long-lived pending orders and reconcile with `transaction-inquiry.md`. It is the one method here with no refund path at all — never ship a refund button that assumes it.
- **Live-only methods can't be sandbox-tested.** Apple Pay, Google Pay, Samsung Pay, bank installments, and BNPL have no sandbox path. That does not hold up launch: every method goes through the same Intention API, the same checkout, and the same HMAC-verified callback, so a passing card test already validates the merchant's own integration code. Check the method-specific items (Integration ID, callback field shape, settlement timing, refund support) on the **first real transaction** per method — see `testing-guide.md` and Phase 3 in `SKILL.md`.

## 4. Instalment options — BNPL and bank instalments

Two different products that both let a customer pay over time, and merchants conflate them. **BNPL** is funded by a fintech provider (Valu, Tabby, …) and the customer usually needs that provider's account. **Bank instalments** are funded by the cardholder's own bank against a card they already hold, and are EGY-only with Live Integration IDs only. Many merchants want both — they convert different customers.

### BNPL providers

The merchant is paid in full up front; Paymob collects the instalments from the customer. Each provider is a separate Integration ID and must be enabled on the account.

| Provider | Regions | Refund | Channels |
|---|---|---|---|
| Valu | EGY | Full / partial | APIs, SDKs, Plugins, Links |
| Souhoola | EGY | Full / partial | APIs, SDKs, Plugins, Links |
| Forsa | EGY | Full / partial | APIs, SDKs, Plugins, Links |
| Aman Installments | EGY | Full / partial | APIs, Plugins, Links |
| Sympl | EGY | Full / partial | APIs, Plugins, Links |
| Halan | EGY | Full / partial | APIs, Plugins, Links |
| Klivvr | EGY | Full / partial | APIs, Plugins, Links |
| Contact | EGY | Full / partial | APIs, Plugins, Links |
| MOGO (MID Takseet) | EGY | Full / partial | APIs, Plugins, Links |
| TRU | EGY | Full / partial | APIs, Plugins, Links |
| Mylo | EGY | Full / partial | APIs, Plugins, Links |
| Premium | EGY | **Full only** | APIs, SDKs, Plugins, Links |
| Seven | EGY | **Full only** | APIs, Plugins, Links |
| Tabby | KSA, UAE | Full / partial | APIs, SDKs, Plugins, Links |
| Tamara | KSA, UAE | **Full only** | APIs, SDKs, Plugins, Links |

**Most BNPLs are refundable.** Earlier versions of this skill said BNPL did not support refunds — that is wrong, and it is the kind of claim that talks a merchant out of a method that would have converted for them. Twelve of the fifteen support partial refunds; Tamara, Premium, and Seven are full-only. Confirm the specific provider in the live docs before shipping a partial-refund path.

Klivvr can collect its fees with the first instalment, where the first instalment is the instalment amount plus fees. If the merchant's order total must match what the customer sees, raise this with them.

Only some providers ship as standalone **Shopify** apps (Sympl, valU — see `shopify-apps.md`); the rest reach Shopify through Paymob Accept's off-site checkout.

### Bank instalments, and the Affordability Widget

Bank instalments are EGY-only, **Live Integration IDs only** (so no sandbox path), and refundable in full or in part. They reach the customer through APIs, plugins, and Payment Links — not the mobile SDKs.

Instalments have a problem the other methods don't: the customer has to know the option exists *before* checkout. A EGP 30,000 sofa looks unaffordable on the product page and the customer leaves; they never reach the checkout where the plan would have been offered. Paymob's **Affordability Widget** exists for exactly this — it renders the available plans on the product or cart page, so the price reads as "from EGP 2,500/month" while the customer is still deciding.

Two modes:

- **View-only** — shows the plans, nothing clickable. `customerCanSelect: false` and no `onSubmit`.
- **Conversion** — the customer picks a plan before checkout. Set `customerCanSelect: true`, pass an `onSubmit` callback, and send the chosen plan's `id` to your backend so it goes on the Intention as `pre_selected_plan`. The customer then only enters card details at checkout.

The widget is frontend code — the snippet, the parameters, and the backend handoff are in `code-frontend.md`. Two things to get right there:

1. **The widget runs entirely in the browser and calls no Paymob API.** Its `onSubmit` hands you a plan object with `id`, `tenure`, and a monthly `amount`.
2. **Only the plan `id` may cross to your backend.** The Intention's `amount` is still the full order total, priced server-side from the merchant's own order record — never the widget's monthly figure, and never any amount the browser sent. This is the server-prices-the-order rule, and the widget is the easiest place in the whole integration to break it.

It takes the **Public Key**, so it is safe in frontend code. It renders nothing when no plans exist for that `integrationId` and `amount`, so a merchant seeing an empty space usually has the wrong Integration ID or an amount below the plan's floor — not a broken script.

---

## 5. When to raise an extra method

The merchant usually names cards and stops. Raise something else only when **they stated a signal** or you can see one in their code — not as a catalog read-out.

| Signal the merchant gave you | Raise | Why |
|---|---|---|
| High-ticket consumer retail in EGY/KSA/UAE; abandoned carts at checkout | **BNPL** for their region | Lifts conversion and average order value on baskets customers won't put on one card |
| High-value durables in EGY — furniture, appliances, electronics | **Bank instalments** alongside BNPL | Bank-funded plans reach a different customer than BNPL apps do |
| Large iOS or Safari share of their traffic | **Apple Pay** | One-tap checkout on the device the traffic is already on — but it costs certificates, and domain verification for Pixel |
| Android traffic in KSA or UAE | **Google Pay** | Same one-tap gain; Live IDs only |
| UAE merchant, Samsung-heavy audience | **Samsung Pay** | UAE-only, API-only |
| EGY customers who are unbanked, or the merchant leans on cash on delivery | **Mobile wallets + kiosk** | Reaches customers with no card at all; kiosk converts COD into prepaid, at the cost of async settlement and no refunds |
| Customers buy from them repeatedly | **Saved cards (CIT→MIT)** | Removes re-entry on every repeat order — `advanced-features.md` |
| Fixed-period access — SaaS, gym, subscription box, membership | **Subscriptions** | Paymob schedules and auto-debits, instead of the merchant hand-rolling a cron that charges tokens |
| Order ships days later; rentals; deposits; made-to-order | **Auth/Capture** | Hold funds at checkout, take them when the order actually ships, void if it can't be fulfilled |
| Marketplace or platform paying third-party sellers | **Split Amount** | Splits one payment across sub-accounts at payment time, instead of the merchant reconciling payouts themselves |
| Orders taken by phone, WhatsApp, or a call centre | **MOTO** | The only path when the customer is not at a checkout — read the PCI and chargeback warnings in `choose-integration.md` first |
| No website, selling over social or invoices | **Payment Links**, or **PayMe** for one permanent reusable link | No code at all — the Payment Links path in `SKILL.md` |

## 6. Rules for suggesting

1. **At most two per conversation**, and once. If the merchant doesn't take them up, drop it.
2. **Tie each one to the signal they gave you.** "You mentioned orders around EGP 30,000 — BNPL is worth enabling for that basket size." Not "Paymob also supports…".
3. **After the card path passes its Phase 3 test**, not during the build. A method suggestion that derails a working integration costs the merchant more than it gains.
4. **Never a go-live blocker.** Say so explicitly: the merchant can launch on cards and enable the rest from the dashboard afterwards.
5. **Name what it costs them** — Paymob enablement, an approval, Live-only IDs, certificates, domain verification, no sandbox test, no refund path. A suggestion without its cost is a sales pitch.
6. **No fees, rates, settlement timing, or reserves**, ever, even if asked. Send the merchant to Paymob (`post-integration.md` §5).
