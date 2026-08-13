---
description: Explain a Paymob error code, HTTP status, or error message and give the cause and fix.
argument-hint: "[error code, HTTP status, or error message]"
allowed-tools: Read
---

The user wants this Paymob error explained: $ARGUMENTS

1. Read the **Troubleshooting** table in `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/SKILL.md` and match `$ARGUMENTS` against its rows (by HTTP status, error text, or symptom). Quote the cause(s) listed for the matching row — do not paraphrase from memory, read the table each time in case it has changed.
2. If the fix involves code, open the reference file matching the user's project language/framework — `references/code-nodejs.md`, `references/code-python.md`, `references/code-php.md`, `references/code-dotnet.md`, `references/code-ruby.md`, or `references/code-frontend.md` — and adapt its corrected snippet to the user's project. Do not write a fix that contradicts what's in that file (for example, don't invent a different HMAC digest, header scheme, or amount unit than what the reference shows).
3. If the matching row is the HMAC-mismatch row, also read `references/hmac-verification.md` before answering and get the field order, digest algorithm, and the `obj.id`/`order.id` (POST) vs `id`/`order_id` (GET redirect) distinction from that file directly — never restate the field order from memory or from this command file, since this file intentionally carries no copy of it.
4. If `$ARGUMENTS` does not match any row in the table, say so explicitly rather than guessing at a cause. Then:
   - Point the user to `references/live-resources.md`, in particular the `llms.txt` doc index, to look up the current, authoritative explanation.
   - Offer to fetch the relevant Paymob docs page yourself, or ask the user to paste the relevant section if the docs are blocked to automated fetches (Paymob's docs sit behind Cloudflare, which can 403 some fetchers).
   - If the user has narrowed it to a specific unlisted status code, note that it may be an account, region, or method-specific error not yet cataloged in this skill.
