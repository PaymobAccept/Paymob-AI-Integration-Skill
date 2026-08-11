#!/usr/bin/env python3
"""Build and verify the standalone skill archive used by upload-based hosts."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "paymob-integration"
DEFAULT_OUTPUT = ROOT / "dist" / "paymob-integration.zip"
ARCHIVE_ROOT = SKILL_DIR.name
FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def source_files() -> list[Path]:
    """Return the canonical skill files in stable archive order."""
    return sorted(path for path in SKILL_DIR.rglob("*") if path.is_file())


def build_archive(output: Path) -> None:
    """Create a deterministic ZIP with one top-level skill folder."""
    output = output.resolve()
    if SKILL_DIR in output.parents:
        raise ValueError("Output archive must be outside the canonical skill directory")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in source_files():
            relative = source.relative_to(SKILL_DIR)
            archive_name = PurePosixPath(ARCHIVE_ROOT, *relative.parts).as_posix()
            info = zipfile.ZipInfo(archive_name, FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())


def archive_errors(archive_path: Path) -> list[str]:
    """Return structural or content errors for an upload archive."""
    errors: list[str] = []
    expected = {
        PurePosixPath(ARCHIVE_ROOT, *path.relative_to(SKILL_DIR).parts).as_posix()
        for path in source_files()
    }
    try:
        with zipfile.ZipFile(archive_path) as archive:
            names = {name for name in archive.namelist() if not name.endswith("/")}
            bad_entries = archive.testzip()
    except (FileNotFoundError, zipfile.BadZipFile) as exc:
        return [f"Cannot read archive: {exc}"]

    skill_entry = f"{ARCHIVE_ROOT}/SKILL.md"
    if skill_entry not in names:
        errors.append(f"Missing top-level skill entry: {skill_entry}")
    if any(PurePosixPath(name).parts[0] != ARCHIVE_ROOT for name in names):
        errors.append(f"Every archive entry must be inside {ARCHIVE_ROOT}/")
    if names != expected:
        missing = sorted(expected - names)
        unexpected = sorted(names - expected)
        if missing:
            errors.append(f"Archive is missing canonical files: {', '.join(missing)}")
        if unexpected:
            errors.append(f"Archive has unexpected files: {', '.join(unexpected)}")
    if bad_entries:
        errors.append(f"Archive contains a corrupt entry: {bad_entries}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package skills/paymob-integration for skill upload interfaces."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Archive path (default: {DEFAULT_OUTPUT.relative_to(ROOT)})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        build_archive(output)
    except (OSError, ValueError) as exc:
        print(f"Packaging failed: {exc}", file=sys.stderr)
        return 1

    errors = archive_errors(output)
    if errors:
        print("Archive validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Created upload-ready skill archive: {output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
