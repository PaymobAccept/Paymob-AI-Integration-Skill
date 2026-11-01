---
description: Walk through Paymob's integration chooser and recommend the right payment model and checkout surface for this merchant.
argument-hint: "[describe the business or how payments are taken]"
allowed-tools: Read Glob Grep
---

Read `references/choose-integration.md` in full, then run its questionnaire with the user and recommend a method. That file is the only source for the routing — do not recommend from memory.

**Locating the reference file.** Use the first of these that exists:

1. `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/references/` — plugin install
2. `~/.claude/skills/paymob-integration/references/` — personal skill install. `~` is the user's home directory; on Windows expand it yourself (`%USERPROFILE%\.claude\skills\…`), since a literal `~` will not resolve there.
3. `skills/paymob-integration/references/` — repository checkout, relative to the working directory

`${CLAUDE_PLUGIN_ROOT}` is substituted only for plugin installs. If you see it unexpanded, you are not in one — use path 2 or 3. If none resolve, search for `choose-integration.md` under any `paymob-integration` directory.

**If you cannot read the file, say so and stop.** Do not route from memory — sending a merchant down the wrong payment model costs them a rebuild, and the enablement steps and HMAC types differ per model.

**How to run it:**

1. **Mine `$ARGUMENTS` and the conversation first.** If the user described their business, answer as many of the file's questions as you honestly can from what they already said, and tell them which ones you inferred so they can correct you. Never invent an answer to skip a question.
2. **Ask the remaining questions one at a time**, in the file's order. Do not dump all five at once, and do not ask again about the platform or web-vs-mobile if the conversation already settled them. Remember the file wants **two** answers — a payment model and a checkout surface — so don't stop at the first method a question names, unless it was MOTO or an off-session MIT charge, which have no surface.
3. **Also check the codebase when you have one.** An existing `subscriptions` table, a cron that charges customers, an admin order-entry screen, or a marketplace `sellers` model each answer a question faster than asking does. Cite the file you saw it in.
4. **Give the recommendation** using the method card from the file: what to build, why it beat the nearest alternative in one sentence, the worked example, what Paymob must enable on the account, which Integration IDs to fetch, and which HMAC type the callbacks will carry.
5. **Name what you could not confirm.** If the card says Paymob doesn't publish a shape (MOTO, Verification), say so and tell the user to confirm with their account manager. Do not fill the gap with plausible-looking fields.
6. **For MOTO specifically**, always surface all four warnings from its card — account enablement, PCI DSS scope from staff handling PAN/CVV, merchant-side chargeback liability, and the unpublished request shape — and check first whether a Payment Link would do the job instead.
7. **Close with the next step**, which is normally the matching reference file and Phase 2A or 2B of the skill.

If the user asks which *payment methods* to enable rather than which integration model to build — cards, wallets, BNPL, Apple Pay — that is `/paymob-suggest-methods`; point them there instead of answering from this file.
