# Paymob Integration Plugin for Claude

A Claude Code / Cowork plugin that gives Claude expert-level, **workflow-driven** knowledge of Paymob payment gateway integration across **Egypt, UAE, KSA, and Oman**. It routes the developer by platform, walks through onboarding, and produces correct, copy-ready code for accepting cards, mobile wallets, BNPLs, Apple Pay, Google Pay, kiosk, and bank installments on any tech stack.

## What It Does

When you ask Claude for help integrating Paymob, this plugin provides:

- **Platform routing first** — detects Shopify, an official e-commerce plugin platform (WooCommerce, Magento, Odoo, OpenCart, PrestaShop, …), or a custom build, and steers you to the fastest correct path instead of hand-coding when a prebuilt integration exists.
- **Guided onboarding** — merchant-status check, dashboard credential collection, and sandbox-first testing before go-live.
- **Complete Intention API knowledge** — the only official payment-creation flow, with Unified Checkout (redirect) and the Pixel SDK (embedded).
- **Native Mobile SDK flow** — iOS/Android/Flutter/React Native, with the Secret Key kept off the device.
- **Corrected, copy-ready code in your stack** — Node.js/TypeScript/NestJS, Python/Django/Flask/FastAPI, PHP/Laravel, .NET/C#, Ruby/Rails, and React/Next.js/Vue.
- **All 3 HMAC types** — transaction, card token, and subscription — with exact field orders, SHA-512, and timing-safe comparison.
- **Reconciliation** — a Transaction Inquiry fallback for callbacks that never arrive, stuck "pending" orders, and admin lookups.
- **Core & advanced features** — subscriptions, saved cards (CIT/MIT), Auth/Capture, refund/void, split features, convenience fees.
- **Live-doc discipline** — points at Paymob's `llms.txt` index, developer docs, Integration Wizard, and community forum so the agent can confirm anything that may have changed.

## Installation

### Claude Code (CLI)

```bash
claude plugin install --git https://github.com/PaymobAccept/Paymob-Claude-Integration-Skill
```

### Cowork (Desktop)

Install from the plugin marketplace, or point to this repo as a custom marketplace source.

### Local Development

```bash
git clone https://github.com/PaymobAccept/Paymob-Claude-Integration-Skill.git
claude --plugin-dir ./Paymob-Claude-Integration-Skill
```

## Usage

Once installed, Claude automatically activates the skill when you ask about Paymob — or even for a generic regional payment request ("add a payment gateway to my UAE store"). Try prompts like:

- "Help me integrate Paymob card payments in my Next.js app"
- "Add Vodafone Cash wallet payments to my Laravel backend"
- "My Paymob HMAC validation keeps failing — here's my code..."
- "Set up Paymob subscriptions with Python/FastAPI"
- "Integrate Apple Pay with Paymob in my React Native app"
- "Reconcile a Paymob order that's stuck pending"
- "Add Paymob to my Shopify / WooCommerce store"

## Plugin Structure

```
Paymob-Claude-Integration-Skill/
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest (v3.0.0)
├── skills/
│   └── paymob-integration/
│       ├── SKILL.md                   # Workflow backbone: platform routing → onboarding → web/mobile → testing
│       └── references/
│           ├── shopify-apps.md        # Paymob Shopify apps (on-site / off-site / BNPL) + install path
│           ├── intention-api.md       # Create Intention spec, Unified Checkout, common errors
│           ├── mobile-sdks.md         # Native SDK flow (iOS / Android / Flutter / React Native)
│           ├── hmac-verification.md   # Transaction HMAC: field order, SHA-512, worked example
│           ├── transaction-inquiry.md # Pull-based status checks / reconciliation
│           ├── test-credentials.md    # Sandbox cards, wallets, OTPs
│           ├── advanced-features.md   # Subscriptions, saved cards (CIT/MIT), Auth/Cap, refund/void, split, fees
│           ├── live-resources.md      # llms.txt, dev docs, Integration Wizard, community — when/how to use
│           ├── code-nodejs.md         # Node.js / TypeScript / Express / NestJS
│           ├── code-python.md         # Python / Django / Flask / FastAPI
│           ├── code-php.md            # PHP / Laravel
│           ├── code-dotnet.md         # .NET / C# / ASP.NET
│           ├── code-ruby.md           # Ruby / Rails
│           └── code-frontend.md       # React / Next.js / Vue + Unified Checkout / Pixel SDK
├── universal-prompt.md                # Cross-platform prompt (ChatGPT, Gemini, Cursor, Windsurf, …)
├── LICENSE
└── README.md
```

## Payment Methods Covered

| Method | Regions | Notes |
|--------|---------|-------|
| **Cards** (Visa, MC, Amex, MADA, OmanNet) | EGY, KSA, UAE, OMN | 3DS, MOTO, Card-on-File, Auth/Cap |
| **Mobile Wallets** (Vodafone Cash, Orange Cash, e& money, WePay, StcPay) | EGY, KSA | — |
| **BNPLs** (Valu, Tabby, Tamara, Souhoola, Sympl, and more) | EGY, KSA, UAE | 15+ providers |
| **Apple Pay** | EGY, KSA, UAE, OMN | Requires certificates |
| **Google Pay** | KSA, UAE, OMN | Not yet in Egypt |
| **Bank Installments** | EGY | Live IDs only |
| **Kiosk** (Aman, Masary) | EGY | No refund support |

## Supported Regions

| Region | Base URL |
|--------|----------|
| Egypt (EGY) | `https://accept.paymob.com` |
| Oman (OMN) | `https://oman.paymob.com` |
| Saudi Arabia (KSA) | `https://ksa.paymob.com` |
| UAE | `https://uae.paymob.com` |

## Staying Current

Specs embedded here are known-good as of **June 2026**. Paymob changes endpoints, field orders, and SDK versions on its own schedule — the skill instructs the agent to cross-check the live docs (`references/live-resources.md`, especially the machine-readable `llms.txt` index) and lets the live docs win on any disagreement.

## Contributing

Contributions are welcome! If Paymob releases new APIs or you have improvements for a specific tech stack:

1. Fork this repo
2. Create a branch (`git checkout -b feature/add-go-support`)
3. Edit the relevant reference file or add a new one
4. Submit a pull request

## Cross-Platform Version

This repo includes a universal system prompt (`universal-prompt.md`) that works with ChatGPT, Gemini, Cursor, Windsurf, and any other AI assistant. Paste it into your AI's system prompt or custom instructions.

## License

MIT — see [LICENSE](LICENSE) for details.
