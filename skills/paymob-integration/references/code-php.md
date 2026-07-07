# Paymob — PHP / Laravel

Clean, correct reference (Intention API + Unified Checkout + HMAC-verified webhook). Read `intention-api.md` and `hmac-verification.md` alongside this.

## Environment (`.env`)

```env
PAYMOB_BASE_URL=https://accept.paymob.com
PAYMOB_SECRET_KEY=sk_test_xxxxxxxx
PAYMOB_PUBLIC_KEY=pk_test_xxxxxxxx
PAYMOB_HMAC_SECRET=your_hmac_secret
PAYMOB_INTEGRATION_ID_CARD=123456
APP_URL=https://yoursite.com
```

## Plain PHP client (`Paymob.php`)

Uses cURL — no dependencies. (In Laravel, swap cURL for the `Http` facade; logic is identical.)

```php
<?php

class Paymob
{
    private string $base;
    private string $secret;
    private string $public;
    private string $hmacSecret;

    public function __construct()
    {
        $this->base       = rtrim(getenv('PAYMOB_BASE_URL') ?: 'https://accept.paymob.com', '/');
        $this->secret     = getenv('PAYMOB_SECRET_KEY');
        $this->public     = getenv('PAYMOB_PUBLIC_KEY');
        $this->hmacSecret = getenv('PAYMOB_HMAC_SECRET');
    }

    public function createIntention(array $args): array
    {
        $payload = [
            'amount'          => $args['amount_cents'],
            'currency'        => $args['currency'],
            'payment_methods' => $args['payment_methods'],
            'items'           => $args['items'] ?? [],
            'special_reference' => $args['special_reference'],
            'billing_data'    => [
                'first_name'   => $args['customer']['first_name'],
                'last_name'    => $args['customer']['last_name'],
                'email'        => $args['customer']['email'],
                'phone_number' => $args['customer']['phone'],   // REQUIRED
                'apartment' => 'NA', 'floor' => 'NA', 'street' => 'NA', 'building' => 'NA',
                'shipping_method' => 'NA', 'postal_code' => 'NA', 'city' => 'NA',
                'state' => 'NA', 'country' => 'EGY',
            ],
            'customer' => [
                'first_name' => $args['customer']['first_name'],
                'last_name'  => $args['customer']['last_name'],
                'email'      => $args['customer']['email'],
            ],
            'notification_url' => getenv('APP_URL') . '/api/paymob/webhook',
            'redirection_url'  => getenv('APP_URL') . '/payment/complete',
        ];

        $res = $this->post('/v1/intention/', $payload);
        return ['id' => $res['id'], 'client_secret' => $res['client_secret']];
    }

    public function checkoutUrl(string $clientSecret): string
    {
        return "{$this->base}/unifiedcheckout/?publicKey={$this->public}&clientSecret={$clientSecret}";
    }

    public function verifyTransactionPostHmac(array $obj, string $receivedHmac): bool
    {
        $fields = [
            $obj['amount_cents'], $obj['created_at'], $obj['currency'], $obj['error_occured'],
            $obj['has_parent_transaction'], $obj['id'], $obj['integration_id'], $obj['is_3d_secure'],
            $obj['is_auth'], $obj['is_capture'], $obj['is_refunded'], $obj['is_standalone_payment'],
            $obj['is_voided'], $obj['order']['id'], $obj['owner'], $obj['pending'],
            $obj['source_data']['pan'], $obj['source_data']['sub_type'],
            $obj['source_data']['type'], $obj['success'],
        ];
        $concat   = implode('', array_map([$this, 'boolStr'], $fields));
        $computed = hash_hmac('sha512', $concat, $this->hmacSecret);
        return hash_equals($computed, $receivedHmac);
    }

    public function refund(int $txnId, int $amountCents): array
    {
        return $this->post('/api/acceptance/void_refund/refund',
            ['transaction_id' => $txnId, 'amount_cents' => $amountCents]);
    }

    public function voidTxn(int $txnId): array
    {
        return $this->post('/api/acceptance/void_refund/void', ['transaction_id' => $txnId]);
    }

    public function capture(int $txnId, int $amountCents): array
    {
        return $this->post('/api/acceptance/capture',
            ['transaction_id' => $txnId, 'amount_cents' => $amountCents]);
    }

    /** Paymob concatenates booleans as lowercase true/false; PHP's (string)true is "1". */
    private function boolStr($v): string
    {
        if (is_bool($v)) return $v ? 'true' : 'false';
        return (string) $v;
    }

    private function post(string $path, array $body): array
    {
        $ch = curl_init($this->base . $path);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => json_encode($body),
            CURLOPT_HTTPHEADER     => [
                'Authorization: Token ' . $this->secret,   // literal "Token", not "Bearer"
                'Content-Type: application/json',
            ],
        ]);
        $out  = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        $data = json_decode($out, true) ?? [];
        if ($code >= 400) {
            throw new RuntimeException("Paymob error $code: $out");
        }
        return $data;
    }
}
```

> **Boolean fix:** PHP casts `true` to `"1"`, but Paymob's HMAC expects `"true"`/`"false"`. Use `boolStr()` (above) instead of plain `(string)` when concatenating, or HMAC verification silently fails.

## Laravel webhook route

```php
// routes/web.php  (or api.php)
use Illuminate\Http\Request;

Route::post('/api/paymob/webhook', function (Request $request) {
    $paymob   = new Paymob();
    $obj      = $request->input('obj', []);
    $received = $request->query('hmac', '');

    if (empty($obj) || ! $paymob->verifyTransactionPostHmac($obj, $received)) {
        return response()->json(['error' => 'Invalid HMAC'], 401);
    }
    if (($obj['success'] ?? false) && ! ($obj['pending'] ?? false)) {
        // markOrderPaid($obj['order']['id']) idempotently, then fulfill
    }
    return response()->json(['received' => true]);  // 200 stops Paymob retries
});
```

In Laravel, exclude this route from CSRF protection (add the path to `VerifyCsrfToken::$except`).

## Gotchas

- Header `Authorization: Token <secret>` (not Bearer). Amount in **cents**. `phone_number` required.
- Use `boolStr()` so booleans concatenate as `true`/`false` for HMAC.
- Always `hash_equals()` (timing-safe). Verify HMAC before trusting `success`; never trust redirect params. `client_secret` is single-use.
