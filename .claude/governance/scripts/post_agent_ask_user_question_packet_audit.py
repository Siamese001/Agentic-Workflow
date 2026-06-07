#!/usr/bin/env python3
"""
post_agent_ask_user_question_packet_audit.py — Vacuum-closure audit.

Plan: author-gate-ssot-consolidation-b7c3e1 W4.P4.1 / W4.P4.2.

Closes the 2026-05-03 RCA enforcement vacuum where ``ask_user_question`` could
fire without a paired ``AUTHOR_GATE_PACKET:`` and bypass all three sibling
audits (schema, ui, miss). Severity ladder per RCA proposal:

    ask_user_question + valid packet                    → OK (no row)
    ask_user_question + invalid packet                  → severity=high
    ask_user_question + no packet + decision-density≥t  → severity=critical
    ask_user_question + no packet + low density         → OK (e.g., "what filename?")

Density threshold = 2 decision-class keywords in response prose.

Output: ``artifacts/governance/ask_user_question_packet_violations.jsonl``
Bypass: ``ASK_PACKET_AUDIT_BYPASS=1`` (logs row with reason=bypass).
Fail policy: OPEN (advisory, exits 0).

CONSTITUTIONAL
    - No subprocess / shell.
    - Specific exceptions only.
    - Bounded: response capped at 1 MB before scan.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "governance" / "ask_user_question_packet_violations.jsonl"
)
MAX_RESPONSE_BYTES = 1_048_576

# Shared schema loader (plan W4.P4.1).
sys.path.insert(0, str(REPO_ROOT))
try:
    from tools.author_gate.schema_loader import validate as _schema_validate  # noqa: E402
except ImportError:  # guardian: allow-broad -- audit must stay fail-open
    _schema_validate = None  # type: ignore

_ASK_INVOKE_RE = re.compile(r"<invoke\s+name=\"ask_user_question\">")
_PACKET_START_RE = re.compile(r"AUTHOR_GATE_PACKET:\s*(?=\{)")

_DECISION_KEYWORDS = (
    "refactor",
    "delete",
    "archive",
    "bare except",
    "except exception",
    "subprocess",
    "shell=true",
    "cross-layer",
    "blast radius",
    "rename file",
    "move file",
    "new dependency",
    "add dependency",
    "breaking change",
    "migration",
    "extract",
    "consolidate",
    "deprecat",
)
DENSITY_THRESHOLD = 2


def _balanced_slice(text: str, start: int) -> str | None:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
        elif in_str:
            if ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    return None


def _extract_packet(text: str) -> dict[str, Any] | None:
    matches = list(_PACKET_START_RE.finditer(text))
    if not matches:
        return None
    raw = _balanced_slice(text, matches[-1].end())
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _decision_keyword_count(text: str) -> int:
    lower = text.lower()
    return sum(1 for kw in _DECISION_KEYWORDS if kw in lower)


def audit_response(text: str) -> list[dict[str, Any]]:
    """Pure function. Returns list of violation rows (empty if compliant)."""
    if not _ASK_INVOKE_RE.search(text):
        return []
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    packet = _extract_packet(text)
    density = _decision_keyword_count(text)

    if packet is not None:
        # Validate against canonical schema.
        if _schema_validate is None:
            return []  # advisory; no schema lib means no judgment
        findings = [
            f for f in _schema_validate(packet)
            if f.get("invariant") != "schema_lib_missing"
        ]
        if not findings:
            return []  # OK — valid packet paired with ask_user_question
        return [
            {
                "ts": ts,
                "severity": "high",
                "reason": "invalid_packet_paired_with_ask_user_question",
                "decision_id": packet.get("decision_id"),
                "decision_type": packet.get("decision_type"),
                "schema_findings": findings[:10],
                "decision_keyword_count": density,
            }
        ]

    # No packet present — severity depends on decision density.
    if density >= DENSITY_THRESHOLD:
        return [
            {
                "ts": ts,
                "severity": "critical",
                "reason": "ask_user_question_without_packet_high_density",
                "decision_keyword_count": density,
                "threshold": DENSITY_THRESHOLD,
                "remediation": (
                    "Emit AUTHOR_GATE_PACKET: { ... } before ask_user_question. "
                    "Use .claude/skills/author-gate-packet-builder/emit_packet.py."
                ),
            }
        ]
    # Low-density ask is OK (e.g., "what filename?")
    return []


def _append(row: dict[str, Any]) -> None:
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- audit log is non-fatal
        pass


def _read_stdin_text() -> str:
    try:
        raw = sys.stdin.read(MAX_RESPONSE_BYTES + 1)
    except OSError:
        return ""
    if not raw.strip():
        return ""
    if len(raw) > MAX_RESPONSE_BYTES:
        raw = raw[:MAX_RESPONSE_BYTES]
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(payload, dict):
        for key in ("response", "response_text", "text", "assistant_text", "content"):
            val = payload.get(key)
            if isinstance(val, str):
                return val
        return json.dumps(payload, ensure_ascii=False)
    return raw


def main() -> int:
    if os.environ.get("ASK_PACKET_AUDIT_BYPASS") == "1":
        _append(
            {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": "bypass",
            }
        )
        return 0
    text = _read_stdin_text()
    if not text:
        return 0
    for row in audit_response(text):
        _append(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
