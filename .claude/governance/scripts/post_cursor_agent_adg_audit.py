#!/usr/bin/env python3
"""
post_cursor_agent_adg_audit.py — ADG-first enforcement audit (Cursor Agent).

Reads agent response payload from stdin (tool_info.response / response / content).
Detects grep-style tool calls used for dependency analysis and logs violations.
Fail policy: OPEN — any error → exit 0 silently.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[3]
violations_log = repo_root / "artifacts" / "cursor" / "adg_first_violations.jsonl"
_legacy_violations_log = repo_root / "artifacts" / "windsurf" / "adg_first_violations.jsonl"

_DEP_ANALYSIS_QUERY_PATTERNS = [
    re.compile(r"\bfrom\s+\w+.*\bimport\b", re.IGNORECASE),
    re.compile(r"\bimport\s+\w+", re.IGNORECASE),
    re.compile(r"^[A-Z][A-Z_]+$"),
    re.compile(r"^[a-z_]+\("),
    re.compile(r"^class\s+\w+"),
]

_literal_confirm_patterns = [
    re.compile(r"TODO|FIXME|HACK|NOTE|XXX", re.IGNORECASE),
    re.compile(r"guardian:|noqa|type:\s*ignore", re.IGNORECASE),
    re.compile(r"^#"),
    re.compile(r"DEPRECATED|REMOVED|ARCHIVED", re.IGNORECASE),
]

_GREP_TOOL = r"(?:grep_search|\bGrep\b|\brg\b|\bgrep\b)"

_GREP_CALL_RE = re.compile(
    rf"{_GREP_TOOL}.*?(?:Query|pattern)[\"']?\s*[:=]\s*[\"'](.+?)[\"']",
    re.DOTALL | re.IGNORECASE,
)

_GREP_DEP_HEURISTIC_PATTERNS = [
    re.compile(
        rf"{_GREP_TOOL}.*?(?:import|from\s+\w+(?:\.\w+)?\s+import)",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        rf"{_GREP_TOOL}.*?(?:consumer|depends_on|imports_from|references|blast.?radius|"
        r"who.?uses|who.?calls|who.?imports|fan.?in|fan.?out)",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        rf"{_GREP_TOOL}.*?(?:SOVEREIGN|LAYER_OVERRIDE|build_sovereign|"
        r"structure_blueprint|TerritoryDefinition|SubfolderDefinition)",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        rf"{_GREP_TOOL}.*?(?:class\s+[A-Z]\w+|def\s+\w+).*?(?:Includes|glob).*?\.py",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        rf"{_GREP_TOOL}.*?(?:Includes|glob).*?\*\.py.*?(?:Query|pattern).*?[A-Z][a-z]\w{{3,}}",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        rf"{_GREP_TOOL}.*?(?:Query|pattern).*?[A-Z][a-z]\w{{3,}}.*?(?:Includes|glob).*?\*\.py",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        r"(?:Shell|beforeShellExecution).*?\b(?:rg|grep)\b.*?(?:import|from\s+\w+)",
        re.DOTALL | re.IGNORECASE,
    ),
]

_ADG_TOOLS = (
    r"nodes_by_file|edge_fanin|edge_fanout|node|nodes_by_layer|find_node|"
    r"violations|p0_wave_plan|blast_radius|semantic_fanout|p_view_query"
)
_adg_mcp_call_re = re.compile(
    rf"(?:(?:mcp\d+_)?adg_(?:{_ADG_TOOLS})"
    rf"|adg_sqlite[^\n]{{0,240}}?adg_(?:{_ADG_TOOLS})"
    rf'|toolName["\']?\s*:\s*["\']adg_(?:{_ADG_TOOLS})'
    rf'|server["\']?\s*:\s*["\']adg_sqlite["\'][^\n]{{0,240}}?adg_(?:{_ADG_TOOLS}))',
    re.IGNORECASE | re.DOTALL,
)

_adg_health_call_re = re.compile(
    r"(?:(?:mcp\d+_)?adg_health"
    r"|adg_sqlite[^\n]{0,120}?adg_health"
    r'|toolName["\']?\s*:\s*["\']adg_health'
    r'|server["\']?\s*:\s*["\']adg_sqlite["\'][^\n]{0,120}?adg_health)',
    re.IGNORECASE | re.DOTALL,
)

_degraded_fallback_re = re.compile(r"DEGRADED_FALLBACK\s*:", re.IGNORECASE)

_sqlite_direct_adg_re = re.compile(
    r"sqlite3\.connect\([^)]*adg_indexed[^)]*\)|adg_indexed_\d+_\d+\.sqlite",
    re.IGNORECASE,
)
_BYPASS_ENV = "ADG_SQLITE_FALLBACK_BYPASS"


def _adg_snapshot_available() -> bool:
    try:
        adg_dir = repo_root / "artifacts" / "adg"
        if not adg_dir.is_dir():
            return False
        for entry in adg_dir.glob("adg_indexed_*.sqlite"):
            if entry.is_file() and entry.stat().st_size > 0:
                return True
        return False
    except OSError:  # guardian: allow-silent-swallow -- best-effort detection
        return False


def _build_remediation(violation_type: str, context: str) -> str:
    if "import" in context.lower():
        return (
            "REQUIRED: adg_sqlite MCP adg_nodes_by_file(file_path=<target>) "
            "→ adg_edge_fanin(tgt_id=<node>, relation_type='imports')."
        )
    if any(kw in context.lower() for kw in ("consumer", "blast", "impact", "who uses")):
        return (
            "REQUIRED: adg_sqlite MCP adg_nodes_by_file(file_path=<target>) "
            "→ for EACH symbol node: adg_edge_fanin(tgt_id=<symbol_id>)."
        )
    return (
        "REQUIRED: Use adg_sqlite MCP instead of Grep/grep_search for dependency analysis. "
        "Fallback: sqlite3 on artifacts/adg/adg_indexed_<ts>.sqlite — NOT grep."
    )


def detect_violations(response_text: str) -> list[dict]:
    violations = []
    adg_mcp_used = bool(_adg_mcp_call_re.search(response_text))
    adg_health_checked = bool(_adg_health_call_re.search(response_text))
    degraded_fallback_declared = bool(_degraded_fallback_re.search(response_text))
    sqlite_direct_used = bool(_sqlite_direct_adg_re.search(response_text))
    adg_snapshot_present = _adg_snapshot_available()
    bypass_set = bool(__import__("os").environ.get(_BYPASS_ENV))

    seen_starts: set[int] = set()
    all_matches = []
    for pattern in _GREP_DEP_HEURISTIC_PATTERNS:
        for match in pattern.finditer(response_text):
            if match.start() not in seen_starts:
                match_text = match.group(0)
                is_literal = any(lp.search(match_text) for lp in _literal_confirm_patterns)
                if not is_literal:
                    seen_starts.add(match.start())
                    all_matches.append(match)

    for match in all_matches:
        context_start = max(0, match.start() - 100)
        context_end = min(len(response_text), match.end() + 100)
        context = response_text[context_start:context_end].strip()
        is_silent_fallback = not adg_mcp_used and not adg_health_checked and not degraded_fallback_declared

        if bypass_set:
            sev = "info"
        elif sqlite_direct_used and adg_mcp_used:
            sev = "info"
        elif sqlite_direct_used:
            sev = "info"
        elif adg_mcp_used:
            sev = "warning"
        elif adg_health_checked and degraded_fallback_declared:
            sev = "info"
        elif adg_health_checked or degraded_fallback_declared:
            sev = "error"
        elif adg_snapshot_present:
            sev = "critical"
        else:
            sev = "critical"

        violations.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "violation_type": (
                    "grep_when_sqlite_available"
                    if (adg_snapshot_present and not sqlite_direct_used and not adg_mcp_used)
                    else "grep_for_dependency_analysis"
                ),
                "severity": sev,
                "silent_fallback": is_silent_fallback,
                "context_snippet": context[:300],
                "adg_mcp_also_used": adg_mcp_used,
                "adg_health_checked": adg_health_checked,
                "degraded_fallback_declared": degraded_fallback_declared,
                "sqlite_direct_used": sqlite_direct_used,
                "adg_snapshot_present": adg_snapshot_present,
                "bypass_set": bypass_set,
                "remediation": _build_remediation("grep_for_dependency_analysis", context),
                "rule": "constitutional.md §22, §23, §28",
            }
        )

    return violations


def _append_violations(violations: list[dict]) -> None:
    for path in (violations_log, _legacy_violations_log):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                for v in violations:
                    f.write(json.dumps(v) + "\n")
        except OSError:  # guardian: allow-silent-swallow -- audit log write: non-fatal, fail-open
            pass


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        tool_info = payload.get("tool_info", payload)
        if isinstance(tool_info, dict):
            for key in ("response", "text", "content"):
                val = tool_info.get(key)
                if isinstance(val, str) and val.strip():
                    return val
        for key in ("response", "text", "content"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def main() -> int:
    if sys.stdin.isatty():
        return 0
    critical_count = 0
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        try:
            payload: object = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
        text = _extract_response_text(payload)
        if not text.strip():
            return 0
        violations = detect_violations(text)
        critical_count = sum(1 for v in violations if v.get("severity") == "critical")
        if violations:
            _append_violations(violations)
            print(
                f"[adg_audit] DETECTED {len(violations)} grep-for-deps violation(s)"
                f" ({critical_count} critical).",
                file=sys.stderr,
            )
        try:
            from tools.ledgers.hook_helpers import emit_ledger_event

            emit_ledger_event(
                ledger="tool_routing",
                event_kind="routing_violation" if violations else "retrieval_scan_clean",
                prediction={"chosen_tool": "grep_search" if violations else "unknown"},
                outcome={"fallback_triggered": bool(violations)},
                score_band="miss" if violations else "correct",
                score_numeric=float(len(violations)),
                repo_area=".claude/governance/scripts/post_cursor_agent_adg_audit.py",
            )
        except Exception:  # noqa: BLE001
            pass
    except (OSError, ValueError):  # guardian: allow-silent-swallow -- fail-open
        pass

    if critical_count > 0 and not __import__("os").environ.get(_BYPASS_ENV):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
