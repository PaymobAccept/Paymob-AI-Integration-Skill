---
description: Draft a redacted Paymob support ticket from the current issue and route it to the right channel (Mobe, forum, wizard Contact Support, email, or MCP).
argument-hint: "[short description of the problem, optional]"
disable-model-invocation: true
allowed-tools: Read Glob Grep
---

The user needs help from Paymob with: $ARGUMENTS

**Finding the skill files.** `post-integration.md` is in the skill's `references/` directory. Use the first of these paths that exists:

1. `${CLAUDE_PLUGIN_ROOT}/skills/paymob-integration/references/`, for a plugin install
2. `~/.claude/skills/paymob-integration/references/`, for a personal skill install. `~` is the user's home directory. On Windows, expand it yourself (`%USERPROFILE%\.claude\skills\…`), because a literal `~` won't resolve there.
3. `skills/paymob-integration/references/`, for a repository checkout, relative to the working directory

`${CLAUDE_PLUGIN_ROOT}` is only substituted for plugin installs. If it shows up unexpanded, this isn't a plugin install, so use path 2 or 3. If none of the paths resolve, search for `post-integration.md` under any `paymob-integration` directory.

**If you cannot read `post-integration.md`, say so and stop.** Don't route or draft from memory. The channel list and redaction rules are in that file.

## Step 1 — decide whether a ticket is needed

Read §5 of `post-integration.md`. If a Paymob tool can answer the problem itself, suggest that tool first and stop there unless the user still wants a ticket:

- HMAC mismatch: the HMAC Signature Troubleshooter
- Callbacks not arriving: hooks.paymob.com
- Request shape: Code Lab
- WordPress store: Store Check
- "How do I…": Mobe

This follows the tables in §4 and §5.

## Step 2 — gather the facts, never the secrets

Fill in the ticket template from §5 using the conversation, the codebase, and logs the user points you to. Ask only for what's missing: region, test or live mode, integration path, Integration IDs, payment method, Paymob transaction ID and order ID, merchant order ID, timestamp with timezone, the exact error, and business impact.

- Never read a `.env` value. Never ask for the Secret Key, API Key, HMAC Secret, or an auth token, and never include one.
- Never include a full card number, CVV, OTP, or MPIN. Mask customer phone numbers and emails.
- If a pasted log or payload contains any of these, redact it before quoting, and tell the user you did.

## Step 3 — present the draft and the channel

Show the finished ticket (subject and body) in one copyable block. Then name the channel from §5 that fits:

- Account, transaction, settlement, dispute, go-live, or incident: the **Contact Support** form on `https://wizard.paymob.com/` (Your Name, Email Address, Subject, Message), or email `support@paymob.com`
- Integration Q&A: `https://community.paymob.com/`
- Contract, fee, or settlement-schedule questions: the merchant's Paymob account manager

The wizard form is behind a security check, so the user submits it themselves. Don't promise a response time.

## Step 4 — only if the user asks you to file it and the Paymob MCP server is connected

Follow the MCP steps in §5 and the live-action safety rules in `SKILL.md`:

1. Show the exact text, account, and mode, and get explicit confirmation.
2. Call `create_support_ticket` once. It isn't pre-approved for this command, so the usual permission prompt appears. Don't auto-retry after a timeout or an unclear response.
3. Report the ticket reference that comes back.
