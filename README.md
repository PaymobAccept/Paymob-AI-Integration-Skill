# Paymob Integration Skill for AI Agents

![version](https://img.shields.io/badge/version-3.2.1-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![works with](https://img.shields.io/badge/works%20with-Claude%20%C2%B7%20Cursor%20%C2%B7%20Windsurf%20%C2%B7%20Copilot%20%C2%B7%20Codex-8A2BE2)
![regions](https://img.shields.io/badge/regions-EGY%20%C2%B7%20UAE%20%C2%B7%20KSA%20%C2%B7%20OMN-orange)

Give any AI coding agent expert, **workflow-driven** knowledge of the [Paymob](https://paymob.com) payment gateway across **Egypt, UAE, KSA, and Oman**. The agent routes the developer by platform, walks through onboarding, and produces correct, copy-ready code for accepting cards, mobile wallets, BNPLs, Apple Pay, Google Pay, kiosk, and bank installments — on any tech stack.

Ships as a native **Codex/ChatGPT plugin**, a **Claude Code/Cowork plugin**, and a portable prompt (`universal-prompt.md`) + `AGENTS.md` for Cursor, Windsurf, GitHub Copilot, Gemini, and other agents.

---

## Works with any AI agent

It's all plain Markdown — any AI assistant can use it. Find your tool below; most setups take a single step.

> **Using an “Upload skill” screen?** Do not upload GitHub's full repository ZIP. Build or download the dedicated `paymob-integration.zip` described under [Skill upload](#skill-upload-claudeai--chatgpt); it contains one top-level skill folder and leaves every plugin/editor entry point unchanged.

### 1. OpenAI Codex → install the standalone skill

Ask Codex:

```text
Use $skill-installer to install https://github.com/PaymobAccept/Paymob-AI-Integration-Skill/tree/main/skills/paymob-integration
```

Targeting the `skills/paymob-integration` subdirectory is required; the repository root is a multi-agent plugin package, not a standalone skill directory. The standalone skill includes all references. Add the optional live Paymob server separately with `codex mcp add paymob --url https://mcp.paymob.com/mcp`.

### 2. Coding agents → drop in `AGENTS.md` (easiest, recommended)

[`AGENTS.md`](https://agents.md) is an open standard that coding agents read **automatically** from your project's root folder. Natively supported by **OpenAI Codex, Cursor, GitHub Copilot, Windsurf, Gemini CLI, Aider, Zed, Jules, Devin, Factory, Amp, RooCode, Warp, JetBrains Junie**, and more.

**One step** — copy this repo's [`AGENTS.md`](AGENTS.md) into the root of *your* project:

```bash
# run this from your project's root folder
curl -O https://raw.githubusercontent.com/PaymobAccept/Paymob-AI-Integration-Skill/main/AGENTS.md
```

- Already have an `AGENTS.md`? Just paste this one's contents into it under a `## Paymob` heading.
- Now ask your agent in plain English — *"Add Paymob card payments to my checkout"* — and it follows the Paymob rules automatically.

### 3. Chat assistants (ChatGPT · Gemini · Claude.ai · Copilot Chat …) → paste `universal-prompt.md`

1. Open [`universal-prompt.md`](universal-prompt.md) and **copy the whole file**.
2. Paste it into the assistant's **system prompt** / **custom instructions** (ChatGPT: *Settings → Personalization → Custom instructions*; Gemini: a *Gem*; Claude.ai: a *Project*'s instructions).
3. Describe what you're building. It's fully self-contained — no other files needed.

### 4. Prefer a pinned editor rules file? (optional)

If you'd rather use your editor's native rules file instead of `AGENTS.md`, save [`universal-prompt.md`](universal-prompt.md) as:

| Tool | Save it as (in your project) |
|---|---|
| Cursor | `.cursor/rules/paymob.mdc` |
| Windsurf / Devin Desktop | `.windsurf/rules/paymob.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cline · Continue · Roo | the tool's rules / context file |

### 5. Claude Code / Cowork → install the full plugin

Add this repository as a marketplace, then install the plugin. The plugin auto-registers the bundled live Paymob MCP server (see [below](#live-access--paymob-mcp-server)):

```bash
claude plugin marketplace add PaymobAccept/Paymob-AI-Integration-Skill
claude plugin install paymob-integration@paymob
```

Cowork and local-development options are under [Installation](#installation).

> **One source of truth, no drift:** the full skill lives in `skills/paymob-integration/`; `universal-prompt.md` is its self-contained portable copy; `AGENTS.md` is a short router to it.

---

## What it does

When you ask the agent for help integrating Paymob, it provides:

- **Platform routing first** — detects Shopify, an official e-commerce plugin platform (WooCommerce, Magento, Odoo, OpenCart, PrestaShop, …), or a custom build, and steers you to the fastest correct path instead of hand-coding when a prebuilt integration already exists.
- **Guided onboarding** — merchant-status check, dashboard credential collection, and sandbox-first testing before go-live.
- **Complete Intention API knowledge** — the only official payment-creation flow, with Unified Checkout (redirect) and the Pixel SDK (embedded).
- **Native Mobile SDK flow** — iOS / Android / Flutter / React Native, keeping the Secret Key off the device.
- **Corrected, copy-ready code in your stack** — Node.js/TypeScript/NestJS, Python/Django/Flask/FastAPI, PHP/Laravel, .NET/C#, Ruby/Rails, and React/Next.js/Vue.
- **All 3 HMAC types** — transaction, card token, and subscription — with exact field orders, SHA-512, and timing-safe comparison.
- **Reconciliation** — a Transaction Inquiry fallback for callbacks that never arrive, stuck "pending" orders, and admin lookups.
- **Core & advanced features** — subscriptions, saved cards (CIT/MIT), Auth/Capture, refund/void, split features, convenience fees.
- **Live-doc discipline** — points at Paymob's `llms.txt` index, developer docs, Integration Wizard, and community forum so the agent can confirm anything that may have changed.
- **Safe multi-agent execution** — separates codebase mapping, live-doc verification, and security review while keeping file edits and all live payment actions serialized through one primary agent.

---

## Live access — Paymob MCP server

Beyond *generating* code, agents can act on a merchant's **real Paymob account** through Paymob's official [MCP server](https://mcp.paymob.com/mcp) — creating payment intentions and links, pulling transactions/balances, exporting reports, requesting settlements, and opening support tickets (~25 tools). Great for interactive testing and reconciliation.

This plugin **bundles** it: the repo ships a root [`.mcp.json`](.mcp.json), so enabling the plugin registers the `paymob` server automatically. To add it to any other MCP client:

```json
{
  "mcpServers": {
    "paymob": { "type": "http", "url": "https://mcp.paymob.com/mcp" }
  }
}
```

Or in Codex or Claude Code standalone:

```bash
codex mcp add paymob --url https://mcp.paymob.com/mcp
claude mcp add --transport http paymob https://mcp.paymob.com/mcp
```

You authenticate **in-session** with your own Paymob API credentials (test mode first — it includes money-movement tools). It complements, but does **not** replace, the HMAC-verified webhook as the source of truth. Full setup, the tool catalog, and security notes: [`references/mcp-server.md`](skills/paymob-integration/references/mcp-server.md).

---

## Installation

### Skill upload (Claude.ai / ChatGPT)

The GitHub source archive is a **multi-agent plugin repository**, so its `SKILL.md` is intentionally nested at `skills/paymob-integration/SKILL.md`. Upload interfaces need a skill-only archive instead. Build it from a checkout:

```bash
python scripts/package_skill.py
```

Then upload `dist/paymob-integration.zip`. Its structure is:

```text
paymob-integration.zip
└── paymob-integration/
    ├── SKILL.md
    ├── agents/
    └── references/
```

`paymob-integration/` is the ZIP's single top-level folder, so `SKILL.md` is not nested behind the repository folder and `skills/`. GitHub Actions also publishes this file as the `paymob-integration-skill-upload` workflow artifact; extract the downloaded Actions artifact once, then upload the contained `paymob-integration.zip`.

This packaging step only copies the canonical skill into an ignored `dist/` archive. It does not move or duplicate tracked source, so Codex, Claude Code/Cowork plugins, Cursor, Windsurf, Copilot, and other `AGENTS.md` consumers keep their existing installation paths.

### OpenAI Codex (standalone skill)

In a Codex task, ask:

```text
Use $skill-installer to install https://github.com/PaymobAccept/Paymob-AI-Integration-Skill/tree/main/skills/paymob-integration
```

This repository also contains a valid `.codex-plugin/plugin.json` for marketplace packaging. During plugin development, validate the repository first and install it through a configured local marketplace; Codex CLI plugins are installed from marketplace sources.

### Claude Code (CLI)

```bash
claude plugin marketplace add PaymobAccept/Paymob-AI-Integration-Skill
claude plugin install paymob-integration@paymob
```

The repository's `.claude-plugin/marketplace.json` makes the GitHub repository a directly installable custom marketplace. To verify a local checkout before publishing, run `claude plugin validate .`.

### Cowork (Desktop)

Add `PaymobAccept/Paymob-AI-Integration-Skill` as a custom marketplace source, then install **Paymob Integration** from that marketplace.

### Other agents (Cursor, Windsurf, Copilot, …)

```bash
git clone https://github.com/PaymobAccept/Paymob-AI-Integration-Skill.git
```

Then follow the [Works with any AI agent](#works-with-any-ai-agent) table — copy `AGENTS.md` or `universal-prompt.md` into your own project at the location your tool expects.

### Local development (Claude Code)

```bash
claude --plugin-dir ./Paymob-AI-Integration-Skill
```

Validate the package before publishing:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
```

---

## Usage

Once installed, the agent activates on any Paymob request — or even a generic regional payment request ("add a payment gateway to my UAE store"). Try prompts like:

- "Help me integrate Paymob card payments in my Next.js app"
- "Add Vodafone Cash wallet payments to my Laravel backend"
- "My Paymob HMAC validation keeps failing — here's my code..."
- "Set up Paymob subscriptions with Python/FastAPI"
- "Integrate Apple Pay with Paymob in my React Native app"
- "Reconcile a Paymob order that's stuck pending"
- "Add Paymob to my Shopify / WooCommerce store"

---

## Repository structure

```
Paymob-AI-Integration-Skill/
├── AGENTS.md                          # Cross-agent entrypoint (Codex, Aider, Zed, Gemini CLI, …)
├── universal-prompt.md                # Portable prompt (Cursor, Windsurf, Copilot, ChatGPT, Gemini, …)
├── .mcp.json                          # Bundled Paymob MCP server (auto-registers when the plugin is enabled)
├── .codex-plugin/
│   └── plugin.json                    # Codex/ChatGPT plugin manifest (v3.2.1)
├── .claude-plugin/
│   ├── plugin.json                    # Claude Code plugin manifest (v3.2.1)
│   └── marketplace.json               # Claude custom marketplace catalog
├── skills/
│   └── paymob-integration/
│       ├── SKILL.md                   # Workflow backbone + multi-agent safety
│       ├── agents/
│       │   └── openai.yaml            # Codex UI, invocation, and MCP metadata
│       └── references/
│           ├── shopify-apps.md        # Paymob Shopify apps (on-site / off-site / BNPL) + install path
│           ├── intention-api.md       # Create Intention spec, Unified Checkout, common errors
│           ├── mobile-sdks.md         # Native SDK flow (iOS / Android / Flutter / React Native)
│           ├── hmac-verification.md   # Transaction HMAC: field order, SHA-512, worked example
│           ├── transaction-inquiry.md # Pull-based status checks / reconciliation
│           ├── test-credentials.md    # Sandbox cards, wallets, OTPs
│           ├── advanced-features.md   # Subscriptions, saved cards (CIT/MIT), Auth/Cap, refund/void, split, fees
│           ├── live-resources.md      # llms.txt, dev docs, Integration Wizard, community — when/how to use
│           ├── mcp-server.md          # Official Paymob MCP server: connect, authenticate, tool catalog, security
│           ├── code-nodejs.md         # Node.js / TypeScript / Express / NestJS
│           ├── code-python.md         # Python / Django / Flask / FastAPI
│           ├── code-php.md            # PHP / Laravel
│           ├── code-dotnet.md         # .NET / C# / ASP.NET
│           ├── code-ruby.md           # Ruby / Rails
│           └── code-frontend.md       # React / Next.js / Vue + Unified Checkout / Pixel SDK
├── .gitignore                         # Excludes generated archives and Python caches
├── requirements-dev.txt               # PyYAML dependency for schema validation
├── scripts/
│   ├── package_skill.py               # Deterministic skill-only upload ZIP builder
│   └── validate.py                    # Cross-platform package and archive validation
├── mind_map.md                        # Compact architecture and maintenance map
├── LICENSE
└── README.md
```

---

## Payment methods covered

| Method | Regions | Notes |
|--------|---------|-------|
| **Cards** (Visa, MC, Amex, MADA, OmanNet) | EGY, KSA, UAE, OMN | 3DS, MOTO, Card-on-File, Auth/Cap |
| **Mobile Wallets** (Vodafone Cash, Orange Cash, e& money, WePay, StcPay) | EGY, KSA | — |
| **BNPLs** (Valu, Tabby, Tamara, Souhoola, Sympl, and more) | EGY, KSA, UAE | 15+ providers |
| **Apple Pay** | EGY, KSA, UAE, OMN | Requires certificates |
| **Google Pay** | KSA, UAE, OMN | Not yet in Egypt |
| **Bank Installments** | EGY | Live IDs only |
| **Kiosk** (Aman, Masary) | EGY | No refund support |

## Supported regions

| Region | Base URL |
|--------|----------|
| Egypt (EGY) | `https://accept.paymob.com` |
| Oman (OMN) | `https://oman.paymob.com` |
| Saudi Arabia (KSA) | `https://ksa.paymob.com` |
| UAE | `https://uae.paymob.com` |

---

## Security

- Only the **Public Key** (`pk_*`) is safe in frontend code. The **Secret Key**, **API Key**, and **HMAC Secret** are server-side only — never commit them or ship them in a mobile binary.
- **The HMAC-verified webhook callback is the source of truth** for payment status — never the browser redirect params or a mobile SDK result.
- Always verify HMAC with **SHA-512** and a timing-safe comparison, and process callbacks atomically: unique `obj.id`, compare-and-set order state, and a uniquely keyed transactional outbox; use `order.id` / `special_reference` only for correlation.

## Staying current

Specs embedded here are known-good as of **June 2026**. Paymob changes endpoints, field orders, and SDK versions on its own schedule — the skill instructs the agent to cross-check the live docs ([`references/live-resources.md`](skills/paymob-integration/references/live-resources.md), especially the machine-readable `llms.txt` index) and lets the live docs win on any disagreement.

## Support & resources

- 📚 Developer docs — https://developers.paymob.com/
- 🧭 Integration Wizard (roadmap, runnable samples, HMAC/webhook tester) — https://wizard.paymob.com/
- 💬 Community forum — https://community.paymob.com/
- ✉️ Support — support@paymob.com

## Contributing

Contributions are welcome! If Paymob releases new APIs or you have improvements for a specific tech stack:

1. Fork this repo
2. Create a branch (`git checkout -b feature/add-go-support`)
3. Edit the relevant reference file (or add a new one) — keep `SKILL.md`, `universal-prompt.md`, and `AGENTS.md` in sync
4. Submit a pull request

## License

MIT — see [LICENSE](LICENSE) for details.
