#!/usr/bin/env python3
"""
post_cursor_agent_router_decision_audit.py — Closed-Loop Router enforcement post-hook.

Reads the cursor agent response payload from stdin. Detects when Cursor Agent has edited
or substantially referenced a router-implementing file but the response carries
neither a `ROUTER_DECISION:` marker nor a paired `emit_ledger_event(ledger="router_..."`
call. Logs violations to artifacts/cursor/router_enforcement_violations.jsonl.

Constitutional anchor: §28.
Rule: .cursor/rules/closed-loop-router-enforcement.md.

Behavior (ADVISORY — always exits 0):
- False negatives are acceptable; false positives are not.
- Bypass via ROUTER_ENFORCEMENT_BYPASS=1 logs a bypass row and skips audit.
- No user data sent anywhere — purely local JSONL append.

Fail policy: OPEN — any error exits 0 silently.
Zero hardcoded paths — repo_root resolved from __file__.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "router_enforcement_violations.jsonl"

# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# Plain-text marker emitted by routers (or by Cursor Agent when demonstrating a router):
#   ROUTER_DECISION: layer=L0 router=bandit decision_id=... trace_id=... ...
_ROUTER_DECISION_RE = re.compile(
    r"ROUTER_DECISION:\s*"
    r"layer=(?P<layer>L[0-6])\s+"
    r"router=(?P<router>[a-z][a-z0-9_]*)\s+"
    r"decision_id=(?P<decision_id>[A-Za-z0-9._-]+)"
    r"(?P<tail>[^\n]*)",
    re.MULTILINE,
)

# Library-call evidence: emit_ledger_event with ledger="router_..."
_EMIT_LIBRARY_RE = re.compile(
    r"emit_ledger_event\s*\(\s*[\s\S]{0,200}?ledger\s*=\s*[\"']router_[a-z0-9_]+[\"']",
    re.MULTILINE,
)

# Router-implementing file patterns (matched against any path-like substring in the response).
# These are intentionally broad: any edit that touches one of these is presumed to
# concern router code and therefore expected to carry router-decision evidence.
_ROUTER_FILE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"agentic_core/L[0-6]_[a-z_]+/[\w/]*router[\w]*\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L[0-6]_[a-z_]+/[\w/]*bandit[\w]*\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L[0-6]_[a-z_]+/[\w/]*promo[\w]*\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L[0-6]_[a-z_]+/[\w/]*regret[\w]*\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L6_observability/routing_[\w]+\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L6_observability/heal_router[\w]*\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L6_observability/regret_accounting\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L6_observability/flywheel_promoter\.py", re.IGNORECASE),
    re.compile(r"agentic_core/L6_observability/promotion_gates\.py", re.IGNORECASE),
)

# Edit-intent keywords: signals that Cursor Agent is *editing* the file, not just
# referencing it in prose. We require at least one of these in the response
# alongside a router-file path before flagging a missing-evidence violation.
_EDIT_INTENT_RE = re.compile(
    r"\b(edit|edited|edits|edit_file|multi_edit|write_to_file|created file|"
    r"created the file|wrote to|wrote the file|modified|modifying|"
    r"replace|replaced|replacing|added to|removed from|"
    r"refactored|implementing|added|removed)\b",
    re.IGNORECASE,
)

# Promote-evidence floor: §28 requires four fields on verdict=promote.
_PROMOTE_VERDICT_RE = re.compile(r"verdict\s*=\s*promote\b", re.IGNORECASE)
_WILSON_RE = re.compile(r"wilson_lower\s*=\s*(?P<v>\d+(?:\.\d+)?)")
_Z_RE = re.compile(r"z_score\s*=\s*(?P<v>\d+(?:\.\d+)?)")
_UPLIFT_RE = re.compile(r"uplift\s*=\s*(?P<v>-?\d+(?:\.\d+)?)")
_N_RE = re.compile(r"\bn\s*=\s*(?P<v>\d+)")

# Regret cycle floor: by_layer_json must be non-empty.
_REGRET_CYCLE_RE = re.compile(r"router\s*=\s*regret\b", re.IGNORECASE)
_BY_LAYER_JSON_RE = re.compile(r"by_layer_json\s*=\s*(?P<v>\S+)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _extract_response_text(payload: Any) -> str:
    """Mirror of post_cursor_agent_author_gate_capture._extract_response_text."""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        tool_info = payload.get("tool_info")
        if isinstance(tool_info, dict):
            for key in ("response", "text", "content", "message", "cascade_response"):
                val = tool_info.get(key)
                if isinstance(val, str) and val.strip():
                    return val
        for key in ("response", "text", "content", "message", "cascade_response"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def _matched_router_files(text: str) -> list[str]:
    """Return unique router-implementing file paths mentioned in text."""
    hits: set[str] = set()
    for pat in _ROUTER_FILE_PATTERNS:
        for m in pat.finditer(text):
            hits.add(m.group(0))
    return sorted(hits)


def _append_violation(record: dict[str, Any]) -> None:
    """Append a JSONL row to the violations log. Fail-open."""
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        # guardian: allow-silent-swallow -- violations log: non-fatal, fail-open
        pass


# ---------------------------------------------------------------------------
# Audit checks
# ---------------------------------------------------------------------------


def audit_response(text: str) -> list[dict[str, Any]]:
    """Run all audits on a response. Return list of violation records.

    Audit categories:
      A. router_files_without_evidence — edit-intent on router file but no marker
         AND no library-call reference.
      B. promote_without_floor — verdict=promote without all four required floor fields.
      C. regret_without_attribution — router=regret marker without by_layer_json.
      D. marker_missing_required_field — ROUTER_DECISION marker missing a required
         common field (decision_id, trace_id, etc.).
    """
    violations: list[dict[str, Any]] = []

    has_marker = bool(_ROUTER_DECISION_RE.search(text))
    has_library_call = bool(_EMIT_LIBRARY_RE.search(text))
    edit_intent = bool(_EDIT_INTENT_RE.search(text))
    router_files = _matched_router_files(text)

    # Audit A — router edits without evidence
    if router_files and edit_intent and not has_marker and not has_library_call:
        violations.append(
            {
                "ts": _now_iso(),
                "kind": "router_files_without_evidence",
                "router_files": router_files,
                "has_marker": False,
                "has_library_call": False,
                "severity": "advisory",
                "constitutional_ref": "§28",
            }
        )

    # Audit B — promote verdict floor
    for m in _ROUTER_DECISION_RE.finditer(text):
        tail = m.group("tail") or ""
        if not _PROMOTE_VERDICT_RE.search(tail):
            continue
        gaps = []
        wm = _WILSON_RE.search(tail)
        if not wm:
            gaps.append("wilson_lower:missing")
        else:
            try:
                if float(wm.group("v")) < 0.60:
                    gaps.append(f"wilson_lower:{wm.group('v')}<0.60")
            except ValueError:
                gaps.append("wilson_lower:unparseable")
        zm = _Z_RE.search(tail)
        if not zm:
            gaps.append("z_score:missing")
        else:
            try:
                if float(zm.group("v")) < 1.96:
                    gaps.append(f"z_score:{zm.group('v')}<1.96")
            except ValueError:
                gaps.append("z_score:unparseable")
        um = _UPLIFT_RE.search(tail)
        if not um:
            gaps.append("uplift:missing")
        else:
            try:
                if float(um.group("v")) <= 0:
                    gaps.append(f"uplift:{um.group('v')}<=0")
            except ValueError:
                gaps.append("uplift:unparseable")
        nm = _N_RE.search(tail)
        if not nm:
            gaps.append("n:missing")
        else:
            try:
                if int(nm.group("v")) < 30:
                    gaps.append(f"n:{nm.group('v')}<30")
            except ValueError:
                gaps.append("n:unparseable")
        if gaps:
            violations.append(
                {
                    "ts": _now_iso(),
                    "kind": "promote_without_floor",
                    "decision_id": m.group("decision_id"),
                    "layer": m.group("layer"),
                    "router": m.group("router"),
                    "gaps": gaps,
                    "severity": "blocking",
                    "constitutional_ref": "§28",
                }
            )

    # Audit C — regret without attribution
    for m in _ROUTER_DECISION_RE.finditer(text):
        if m.group("router").lower() != "regret":
            continue
        tail = m.group("tail") or ""
        bm = _BY_LAYER_JSON_RE.search(tail)
        if not bm or bm.group("v").strip() in ("{}", "null", "None", "''", '""', "[]"):
            violations.append(
                {
                    "ts": _now_iso(),
                    "kind": "regret_without_attribution",
                    "decision_id": m.group("decision_id"),
                    "by_layer_json": bm.group("v") if bm else None,
                    "severity": "blocking",
                    "constitutional_ref": "§28",
                }
            )

    # Audit D — marker required-field gaps. The regex enforces layer/router/
    # decision_id by construction; we additionally require trace_id and route_id
    # in the tail. (selected is also required but parsed leniently here.)
    for m in _ROUTER_DECISION_RE.finditer(text):
        tail = m.group("tail") or ""
        gaps = []
        if not re.search(r"\btrace_id=\S+", tail):
            gaps.append("trace_id:missing")
        if not re.search(r"\broute_id=\S+", tail):
            gaps.append("route_id:missing")
        if not re.search(r"\bselected=\S+", tail):
            gaps.append("selected:missing")
        if gaps:
            violations.append(
                {
                    "ts": _now_iso(),
                    "kind": "marker_missing_required_field",
                    "decision_id": m.group("decision_id"),
                    "layer": m.group("layer"),
                    "router": m.group("router"),
                    "gaps": gaps,
                    "severity": "advisory",
                    "constitutional_ref": "§28",
                }
            )

    return violations


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    # Standalone-invocation guard (mirrors author-gate hook).
    if sys.stdin.isatty():
        return 0

    # Bypass
    if os.environ.get("ROUTER_ENFORCEMENT_BYPASS") == "1":
        _append_violation(
            {
                "ts": _now_iso(),
                "kind": "bypass",
                "reason": "ROUTER_ENFORCEMENT_BYPASS=1",
                "severity": "info",
            }
        )
        return 0

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        try:
            payload: Any = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw

        text = _extract_response_text(payload)
        if not text.strip():
            return 0

        violations = audit_response(text)
        for v in violations:
            _append_violation(v)
    except (OSError, ValueError):
        # guardian: allow-silent-swallow -- audit hook: non-fatal, fail-open
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
