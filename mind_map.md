# Project Summary

Portable, cross-agent Paymob integration guidance packaged as a Codex/ChatGPT plugin, a Claude plugin, a standalone agent skill, `AGENTS.md`, and a universal prompt. It covers Egypt, UAE, KSA, and Oman.

# Detected Tech Stack

- Markdown-based agent skill and references
- JSON plugin and MCP manifests
- YAML Codex skill metadata
- Python repository validation with PyYAML for host metadata schemas
- Deterministic Python ZIP packaging for upload-based skill hosts
- GitHub Actions for validation and downloadable test artifacts

# How To Run

- Install validation dependency: `python -m pip install -r requirements-dev.txt`
- Validate: `python scripts/validate.py`
- Build the skill-upload ZIP: `python scripts/package_skill.py`
- Validate the skill with Codex tooling: `python <skill-creator>/scripts/quick_validate.py skills/paymob-integration`
- Validate the Codex plugin with Codex tooling: `python <plugin-creator>/scripts/validate_plugin.py .`

# Folder Map

- `.codex-plugin/plugin.json`: Codex/ChatGPT plugin manifest
- `.claude-plugin/plugin.json`: Claude plugin manifest
- `.claude-plugin/marketplace.json`: Claude custom marketplace catalog
- `.mcp.json`: optional official Paymob MCP connection
- `skills/paymob-integration/`: canonical skill package
- `skills/paymob-integration/agents/openai.yaml`: Codex skill UI, invocation, and MCP metadata
- `skills/paymob-integration/references/`: API, security, SDK, testing, and stack guides
- `AGENTS.md`: repository-level cross-agent router and safety rules
- `universal-prompt.md`: self-contained prompt for assistants without skill support
- `requirements-dev.txt`: validation-only PyYAML dependency
- `scripts/package_skill.py`: deterministic skill-only ZIP builder with one top-level `paymob-integration/` folder
- `scripts/validate.py`: package, marketplace, installation-doc, semantic-safety, YAML metadata, link, manifest, and upload-archive validation
- `.github/workflows/validate.yml`: CI validation plus the `paymob-integration-skill-upload` artifact

# Main Entry Points

- Skill hosts: `skills/paymob-integration/SKILL.md`
- Codex/ChatGPT plugin hosts: `.codex-plugin/plugin.json`
- Claude plugin hosts: `.claude-plugin/plugin.json`
- Generic coding agents: `AGENTS.md`
- Chat assistants: `universal-prompt.md`

# Architecture Flow

Host discovers manifest or skill -> skill routes by commerce platform -> merchant onboarding check -> web/API or mobile branch -> verified webhook -> reconciliation -> sandbox verification -> live rollout.

# Core Modules

- Platform routing and onboarding: `SKILL.md`
- Intention and checkout: `references/intention-api.md`
- Callback security: `references/hmac-verification.md`
- Reconciliation: `references/transaction-inquiry.md`
- Live tools: `.mcp.json` and `references/mcp-server.md`
- Stack implementations: `references/code-*.md`

# Routes / APIs / Commands

- Create payment: `POST {base_url}/v1/intention/`
- Official MCP endpoint: `https://mcp.paymob.com/mcp`
- Validation command: `python scripts/validate.py`
- Upload-package command: `python scripts/package_skill.py`

# Data Model / Storage

No application data store. Consumer applications should persist their own order ID, Paymob order/transaction identifiers, payment status, and idempotency state.

# External Integrations

- Paymob regional APIs and Unified Checkout
- Paymob mobile SDKs
- Official Paymob MCP server
- Live Paymob developer documentation and Integration Wizard

# Project Rules and Patterns

- Treat the HMAC-verified callback as payment truth.
- Keep all secrets server-side.
- Use SHA-512 with documented field order and timing-safe comparison.
- Prefer official platform plugins over custom code.
- Treat embedded specifications as snapshots; current official docs win.
- Use bounded read-only subagents for parallel research and security review; serialize edits and live account writes through the primary agent.

# Clean Code Checklist For This Project

- Keep `SKILL.md` under 500 lines and use direct one-level references.
- Keep plugin versions aligned.
- Keep skill descriptions concise and under host limits.
- Avoid duplicating detailed reference content.
- Validate all local Markdown links and manifest paths.

# Where To Add New Code

- New platform workflow: add a focused reference and route to it from `SKILL.md`.
- New stack: add `references/code-<stack>.md` and update the stack table.
- New plugin metadata: update both manifests when shared versioning changes.
- New deterministic package check: extend `scripts/validate.py`.

# Testing Map

- `scripts/validate.py`: portable repository and generated-archive checks
- `scripts/package_skill.py`: deterministic archive generation and structural verification
- Codex `quick_validate.py`: skill schema and metadata validation
- Codex `validate_plugin.py`: plugin manifest validation
- Forward tests: representative integration, HMAC-debugging, and multi-agent audit prompts

# Known Risks / Technical Debt

- Paymob API and SDK details change independently of this repository.
- The MCP server can perform financial actions; each live write requires current, operation-specific confirmation, preflight state, duplicate protection, and result verification.
- `universal-prompt.md`, `AGENTS.md`, and the canonical skill can drift if changes are not synchronized.
- Direct standalone skill installation must target `skills/paymob-integration`, not the repository root.
- Upload-based hosts must receive the generated `paymob-integration.zip`, not GitHub's full source archive.

# Recent Changes Log

- 2026-08-11: Added Codex plugin packaging, Codex skill metadata, Claude marketplace packaging, primary-agent safety rules, semantic validation automation, and corrected install guidance.
- 2026-08-11: Added a deterministic upload-only skill ZIP, CI artifact publishing, and a 200-character cross-host skill description while preserving all plugin and editor entry points.

# AI Agent Notes

- Read `SKILL.md` first, then only the references needed for the task.
- Never expose credentials in logs, prompts, patches, or committed files.
- For exact live API/SDK details, follow `references/live-resources.md`.
