#!/usr/bin/env python3
"""Validate the portable skill and its Codex and Claude plugin packages."""

from __future__ import annotations

import json
import re
import sys
import uuid
from pathlib import Path

import yaml
from package_skill import archive_errors, build_archive

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "paymob-integration"
SKILL_FILE = SKILL_DIR / "SKILL.md"
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
MCP_MANIFEST = ROOT / ".mcp.json"
OPENAI_METADATA = SKILL_DIR / "agents" / "openai.yaml"
README = ROOT / "README.md"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
AGENTS = ROOT / "AGENTS.md"
UNIVERSAL_PROMPT = ROOT / "universal-prompt.md"
MCP_REFERENCE = SKILL_DIR / "references" / "mcp-server.md"
HMAC_REFERENCE = SKILL_DIR / "references" / "hmac-verification.md"
ADVANCED_REFERENCE = SKILL_DIR / "references" / "advanced-features.md"
COMMANDS_DIR = ROOT / "commands"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_LINK_PATTERN = re.compile(r"\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)")
PLUGIN_ROOT_REFERENCE_PATTERN = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`\"')]+)")
ALLOWED_COMMAND_FRONTMATTER_KEYS = {
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "arguments",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "disallowed-tools",
    "model",
    "effort",
    "context",
    "agent",
    "background",
    "hooks",
    "paths",
    "shell",
    "metadata",
    "license",
    "compatibility",
}
# Matches a hardcoded Paymob key/secret literal, as opposed to an env var name
# or a doc reference — command files must only ever read secrets at runtime.
COMMAND_SECRET_PATTERN = re.compile(
    r"\b(sk|pk)_(live|test)_[A-Za-z0-9]{10,}\b"
    r"|PAYMOB_(?:HMAC_SECRET|SECRET_KEY|API_KEY)\s*[=:]\s*['\"][^'\"\s]{6,}['\"]"
)
# The literal field-order list from hmac-verification.md; a command file that
# reproduces it has drifted from the single-source-of-truth rule.
HMAC_FIELD_ORDER_RESTATEMENT_PATTERN = re.compile(
    r"amount_cents\s*\r?\n\s*created_at\s*\r?\n\s*currency"
)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing required file: {path.relative_to(ROOT)}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return {}


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"Missing required file: {path.relative_to(ROOT)}")
    except UnicodeDecodeError as exc:
        errors.append(f"Invalid UTF-8 in {path.relative_to(ROOT)}: {exc}")
    return ""


def validate_skill(errors: list[str]) -> str:
    try:
        raw = SKILL_FILE.read_bytes()
    except FileNotFoundError:
        errors.append("Missing skills/paymob-integration/SKILL.md")
        return ""

    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("SKILL.md must be UTF-8 without a byte-order marker")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"SKILL.md is not valid UTF-8: {exc}")
        return ""

    match = re.match(r"^---\r?\n(?P<header>.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        errors.append("SKILL.md must start with closed YAML frontmatter")
        return ""
    try:
        frontmatter = yaml.safe_load(match.group("header"))
    except yaml.YAMLError as exc:
        errors.append(f"SKILL.md frontmatter is invalid YAML: {exc}")
        return ""
    if not isinstance(frontmatter, dict):
        errors.append("SKILL.md frontmatter must be a YAML object")
        return ""

    allowed = {"name", "description", "license", "allowed-tools", "metadata"}
    unexpected = sorted(set(frontmatter) - allowed)
    if unexpected:
        errors.append(f"SKILL.md has unsupported frontmatter keys: {', '.join(unexpected)}")
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        errors.append(f"Invalid skill name: {name!r}")
        name = ""
    if isinstance(name, str) and len(name) > 64:
        errors.append("Skill name exceeds 64 characters")
    if not isinstance(description, str) or not description.strip():
        errors.append("Skill description is missing or is not a string")
    elif len(description.strip()) > 200:
        errors.append(
            f"Skill description is {len(description.strip())} characters; maximum is 200"
        )
    elif "<" in description or ">" in description:
        errors.append("Skill description cannot contain angle brackets")
    if SKILL_DIR.name != name:
        errors.append(f"Skill folder {SKILL_DIR.name!r} must match name {name!r}")
    if not OPENAI_METADATA.is_file():
        errors.append("Missing skills/paymob-integration/agents/openai.yaml")
    return name

def validate_openai_metadata(skill_name: str, errors: list[str]) -> None:
    metadata_text = read_text(OPENAI_METADATA, errors)
    if not metadata_text:
        return
    try:
        metadata = yaml.safe_load(metadata_text)
    except yaml.YAMLError as exc:
        errors.append(f"agents/openai.yaml is invalid YAML: {exc}")
        return
    if not isinstance(metadata, dict):
        errors.append("agents/openai.yaml must contain a YAML object")
        return
    unexpected = sorted(set(metadata) - {"interface", "dependencies", "policy"})
    if unexpected:
        errors.append(f"agents/openai.yaml has unsupported keys: {', '.join(unexpected)}")

    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        errors.append("agents/openai.yaml interface must be an object")
    else:
        allowed_interface = {
            "display_name", "short_description", "icon_small", "icon_large",
            "brand_color", "default_prompt",
        }
        unknown = sorted(set(interface) - allowed_interface)
        if unknown:
            errors.append(f"agents/openai.yaml interface has unsupported keys: {', '.join(unknown)}")
        for field in ("display_name", "short_description", "default_prompt"):
            if not isinstance(interface.get(field), str) or not interface[field].strip():
                errors.append(f"agents/openai.yaml interface.{field} must be non-empty")
        prompt = interface.get("default_prompt", "")
        if isinstance(prompt, str) and "$" + skill_name not in prompt:
            errors.append("agents/openai.yaml default_prompt must mention the skill")

    policy = metadata.get("policy")
    if not isinstance(policy, dict) or not isinstance(
        policy.get("allow_implicit_invocation"), bool
    ):
        errors.append("agents/openai.yaml policy.allow_implicit_invocation must be boolean")

    dependencies = metadata.get("dependencies")
    tools = dependencies.get("tools") if isinstance(dependencies, dict) else None
    if not isinstance(tools, list) or not tools:
        errors.append("agents/openai.yaml dependencies.tools must be a non-empty list")
        return
    mcp_tools = [item for item in tools if isinstance(item, dict) and item.get("type") == "mcp"]
    if len(mcp_tools) != 1:
        errors.append("agents/openai.yaml must declare exactly one MCP dependency")
        return
    mcp = mcp_tools[0]
    if mcp.get("value") != "paymob":
        errors.append("agents/openai.yaml MCP dependency value must be 'paymob'")
    if mcp.get("transport") != "streamable_http":
        errors.append("agents/openai.yaml MCP transport must be 'streamable_http'")
    if mcp.get("url") != "https://mcp.paymob.com/mcp":
        errors.append("agents/openai.yaml must declare the Paymob MCP URL")

def validate_manifests(skill_name: str, errors: list[str]) -> str:
    codex = load_json(CODEX_MANIFEST, errors)
    claude = load_json(CLAUDE_MANIFEST, errors)
    marketplace = load_json(CLAUDE_MARKETPLACE, errors)
    mcp = load_json(MCP_MANIFEST, errors)

    for field in ("name", "version", "description", "author", "skills", "interface"):
        if not codex.get(field):
            errors.append(f"Codex manifest is missing {field!r}")
    for field in ("name", "version", "description", "author"):
        if not claude.get(field):
            errors.append(f"Claude manifest is missing {field!r}")

    if codex.get("name") != skill_name:
        errors.append("Codex plugin name must match the bundled skill name")
    if claude.get("name") != skill_name:
        errors.append("Claude plugin name must match the bundled skill name")
    if codex.get("version") != claude.get("version"):
        errors.append("Codex and Claude plugin versions must match")

    for manifest_name, manifest in (("Codex", codex), ("Claude", claude)):
        for field in ("skills", "mcpServers"):
            value = manifest.get(field)
            if isinstance(value, str) and not (ROOT / value).exists():
                errors.append(f"{manifest_name} manifest path does not exist: {value}")

    if marketplace.get("name") != "paymob":
        errors.append("Claude marketplace name must be 'paymob'")
    if not isinstance(marketplace.get("owner"), dict):
        errors.append("Claude marketplace must declare an owner object")
    plugins = marketplace.get("plugins")
    entries = [
        item for item in plugins
        if isinstance(item, dict) and item.get("name") == skill_name
    ] if isinstance(plugins, list) else []
    if len(entries) != 1:
        errors.append("Claude marketplace must contain one paymob-integration entry")
    else:
        entry = entries[0]
        if entry.get("source") != {
            "source": "github",
            "repo": "PaymobAccept/Paymob-AI-Integration-Skill",
        }:
            errors.append("Claude marketplace GitHub source is missing or unexpected")
        if entry.get("version") != claude.get("version"):
            errors.append("Claude marketplace and plugin versions must match")

    paymob_mcp = mcp.get("mcpServers", {}).get("paymob", {})
    if paymob_mcp.get("url") != "https://mcp.paymob.com/mcp":
        errors.append("Paymob MCP URL is missing or unexpected")
    if paymob_mcp.get("type") != "http":
        errors.append("Paymob MCP transport type must be 'http'")
    return str(codex.get("version", ""))


def validate_install_docs(version: str, errors: list[str]) -> None:
    readme = read_text(README, errors)
    if not readme:
        return
    required = (
        "claude plugin marketplace add PaymobAccept/Paymob-AI-Integration-Skill",
        "claude plugin install paymob-integration@paymob",
        "tree/main/skills/paymob-integration",
        "codex mcp add paymob --url https://mcp.paymob.com/mcp",
        "python scripts/package_skill.py",
        "dist/paymob-integration.zip",
        "paymob-integration-skill-upload",
        "releases/latest/download/paymob-integration.zip",
        "docs.lovable.dev/features/skills",
        "https://lovable.dev/favicon.ico",
        "Settings → Skills",
        "choose the **ZIP** tab",
        "/paymob-integration",
    )
    for command in required:
        if command not in readme:
            errors.append(f"README is missing install instruction: {command}")
    if "claude plugin install --git" in readme:
        errors.append("README contains the unsupported Claude --git install command")
    if version and f"version-{version}-blue" not in readme:
        errors.append("README version badge must match the plugin manifests")


def validate_release_workflow(errors: list[str]) -> None:
    workflow = read_text(RELEASE_WORKFLOW, errors)
    if not workflow:
        return
    required = (
        'tags:',
        '"v*"',
        'contents: write',
        'python scripts/validate.py',
        'python scripts/package_skill.py',
        'Path(".codex-plugin/plugin.json")',
        'dist/paymob-integration.zip',
        'gh release create',
        '--verify-tag',
    )
    for term in required:
        if term not in workflow:
            errors.append(f"Release workflow is missing required behavior: {term}")


def require_terms(label: str, text: str, terms: tuple[str, ...], errors: list[str]) -> None:
    lowered = text.lower()
    missing = [term for term in terms if term.lower() not in lowered]
    if missing:
        errors.append(f"{label} is missing safety terms: {', '.join(missing)}")


def validate_safety_contract(errors: list[str]) -> None:
    skill = read_text(SKILL_FILE, errors)
    agents = read_text(AGENTS, errors)
    universal = read_text(UNIVERSAL_PROMPT, errors)
    mcp_reference = read_text(MCP_REFERENCE, errors)
    advanced = read_text(ADVANCED_REFERENCE, errors)
    hmac_reference = read_text(HMAC_REFERENCE, errors)

    shared_terms = (
        "explicit confirmation",
        "current account",
        "test/live mode",
        "operation",
        "target",
        "amount",
        "currency",
        "stable operation fingerprint",
        "subagents receive no Paymob credentials",
    )
    require_terms("SKILL.md", skill, shared_terms, errors)
    require_terms("AGENTS.md", agents, shared_terms, errors)
    require_terms("universal-prompt.md", universal, shared_terms, errors)

    for label, text in (
        ("SKILL.md", skill),
        ("AGENTS.md", agents),
        ("universal-prompt.md", universal),
        ("mcp-server.md", mcp_reference),
        ("advanced-features.md", advanced),
    ):
        require_terms(label, text, ("ambiguous", "retry", "verify"), errors)

    require_terms(
        "universal-prompt.md",
        universal,
        (
            "unique Paymob transaction/event ID",
            "compare-and-set",
            "transactional outbox",
            "special_reference",
            "?token={AUTH_TOKEN}",
        ),
        errors,
    )
    require_terms(
        "hmac-verification.md",
        hmac_reference,
        (
            "unique constraint",
            "compare-and-set",
            "transactional outbox",
            "duplicate event",
            "only the committed outbox worker",
        ),
        errors,
    )
    backend_handlers = {
        "nodejs": ("await paymentEventStore.recordSuccessfulEvent", "res.status(200)"),
        "python": ("payment_store.record_successful_event", "return JsonResponse({\"received\": True})"),
        "php": ("recordSuccessfulEvent(", "return response()->json(['received' => true])"),
        "dotnet": ("await paymentStore.RecordSuccessfulEventAsync", "return Results.Ok"),
        "ruby": ("PaymobPaymentEventStore.record_successful_event!", "render json: { received: true }"),
    }
    for stack, (invocation, acknowledgement) in backend_handlers.items():
        code_reference = SKILL_DIR / "references" / f"code-{stack}.md"
        code_text = code_reference.read_text(encoding="utf-8")
        label = str(code_reference.relative_to(ROOT))
        require_terms(
            label,
            code_text,
            ("UNIQUE provider event", "compare-and-set", "outbox worker"),
            errors,
        )
        invocation_at = code_text.find(invocation)
        acknowledgement_at = code_text.find(acknowledgement, max(invocation_at, 0))
        if invocation_at == -1:
            errors.append(f"{label} webhook must invoke its atomic persistence adapter")
        elif acknowledgement_at == -1:
            errors.append(f"{label} must acknowledge only after atomic persistence")
    if re.search(
        r"GET[^\r\n]+Authorization:\s*Token\s*\{secret_key\}",
        universal,
        re.IGNORECASE,
    ):
        errors.append("Transaction Inquiry must not use the Secret Key authorization header")


def validate_commands(errors: list[str]) -> None:
    if not COMMANDS_DIR.is_dir():
        errors.append("Missing commands/ directory")
        return
    command_files = sorted(COMMANDS_DIR.glob("*.md"))
    if not command_files:
        errors.append("commands/ directory has no command files")
        return

    for path in command_files:
        label = str(path.relative_to(ROOT))
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{label} must be UTF-8 without a byte-order marker")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{label} is not valid UTF-8: {exc}")
            continue

        if not NAME_PATTERN.fullmatch(path.stem):
            errors.append(f"{label} filename must be lowercase kebab-case")

        match = re.match(r"^---\r?\n(?P<header>.*?)\r?\n---\r?\n", text, re.DOTALL)
        if not match:
            errors.append(f"{label} must start with closed YAML frontmatter")
            continue
        try:
            frontmatter = yaml.safe_load(match.group("header"))
        except yaml.YAMLError as exc:
            errors.append(f"{label} frontmatter is invalid YAML: {exc}")
            continue
        if not isinstance(frontmatter, dict):
            errors.append(f"{label} frontmatter must be a YAML object")
            continue

        unexpected = sorted(set(frontmatter) - ALLOWED_COMMAND_FRONTMATTER_KEYS)
        if unexpected:
            errors.append(f"{label} has unsupported frontmatter keys: {', '.join(unexpected)}")

        description = frontmatter.get("description", "")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{label} description is missing or is not a string")
        elif len(description.strip()) > 200:
            errors.append(
                f"{label} description is {len(description.strip())} characters; maximum is 200"
            )
        elif "<" in description or ">" in description:
            errors.append(f"{label} description cannot contain angle brackets")

        if "disable-model-invocation" in frontmatter and not isinstance(
            frontmatter["disable-model-invocation"], bool
        ):
            errors.append(f"{label} disable-model-invocation must be a boolean")

        if "argument-hint" in frontmatter and not isinstance(
            frontmatter["argument-hint"], str
        ):
            errors.append(f"{label} argument-hint must be a string")

        body = text[match.end():]
        if not body.strip():
            errors.append(f"{label} has no body content")
            continue

        for relative in PLUGIN_ROOT_REFERENCE_PATTERN.findall(body):
            if not (ROOT / relative).exists():
                errors.append(f"{label} references a missing file: {relative}")

        if HMAC_FIELD_ORDER_RESTATEMENT_PATTERN.search(body):
            errors.append(
                f"{label} restates the HMAC field order instead of referencing "
                "references/hmac-verification.md"
            )

        if COMMAND_SECRET_PATTERN.search(body):
            errors.append(f"{label} appears to contain a hardcoded secret or key")


def validate_links(errors: list[str]) -> None:
    for markdown in ROOT.rglob("*.md"):
        if ".git" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8")
        for match in LOCAL_LINK_PATTERN.finditer(text):
            relative = match.group(1).replace("%20", " ")
            target = (markdown.parent / relative).resolve()
            if not target.exists():
                errors.append(
                    f"Broken local link in {markdown.relative_to(ROOT)}: {match.group(1)}"
                )


def validate_upload_archive(errors: list[str]) -> None:
    validation_dir = ROOT / "dist"
    validation_dir.mkdir(exist_ok=True)
    prefix = f".validation-{uuid.uuid4().hex}"
    first = validation_dir / f"{prefix}-a.zip"
    second = validation_dir / f"{prefix}-b.zip"
    try:
        build_archive(first)
        build_archive(second)
        errors.extend(
            f"Standalone skill archive: {error}" for error in archive_errors(first)
        )
        if first.read_bytes() != second.read_bytes():
            errors.append("Standalone skill archive must be deterministic")
    except (OSError, ValueError) as exc:
        errors.append(f"Standalone skill packaging failed: {exc}")
    finally:
        first.unlink(missing_ok=True)
        second.unlink(missing_ok=True)


def main() -> int:
    errors: list[str] = []
    skill_name = validate_skill(errors)
    validate_openai_metadata(skill_name, errors)
    version = validate_manifests(skill_name, errors)
    validate_install_docs(version, errors)
    validate_release_workflow(errors)
    validate_safety_contract(errors)
    validate_commands(errors)
    validate_links(errors)
    validate_upload_archive(errors)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Validation passed: skill, plugin catalogs/manifests, installation docs, "
        "release workflow, safety contract, Claude commands, MCP config, metadata, "
        "links, and upload archive."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())