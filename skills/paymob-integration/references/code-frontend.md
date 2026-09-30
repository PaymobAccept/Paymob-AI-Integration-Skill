# Paymob — Frontend (React / Next.js / Vue) + Unified Checkout

The frontend's only job is: call **your** backend to create the Intention, then send the customer to Paymob's **Unified Checkout** (or render the embedded Pixel SDK). The Public Key is the only Paymob credential allowed in the browser; the Secret Key / API Key / HMAC Secret must never reach the client.

## Golden rules

- **Never** create the Intention from the browser — that would require the Secret Key client-side. Always go through your backend (see the `code-*.md` for your stack).
- Only the **Public Key** is safe in frontend code.
- The redirect/return page is **for UX only**. Payment status is decided by your backend's HMAC-verified callback, never by the return-page query params.

## Option A — Redirect to Unified Checkout (simplest, recommended)

Every backend in this skill (`code-*.md`) exposes the same contract, so these snippets work with any of them:

- `POST /api/checkout` with the body `{ orderId, customer: { firstName, lastName, email, phone } }`
- The response is `{ checkoutUrl, clientSecret, publicKey }`

> **CSRF:** Django, Rails, and Laravel keep CSRF protection on the browser-facing checkout route (only the server-to-server webhook is exempt), so add your framework's token header to these `fetch` calls:
> - Django: `X-CSRFToken`, read from the `csrftoken` cookie
> - Rails: `X-CSRF-Token`, read from `<meta name="csrf-token">`
> - Laravel: `X-CSRF-TOKEN` from the meta tag, or `X-XSRF-TOKEN` from the cookie
>
> Node/Express and .NET minimal APIs don't add CSRF by default. If you authenticate with cookies there, add your own CSRF protection.

The browser sends **only the order ID and customer details**. The backend looks up the amount and items from its own order record, so a customer can't edit the price in DevTools. The backend builds `checkoutUrl` as `{base_url}/unifiedcheckout/?publicKey=...&clientSecret=...`, and the frontend just navigates to it.

### React / plain JS

```jsx
// customer = { firstName, lastName, email, phone }  — phone is required by Paymob
async function startCheckout(orderId, customer) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ orderId, customer }),   // no amount: the backend prices the order
  });
  if (!res.ok) throw new Error(`Checkout failed: ${res.status}`);
  const { checkoutUrl } = await res.json();
  window.location.href = checkoutUrl;   // hand off to Paymob's hosted page
}
```

### Next.js (App Router)

```tsx
"use client";
export default function PayButton({ orderId, customer }) {
  async function pay() {
    const res = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ orderId, customer }),
    });
    if (!res.ok) throw new Error(`Checkout failed: ${res.status}`);
    const { checkoutUrl } = await res.json();
    window.location.href = checkoutUrl;
  }
  return <button onClick={pay}>Pay now</button>;
}
```

Implement `/api/checkout` as a Next.js Route Handler (`app/api/checkout/route.ts`) that follows the Express route in `code-nodejs.md`: load the order server-side, call `createIntention`, and return `{ checkoutUrl, clientSecret, publicKey }`. The Secret Key stays on the server.

### Vue 3

```vue
<script setup>
async function pay(orderId, customer) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ orderId, customer }),
  });
  if (!res.ok) throw new Error(`Checkout failed: ${res.status}`);
  const { checkoutUrl } = await res.json();
  window.location.href = checkoutUrl;
}
</script>
<template><button @click="pay(orderId, customer)">Pay now</button></template>
```

### The return page

After payment, Paymob redirects the customer to your `redirection_url` with transaction params (incl. an `hmac`). Show a neutral "we're confirming your payment" state and **fetch the real status from your backend** (which knows the truth from the verified callback). Do not flip the order to "paid" based on these query params.

```jsx
// /payment/complete?merchant_order_id=...&success=...&hmac=...
import { useEffect, useState } from "react";

function PaymentComplete() {
  // merchant_order_id is YOUR special_reference. Don't fall back to Paymob's order_id:
  // it's a different ID space and would look up the wrong order.
  const orderId = new URLSearchParams(location.search).get("merchant_order_id");
  const [status, setStatus] = useState("checking");
  useEffect(() => {
    if (!orderId) { setStatus("unknown"); return; }
    fetch(`/api/orders/${encodeURIComponent(orderId)}/status`)   // your backend, source of truth
      .then(r => r.json()).then(d => setStatus(d.paid ? "paid" : "pending"));
  }, [orderId]);
  return <p>Payment status: {status}</p>;
}
```

## Option B — Embedded Pixel SDK (checkout inside your page)

Source: https://developers.paymob.com/paymob-docs/developers/checkout-experiences/pixel-embedded (last updated by Paymob: September 7, 2026)

Use Pixel when the merchant wants the payment form embedded in their own page (or a WebView) instead of a redirect. Pixel supports **card**, **Google Pay**, and **Apple Pay**. Everything else stays the same: the backend creates the Intention, the frontend gets only the Public Key and the `client_secret`, and payment status still comes from the HMAC-verified callback.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/paymob-pixel@latest/styles.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/paymob-pixel@latest/main.css">
<script src="https://cdn.jsdelivr.net/npm/paymob-pixel@latest/main.js" type="module"></script>

<div id="paymob-elements"></div>
<button id="pay-btn" style="display:none">Pay</button>

<script type="module">
  // Get these from YOUR backend (which created the intention with the Secret Key).
  // Same /api/checkout endpoint as Option A; Pixel uses publicKey + clientSecret instead of checkoutUrl.
  const { publicKey, clientSecret } = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ orderId: ORDER_ID, customer: CUSTOMER }),
  }).then((r) => r.json());

  const payBtn = document.getElementById("pay-btn");

  new Pixel({
    publicKey,                                   // Public Key only — never the Secret Key
    clientSecret,                                // unique per order, expires in 1 hour
    paymentMethods: ["card", "google-pay", "apple-pay"],
    elementId: "paymob-elements",
    disablePay: true,                            // true = use your own button (payFromOutside)
    showSaveCard: false,                         // true = offer "save card" to the customer
    forceSaveCard: false,                        // true = save without asking — needs clear consent terms
    cardValidationChanged: (isValid) => {
      payBtn.style.display = isValid ? "block" : "none";
    },
    beforePaymentComplete: async () => { /* your own pre-payment logic */ },
    afterPaymentComplete: async (response) => {
      // UI only — the backend callback decides whether the order is paid
      window.location.href = "/payment/complete?merchant_order_id=" + encodeURIComponent(ORDER_ID);
    },
    onPaymentCancel: () => console.log("Apple Pay sheet closed"), // Apple Pay only
    customStyle: {
      Font_Family: "Inter",
      Color_Primary: "#144DFF",
      Radius_Border: "8",
      // Direction: "rtl" plus Label_Text / Placeholder_Text / Error_Text / Button_Text for Arabic
    },
  });

  // With disablePay: true, fire the payment from your own button by dispatching an
  // event named "payFromOutside". The docs name the event but not its target —
  // confirm the target (window vs. the Pixel element) on the doc page before shipping.
  payBtn.addEventListener("click", () => {
    window.dispatchEvent(new Event("payFromOutside"));
  });
</script>
```

Key options (full list in the docs above):

| Option / hook | What it does |
|---|---|
| `publicKey`, `clientSecret` | From your backend. `client_secret` is unique per order and expires in an hour |
| `paymentMethods` | Any of `"card"`, `"google-pay"`, `"apple-pay"` |
| `elementId` | ID of the element Pixel renders into |
| `disablePay` | `true` hides Pixel's own Pay button; dispatch the `payFromOutside` event to pay |
| `showSaveCard` / `forceSaveCard` | Offer card saving / save without asking |
| `cardValidationChanged(isValid)` | Fires when card validity changes — use it to enable your own button |
| `beforePaymentComplete` / `afterPaymentComplete(response)` | Your logic before / after Paymob processes the payment (after = UI only) |
| `onPaymentCancel` | Apple Pay only — customer closed the Apple Pay sheet |
| `updateIntentionData` | Refresh Pixel after the intention changes (backend calls the Intention Update API) |
| `customStyle` | Fonts, colors, sizes, spacing, and Arabic/RTL text |

> **Check before shipping.** Paymob's own sample loads `paymob-pixel@latest` from jsDelivr. For production, consider pinning a specific version so a new release can't change the checkout unexpectedly, and re-check the option names against the doc page above. Paymob's docs sample puts the Secret Key in the page for testing only — never do that; the Secret Key stays on the backend.

## Per-region base URL

Swap `accept.paymob.com` for the merchant's region in any URL the frontend builds or receives:

| Region | Base |
|---|---|
| Egypt | `accept.paymob.com` |
| Oman | `oman.paymob.com` |
| KSA | `ksa.paymob.com` |
| UAE | `uae.paymob.com` |

(Ideally the frontend never hardcodes this. Let the backend return the full `checkoutUrl`.)
