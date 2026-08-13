---
description: Show Paymob sandbox test card and wallet credentials, optionally filtered by payment method.
argument-hint: "[card|wallet|kiosk]"
allowed-tools: Read
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/references/test-credentials.md` in full and present the sandbox test credentials it contains to the user. Do not use any test numbers from memory — this file is the only source.

Argument handling for `$ARGUMENTS`:
- `card` → show only the Mastercard and Visa test card sections.
- `wallet` → show only the test mobile wallet section.
- `kiosk`, or any other method the file has no section for (BNPL, Apple/Google Pay, bank installments) → say plainly that this reference file lists credentials for cards and wallets only, and that it has no entry for the requested method. Then point the user to `references/live-resources.md` (the `llms.txt` doc index and developer docs) or `support@paymob.com` for that method's sandbox details. **Do not invent numbers, and do not substitute a card number as a stand-in.** Do not assert how the method's sandbox flow works either — if it isn't in the reference file, it isn't established here.
- No argument → show all sections the file contains (cards and wallet).

Always carry over, verbatim in meaning, these two caveats from the source file regardless of which filter was used:
1. Sandbox test transactions/intentions expire after **30 days** — a full test flow must be completed within that window.
2. Paymob does not officially document separate decline/error-simulation test numbers. If the user needs to test a decline or failure path, tell them to confirm with their Paymob account manager or `support@paymob.com` rather than guessing, since reusing a success-only test card with wrong details may just retry instead of declining.

Remind the user these are **Test-mode only** — never valid against Live keys or Live Integration IDs, and never real card data.
