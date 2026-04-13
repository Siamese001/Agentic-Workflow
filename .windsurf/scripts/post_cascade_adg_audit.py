#!/usr/bin/env python3
"""
post_cascade_adg_audit.py — Windsurf post_cascade_response ADG-first enforcement audit.

Reads the cascade response payload from stdin (tool_info.response).
Detects grep_search calls used for dependency analysis (imports, references,
consumers, fan-in/fan-out) and logs violations.

This is the ONLY retroactive detection layer for the ADG-first enforcement rule
because Windsurf has no pre-tool-use hook for native Cascade tools (grep_search,
find_by_name, list_dir).

Detection heuristic:
    - Scans response for grep_search tool invocations
    - Checks if the Query contains dependency-analysis patterns:
      * import/from patterns (e.g., "from X import Y", "import X")
      * Consumer/usage patterns (e.g., function/class name searches in *.py)
    - Checks if Includes filter targets Python files (*.py)
    - Cross-checks whether mcp1_adg_* calls were also present (mitigating factor)

Behavior (ADVISORY — always exits 0):
    - Appends violation records to artifacts/windsurf/adg_first_violations.jsonl
    - Writes summary to stderr (show_output: false — won't clutter user view)

Fail policy: OPEN — any error → exit 0 silently.
Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FAIL_POLICY = "open"

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "adg_first_violations.jsonl"

# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# Patterns in grep_search Query field that indicate dependency analysis
_DEP_ANALYSIS_QUERY_PATTERNS = [
    # Import tracing
    re.compile(r"\bfrom\s+\w+.*\bimport\b", re.IGNORECASE),
    re.compile(r"\bimport\s+\w+", re.IGNORECASE),
    # Symbol consumer/usage tracing
    re.compile(r"^[A-Z][A-Z_]+$"),  # ALL_CAPS constants (e.g., SOVEREIGN_TERRITORIES)
    re.compile(r"^[a-z_]+\("),  # function call patterns (e.g., build_sovereign_territories)
    re.compile(r"^class\s+\w+"),  # class definition searches
]

# Patterns that indicate the grep was for literal confirmation (allowed)
_LITERAL_CONFIRM_PATTERNS = [
    re.compile(r"TODO|FIXME|HACK|NOTE|XXX", re.IGNORECASE),
    re.compile(r"guardian:|noqa|type:\s*ignore", re.IGNORECASE),
    re.compile(r"^#"),  # comment searches
    re.compile(r"DEPRECATED|REMOVED|ARCHIVED", re.IGNORECASE),
]

# Regex to find grep_search tool calls in the Cascade response markdown
# The response contains tool call blocks with Query and SearchPath parameters
_GREP_CALL_RE = re.compile(
    r"grep_search.*?Query[\"']?\s*[:=]\s*[\"'](.+?)[\"']",
    re.DOTALL | re.IGNORECASE,
)

# Broad heuristic: grep_search near dependency-analysis terminology
# Keyed on observable query features per OpenDev §3.2 decision tree
_GREP_DEP_HEURISTIC_PATTERNS = [
    # Import tracing
    re.compile(
        r"grep_search.*?(?:import|from\s+\w+\.\w+)",
        re.DOTALL | re.IGNORECASE,
    ),
    # Consumer/reference/blast-radius terminology
    re.compile(
        r"grep_search.*?(?:consumer|depends_on|imports_from|references|blast.?radius|"
        r"who.?uses|who.?calls|who.?imports|fan.?in|fan.?out)",
        re.DOTALL | re.IGNORECASE,
    ),
    # Project-specific symbol searches (common violation targets)
    re.compile(
        r"grep_search.*?(?:SOVEREIGN|LAYER_OVERRIDE|build_sovereign|"
        r"structure_blueprint|TerritoryDefinition|SubfolderDefinition)",
        re.DOTALL | re.IGNORECASE,
    ),
    # Searching for Python class/function definitions as a proxy for consumer analysis
    re.compile(
        r"grep_search.*?(?:class\s+[A-Z]\w+|def\s+\w+).*?Includes.*?\.py",
        re.DOTALL | re.IGNORECASE,
    ),
    # Strong indicator: Includes=["*.py"] with symbol-like query (not literal text)
    re.compile(
        r"grep_search.*?Includes.*?\*\.py.*?Query.*?[A-Z][a-z]\w{3,}",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        r"grep_search.*?Query.*?[A-Z][a-z]\w{3,}.*?Includes.*?\*\.py",
        re.DOTALL | re.IGNORECASE,
    ),
]

# Check if ADG MCP calls were also present (mitigating factor)
_ADG_MCP_CALL_RE = re.compile(
    r"mcp1_adg_(?:nodes_by_file|edge_fanin|edge_fanout|node|nodes_by_layer)",
    re.IGNORECASE,
)

# Check if adg_health was called (required before any grep degraded fallback)
_ADG_HEALTH_CALL_RE = re.compile(r"mcp1_adg_health", re.IGNORECASE)

# Check if a DEGRADED_FALLBACK reason was emitted (required when falling back from adg_sqlite)
_DEGRADED_FALLBACK_RE = re.compile(r"DEGRADED_FALLBACK\s*:", re.IGNORECASE)


def _is_dep_analysis_query(query: str) -> bool:
    """Return True if the query looks like dependency analysis, not literal confirmation."""
    # Check if it's a literal confirmation pattern (allowed)
    for pattern in _LITERAL_CONFIRM_PATTERNS:
        if pattern.search(query):
            return False

    # Check if it matches dependency analysis patterns
    for pattern in _DEP_ANALYSIS_QUERY_PATTERNS:
        if pattern.search(query):
            return True

    return False


def detect_violations(response_text: str) -> list[dict]:
    """
    Scan response for grep-for-deps violations.
    Returns list of violation records.
    """
    violations = []

    # Check if ADG MCP was also used (mitigating factor)
    adg_mcp_used = bool(_ADG_MCP_CALL_RE.search(response_text))
    adg_health_checked = bool(_ADG_HEALTH_CALL_RE.search(response_text))
    degraded_fallback_declared = bool(_DEGRADED_FALLBACK_RE.search(response_text))

    # Heuristic detection: grep_search near dependency-analysis terms
    # Check all patterns; deduplicate by start position
    # Exempt matches that contain literal confirmation patterns (TODOs, FIXMEs, guardian, etc.)
    seen_starts: set[int] = set()
    all_matches = []
    for pattern in _GREP_DEP_HEURISTIC_PATTERNS:
        for match in pattern.finditer(response_text):
            if match.start() not in seen_starts:
                match_text = match.group(0)
                # Skip if the matched region contains literal confirmation patterns
                is_literal = any(lp.search(match_text) for lp in _LITERAL_CONFIRM_PATTERNS)
                if not is_literal:
                    seen_starts.add(match.start())
                    all_matches.append(match)

    for match in all_matches:
        context_start = max(0, match.start() - 100)
        context_end = min(len(response_text), match.end() + 100)
        context = response_text[context_start:context_end].strip()

        # Determine severity: critical when no ADG tool, no health check, and no reason code.
        if adg_mcp_used:
            sev = "warning"  # ADG was also used — grep may have been supplementary
        elif adg_health_checked or degraded_fallback_declared:
            sev = "error"  # partial compliance: health checked or reason emitted but ADG skipped
        else:
            sev = "critical"  # silent fallback: no ADG, no health check, no reason code

        violation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "violation_type": "grep_for_dependency_analysis",
            "severity": sev,
            "silent_fallback": not adg_mcp_used and not adg_health_checked and not degraded_fallback_declared,
            "context_snippet": context[:300],
            "adg_mcp_also_used": adg_mcp_used,
            "adg_health_checked": adg_health_checked,
            "degraded_fallback_declared": degraded_fallback_declared,
            "mitigation": (
                "ADG MCP was also used — grep may have been supplementary"
                if adg_mcp_used
                else (
                    "Health checked or DEGRADED_FALLBACK emitted — partial compliance"
                    if adg_health_checked or degraded_fallback_declared
                    else "Silent fallback: no ADG, no health check, no reason code"
                )
            ),
            "rule": "constitutional.md §ADG-First, global_rules.md §ADG-First Analysis",
        }
        violations.append(violation)

    return violations


def _append_violations(violations: list[dict]) -> None:
    """Append violation records to the JSONL log."""
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(VIOLATIONS_LOG, "a", encoding="utf-8") as f:
            for v in violations:
                f.write(json.dumps(v) + "\n")
    except OSError:
        pass


def _extract_response_text(payload: object) -> str:
    """Extract the response text from various payload shapes."""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        # post_cascade_response provides tool_info.response
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
        if violations:
            _append_violations(violations)
            # Log to stderr for debugging (show_output: false in hooks.json,
            # so this won't clutter the user view)
            print(
                f"[adg_audit] DETECTED {len(violations)} grep-for-deps violation(s). "
                f"See: artifacts/windsurf/adg_first_violations.jsonl",
                file=sys.stderr,
            )

    except (OSError, ValueError):
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
