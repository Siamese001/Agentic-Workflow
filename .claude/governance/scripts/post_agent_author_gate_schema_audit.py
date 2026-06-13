#!/usr/bin/env python3
"""
post_agent_author_gate_schema_audit.py — AG-10 packet shape conformance audit.

Sibling of ``post_agent_author_gate_ui_audit.py``. The UI audit checks that
``ask_user_question`` option descriptions carry the right confidence-prefix
shape AFTER a packet is emitted. This audit checks the *packet itself* — it
catches free-form / hand-crafted ``AUTHOR_GATE_PACKET:`` blocks that did NOT
flow through the canonical emitter at
``.claude/skills/author-gate-packet-builder/emit_packet.py``.

Why this exists
---------------
Constitutional §6/§30 mandate that every refactor-class Author-Gate decision
emit a packet AND a ``DECISION_CAPTURED:`` marker so the SQLite ledger,
calibration weekly report, and CI freshness gate stay coherent. When the
packet is hand-composed it usually omits the canonical fields the downstream
parser ``post_agent_author_gate_capture.py`` keys on (``decision_id``,
``policy_snapshot``, ``context_fingerprint.fp``, ``routing.rule_applied``,
per-candidate ``signals/signal_weights/raw_score``) — so the row never lands
in the ledger and the turn shows up as a stale-ledger violation.

What it validates
-----------------
For every ``AUTHOR_GATE_PACKET:`` block in the response:

1. Top-level required fields present and well-typed:
     decision_id           : str matching ``^dec_[0-9a-f]+$``
     policy_snapshot       : str matching ``^author-gate@[0-9a-f]+$``
     context_fingerprint   : object containing ``fp`` (hex) and ``git_sha``
     routing               : object with ``rule_applied`` + ``surface_threshold`` + ``top_score``
     precedent             : object with ``verdict`` in {none, strong, suggestive}
     reason_code_palette   : list of strings
     candidates            : non-empty list
     confidence_top        : numeric
2. Every surfaced candidate (``surfaced=true`` or ``is_recommended=true``)
   carries the canonical signal vector:
     signals               : object
     signal_weights        : object
     raw_score             : numeric
3. ``decision_type`` is one of the seven trigger types per
   ``author-gate-decision-points.md`` (architecture_choice, refactor_scope,
   anti_pattern, deletion_strategy, dependency_addition, test_strategy,
   error_handling).

Fail policy: OPEN (advisory, exit 0). Violations append JSONL to
``artifacts/governance/author_gate_schema_violations.jsonl``.

Bypass: ``AUTHOR_GATE_SCHEMA_BYPASS=1`` logs a row with reason="bypass" and
returns 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _post_agent_payload import extract_response_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_LOG = (
    REPO_ROOT / "artifacts" / "governance" / "author_gate_schema_violations.jsonl"
)

# Shared canonical schema loader (plan author-gate-ssot-consolidation-b7c3e1 W3.P3.1).
sys.path.insert(0, str(REPO_ROOT))
try:
    from tools.author_gate.schema_loader import validate as _schema_validate  # noqa: E402
except ImportError:  # guardian: allow-broad -- audit must stay fail-open
    _schema_validate = None  # type: ignore

_PACKET_START_RE = re.compile(r"AUTHOR_GATE_PACKET:\s*(?=\{)")
_DECISION_ID_RE = re.compile(r"^dec_[0-9a-f]+$")
_POLICY_SNAPSHOT_RE = re.compile(r"^author-gate@[0-9a-f]+$")
_HEX_RE = re.compile(r"^[0-9a-f]+$")

VALID_DECISION_TYPES = frozenset(
    {
        "architecture_choice",
        "refactor_scope",
        "anti_pattern",
        "deletion_strategy",
        "dependency_addition",
        "test_strategy",
        "error_handling",
        # certification_claim is added by the fortknox skill — accept as well.
        "certification_claim",
    }
)

VALID_PRECEDENT_VERDICTS = frozenset({"none", "strong", "suggestive"})


# ---------------------------------------------------------------------------
# IO helpers (mirrored from post_agent_author_gate_ui_audit.py for behavioral
# parity — same balanced-slice + stdin-payload extraction).
# ---------------------------------------------------------------------------

def _append_violation(row: dict[str, Any]) -> None:
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _balanced_slice(text: str, start: int, open_ch: str, close_ch: str) -> str | None:
    if start >= len(text) or text[start] != open_ch:
        return None
    depth = 0
    i = start
    in_str = False
    escape = False
    while i < len(text):
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
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        i += 1
    return None


def _extract_packets(response_text: str) -> list[tuple[int, dict[str, Any] | None, str]]:
    """Return list of (offset, parsed_or_None, raw_or_empty) per packet block."""
    out: list[tuple[int, dict[str, Any] | None, str]] = []
    for match in _PACKET_START_RE.finditer(response_text):
        obj_start = match.end()
        raw = _balanced_slice(response_text, obj_start, "{", "}")
        if raw is None:
            out.append((obj_start, None, ""))
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            out.append((obj_start, None, raw))
            continue
        if isinstance(parsed, dict):
            out.append((obj_start, parsed, raw))
        else:
            out.append((obj_start, None, raw))
    return out


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _missing(packet: dict[str, Any], path: str) -> bool:
    """Return True if the dotted path is absent or falsy-empty."""
    cur: Any = packet
    for part in path.split("."):
        if not isinstance(cur, dict):
            return True
        if part not in cur:
            return True
        cur = cur[part]
    if cur is None:
        return True
    if isinstance(cur, (str, list, dict)) and not cur:
        return True
    return False


def _validate_packet(packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Return list of violation records (empty if conformant).

    Plan author-gate-ssot-consolidation-b7c3e1 W3.P3.1: prefer jsonschema
    against the canonical SSOT schema; bespoke checks below remain as
    secondary guards (legacy invariants not expressible in JSON Schema).
    """
    findings: list[dict[str, Any]] = []

    # Schema-first (canonical). Findings carry path + validator + message.
    if _schema_validate is not None:
        for f in _schema_validate(packet):
            if f.get("invariant") == "schema_lib_missing":
                break
            findings.append(f)

    # 1. decision_id format
    decision_id = packet.get("decision_id")
    if not isinstance(decision_id, str) or not _DECISION_ID_RE.match(decision_id):
        findings.append(
            {
                "invariant": "decision_id_format",
                "expected": "^dec_[0-9a-f]+$",
                "observed": decision_id,
            }
        )

    # 2. policy_snapshot format — proves emit_packet.py ran
    policy = packet.get("policy_snapshot")
    if not isinstance(policy, str) or not _POLICY_SNAPSHOT_RE.match(policy):
        findings.append(
            {
                "invariant": "policy_snapshot_format",
                "expected": "^author-gate@[0-9a-f]+$",
                "observed": policy,
                "remediation": (
                    "Pipe spec to .claude/skills/author-gate-packet-builder/"
                    "emit_packet.py — do not hand-craft the packet."
                ),
            }
        )

    # 3. context_fingerprint shape
    fp = packet.get("context_fingerprint")
    if not isinstance(fp, dict):
        findings.append({"invariant": "context_fingerprint_missing", "observed_type": type(fp).__name__})
    else:
        fp_hex = fp.get("fp")
        if not isinstance(fp_hex, str) or not _HEX_RE.match(fp_hex):
            findings.append({"invariant": "context_fingerprint_fp_format", "observed": fp_hex})
        if not isinstance(fp.get("git_sha"), str):
            findings.append({"invariant": "context_fingerprint_git_sha_missing"})

    # 4. routing object
    routing = packet.get("routing")
    if not isinstance(routing, dict):
        findings.append({"invariant": "routing_missing", "observed_type": type(routing).__name__})
    else:
        for key in ("rule_applied", "surface_threshold", "top_score"):
            if key not in routing or routing[key] is None:
                findings.append({"invariant": f"routing_field_missing", "field": key})

    # 5. precedent object — verdict must be canonical
    precedent = packet.get("precedent")
    if not isinstance(precedent, dict):
        findings.append({"invariant": "precedent_missing", "observed_type": type(precedent).__name__})
    else:
        verdict = precedent.get("verdict")
        if verdict not in VALID_PRECEDENT_VERDICTS:
            findings.append(
                {
                    "invariant": "precedent_verdict_invalid",
                    "expected": sorted(VALID_PRECEDENT_VERDICTS),
                    "observed": verdict,
                }
            )

    # 6. reason_code_palette must be a non-empty list
    if _missing(packet, "reason_code_palette") or not isinstance(packet.get("reason_code_palette"), list):
        findings.append({"invariant": "reason_code_palette_missing"})

    # 7. confidence_top numeric
    conf_top = packet.get("confidence_top")
    if not isinstance(conf_top, (int, float)):
        findings.append({"invariant": "confidence_top_missing_or_non_numeric", "observed": conf_top})

    # 8. decision_type valid
    dtype = packet.get("decision_type")
    if dtype not in VALID_DECISION_TYPES:
        findings.append(
            {
                "invariant": "decision_type_invalid",
                "expected": sorted(VALID_DECISION_TYPES),
                "observed": dtype,
            }
        )

    # 9. candidates list + signal vector on surfaced ones
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        findings.append({"invariant": "candidates_missing_or_empty"})
    else:
        for idx, cand in enumerate(candidates):
            if not isinstance(cand, dict):
                findings.append({"invariant": "candidate_not_object", "index": idx})
                continue
            surfaced = bool(cand.get("surfaced") or cand.get("is_recommended"))
            if not surfaced:
                continue
            for field in ("signals", "signal_weights", "raw_score"):
                val = cand.get(field)
                if val is None or (isinstance(val, dict) and not val):
                    findings.append(
                        {
                            "invariant": "candidate_signal_vector_missing",
                            "index": idx,
                            "candidate_id": cand.get("id"),
                            "field": field,
                        }
                    )

    return findings


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def audit_response(response_text: str) -> list[dict[str, Any]]:
    """Pure function — returns a list of violation records (empty if clean)."""
    out: list[dict[str, Any]] = []
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for packet_idx, (offset, parsed, raw) in enumerate(_extract_packets(response_text)):
        if parsed is None:
            out.append(
                {
                    "ts": ts,
                    "packet_index": packet_idx,
                    "offset": offset,
                    "invariant": "packet_unparseable",
                    "raw_excerpt": raw[:200] if raw else "",
                }
            )
            continue
        for finding in _validate_packet(parsed):
            finding.update(
                {
                    "ts": ts,
                    "packet_index": packet_idx,
                    "offset": offset,
                    "decision_id": parsed.get("decision_id"),
                    "decision_type": parsed.get("decision_type"),
                }
            )
            out.append(finding)

    return out


def _read_stdin_text() -> str:
    return extract_response_text(sys.stdin.read())


def main() -> int:
    if os.environ.get("AUTHOR_GATE_SCHEMA_BYPASS") == "1":
        _append_violation(
            {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": "bypass",
            }
        )
        return 0

    text = _read_stdin_text()
    if not text:
        return 0

    violations = audit_response(text)
    for row in violations:
        _append_violation(row)

    # Advisory — never break the chain.
    return 0


if __name__ == "__main__":
    sys.exit(main())
