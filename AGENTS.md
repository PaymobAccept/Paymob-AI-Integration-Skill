# AGENTS.md — Paymob Payment Integration

This repository is a portable **skill** that makes any AI coding agent an expert at integrating the **Paymob** payment gateway (Egypt, UAE, KSA, Oman). It is not an app to build — it is guidance to apply to the *user's* project.

> **Only have this file?** The full skill (workflow + per-stack code + references) lives at **https://github.com/PaymobAccept/Paymob-AI-Integration-Skill**. When a path referenced below is not present in the current project, fetch it from that repo — raw base: `https://raw.githubusercontent.com/PaymobAccept/Paymob-AI-Integration-Skill/main/`.

**AI agents:** use the following authority order:

- For volatile endpoint shapes, HMAC fields, SDK versions, and regional behavior, the current official Paymob docs referenced by `skills/paymob-integration/references/live-resources.md` win.
- For the packaged workflow, `skills/paymob-integration/SKILL.md` and its task-specific references are canonical.
- `universal-prompt.md` is the self-contained fallback for hosts that cannot load the skill package; keep it synchronized with the canonical skill.
- For **live account actions**, Paymob's official MCP server is `https://mcp.paymob.com/mcp`. Setup and its versioned tool catalog are in `skills/paymob-integration/references/mcp-server.md`. It never replaces the HMAC-verified webhook as the source of truth.

## Multi-agent work

For broad integrations or audits, delegate independent read-only tasks such as codebase mapping, current-doc verification, and security review. Subagents receive no Paymob credentials, do not use authenticated Paymob tools, and return findings only with file/line references. Keep one primary agent responsible for requirements, final edits, tests, and every live action. If edits must be delegated, give agents exclusive non-overlapping paths and merge through the primary agent.

## Non-negotiable rules

1. **Intention API only.** Create payments with `POST {base_url}/v1/intention/`. Never use or suggest the legacy 3-step flow (auth token → order → payment key).
2. **HMAC is always SHA-512.** Concatenate the documented fields in the exact order, hex-lowercase, and compare timing-safely. There are 3 HMAC types (transaction = 20 fields, card token = 8 fields, subscription = string formula) — use the right one per callback.
3. **The HMAC-verified webhook callback is the source of truth** for payment status — never the browser `redirection_url` params (unauthenticated) or a mobile SDK result (UX only). Deduplicate callbacks on unique Paymob transaction/event ID (`obj.id`); in one database transaction, compare-and-set the order state and insert a uniquely keyed fulfillment outbox record. Use `order.id` / `special_reference` only for correlation.
4. **Amount is in the smallest currency unit** (cents/piasters): 100.00 EGP = `10000`.
5. **Post-payment auth uses the header** `Authorization: Token {secret_key}` — never `Bearer`, never `auth_token` in the body. Transaction Inquiry is the documented API-Key → short-lived `AUTH_TOKEN` exception.
6. **Secrets stay server-side.** Only the Public Key (`pk_*`) is safe in frontend code. Never expose or commit the Secret Key, API Key, or HMAC Secret; never create the intention from a browser or mobile app.
7. **Prefer a prebuilt integration when one exists.** Shopify → a Paymob app; WooCommerce/Magento/Odoo/OpenCart/PrestaShop/… → Paymob's official plugin. Only hand-code for custom/headless checkouts.
8. **Every live write needs current, specific authorization.** Obtain explicit confirmation for the current account, test/live mode, operation, target, amount, and currency; never reuse blanket approval. Read remote state first and keep a stable operation fingerprint/merchant reference.
9. **Never auto-retry an ambiguous financial write.** After a timeout or unclear response, query Paymob to determine whether it succeeded before retrying. Verify and report the remote result after every write.

## Regional base URLs

| Region | Base URL |
|--------|----------|
| Egypt  | `https://accept.paymob.com` |
| Oman   | `https://oman.paymob.com` |
| KSA    | `https://ksa.paymob.com` |
| UAE    | `https://uae.paymob.com` |

Default to Egypt unless the user specifies a region. Use **test-mode** keys with **test-mode** Integration IDs against the production base URL for sandbox testing (mismatched modes return 404 on intention creation).

## Credentials the user provides (from the Paymob dashboard)

`PAYMOB_SECRET_KEY` (server only) · `PAYMOB_PUBLIC_KEY` (frontend-safe) · `PAYMOB_HMAC_SECRET` (webhook validation) · `PAYMOB_API_KEY` (Transaction Inquiry only) · `PAYMOB_INTEGRATION_ID_*` (one per payment method) · `PAYMOB_BASE_URL` (region).

---

For the complete, self-contained instructions to paste into a chat-based assistant (ChatGPT, Gemini, Claude.ai) or a rules file (Cursor, Windsurf, Copilot), use [`universal-prompt.md`](universal-prompt.md).
