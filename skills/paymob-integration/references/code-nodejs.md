# Paymob — Node.js / TypeScript (Express / NestJS)

Clean, correct reference implementation (Intention API + Unified Checkout + HMAC-verified webhook). Read `intention-api.md` and `hmac-verification.md` alongside this.

## Environment variables (`.env`)

```env
PAYMOB_BASE_URL=https://accept.paymob.com        # region base; oman./ksa./uae.paymob.com for others
PAYMOB_SECRET_KEY=sk_test_xxxxxxxx
PAYMOB_PUBLIC_KEY=pk_test_xxxxxxxx
PAYMOB_HMAC_SECRET=your_hmac_secret
PAYMOB_INTEGRATION_ID_CARD=123456                # one per enabled method
APP_URL=https://yoursite.com
```

## Install

```bash
npm install express axios dotenv     # crypto is built into Node
```

## Paymob client (`paymob.ts`)

```typescript
import axios from 'axios';
import crypto from 'crypto';

const BASE = process.env.PAYMOB_BASE_URL!;
const SECRET = process.env.PAYMOB_SECRET_KEY!;
const PUBLIC = process.env.PAYMOB_PUBLIC_KEY!;
const HMAC_SECRET = process.env.PAYMOB_HMAC_SECRET!;

const api = axios.create({
  baseURL: BASE,
  headers: { Authorization: `Token ${SECRET}`, 'Content-Type': 'application/json' },
});

export interface IntentionInput {
  amountCents: number;
  currency: string;                       // e.g. 'EGP'
  paymentMethods: number[];               // Integration IDs
  specialReference: string;               // your own order id, echoed back as merchant_order_id
  customer: { firstName: string; lastName: string; email: string; phone: string };
  items?: { name: string; amount: number; quantity: number; description?: string }[];
}

export async function createIntention(input: IntentionInput) {
  const { data } = await api.post('/v1/intention/', {
    amount: input.amountCents,
    currency: input.currency,
    payment_methods: input.paymentMethods,
    items: input.items ?? [],
    special_reference: input.specialReference,
    billing_data: {
      first_name: input.customer.firstName,
      last_name: input.customer.lastName,
      email: input.customer.email,
      phone_number: input.customer.phone,        // REQUIRED — omitting causes a 400
      apartment: 'NA', floor: 'NA', street: 'NA', building: 'NA',
      shipping_method: 'NA', postal_code: 'NA', city: 'NA', state: 'NA', country: 'EGY',
    },
    customer: {
      first_name: input.customer.firstName,
      last_name: input.customer.lastName,
      email: input.customer.email,
    },
    notification_url: `${process.env.APP_URL}/api/paymob/webhook`,
    redirection_url: `${process.env.APP_URL}/payment/complete`,
  });
  return { id: data.id, clientSecret: data.client_secret as string };
}

export function checkoutUrl(clientSecret: string) {
  return `${BASE}/unifiedcheckout/?publicKey=${PUBLIC}&clientSecret=${clientSecret}`;
}

// Transaction HMAC for POST webhook (20 fields from req.body.obj, in this exact order)
export function verifyTransactionPostHmac(obj: any, receivedHmac: string): boolean {
  const fields = [
    obj.amount_cents, obj.created_at, obj.currency, obj.error_occured,
    obj.has_parent_transaction, obj.id, obj.integration_id, obj.is_3d_secure,
    obj.is_auth, obj.is_capture, obj.is_refunded, obj.is_standalone_payment,
    obj.is_voided, obj.order.id, obj.owner, obj.pending,
    obj.source_data.pan, obj.source_data.sub_type, obj.source_data.type, obj.success,
  ];
  const computed = crypto.createHmac('sha512', HMAC_SECRET)
    .update(fields.map(String).join('')).digest('hex');
  return computed.length === receivedHmac.length &&
    crypto.timingSafeEqual(Buffer.from(computed), Buffer.from(receivedHmac));
}

// Post-payment ops
export const refund  = (txnId: number, amountCents: number) =>
  api.post('/api/acceptance/void_refund/refund', { transaction_id: txnId, amount_cents: amountCents }).then(r => r.data);
export const voidTxn = (txnId: number) =>
  api.post('/api/acceptance/void_refund/void', { transaction_id: txnId }).then(r => r.data);
export const capture = (txnId: number, amountCents: number) =>
  api.post('/api/acceptance/capture', { transaction_id: txnId, amount_cents: amountCents }).then(r => r.data);
```

## Express routes (`routes.ts`)

```typescript
import express from 'express';
import { createIntention, checkoutUrl, verifyTransactionPostHmac } from './paymob';

const router = express.Router();

router.post('/api/checkout', express.json(), async (req, res) => {
  const { amount, items, customer, orderId } = req.body;
  const { clientSecret } = await createIntention({
    amountCents: Math.round(amount * 100),
    currency: 'EGP',
    paymentMethods: [Number(process.env.PAYMOB_INTEGRATION_ID_CARD)],
    specialReference: String(orderId),
    customer,
    items: (items ?? []).map((i: any) => ({
      name: i.name, amount: Math.round(i.price * 100), quantity: i.quantity,
    })),
  });
  res.json({ checkoutUrl: checkoutUrl(clientSecret) });
});

// Paymob POSTs the result here; hmac is a query param
router.post('/api/paymob/webhook', express.json(), (req, res) => {
  const obj = req.body.obj;
  const receivedHmac = String(req.query.hmac ?? '');
  if (!obj || !verifyTransactionPostHmac(obj, receivedHmac)) {
    return res.status(401).json({ error: 'Invalid HMAC' });
  }
  // Idempotent on order.id / special_reference (merchant_order_id)
  if (obj.success === true && obj.pending === false) {
    // markOrderPaid(obj.order.id, obj.order.merchant_order_id) — then fulfill
  }
  res.status(200).json({ received: true });   // 200 even on ignore, to stop retries
});

export default router;
```

## NestJS note

Wrap `createIntention`/`verifyTransactionPostHmac` in an injectable `PaymobService`, and read the raw `hmac` from `@Query('hmac')` in the webhook controller. The crypto logic is identical.

## Gotchas

- Header is `Token <secret>` — **not** `Bearer`.
- Amount is **cents** (`Math.round(amount * 100)`).
- `billing_data.phone_number` is required.
- Verify HMAC **before** trusting `obj.success`. The redirect URL params are not authenticated — don't mark orders paid from them.
- `client_secret` is single-use — create a new Intention per attempt.
