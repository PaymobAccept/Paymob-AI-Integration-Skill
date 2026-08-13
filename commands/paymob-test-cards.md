---
description: Show Paymob sandbox test cards, wallet, and kiosk credentials, optionally filtered by payment method.
argument-hint: "[card|wallet|kiosk]"
allowed-tools: Read
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/references/test-credentials.md` in full and present the sandbox test credentials it contains to the user. Do not use any test numbers from memory — this file is the only source.

Argument handling for `$ARGUMENTS`:
- `card` → show only the Mastercard and Visa test card sections.
- `wallet` → show only the test mobile wallet section.
- `kiosk` → this reference file does not currently list kiosk sandbox credentials. Say so explicitly, then point the user to `references/live-resources.md` (the `llms.txt` doc index and developer docs) or `support@paymob.com` to get current kiosk sandbox details — do not invent kiosk numbers.
- No argument → show all sections the file contains (cards and wallet).

Always carry over, verbatim in meaning, these two caveats from the source file regardless of which filter was used:
1. Sandbox test transactions/intentions expire after **30 days** — a full test flow must be completed within that window.
2. Paymob does not officially document separate decline/error-simulation test numbers. If the user needs to test a decline or failure path, tell them to confirm with their Paymob account manager or `support@paymob.com` rather than guessing, since reusing a success-only test card with wrong details may just retry instead of declining.

Remind the user these are **Test-mode only** — never valid against Live keys or Live Integration IDs, and never real card data.
