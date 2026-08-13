# Security Policy

This repository ships integration guidance and tooling for the Paymob payment gateway — Intention API requests, HMAC webhook verification, and reconciliation flows. A vulnerability here (an incorrect HMAC check, a leaked-secret pattern, a bad idempotency example) can propagate into every merchant integration built from it, so please report issues privately rather than filing a public GitHub issue.

## Reporting a vulnerability

**Preferred:** open a [GitHub Security Advisory](https://github.com/PaymobAccept/Paymob-AI-Integration-Skill/security/advisories/new) for this repository. This reaches the maintainers privately and lets us coordinate a fix and disclosure timeline before any details go public.

**Alternative:** email **support@paymob.com** with a subject line starting `SECURITY:` and a description of the issue. Do not include real API keys, Secret Keys, or HMAC secrets in a report — a redacted example or a synthetic reproduction is enough for us to investigate.

Please do not open a public issue or pull request that discloses an unpatched vulnerability, since this repository's content is consumed directly by AI coding agents integrating live payment flows.

## What counts as a security issue here

This is guidance and skill/plugin content, not a running service, so most reports will be about content correctness rather than a running exploit. Examples worth reporting through the channel above rather than a normal issue:

- An HMAC verification example, field order, or digest algorithm that would let a forged webhook callback pass verification.
- Guidance or example code that would log, echo, or otherwise expose a Secret Key, API Key, or HMAC Secret.
- An idempotency or reconciliation example that could cause a payment to be applied twice, or a state change from an unverified callback.
- A bundled MCP server configuration (`.mcp.json`) or command file pointing at an unexpected or unverified endpoint.
- Anything that would cause an AI agent following this skill to act on unauthenticated or unconfirmed payment data.

Typos, broken links, and non-security documentation issues are welcome as regular [issues](https://github.com/PaymobAccept/Paymob-AI-Integration-Skill/issues) or pull requests.

## Supported versions

This project is distributed as source (a Claude Code / Codex plugin, a portable skill, and a universal prompt) rather than as installable released packages with independent patch lines. Security fixes are made to the `main` branch and included in the next tagged release; there is no support for versions older than the latest tag.

## Scope

This policy covers the content and packaging in this repository (`skills/`, `commands/`, `.claude-plugin/`, `.codex-plugin/`, `.mcp.json`, `AGENTS.md`, `universal-prompt.md`, and the validation/packaging scripts). It does not cover Paymob's own APIs, dashboard, or the `https://mcp.paymob.com/mcp` server's implementation — report those directly to Paymob support at **support@paymob.com** or through your account manager.
