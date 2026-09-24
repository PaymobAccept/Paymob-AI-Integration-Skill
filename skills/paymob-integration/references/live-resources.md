# Live Paymob Resources — what each is, and when/how to use it

This skill embeds known-good specs, but Paymob changes endpoints, HMAC field orders, and SDK versions on its own schedule. These live resources let the coding agent (and the merchant) stay current. **When an embedded spec in this skill disagrees with the live docs, the live docs win.**

---

## 1. `llms.txt` — machine-readable documentation index (use this first)

**URL:** `https://developers.paymob.com/paymob-docs/getting-started/overview/llms.txt`

**What it is:** an LLM-oriented index file that lists Paymob's documentation pages and their URLs in a compact, plain-text form designed to be consumed by AI agents. It is the canonical, always-current map of the docs.

**How the agent should use it:**
- **Fetch it at the start of any non-trivial integration**, before hardcoding an endpoint path, a request field, or an HMAC field order. Use it to resolve the exact current doc URL for the topic you're implementing, then fetch that page.
- Treat it as the source of truth for *which* doc page covers *what* — paths in this skill (e.g. for the Intention API or HMAC) point at specific doc pages, but `llms.txt` reflects any reorganization or new pages Paymob has published since.
- If a `WebFetch`/HTTP fetch of the docs is blocked (Paymob fronts the docs with Cloudflare, which can return 403 to some automated fetchers), have the **merchant/user** open the link in a browser and paste the relevant section, or use the Integration Wizard's AI assistant (below) which has the docs indexed.

**How to wire it into code:** there is nothing to "call" programmatically as part of the payment flow — `llms.txt` is a build-time/authoring aid for the agent, not a runtime dependency. Do **not** make the merchant's production app fetch `llms.txt` at runtime; use it only while writing/validating the integration code.

---

## 2. Developer docs — the authoritative reference

**URL:** `https://developers.paymob.com/`

**What it is:** Paymob's official developer documentation portal: getting started, integration paths (Intention API, Unified Checkout, mobile SDKs, e-commerce plugins), webhooks & HMAC, transaction inquiry, refunds/void/capture, subscriptions, and FAQs/test credentials.

**How the agent should use it:**
- The definitive cross-check for request/response shapes, error payloads, and field orders. Every embedded reference in this skill cites its source doc URL — follow that link to confirm before going live.
- Use it (not memory) for anything version-sensitive: exact mobile-SDK package names/init code, current HMAC field lists per callback type, and any newly added payment method.

**How to wire it into code:** reference-only. Same as `llms.txt` — an authoring aid, not a runtime call.

---

## 3. Integration Wizard — roadmap, code lab, sandbox tools, Store Check, AI assistant

**URL:** `https://wizard.paymob.com/`

**What it is:** Paymob's interactive onboarding planner for merchants and developers. It:
- builds a **personalized setup guide** from the merchant's country, account status (no account / partial credentials / ready), platform (Shopify, WooCommerce, Magento 2, other plugins, custom web, mobile app, or no-code Payment Links), tech stack, and payment methods;
- covers every integration path, including **Unified Checkout** (redirect), **Pixel** (embedded in the merchant's page), **Payment Links** (no code), plugins, and mobile SDKs;
- provides a **code lab** with runnable samples, a **Test Cards** tab, a sandbox **Payment Links** creator, and a **"Pay with test card"** demo that creates a payment matching the chosen path and mode (with a Test/Live switch);
- includes an **HMAC checker**: paste the received `hmac`, the full webhook payload JSON, and the HMAC secret — the diagnosis runs entirely in the browser;
- includes **Store Check** (see below);
- has an AI assistant ("Mobe") and support ticket submission.

### Store Check (WooCommerce / WordPress)

Store Check audits a live storefront's Paymob setup:
- **Public scan** — enter the store's website address; no login needed.
- **Connected check** — deeper diagnosis of gateway settings and orders. Needs the **Paymob Wizard Connector** WordPress plugin:
  1. Download it from `https://wizard.paymob.com/store-doctor/downloads/paymob-wizard-connector.zip`.
  2. In wp-admin: **Plugins → Add New → Upload Plugin**, upload the zip, and activate it.
  3. Open Store Check from the **Paymob Wizard** menu in WordPress, or sign in on the wizard with the store URL and WordPress username. No WordPress application password is needed, and none is ever put in a URL.

The Wizard Connector is a **standalone helper** for diagnosis. It is **not** the Paymob WooCommerce payment plugin and does not process payments — the merchant still needs the official Paymob payment plugin installed and configured. Don't confuse the two when giving install steps.

**How the agent should use it:**
- **Point the merchant here for self-serve onboarding** and a tailored roadmap (complements Phase 1 in `SKILL.md`).
- **For HMAC/webhook debugging**, recommend the HMAC checker — the merchant can confirm in isolation that their computed signature matches before suspecting their app code. Pair it with `https://hooks.paymob.com` (section 5) to capture a real payload first.
- **For WooCommerce merchants**, suggest Store Check after the payment plugin is configured (see `testing-guide.md`).
- It is a **human-facing interactive tool**, not a programmatic API — don't try to script it. Hand the merchant the link and tell them what to do there.

**How to wire it into code:** not a code dependency. It is a complementary tool for the human in the loop.

---

## 4. Community forum — troubleshooting & escalation

**URL:** `https://community.paymob.com/`

**What it is:** Paymob's Discourse-based developer/merchant community: Getting Started threads, integration Q&A, region-specific issues (e.g. account/registration errors), best-practice discussions, and Paymob-team posts.

**How the agent should use it:**
- When a problem isn't resolved by the embedded references or the official docs (e.g. an undocumented error code, a region-specific onboarding snag), point the merchant to search/post here, or to email `support@paymob.com`.
- Good source for real-world gotchas (e.g. enabling free trials with subscriptions, regional account errors) that aren't in the formal docs.

**How to wire it into code:** not a code dependency — an escalation/troubleshooting pointer for the human.

---

## 5. Webhook inspector — hooks.paymob.com

**URL:** `https://hooks.paymob.com`

**What it is:** Paymob's webhook tester. Opening the page gives the visitor a unique Hook URL (`https://hooks.paymob.com/<uuid>`) and shows every POST, GET, or PUT sent to it as it arrives. Paymob-operated, safe to recommend publicly, and it keeps **no data** — requests appear only while the page is open.

**How the agent should use it:**
- When the merchant is developing locally and has no public URL yet, or wants to see the exact callback Paymob sends, suggest it as the intention's `notification_url` (and optionally `redirection_url`) in **test mode**.
- The agent cannot create the Hook URL itself — ask the user to open the page, copy the Hook URL, and paste it back. Tell them to keep the tab open while the test payment runs.
- It only **displays** requests; it does not forward them. For an end-to-end test of the merchant's own handler, use a tunnel or deployed URL — see *Making `notification_url` reachable* in `intention-api.md`.

**How to wire it into code:** never. It's a test-time inspection aid; never ship it as a production `notification_url`.

---

## Summary: include in the skill, not in the merchant's runtime

| Resource | Role | Used by | In production app's code? |
|---|---|---|---|
| `llms.txt` | Doc index for the agent | Coding agent (authoring) | No |
| developer docs | Authoritative spec | Coding agent (authoring) | No |
| Integration Wizard | Roadmap, code lab, sandbox tools, HMAC checker, Store Check, AI assistant | Merchant (human) | No |
| Community forum | Q&A / escalation | Merchant (human) | No |
| hooks.paymob.com | Live webhook inspector (test mode) | Merchant (human) | No — never as a production `notification_url` |

All of these are **authoring-, testing-, and support-time aids**, not runtime services the integration calls. The only Paymob endpoints the merchant's app actually calls are the Intention API, the Unified Checkout URL / Mobile SDK, the webhook callback you expose, and (optionally) the Transaction Inquiry API.
