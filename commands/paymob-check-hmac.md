---
description: Audit a Paymob webhook HMAC verification implementation for correctness and safe failure behavior.
argument-hint: "[path to the webhook handler, optional]"
disable-model-invocation: true
---

Audit the user's Paymob webhook HMAC verification code: $ARGUMENTS

**Non-negotiable ground rules for this command, before anything else:**
- Never ask the user to paste their HMAC secret, API key, or Secret Key into this conversation.
- Never read a `.env` file's actual secret value, and never echo, print, or write any secret into chat output, logs, or a file you create.
- The default mode is a **static code audit** — no computation is required to complete it.

## Step 1 — locate the code

If `$ARGUMENTS` names a path, start there. Otherwise search for the callback route bound to `notification_url` / the `hmac` query parameter, or for `PAYMOB_HMAC_SECRET` usage.

## Step 2 — audit against `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/references/hmac-verification.md`

Read that file first — don't rely on memory for the field order or algorithm, since this command carries no copy of the spec. Then check each item below and report pass/fail with file/line references:

1. **Digest**: HMAC-**SHA-512**, not SHA-256 or any other digest.
2. **Source and order**: the concatenation reads fields from `body.obj` (the POST payload) in exactly the field order given in `hmac-verification.md` — flag any other ordering, including "alphabetical by key name," as a failure.
3. **No id/order.id conflation**: the code must not treat `obj.id` (the transaction/event id) and `obj.order.id` (the order id) as interchangeable — both are distinct fields in the concatenation.
4. **Raw values**: fields are concatenated as received — no reformatted timestamps, no rounded or reformatted numbers, no inserted whitespace.
5. **Fail closed**: a non-matching computed HMAC results in **no state change** — the handler returns/rejects before any database write, with no fallback path that updates order status anyway.
6. **Idempotency**: enforced via a **unique constraint on `obj.id`** plus a transactional outbox, not a bare application-level "already processed" flag with no backing unique index. Flag an in-memory set, a non-unique-indexed boolean column, or a check-then-write pattern without a DB constraint as a failure, even if it looks like it works in testing.

If the merchant's integration also handles card-token or subscription callbacks, note that those use a different field list per `hmac-verification.md` and must not be assumed to share the transaction-callback order — check whether the code accounts for that separately.

Present the result as a pass/fail checklist per item, plus anything missing entirely (e.g., no idempotency handling at all) rather than assuming it exists elsewhere in the codebase.

## Step 3 — only if the user explicitly asks you to compute or verify an HMAC against a real callback payload

- Do this by writing and running a short script that reads the secret from the environment (`process.env.PAYMOB_HMAC_SECRET` or the equivalent in the user's language) at run time — never by hardcoding the secret, never by asking the user to paste it here, and never by having the script print, log, or return the secret itself.
- Only surface the computed hash and whether it matches; avoid printing the full concatenated string if it contains payload PII the user hasn't already shown you.
- Delete or avoid committing any throwaway script that touches the secret.

## Step 4 — isolated testing

For testing outside the codebase, point the user to Paymob's HMAC validator and webhook tester at `https://wizard.paymob.com/`, which lets them confirm their signature computation in isolation without exposing the secret in this conversation.
