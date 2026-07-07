# Live Paymob Resources — what each is, and when/how to use it

This skill embeds known-good specs, but Paymob changes endpoints, HMAC field orders, and SDK versions on its own schedule. These four live resources let the coding agent (and the merchant) stay current. **When an embedded spec in this skill disagrees with the live docs, the live docs win.**

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

## 3. Integration Wizard — interactive roadmap + code lab + tester + AI assistant

**URL:** `https://wizard.paymob.com/`

**What it is:** an interactive, AI-guided onboarding tool that:
- generates a **personalized integration roadmap** from the merchant's business type, platform, tech stack, and market;
- provides a **code laboratory** with tabbed, runnable SDK code samples and developer utilities — notably an **HMAC signature validator**, a **webhook tester**, and linting;
- includes an **AI assistant ("Mobe")** for real-time integration Q&A;
- offers **support ticket submission** for deeper help.

**How the agent should use it:**
- **Point the merchant here for self-serve onboarding** and a tailored roadmap (complements Phase 1 in `SKILL.md`).
- **For debugging HMAC/webhook issues**, recommend the Wizard's HMAC validator and webhook tester — the merchant can confirm in isolation that their computed signature matches Paymob's before suspecting their app code (see Phase 3 testing).
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

## Summary: include in the skill, not in the merchant's runtime

| Resource | Role | Used by | In production app's code? |
|---|---|---|---|
| `llms.txt` | Doc index for the agent | Coding agent (authoring) | No |
| developer docs | Authoritative spec | Coding agent (authoring) | No |
| Integration Wizard | Roadmap, code lab, HMAC/webhook tester, AI assistant | Merchant (human) | No |
| Community forum | Q&A / escalation | Merchant (human) | No |

All four are **authoring- and support-time aids**, not runtime services the integration calls. The only Paymob endpoints the merchant's app actually calls are the Intention API, the Unified Checkout URL / Mobile SDK, the webhook callback you expose, and (optionally) the Transaction Inquiry API.
