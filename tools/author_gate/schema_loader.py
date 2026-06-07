"""Shared loader for the canonical Author-Gate packet schema.

Single source of truth used by:
  - .claude/skills/author-gate-packet-builder/emit_packet.py (validate before emit)
  - .claude/governance/scripts/post_cursor_agent_author_gate_schema_audit.py (validate captured)
  - .claude/governance/scripts/post_cursor_agent_author_gate_ui_audit.py (read routing enum)
  - .claude/governance/scripts/post_cursor_agent_author_gate_miss_detector.py (presence check)
  - .claude/governance/scripts/post_cursor_agent_ask_user_question_packet_audit.py (vacuum closure)

Plan: author-gate-ssot-consolidation-b7c3e1 (W1.2 / W3 shared loader).

CONSTITUTIONAL
    - No subprocess, no shell.
    - Specific exceptions only.
    - Fail-soft: when jsonschema is unavailable, ``validate`` returns a single
      ``[{"invariant": "schema_lib_missing"}]`` finding so callers stay
      advisory.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / ".claude" / "schemas" / "author_gate_packet.schema.json"


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    """Load and cache the canonical schema. Raises FileNotFoundError if missing."""
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def _get_validator() -> Any:
    """Return a cached jsonschema Draft 2020-12 validator instance, or None."""
    try:
        from jsonschema import Draft202012Validator  # type: ignore
    except ImportError:
        return None
    return Draft202012Validator(load_schema())


def validate(packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Return list of finding dicts. Empty = valid.

    Each finding has at minimum:
      - invariant: short code string
      - path: dotted JSON-pointer-ish path of the offending field
      - message: human-readable description

    Fail-soft: returns ``[{"invariant": "schema_lib_missing"}]`` when
    ``jsonschema`` is not installed; callers should treat as advisory.
    """
    v = _get_validator()
    if v is None:
        return [{"invariant": "schema_lib_missing", "path": "", "message": "jsonschema lib unavailable"}]
    findings: list[dict[str, Any]] = []
    for err in sorted(v.iter_errors(packet), key=lambda e: list(e.absolute_path)):
        findings.append(
            {
                "invariant": "schema_violation",
                "path": ".".join(str(p) for p in err.absolute_path) or "<root>",
                "validator": err.validator,
                "message": err.message,
            }
        )
    return findings


def is_valid(packet: dict[str, Any]) -> bool:
    """Convenience boolean form."""
    return not validate(packet)


def routing_rule_pattern() -> str:
    """Return the regex pattern for routing.rule_applied — used by ui_audit."""
    schema = load_schema()
    return (
        schema["$defs"]["routing"]["properties"]["rule_applied"]["pattern"]
    )


__all__ = ["load_schema", "validate", "is_valid", "routing_rule_pattern", "SCHEMA_PATH"]
