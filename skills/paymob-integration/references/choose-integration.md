# Choosing the Integration Method

`SKILL.md` Step -1 settles *what the store runs on* and Step 0.5 settles *web or mobile*. This file settles the third question, the one merchants rarely think to ask: **how the money is actually taken.**

A merchant who bills monthly, takes orders by phone, or ships a week after checkout needs a different payment model from a one-off card charge — and if nobody asks, they get the one-off charge and find out later. Work through §1, then read the card in §3 for whatever it lands on.

For *which payment methods* to enable (cards, wallets, BNPL, Apple Pay…) and when to suggest one unprompted, see `payment-methods.md`.

---

## 1. The questions

Ask these **one at a time**, in order. Skip anything Step -1 or Step 0.5 already settled, and skip anything the merchant's own description already answers — this is a conversation, not a form.

You are looking for **two** answers, not one:

- a **payment model** — how money moves (Q1, Q2, Q3, Q5)
- a **surface** — where the customer pays (Q4)

They are independent, and most merchants need one of each. A furniture shop that ships next week needs Auth/Capture *and* a checkout surface; a marketplace needs Split Amount *and* a surface. So don't stop at the first method a question names — stop when you have both. The exceptions are MOTO and MIT, which have no customer-facing surface at all: if Q1 lands there, Q4 doesn't apply.

**Q1 — Who types in the card details?**
> "When someone pays you, who enters the card details — the customer themselves, your staff while on a call with them, or nobody because it's charged automatically on a card they already gave you?"

| Answer | Goes to |
|---|---|
| The customer | Q2 |
| Staff, on a call | **MOTO** (§3) — then stop and read the warnings |
| Nobody, charged automatically | **Saved cards (CIT→MIT)** or **Subscriptions** — Q2 decides which |

**Q2 — How often does money move?**
> "Is this a one-off payment each time, a fixed amount on a regular schedule, or an irregular charge on a card they've saved with you?"

| Answer | Goes to |
|---|---|
| Once per order | Q3 |
| Fixed amount, fixed schedule | **Subscriptions** (§3) |
| Irregular, on a stored card | **Saved cards — CIT then MIT** (§3) |
| Once, but taken later than checkout | **Auth/Capture** (§3) |

**Q3 — Who receives the money?**
> "Does all of it go to you, or is some of it owed to other sellers on your platform?"

| Answer | Goes to |
|---|---|
| All to the merchant | Q4 |
| Split across sellers / sub-accounts | **Split Amount** (§3) |
| One customer paying across several cards | **Split Payment** (§3) |

**Q4 — Where does the customer pay?**
> "Should checkout open as a Paymob page, sit inside your own page, open in your app, or just be a link you send them?"

| Answer | Goes to |
|---|---|
| A Paymob page (redirect) | **Unified Checkout** (§3) |
| Inside the merchant's own page | **Pixel, embedded** (§3) |
| Inside their mobile app | **Mobile SDK** (§3) |
| A link they send | **Payment Links / PayMe** (§3) |
| No checkout at all | Back to Q1 — this is MOTO or MIT |

**Q5 — Does anything have to happen before you fulfil the order?**
> "Do you ship or deliver days later, take a deposit, or need to check the card is good before charging it?"

| Answer | Goes to |
|---|---|
| Ships later / deposit / rental | **Auth/Capture** (§3) |
| Need to check a card is valid first | **Verification** (§3) |
| No — charge at checkout | Done |

## 2. Routing matrix

| The merchant's situation | Build | Spec lives in |
|---|---|---|
| Standard online store, custom code | Unified Checkout (redirect) | `intention-api.md`, `code-frontend.md` |
| Wants checkout not to leave their page | Pixel (embedded) | `code-frontend.md` Option B |
| Native iOS / Android / Flutter / RN app | Mobile SDK | `mobile-sdks.md` |
| No website, sells over social / invoices | Quick Link per sale, or PayMe for one permanent link | Payment Links path in `SKILL.md` |
| High-ticket EGY items that look unaffordable on the product page | Affordability Widget, alongside the checkout surface | `code-frontend.md` Option C, `payment-methods.md` §4 |
| Shopify, WooCommerce, Magento, Odoo, … | The Paymob app or official plugin | `shopify-apps.md`, plugin path in `SKILL.md` |
| Phone / call-centre / WhatsApp orders | MOTO | §3 below — shape not published, confirm with Paymob |
| Monthly or annual billing, fixed amount | Subscriptions | `advanced-features.md` |
| Repeat orders, charge-on-file, irregular amounts | Saved cards (CIT→MIT) | `advanced-features.md` |
| Ships later, rentals, deposits, made-to-order | Auth/Capture | `advanced-features.md` |
| Marketplace paying third-party sellers | Split Amount | `advanced-features.md` |
| One order paid across up to 3 cards | Split Payment | `advanced-features.md` |
| Check a card is good before charging it | Verification | §3 below — confirm with Paymob |

Everything in this table except Payment Links, plugins, and Shopify apps still needs the **same backbone**: a server-side Intention, an HMAC-verified callback as the source of truth, and atomic order updates. The payment model changes the Intention fields and which HMAC type the callback carries — it never removes the webhook.

## 3. Method cards

### Unified Checkout (redirect)

- **Choose it when** — the merchant has a custom or headless site and wants every Paymob method with the least work. This is the default; pick it unless something below overrides.
- **Don't choose it when** — leaving the merchant's domain mid-checkout is unacceptable to them (use Pixel), or there is no website (use Payment Links).
- **Example** — a Next.js storefront: the backend creates an Intention with the card and wallet Integration IDs and returns `client_secret`; the browser goes to `{base_url}/unifiedcheckout/?publicKey=pk_...&clientSecret=csk_...`; the callback marks the order paid.
- **Needs** — Public Key, one Integration ID per method, a public HTTPS `notification_url`. Transaction HMAC (20 fields). `intention-api.md`.

### Pixel (embedded)

- **Choose it when** — checkout must stay visually inside the merchant's own page.
- **Don't choose it when** — the merchant needs methods Pixel doesn't render. Pixel covers cards, Google Pay, and Apple Pay; wallets, BNPL, and kiosk go through Unified Checkout. Check `payment-methods.md` against the methods they asked for before promising this.
- **Example** — a SaaS upgrade modal that collects card details without navigating away.
- **Needs** — same Intention as above; Apple Pay through Pixel additionally needs **domain verification plus certificates**. Transaction HMAC. `code-frontend.md` Option B.

### Mobile SDK

- **Choose it when** — a native iOS, Android, Flutter, or React Native app takes the payment in-app.
- **Don't choose it when** — the app can open a web view and the team is small; the redirect path ships in days, the SDK path in days to weeks.
- **Example** — a delivery app presenting Paymob's hosted checkout screen after the customer taps Pay.
- **Needs** — the Intention is still created **by the merchant's backend**, never in the app, so the Secret Key never ships in a binary. The SDK result updates the UI only; the backend callback remains the source of truth. `mobile-sdks.md`.

### Payment Links / PayMe

- **Choose it when** — no website, no developer: social selling, invoicing, a one-off bill.
- **Don't choose it when** — the merchant needs the payment tied to an order record in their own system. Then generate links from their backend via the QuickLink APIs, or build a real checkout.
- **Example** — an Instagram seller creates a **Quick Link** per order and sends it on WhatsApp, because the amount differs every time.
- **Quick Link or PayMe?** Ask whether the amount changes per sale. Quick Link is one link per order with the amount fixed on the link. **PayMe** is one permanent reusable handle for the bio, the email signature, or a printed QR — Live mode only, permanently tied to the merchant's MID, renameable once before changes need a risk review, and deactivating the main handle deactivates all its branch handles. SMS sharing is Egyptian numbers only.
- **Needs** — a Paymob account and nothing else. Testing before sharing real links: `testing-guide.md`.

### Plugins & Shopify apps

- **Choose it when** — the store runs on Shopify or any platform with an official Paymob plugin. Always prefer this over hand-coding; the plugin already handles the Intention, checkout, callback, and HMAC.
- **Don't choose it when** — the merchant is deliberately building a headless checkout that bypasses the platform's native one.
- **Example** — a WooCommerce store installs Paymob's plugin, enters its keys and Integration IDs, and runs a Test Mode order.
- **Needs** — `shopify-apps.md`, and the prebuilt-plugin path in `SKILL.md`. Do not write Intention or HMAC code for these.

### MOTO (Mail Order / Telephone Order)

- **Choose it when** — the customer is on the phone, on WhatsApp, or ordering by mail, and staff take the card details. Call centres, phone-ordered B2B invoices, back-office re-charges.
- **Don't choose it when** — the customer could just as easily be sent a link or a checkout page. **Send a Payment Link instead** whenever that is possible: it keeps card data entirely out of the merchant's hands and off their staff's screens. MOTO is the fallback for when that genuinely is not an option.
- **Example** — a travel agency takes a booking by phone, reads the card details into its back-office tool, and charges without the customer completing a 3DS challenge.
- **Needs — and read all four before you propose it:**
  1. **Paymob must enable MOTO on the account.** It is not self-serve; expect a separate Integration ID. The merchant arranges it with their account manager.
  2. **PCI DSS scope.** Staff handling PAN and CVV pulls the merchant into PCI scope. Never build a screen that stores, logs, or persists a PAN or CVV, never put them in an order record, and say plainly that this is a compliance decision for the merchant, not a technical one.
  3. **Chargeback liability.** MOTO is card-not-present with no 3DS challenge, so liability sits with the merchant, not the issuer. The merchant should know that before launching it, not after the first dispute.
  4. **The request shape is not published.** Paymob documents MOTO as a card transaction type but does not publish its enablement path or request fields. Confirm both against the live docs (`live-resources.md`) or the merchant's account manager — **do not infer or invent fields.** If you can't confirm them, say so and stop rather than guessing.
- Refund and void are both supported, full or partial. Pair it with **Verification** when a card has to be checked before a later charge.

### Subscriptions

- **Choose it when** — a fixed amount recurs on a fixed schedule: SaaS seats, a gym membership, a subscription box, an annual licence.
- **Don't choose it when** — the amount varies per cycle or the schedule is irregular. That is **saved cards (CIT→MIT)**, where the merchant decides each charge. Also note Paymob must enable subscriptions on the account.
- **Example** — a Cairo gym billing EGP 600 a month: create a plan with `amount_cents: 60000` and `frequency: 30`; attach it to an Intention so the first charge runs through normal checkout as a CIT; renewals auto-debit; cancel through the subscription endpoint when the member leaves.
- **Needs** — plan management uses a **Bearer** auth token from the API-Key endpoint, while attaching the plan to a payment uses the usual `Authorization: Token {SECRET_KEY}`. Valid `frequency` values in days: 7, 15, 30, 60, 90, 180, 360. **Subscription callbacks use a different HMAC** — a string formula, with `hmac` in the request body, not the 20-field query-string concatenation. Getting that wrong silently rejects every renewal. `advanced-features.md`.

### Saved cards (CIT → MIT)

- **Choose it when** — customers buy repeatedly and the merchant wants one-click re-ordering, or needs to charge an irregular amount later (usage billing, a top-up, a no-show fee).
- **Don't choose it when** — a fixed schedule would do; subscriptions handle the scheduling for you.
- **Example** — a ride-hailing app tokenizes the card on the first ride (CIT, through checkout), then charges the token at the end of each later ride (MIT, off-session) with no customer interaction.
- **Needs** — tokenization enabled on the Integration ID, and `extras.save_card` on the Intention (confirm the current flag name in the live docs). The tokenization callback uses the **Card Token HMAC** — 8 fields, a different order from the transaction HMAC. Store only the token and masked PAN, never raw card data, and verify the token callback's `email` matches the customer record. MIT charges are off-session payments the customer pre-authorized and must comply with scheme rules. `advanced-features.md`.

### Auth/Capture

- **Choose it when** — the merchant shouldn't take the money at checkout: the order ships days later, stock might be unavailable, it's a rental or a deposit, or the final amount isn't known yet.
- **Don't choose it when** — fulfilment is instant. The extra state (authorized / captured / voided / expired) is real complexity in the order model for no gain.
- **Example** — a furniture shop authorizes EGP 30,000 at checkout, captures when the sofa actually leaves the warehouse, and voids if it turns out to be out of stock.
- **Needs** — `is_auth: true` on the Intention (some accounts expect `payment_type: "AUTH"` — confirm which), then the capture endpoint later, or void to release the hold. The callback arrives with `is_auth: true` and funds held, **not** settled — the merchant's order model must not treat that as paid. `advanced-features.md`.

### Verification

- **Choose it when** — the merchant needs to confirm a card is valid and funded before relying on it for a later charge, without reserving or moving money.
- **Don't choose it when** — an Auth/Capture hold would serve, which is usually the case. Verification is narrow.
- **Example** — a rental company checks a card at booking time, then charges it by MOTO on the day.
- **Needs** — enabled per account by Paymob; the request shape is not published. Confirm with the live docs or the account manager, and do not invent fields.

### Split Amount

- **Choose it when** — a marketplace or platform owes part of each payment to third-party sellers and wants Paymob to divide it at payment time.
- **Don't choose it when** — the merchant keeps the whole amount and settles sellers on their own schedule.
- **Example** — a multi-vendor marketplace splitting one EGP 5,000 basket across two sellers and its own commission.
- **Needs** — the feature enabled on the account, and sub-accounts configured. The field shape evolves — pull the current spec from the live docs. `advanced-features.md`.

### Split Payment

- **Choose it when** — one customer wants to pay a single order across up to about three cards.
- **Don't choose it when** — you actually meant Split Amount. These two names are easy to confuse and do unrelated things.
- **Example** — a high-value booking paid half on a personal card and half on a corporate one.
- **Needs** — the feature enabled on the account; confirm the current spec in the live docs. `advanced-features.md`.

## 4. Combining them

- **Subscriptions are built on saved cards.** The first charge is a CIT through checkout; renewals are MITs against the stored card. A merchant asking for "recurring billing" usually needs only subscriptions, not both.
- **Verification pairs with MOTO** — check the card now, charge it later.
- **Auth/Capture and subscriptions don't combine.** A plan charges on its schedule; it doesn't hold funds.
- **Unified Checkout and Pixel are alternatives, not layers.** Pick one surface per flow.
- **Split Amount composes with any surface** — it changes who gets paid, not where the customer pays.
- Whatever the combination, the webhook rules do not move: HMAC-verify first, deduplicate on `obj.id`, compare-and-set the order state and insert the outbox record in one transaction, and use `order.id` / `special_reference` only to correlate. `hmac-verification.md`.

## 5. Before you write code

Confirm with the merchant, in one message:

1. The method you landed on and **why it beat the alternative** — one sentence each.
2. What Paymob has to enable on their account (MOTO, Verification, subscriptions, split, tokenization all need it) and that this is not instant.
3. Which Integration IDs they need to fetch.
4. Which HMAC type the callbacks will use — transaction, card token, or subscription.
5. Anything you could not confirm in the live docs, named explicitly rather than implemented on a guess.
