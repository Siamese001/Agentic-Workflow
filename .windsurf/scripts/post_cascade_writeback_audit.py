#!/usr/bin/env python3
"""
post_cascade_writeback_audit.py — Windsurf post_cascade_response writeback discipline audit.

Reads the cascade response payload from stdin. Detects signals indicating a
Memory or Notion writeback was due, then confirms whether a `WRITEBACK:` receipt
line or a recent Memory DB update corroborates that the writeback actually
happened. Missed writebacks are appended to the violations log.

Policy SSOT: .windsurf/rules/memory-notion-writeback.md
Entity/row templates: .windsurf/skills/writeback-discipline/

Detection signals (any one fires → writeback due):
    1. Response mentions creating/editing `docs/architecture/adr/ADR-*.md`
    2. Response mentions editing `.windsurf/mcp_config.json`
    3. Response mentions editing `.windsurf/scripts/*_gate.py`
    4. Response resolved a scored `ask_user_question` (DECISION_CAPTURED marker)
    5. Response mentions creating/editing `.windsurf/plans/*-<6hex>.md`
    6. Response contains recurring-bug language (fix recipes, RCA, root cause)
    7. Response mentions SC/AP defect emission from ADG run

Corroboration (proves writeback happened):
    - Explicit `WRITEBACK: target=... kind=... id=...` receipt line in response, OR
    - memory knowledge_graph.sqlite has a row updated within the last N minutes
      for a protected entityType (ProceduralPattern, ProjectContext,
      ArchitecturalInvariant, EpisodicEvent)

Behavior (ADVISORY — always exits 0):
    - Appends violation records to artifacts/windsurf/writeback_violations.jsonl
    - Writes summary to stderr (show_output not set — non-blocking)

Escape hatch: WRITEBACK_AUDIT_BYPASS=1 → logs a bypass row and exits 0.

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — repo_root resolved from __file__.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FAIL_POLICY = "open"
CORROBORATION_WINDOW_MINUTES = 10

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "writeback_violations.jsonl"
MEMORY_DB = REPO_ROOT / "artifacts" / "memory" / "knowledge_graph.sqlite"

# ---------------------------------------------------------------------------
# Signal patterns — regex-based detection on the response text
# ---------------------------------------------------------------------------

SIGNALS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "adr_created_or_modified",
        re.compile(r"docs[/\\]architecture[/\\]adr[/\\]ADR-\d+", re.IGNORECASE),
        "notion:ADR Registry",
    ),
    (
        "mcp_config_modified",
        re.compile(r"\.windsurf[/\\]mcp_config\.json", re.IGNORECASE),
        "notion:MCP Registry",
    ),
    (
        "gate_behavior_changed",
        re.compile(r"\.windsurf[/\\]scripts[/\\][a-z_]+_gate\.py", re.IGNORECASE),
        "notion:MCP Registry Notes",
    ),
    (
        "hitl_decision_resolved",
        re.compile(r"DECISION_CAPTURED:\s*type=", re.IGNORECASE),
        "notion:HITL Decision Ledger",
    ),
    (
        "plan_created_or_modified",
        re.compile(r"\.windsurf[/\\]plans[/\\][\w\-]+-[0-9a-f]{6}\.md", re.IGNORECASE),
        "memory:Project:* + notion:Wave/Phase Convergence",
    ),
    (
        "rca_or_recurring_fix",
        re.compile(
            r"\b(?:root\s+cause|RCA|recurring|next\s+time|fix\s+recipe|diagnosed|"
            r"anti-?pattern\s+detected|procedural\s+pattern)\b",
            re.IGNORECASE,
        ),
        "memory:ProceduralPattern",
    ),
    (
        "sc_ap_violations_emitted",
        re.compile(
            r"(?:generate_full_adg|adg\s+generation).*?(?:SC-|AP-)\d+|"
            r"(?:SC-|AP-)\d+.*?(?:violation|defect)",
            re.IGNORECASE | re.DOTALL,
        ),
        "notion:SC/AP Violation Backlog",
    ),
]

# Receipt pattern emitted by the skill's writeback template
RECEIPT_RE = re.compile(
    r"WRITEBACK:\s*target=(?P<target>memory|notion)"
    r"\s*,\s*kind=(?P<kind>[\w\-/:]+)"
    r"\s*,\s*id=(?P<id>[\S]+)",
    re.IGNORECASE,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_log_parent() -> None:
    VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)


def _append_log(record: dict[str, Any]) -> None:
    _ensure_log_parent()
    try:
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:  # fail-open
        print(f"[writeback_audit] log write failed: {exc}", file=sys.stderr)


sys.path.insert(0, str(Path(__file__).resolve().parent))
from _post_cascade_payload import extract_response_text  # noqa: E402


def _read_stdin_response() -> str:
    try:
        payload = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        return ""
    # Delegate to shared extractor — handles tool_info.response nesting.
    return extract_response_text(payload)


def _detect_signals(response: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for name, pattern, target in SIGNALS:
        match = pattern.search(response)
        if match:
            hits.append(
                {
                    "signal": name,
                    "target_hint": target,
                    "evidence": match.group(0)[:160],
                }
            )
    return hits


def _extract_receipts(response: str) -> list[dict[str, str]]:
    return [
        {"target": m.group("target"), "kind": m.group("kind"), "id": m.group("id")}
        for m in RECEIPT_RE.finditer(response)
    ]


def _recent_memory_updates(window_minutes: int) -> int:
    """Count protected-type entities updated within the window.

    Returns 0 on any DB error (fail-open). Uses a short connection timeout
    to avoid blocking the hook.
    """
    if not MEMORY_DB.exists():
        return 0
    cutoff = datetime.now(timezone.utc).timestamp() - window_minutes * 60
    protected_types = (
        "ProceduralPattern",
        "ProjectContext",
        "ArchitecturalInvariant",
        "EpisodicEvent",
    )
    try:
        con = sqlite3.connect(f"file:{MEMORY_DB}?mode=ro", uri=True, timeout=2.0)
        try:
            placeholders = ",".join("?" * len(protected_types))
            cur = con.execute(
                f"SELECT COUNT(*) FROM entities WHERE entity_type IN ({placeholders}) "
                f"AND updated_at >= ?",
                (*protected_types, cutoff),
            )
            row = cur.fetchone()
            return int(row[0]) if row else 0
        finally:
            con.close()
    except (sqlite3.DatabaseError, sqlite3.OperationalError, ValueError):
        return 0


def _classify_violation(
    signals: list[dict[str, str]],
    receipts: list[dict[str, str]],
    recent_memory_count: int,
) -> list[dict[str, Any]]:
    """A signal is a violation if no receipt or recent-memory corroboration exists.

    Rules:
    - memory:* signals corroborated by ANY receipt with target=memory OR recent_memory_count > 0
    - notion:* signals corroborated by ANY receipt with target=notion
    - signals with dual targets (memory+notion) require both corroborations
    """
    memory_receipts = [r for r in receipts if r["target"].lower() == "memory"]
    notion_receipts = [r for r in receipts if r["target"].lower() == "notion"]

    violations: list[dict[str, Any]] = []
    for sig in signals:
        target_hint = sig["target_hint"].lower()
        needs_memory = "memory:" in target_hint
        needs_notion = "notion:" in target_hint

        memory_ok = bool(memory_receipts) or recent_memory_count > 0
        notion_ok = bool(notion_receipts)

        missing: list[str] = []
        if needs_memory and not memory_ok:
            missing.append("memory")
        if needs_notion and not notion_ok:
            missing.append("notion")

        if missing:
            violations.append(
                {
                    "signal": sig["signal"],
                    "target_hint": sig["target_hint"],
                    "missing_writeback": missing,
                    "evidence": sig["evidence"],
                }
            )
    return violations


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
    # Bypass hatch
    if os.environ.get("WRITEBACK_AUDIT_BYPASS") == "1":
        _append_log(
            {
                "timestamp": _utc_now_iso(),
                "kind": "bypass",
                "reason": "WRITEBACK_AUDIT_BYPASS=1",
            }
        )
        return 0

    response = _read_stdin_response()
    if not response:
        return 0

    signals = _detect_signals(response)
    if not signals:
        return 0  # nothing to audit

    receipts = _extract_receipts(response)
    recent_memory_count = _recent_memory_updates(CORROBORATION_WINDOW_MINUTES)
    violations = _classify_violation(signals, receipts, recent_memory_count)

    if not violations:
        return 0  # all signals corroborated

    record = {
        "timestamp": _utc_now_iso(),
        "kind": "missed_writeback",
        "signals_total": len(signals),
        "receipts_total": len(receipts),
        "recent_memory_updates_10min": recent_memory_count,
        "violations": violations,
    }
    _append_log(record)

    summary = (
        f"[writeback_audit] {len(violations)} missed writeback(s): "
        f"{', '.join(v['signal'] for v in violations)} "
        f"-> log: {VIOLATIONS_LOG.relative_to(REPO_ROOT)}"
    )
    print(summary, file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:  # fail-open
        print(f"[writeback_audit] fail-open on exception: {exc}", file=sys.stderr)
        sys.exit(0)
