"""
HITL Rules CI Validator — checks rule/doc files for correct schema sections.

Three validators:
  validate_yaml_config_section  — §HITL-9 YAML config block
  validate_option_shape_section — §HITL-10 option shape fields
  validate_no_hardcoded_2to4    — forbidden 2-4 count patterns; required pipeline patterns

Exit codes (when run as __main__):
    0 — all checks passed
    1 — violations found

Usage:
    python ops_scripts/ci/validate_hitl_rules.py <file> [<file> ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# §HITL-9 YAML config block validator
# ---------------------------------------------------------------------------

_HITL9_REQUIRED_KEYS = [
    "surface_threshold: 0.72",
    "dominance_score_threshold: 0.85",
    "dominance_delta: 0.12",
    "allow_single_option_hitl: true",
]


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def validate_yaml_config_section(path: Path) -> list[str]:
    """Return list of error strings for §HITL-9 YAML config issues in *path*."""
    text, read_error = _read_text(path)
    errors: list[str] = []
    if read_error is not None or text is None:
        errors.append(f"file read failed: {read_error}")
        return errors

    if "\u00a7HITL-9" not in text:
        errors.append("\u00a7HITL-9 section not found")
        return errors

    match = re.search(r"##\s+\u00a7HITL-9[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    section = match.group(1) if match else text

    if "```yaml" not in section:
        errors.append("YAML config block not found in \u00a7HITL-9 section")
        return errors

    for key in _HITL9_REQUIRED_KEYS:
        if key not in section:
            errors.append(f"Required key missing from \u00a7HITL-9 YAML block: {key}")

    return errors


# ---------------------------------------------------------------------------
# §HITL-10 option shape section validator
# ---------------------------------------------------------------------------

_HITL10_REQUIRED_FIELDS = [
    "decision_thesis:",
    "value_to_goal:",
    "key_tradeoffs:",
    "execution_impact:",
    "risk_profile:",
    "time_to_value:",
]


def validate_option_shape_section(path: Path) -> list[str]:
    """Return list of error strings for §HITL-10 option shape issues in *path*."""
    text, read_error = _read_text(path)
    errors: list[str] = []
    if read_error is not None or text is None:
        errors.append(f"file read failed: {read_error}")
        return errors

    if "\u00a7HITL-10" not in text:
        errors.append("\u00a7HITL-10 section not found")
        return errors

    match = re.search(r"##\s+\u00a7HITL-10[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    section = match.group(1) if match else text

    for field in _HITL10_REQUIRED_FIELDS:
        if field not in section:
            errors.append(f"Required field missing from \u00a7HITL-10 section: {field}")

    return errors


# ---------------------------------------------------------------------------
# Hardcoded 2-4 count pattern validator
# ---------------------------------------------------------------------------

_FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    ("Present 2-4 concrete options", "Present 2-4 concrete options"),
    (r"Options \(2-4\)", r"Options \(2-4\)"),
]

_REQUIRED_PATTERNS: list[tuple[str, str]] = [
    ("surface_threshold = 0.72", "surface_threshold = 0.72"),
    ("dominance rule", "dominance rule"),
    ("Surface 1\u2013N options", "Surface 1\u2013N options"),
    ("LOW_CONFIDENCE_AMBIGUITY", "LOW_CONFIDENCE_AMBIGUITY"),
]


def validate_no_hardcoded_2to4(path: Path) -> list[str]:
    """Return list of error strings for hardcoded 2-4 count pattern issues in *path*."""
    text, read_error = _read_text(path)
    errors: list[str] = []
    if read_error is not None or text is None:
        errors.append(f"file read failed: {read_error}")
        return errors

    for regex, label in _FORBIDDEN_PATTERNS:
        if re.search(regex, text):
            errors.append(f"Forbidden pattern found: {label}")

    for pattern, label in _REQUIRED_PATTERNS:
        if pattern not in text:
            errors.append(f"Required pattern missing: {label}")

    return errors


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _run(paths: list[Path]) -> int:
    if not paths:
        print("[SKIP] validate_hitl_rules: no files provided")
        return 0

    exit_code = 0
    for path in paths:
        if not path.exists():
            print(f"[MISSING_FILE] {path}", file=sys.stderr)
            exit_code = 1
            continue
        for fn in (validate_yaml_config_section, validate_option_shape_section, validate_no_hardcoded_2to4):
            errs = fn(path)
            for e in errs:
                print(f"[{fn.__name__}] {path}: {e}", file=sys.stderr)
                exit_code = 1
    return exit_code


if __name__ == "__main__":
    _paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else []
    sys.exit(_run(_paths))
