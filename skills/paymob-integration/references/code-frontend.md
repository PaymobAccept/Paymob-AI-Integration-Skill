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

When you want the payment form embedded rather than a full redirect. You still create the Intention on the backend and pass the `client_secret` + Public Key to the SDK.

```html
<script src="https://accept.paymob.com/unifiedcheckout/static/scripts/paymob-sdk.js"></script>
<div id="paymob-container"></div>
<script>
  // base + script path can change — confirm the current embed snippet in the live docs
  // (developers.paymob.com / wizard.paymob.com) before shipping.
  const paymob = Paymob.init({
    publicKey: "pk_test_xxxxxxxx",      // Public Key only — never the Secret Key
    clientSecret: CLIENT_SECRET_FROM_YOUR_BACKEND,
    elementId: "paymob-container",
    afterPaymentComplete: (result) => {
      // UI only — confirm real status from your backend callback
      window.location.href = "/payment/complete";
    },
    onPaymentCancel: () => console.log("cancelled"),
  });
</script>
```

> The embedded SDK's exact script URL, init options, and callback names are versioned by Paymob and can change. Pull the current embed snippet from `developers.paymob.com` (or the Integration Wizard's code lab) rather than relying on this sample verbatim — see `live-resources.md`.

## Per-region base URL

Swap `accept.paymob.com` for the merchant's region in any URL the frontend builds or receives:

| Region | Base |
|---|---|
| Egypt | `accept.paymob.com` |
| Oman | `oman.paymob.com` |
| KSA | `ksa.paymob.com` |
| UAE | `uae.paymob.com` |

(Ideally the frontend never hardcodes this — let the backend return the full `checkout_url`.)
