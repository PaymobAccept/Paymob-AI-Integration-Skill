---
description: Show Paymob sandbox test card and wallet credentials, optionally filtered by payment method.
argument-hint: "[card|wallet|kiosk|bnpl]"
allowed-tools: Read Glob
---

Read `references/test-credentials.md` in full and present the sandbox test credentials it contains to the user. Do not use any test numbers from memory — this file is the only source.

**Locating the reference file.** Use the first of these that exists:

1. `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/references/` — plugin install
2. `~/.claude/skills/paymob-integration/references/` — personal skill install. `~` is the user's home directory; on Windows expand it yourself (`%USERPROFILE%\.claude\skills\…`), since a literal `~` will not resolve there.
3. `skills/paymob-integration/references/` — repository checkout, relative to the working directory

`${CLAUDE_PLUGIN_ROOT}` is substituted only for plugin installs. If you see it unexpanded, you are not in one — use path 2 or 3. If none resolve, search for `test-credentials.md` under any `paymob-integration` directory.

**If you cannot read the file, say so and stop.** Do not list card numbers from memory — stale or invented test credentials waste a merchant's debugging time on a payment that was never going to succeed.

Argument handling for `$ARGUMENTS`:
- `card` → show only the Mastercard and Visa test card sections.
- `wallet` → show only the test mobile wallet section.
- `kiosk`, `bnpl`, or a named BNPL provider (Valu, Souhoola, Tabby, Tamara, Sympl, …) → report what the file's **Methods with no sandbox test path** section says. Do not offer a workaround that section doesn't list, and do not substitute a test card so the method looks covered.
- Any other method the file has no section for (Apple/Google Pay, bank installments) → say plainly that the file has no entry for it, then point the user to `references/live-resources.md` (the `llms.txt` doc index and developer docs) or `support@paymob.com`. **Do not invent numbers, and do not substitute a card number as a stand-in.** Do not assert how that method's sandbox flow works either — if it isn't in the reference file, it isn't established here.
- No argument → show all sections the file contains (cards and wallet).

Always carry over, verbatim in meaning, these two caveats from the source file regardless of which filter was used:
1. Sandbox test transactions/intentions expire after **30 days** — a full test flow must be completed within that window.
2. Paymob does not officially document separate decline/error-simulation test numbers. If the user needs to test a decline or failure path, tell them to confirm with their Paymob account manager or `support@paymob.com` rather than guessing, since reusing a success-only test card with wrong details may just retry instead of declining.

Remind the user these are **Test-mode only** — never valid against Live keys or Live Integration IDs, and never real card data.
