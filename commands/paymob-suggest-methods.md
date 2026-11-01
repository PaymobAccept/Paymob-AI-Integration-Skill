---
description: Recommend which Paymob payment methods to enable for a merchant's business, with regional availability, refund support, and what each one costs to add.
argument-hint: "[describe the business, region, and typical order value]"
allowed-tools: Read Glob Grep
---

Read `references/payment-methods.md` in full, then recommend methods for this merchant using its catalog and its **When to raise an extra method** table. That file is the only source for availability and refund support — do not answer from memory.

**Locating the reference file.** Use the first of these that exists:

1. `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/references/` — plugin install
2. `~/.claude/skills/paymob-integration/references/` — personal skill install. `~` is the user's home directory; on Windows expand it yourself (`%USERPROFILE%\.claude\skills\…`), since a literal `~` will not resolve there.
3. `skills/paymob-integration/references/` — repository checkout, relative to the working directory

`${CLAUDE_PLUGIN_ROOT}` is substituted only for plugin installs. If you see it unexpanded, you are not in one — use path 2 or 3. If none resolve, search for `payment-methods.md` under any `paymob-integration` directory.

**If you cannot read the file, say so and stop.** Do not list methods from memory — regional availability, refund support, and Live-only restrictions change, and a wrong answer here sends the merchant to build against a method their account can't use.

**How to run it:**

1. **Establish the region first** (EGY, KSA, UAE, OMN). Ask if `$ARGUMENTS` and the conversation don't say. Almost every row in the catalog is region-dependent, so a recommendation without a region is a guess.
2. **Look for the signals** the file's table is keyed on: typical order value, what they sell, who their customers are, device mix, whether they ship later, whether other sellers get paid, whether orders come in by phone. Use what the user said and what the codebase shows — don't interrogate them for every row.
3. **Recommend at most two**, each tied to the signal that prompted it, following the file's **Rules for suggesting**. If the user gave no signal at all, say cards are the right starting point and ask the one question that would change your answer, rather than reciting the catalog.
4. **Name what each one costs them** — Paymob enablement or approval, Live-only Integration IDs, certificates and domain verification for Apple Pay, no sandbox test path, no refund support for kiosk. A recommendation without its cost is a sales pitch.
5. **Say plainly that none of it blocks go-live.** The merchant launches on cards and enables the rest from the dashboard afterwards.
6. **Never quote fees, rates, settlement timing, or reserves**, even if asked directly — those are contractual. Send them to their Paymob account manager or `support@paymob.com`.
7. If a method they asked about isn't in the file, say so rather than guessing, and point to `references/live-resources.md`.

If the user is really asking *how* to take payments — recurring, phone orders, hold-then-capture, marketplace splits — that is `/paymob-choose-integration`; point them there instead.
