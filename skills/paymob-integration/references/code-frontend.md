# Paymob — Frontend (React / Next.js / Vue) + Unified Checkout

The frontend's only job is: call **your** backend to create the Intention, then send the customer to Paymob's **Unified Checkout** (or render the embedded Pixel SDK). The Public Key is the only Paymob credential allowed in the browser; the Secret Key / API Key / HMAC Secret must never reach the client.

## Golden rules

- **Never** create the Intention from the browser — that would require the Secret Key client-side. Always go through your backend (see the `code-*.md` for your stack).
- Only the **Public Key** is safe in frontend code.
- The redirect/return page is **for UX only**. Payment status is decided by your backend's HMAC-verified callback, never by the return-page query params.

## Option A — Redirect to Unified Checkout (simplest, recommended)

Your backend returns a `checkout_url` (it builds `https://{base}/unifiedcheckout/?publicKey=...&clientSecret=...`). The frontend just navigates to it.

### React / plain JS

```jsx
async function startCheckout(cart, customer, orderId) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      amount: cart.total,          // your backend converts to cents
      orderId,
      items: cart.items,
      first_name: customer.firstName,
      last_name: customer.lastName,
      email: customer.email,
      phone: customer.phone,       // required by Paymob
    }),
  });
  const { checkoutUrl } = await res.json();
  window.location.href = checkoutUrl;   // hand off to Paymob's hosted page
}
```

### Next.js (App Router)

```tsx
"use client";
export default function PayButton({ cart, customer, orderId }) {
  async function pay() {
    const res = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount: cart.total, orderId, items: cart.items, ...customer }),
    });
    const { checkoutUrl } = await res.json();
    window.location.href = checkoutUrl;
  }
  return <button onClick={pay}>Pay now</button>;
}
```

Implement `/api/checkout` as a Next.js Route Handler that calls `createIntention` from `code-nodejs.md` server-side (keeps the Secret Key on the server).

### Vue 3

```vue
<script setup>
async function pay(cart, customer, orderId) {
  const res = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount: cart.total, orderId, items: cart.items, ...customer }),
  });
  const { checkoutUrl } = await res.json();
  window.location.href = checkoutUrl;
}
</script>
<template><button @click="pay(cart, customer, orderId)">Pay now</button></template>
```

### The return page

After payment, Paymob redirects the customer to your `redirection_url` with transaction params (incl. an `hmac`). Show a neutral "we're confirming your payment" state and **fetch the real status from your backend** (which knows the truth from the verified callback). Do not flip the order to "paid" based on these query params.

```jsx
// /payment/complete?order_id=...&success=...&hmac=...
function PaymentComplete() {
  const orderId = new URLSearchParams(location.search).get("merchant_order_id")
                ?? new URLSearchParams(location.search).get("order_id");
  const [status, setStatus] = useState("checking");
  useEffect(() => {
    fetch(`/api/orders/${orderId}/status`)   // your backend, source of truth
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
  const { publicKey, clientSecret } = await fetch("/api/paymob/create-intention", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ orderId: ORDER_ID }),
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
      window.location.href = "/payment/complete";
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

(Ideally the frontend never hardcodes this — let the backend return the full `checkout_url`.)
