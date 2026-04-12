"""CI gate: validate ask_user_question block format compliance.

Checks per file:
  BANNED_OLD_FORMAT       — Pros:/Cons: patterns forbidden (old format)
  MISSING_CONFIDENCE_SCORE — option label missing [0.NN HIGH|MEDIUM|LOW]
  MISSING_STAR_MARKER     — HIGH-confidence option (>=0.85) missing ⭐
  MISSING_DECISION_THESIS — option description missing decision_thesis:
  LOW_CONFIDENCE_SURFACED — option label with LOW band surfaced (should be suppressed)
"""

from __future__ import annotations

import re
from pathlib import Path

_CONFIDENCE_RE = re.compile(r"\[(\d+\.\d+)\s+(HIGH|MEDIUM|LOW)\]")
_BANNED_RE = re.compile(r"(?:Pros|Cons)(?:\*\*)?:")
_AQ_BLOCK_RE = re.compile(r"ask_user_question\([\s\S]*?\n\s*\)")


def _extract_aq_blocks(text: str) -> list[str]:
    """Return all ask_user_question(...) block strings."""
    return _AQ_BLOCK_RE.findall(text)


def _extract_options(block: str) -> list[tuple[str, str]]:
    """Return (label, description) pairs for each option object in block."""
    options: list[tuple[str, str]] = []
    for obj in re.findall(r"\{([^{}]*)\}", block, re.DOTALL):
        label_m = re.search(r'label:\s*"([^"]*)"', obj)
        if not label_m:
            continue
        desc_m = re.search(r'description:\s*"([^"]*)"', obj)
        label = label_m.group(1)
        description = desc_m.group(1) if desc_m else ""
        options.append((label, description))
    return options


def validate_file(path: Path) -> list[tuple[str, str]]:
    """Validate HITL format in a file. Returns list of (location, violation_type) tuples."""
    text = path.read_text(encoding="utf-8")
    violations: list[tuple[str, str]] = []

    for i, line in enumerate(text.splitlines(), 1):
        if _BANNED_RE.search(line):
            violations.append((f"line {i}", "BANNED_OLD_FORMAT"))

    for block in _extract_aq_blocks(text):
        for label, description in _extract_options(block):
            conf_m = _CONFIDENCE_RE.search(label)

            if not conf_m:
                violations.append((f"label={label!r}", "MISSING_CONFIDENCE_SCORE"))
            else:
                score = float(conf_m.group(1))
                band = conf_m.group(2)

                if band == "HIGH" and score >= 0.85 and "\u2b50" not in label:
                    violations.append((f"label={label!r}", "MISSING_STAR_MARKER"))

                if band == "LOW":
                    violations.append((f"label={label!r}", "LOW_CONFIDENCE_SURFACED"))

            if description and "decision_thesis:" not in description:
                violations.append((f"label={label!r}", "MISSING_DECISION_THESIS"))

    return violations
