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

## Replit and other hosted builders

For Replit, read `skills/paymob-integration/references/replit.md` (or `references/replit.md` relative to the installed skill). Verify the skill import separately from payment connector availability. A missing connector alone does not establish an API prohibition; inspect the backend and enforced host restrictions. Use Replit Secrets, verify test/production `APP_URL` origins and public webhook reachability, and keep MCP optional. Preserve the user's provider choice and existing project rules, including the project-root `replit.md`; explain an enforced host restriction without trying to bypass it. Missing credentials permit scaffolding and local mocked tests, not authenticated API calls or a claim that payments work.

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
10. **`notification_url` must be public HTTPS** (it works for all payment methods). Paymob can't reach `localhost`: to just see callbacks, use a `https://hooks.paymob.com` Hook URL (the user opens the page and pastes it back; no retention, display only); to test the handler, use a tunnel or deployed URL. Never ship either as the live URL.
11. **Always offer a test payment before go-live.** Ask "Ready to run a test payment?", confirm test mode (Shopify app test mode button, plugin Test Mode, or test keys + Test Integration IDs), and show only the test details for the enabled methods from `skills/paymob-integration/references/test-credentials.md`. How to test each integration type: `skills/paymob-integration/references/testing-guide.md`.
12. **The amount is priced server-side.** The checkout endpoint takes an order ID and customer details, and reads the amount and items from the merchant's own order record. It never takes them from the browser.
13. **Settle the payment model before writing checkout code.** Platform and web-vs-mobile are only two of three questions; the third is how the money is taken — one-off, subscription, saved card (CIT→MIT), Auth/Capture, MOTO phone order, or a marketplace split. Work through `skills/paymob-integration/references/choose-integration.md`, which carries the questionnaire, the trade-offs, a worked example per method, and what Paymob must enable on the account. Three of these change which HMAC type the callbacks carry; switching later is a rebuild. **MOTO and Verification have no published request shape** — confirm with the live docs or the merchant's account manager, never invent fields, and surface the PCI-scope and chargeback-liability consequences before proposing MOTO.
14. **Suggest extra payment methods only off a stated signal.** `skills/paymob-integration/references/payment-methods.md` has the per-region catalog and the rules: at most two, tied to something the merchant told you, after the card path passes its test, each named with what it costs to add (Paymob enablement, Live-only Integration IDs, certificates, no sandbox path, no refunds), and never as a go-live blocker. Most BNPLs and bank instalments **are** refundable; kiosk is not. Never quote fees, rates, settlement timing, or reserves.
15. **Leave no AI-authorship markers in the merchant's code.** No "generated by AI" file headers or comments, no robot emoji, "Generated with", or `Co-Authored-By` trailers on commits or pull requests in the merchant's repository. Follow that repository's own conventions, and flag genuine uncertainty by name — an unverified field shape, an untested method — instead of disclaiming the delivered work as machine-written.
16. **After integration, use Paymob's own tools and never leak secrets.** For go-live, operations, diagnosis, and support, follow `skills/paymob-integration/references/post-integration.md`. Paymob approval, not code, makes an account live. The wizard's go-live document upload isn't live approval. Diagnose with the Integration Wizard (`https://wizard.paymob.com/`): Code Lab, HMAC Signature Troubleshooter, Store Check at `/store-doctor/`, and Mobe. A support ticket may never contain the Secret Key, API Key, HMAC Secret, auth tokens, full card numbers, CVV, or OTPs. File a ticket through MCP `create_support_ticket` only after explicit confirmation.

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
