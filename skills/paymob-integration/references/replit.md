# Paymob in Replit

Read this when the agent runs in Replit, the project is hosted there, or a payment-provider picker refuses Paymob. Preserve the merchant's existing framework and provider choice.

## Contents

- [Verify installation](#verify-installation)
- [Separate the three integration layers](#separate-the-three-integration-layers)
- [Start skill and MCP setup with one request](#start-skill-and-mcp-setup-with-one-request)
- [Handle a missing connector](#handle-a-missing-connector)
- [Configure the existing app](#configure-the-existing-app)
- [Verify callbacks and persistence](#verify-callbacks-and-persistence)
- [Run the test checkpoint](#run-the-test-checkpoint)
- [Official sources and validation status](#official-sources-and-validation-status)

## Verify installation

1. In Replit Agent, open **+ → Use a skill**, then **Add from GitHub**.
2. Paste the public skill folder URL:
   `https://github.com/PaymobAccept/Paymob-AI-Integration-Skill/tree/main/skills/paymob-integration`
3. Select **Preview skills**, select **paymob-integration**, then **Import**. Preview checks structure; it does not prove the agent loaded the instructions.
4. Select the imported skill for the task. For a project-level copy, the expected entrypoint is `.agents/skills/paymob-integration/SKILL.md`, with `references/` beside it. Workspace imports can be managed by the host instead of appearing at that project path; use the host-provided skill location.
5. Ask the agent to read this guide, `intention-api.md`, and the backend reference matching the project; report which files it actually read without requesting secrets. If the host cannot read supporting files, import the complete skill folder or use the canonical skill's scoped reference-fetch fallback.

An instruction to "use" a GitHub URL is not proof of installation. If GitHub import is unavailable in the workspace, copy the complete `skills/paymob-integration` folder from a reviewed checkout into the project's `.agents/skills/`; preserve existing skills and ask the agent to read the resulting entrypoint explicitly.

Do not replace the project's root `replit.md` or `AGENTS.md`. An optional short section can be appended to `replit.md` after reviewing the existing file:

```markdown
## Paymob payments
Use the imported paymob-integration skill and its Replit reference for Paymob tasks.
Keep credentials in Replit Secrets, use the existing backend and durable database,
and start with test mode. Check host restrictions separately from connector availability.
```

Keep that section as a router, not a second copy of API specs. Update/re-import the skill deliberately; do not assume an installed copy tracks GitHub `main`. Compare a release tag with the repository version before using the release ZIP because a published release can lag source.

## Separate the three integration layers

| Layer | Purpose | Needed for custom app code? |
|---|---|---|
| Paymob integration skill | Instructions and API/code references | Use it for guidance |
| Replit built-in payment connector | Replit's managed provider setup | Not the same as custom API code; check actual host restrictions |
| Paymob MCP account tools | Agent actions on a merchant account | Optional; not required to write the checkout backend |

Importing this skill does not register a payment connector, install Claude slash commands, or connect the Paymob MCP server. Do not require MCP authentication to scaffold or integrate the app's backend. Use `mcp-server.md` only when the user explicitly needs supported account-tool operations; do not assume a repository-root `.mcp.json` is automatically honored by Replit.

## Start skill and MCP setup with one request

If the user wants both integration guidance and MCP account tools, start with one setup request:

```text
Set up the Paymob integration skill and Paymob MCP for this Replit project.
Import the complete skill from:
https://github.com/PaymobAccept/Paymob-AI-Integration-Skill/tree/main/skills/paymob-integration
Verify SKILL.md and its supporting references are readable.
Connect the remote MCP server https://mcp.paymob.com/mcp through Replit's supported
custom MCP flow; if you cannot change those settings, show me the Add to Replit link.
Verify tool discovery and current server help first. Guide me through secure test-account
authentication if this host supports it; never ask for keys in chat or put them in URLs.
Report skill installation, MCP connection, and account authentication as separate statuses.
Do not create payment objects, move money, or deploy anything as part of this setup.
```

Use [Add Paymob MCP to Replit](https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6IlBheW1vYiIsImJhc2VVcmwiOiJodHRwczovL21jcC5wYXltb2IuY29tL21jcCJ9) to open the supported connection flow, or follow the manual MCP settings steps in `mcp-server.md`. The link contains no credentials.

This is **one starting instruction, not a verified one-command installer**. Replit may require the user to import the skill, confirm the MCP connection, or authenticate separately; permissions and its security scanner still apply. Do not claim "fully connected" unless skill loading, MCP tool discovery, and secure test-account authentication have each been verified. A working MCP connection does not by itself prove the app's payment flow works.

## Handle a missing connector

If Agent says "Paymob is not available; choose Stripe or Whop":

1. Confirm the user's requested provider remains Paymob. Dismissing another-provider picker alone does not cancel that request.
2. Inspect the actual app: backend availability, framework, payment code, persistent storage, and deployment type. A frontend-only artifact needs a permitted backend before it can hold secret keys or create intentions.
3. Distinguish **no built-in catalog entry**, **skill not loaded**, **missing backend**, **missing test credentials**, **network failure**, and **enforced host restriction**. Do not report one as another.
4. If custom external API code is permitted, follow the skill's custom web/API branch with `intention-api.md`, `hmac-verification.md`, and the matching backend/frontend references. Preserve the app's stack.
5. If Replit enforces a payment-provider restriction, stop the affected operation, identify the host message/rule and impact, and explain the supported next step (Replit support or a permitted external backend). Do not bypass the restriction, claim the skill overrides it, or replace Paymob without the user's choice.

Replit's public docs distinguish external API integrations from connectors and document built-in monetization providers. They do not establish that every custom payment provider is permitted by every Agent mode or plan. State that uncertainty; an imported skill cannot grant capabilities the host withholds.

## Configure the existing app

First confirm merchant country, enabled methods, account status, and usable **test-mode** credentials. While these are missing, scaffold routes/configuration, order/payment-attempt schemas, and local mocked tests; do not make authenticated requests.

Use **Replit Secrets** for sensitive values. Let the user enter values in the UI; check presence only, never echo secrets or dump the process environment. Host-injected environment variables do not require a `.env` file or dotenv initialization.

| Variable | Use |
|---|---|
| `PAYMOB_SECRET_KEY` | Server-side Intention/payment actions; test key initially |
| `PAYMOB_PUBLIC_KEY` | Checkout public key matching test mode |
| `PAYMOB_HMAC_SECRET` | Server-side webhook verification |
| `PAYMOB_INTEGRATION_ID_CARD` | Test Integration ID for cards; add one per enabled method |
| `PAYMOB_API_KEY` | Only when implementing Transaction Inquiry/reconciliation |
| `PAYMOB_BASE_URL` | Merchant region's Paymob origin; see the canonical regional table |
| `APP_URL` | Merchant app's external HTTPS origin; different from the Paymob origin |

Never place the Secret Key, API Key, or HMAC Secret in frontend/public variables such as `VITE_*`, `NEXT_PUBLIC_*`, or a browser bundle. Review published-app secrets separately under **Publishing → Adjust settings → Production app secrets**; test and production credentials, Integration IDs, and origins must match their intended mode.

Treat the stack examples as adaptation templates: retain the app/router bootstrap and implement the required database persistence adapters. Installing the skill does not supply an executable payment backend or database schema automatically.

## Verify callbacks and persistence

- Build the checkout amount and currency from an owned server-side order record. Authorize checkout and status lookup for the requesting user.
- Configure `notification_url` to the actual backend webhook route and `redirection_url` to the completion page. Derive both from the intended `APP_URL`; keep callback and redirect responsibilities separate.
- Verify an unauthenticated external POST reaches that route. An unsigned test request should receive a controlled rejection and change no order state; a GET that returns a homepage is not evidence of a functioning callback. Account for access controls, sleeping previews, route/SPA fallbacks, and changed origins.
- Validate payload shape before signature extraction. Verify the current documented HMAC fields and SHA-512 comparison before any payment-state mutation; use `hmac-verification.md` and the current live docs.
- Persist the server-created Paymob payment attempt and bind the signed Paymob `order.id` to the owned local order. Do not let unsigned `merchant_order_id` alone select a fulfillment target. Compare signed amount, currency, integration/account, and test/live mode with the stored attempt, and distinguish sale/capture from auth, refund, and void before marking an order paid.
- Use durable database constraints, atomic state transitions, and the fulfillment outbox described by the skill. Do not store orders or callback deduplication only in workspace files or process memory.
- Keep logs redacted. Never log credential values, full customer details, or whole live callback payloads by default. Do not automatically retry an intention after a timeout with an unknown outcome; reconcile it first.

## Run the test checkpoint

Separate evidence of installation from evidence of working payments:

1. **Installation:** confirm the imported skill and required references are readable.
2. **Offline behavior:** test missing credentials, malformed/invalid-HMAC callbacks, amount/currency/order mismatches, unsigned-reference tampering, duplicate callbacks, and auth/refund/void classification. No real credentials are needed.
3. **Integration test:** follow `testing-guide.md`, obtain the user's test-mode checkpoint, create a test intention from the owned server-side order, launch Unified Checkout, and observe the app's own verified callback and durable state update. A mocked flow or hooks.paymob.com display is not proof of this.
4. **Go-live:** use `post-integration.md`; confirm merchant activation and production configuration. A working test payment does not authorize live account writes or deployment.

## Official sources and validation status

Documentation checked **2026-10-14**:

- [Replit Agent Skills](https://docs.replit.com/features/agent/skills) — GitHub imports and project skill structure.
- [Replit Agent Integrations](https://docs.replit.com/features/integrations/overview) — connectors versus external APIs.
- [Replit Monetization](https://docs.replit.com/features/monetization/overview) — built-in payment providers.
- [Replit Secrets](https://docs.replit.com/core-concepts/project-editor/app-setup/secrets) — injected environment variables and published-app secrets.
- [Replit project instructions](https://docs.replit.com/features/project-setup/replit-dot-md) — preserve and extend the root project instructions.

These instructions are documentation-verified. Repository validation and offline checks do not establish successful Replit UI import, Agent policy acceptance, or end-to-end Paymob payments. Record those host-specific results separately when tested.
