---
description: Audit a Paymob integration for go-live readiness and report a pass/fail checklist plus the Paymob-side approval steps still pending.
argument-hint: "[path to the payment code, optional]"
disable-model-invocation: true
allowed-tools: Read Glob Grep
---

Check this Paymob integration for go-live readiness: $ARGUMENTS

**Ground rules:**
- This is a **static, read-only audit**. Don't edit files, don't call Paymob, and don't switch anything to live.
- Never open a `.env` file or secret store to read values. Check only that secrets are *referenced* through environment or config variables, and never echo a secret you come across. If you find a hardcoded key, report its file and line with the value masked.

**Finding the skill files.** Use the first of these paths that exists:

1. `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/`, for a plugin install
2. `~/.claude/skills/paymob-integration/`, for a personal skill install. `~` is the user's home directory. On Windows, expand it yourself (`%USERPROFILE%\.claude\skills\…`), because a literal `~` won't resolve there.
3. `skills/paymob-integration/`, for a repository checkout, relative to the working directory

`${CLAUDE_PLUGIN_ROOT}` is only substituted for plugin installs. If it shows up unexpanded, this isn't a plugin install, so use path 2 or 3.

Read `references/post-integration.md` §1 (the go-live checklist). For checklist items 5 and 6, also read `references/hmac-verification.md`. **If you cannot read these files, say so and stop.** Don't audit from memory. A checklist from memory can pass a wrong HMAC field order or a missing idempotency guard, and those are the failures this check exists to catch.

## Step 1 — identify the integration type

Ask which kind of integration this is if it isn't obvious: custom code, a plugin, a Shopify app, or Payment Links. For plugins, Shopify apps, and Payment Links, skip the code items. Report only checklist items 4, 11, and 12, plus Paymob's approval stages. For WordPress, also recommend Store Check.

## Step 2 — audit the code (custom builds)

For each numbered item in the §1 checklist, report **PASS / FAIL / CAN'T VERIFY**, with the file and line as evidence. Pay particular attention to:

- **Item 7:** the checkout route must compute the amount from the server's own order record. If it reads the amount or item prices from the request body, that's a FAIL.
- **Item 3:** `notification_url` must not be hooks.paymob.com, a tunnel domain (ngrok, trycloudflare, and similar), `localhost`, or a private IP in any production config.
- **Item 2:** check whether the base URL, key mode, and Integration IDs come from the same per-environment config, so live keys can't be paired with test IDs.
- **Items 5 and 6:** audit these against `hmac-verification.md`, the same way `/paymob-check-hmac` does.

Mark anything that depends on the Dashboard or the account (items 4 and 11, and whether live credentials exist) as **CAN'T VERIFY: confirm in Dashboard**. Don't mark it PASS.

## Step 3 — report

1. The checklist table, with FAIL items first and a one-line fix for each.
2. The Paymob approval stages from §1 that the merchant should confirm with Paymob: paperwork, contract, risk, technical approval, and live credentials. Say plainly that code readiness doesn't make the account live.
3. Next steps:
   - The wizard's **Send your go-live documents** (not live approval).
   - A final test payment.
   - Watching the first live transaction for each payment method.
