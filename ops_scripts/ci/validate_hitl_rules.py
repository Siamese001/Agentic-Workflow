"""CI gate: validate HITL rule doc structure and content.

Checks:
  - validate_yaml_config_section: §HITL-9 exists with required YAML config block
  - validate_option_shape_section: §HITL-10 exists with all required option shape fields
  - validate_no_hardcoded_2to4: no old 2-4 hardcoded patterns; required patterns present
"""

from __future__ import annotations

import re
from pathlib import Path

_YAML_REQUIRED_KEYS: list[str] = [
    "surface_threshold: 0.72",
    "dominance_score_threshold: 0.85",
    "dominance_delta: 0.12",
    "allow_single_option_hitl: true",
]

_OPTION_SHAPE_REQUIRED_FIELDS: list[str] = [
    "decision_thesis:",
    "value_to_goal:",
    "key_tradeoffs:",
    "execution_impact:",
    "risk_profile:",
    "time_to_value:",
]

_FORBIDDEN_PATTERNS: list[str] = [
    r"Present 2-4 concrete options",
    r"Options \(2-4\)",
]

_REQUIRED_PATTERNS: list[str] = [
    "surface_threshold = 0.72",
    "dominance rule",
    "Surface 1\u2013N options",
    "LOW_CONFIDENCE_AMBIGUITY",
]


def _extract_section(text: str, marker: str) -> str:
    """Return text from marker to the next ## heading, or end of file."""
    idx = text.find(marker)
    if idx == -1:
        return ""
    section = text[idx:]
    m = re.search(r"\n## ", section)
    if m:
        section = section[: m.start()]
    return section


def validate_yaml_config_section(path: Path) -> list[str]:
    """Check §HITL-9 section exists with a ```yaml block containing all required keys."""
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    section = _extract_section(text, "\u00a7HITL-9")
    if not section:
        errors.append("\u00a7HITL-9 section not found in file")
        return errors

    if "```yaml" not in section:
        errors.append("YAML config block not found in \u00a7HITL-9 section")
        return errors

    for key in _YAML_REQUIRED_KEYS:
        if key not in section:
            errors.append(f"Required key missing from \u00a7HITL-9 YAML block: {key}")

    return errors


def validate_option_shape_section(path: Path) -> list[str]:
    """Check §HITL-10 section exists with all required option shape fields."""
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    section = _extract_section(text, "\u00a7HITL-10")
    if not section:
        errors.append("\u00a7HITL-10 section not found in file")
        return errors

    for field in _OPTION_SHAPE_REQUIRED_FIELDS:
        if field not in section:
            errors.append(f"Required field missing from \u00a7HITL-10 section: {field}")

    return errors


def validate_no_hardcoded_2to4(path: Path) -> list[str]:
    """Check no old hardcoded 2-4 option patterns; verify required confidence-gated patterns present."""
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    for pattern in _FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            errors.append(f"Forbidden pattern found: {pattern}")

    for pattern in _REQUIRED_PATTERNS:
        if pattern not in text:
            errors.append(f"Required pattern missing: {pattern}")

    return errors
