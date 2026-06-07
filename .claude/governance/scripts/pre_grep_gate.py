#!/usr/bin/env python3
"""pre_grep_gate.py — Deterministic ADG-first chokepoint for the native ``Grep`` tool.

Plan: grep-pretooluse-adg-gate-a3f1c7. Companion thin hook:
``.claude/hooks/before_grep.py`` (registered under ``PreToolUse`` matcher ``Grep``).

Why this exists
---------------
The repo declares ADG-first for every dependency / import / consumer / reference /
blast-radius / fan-in / fan-out query (constitutional §5, §22, §23, §28, §34), but the
only controls acting on a structural ``Grep`` were *advisory* (prompt-submit warning) and
*post-hoc* (Stop-hook audit). This gate adds the missing deterministic control: it can
return **exit 2 (block)** before a structural grep runs, while staying **fail-open** when
ADG cannot serve so a broken graph never wedges a turn.

Decision contract (``evaluate``)
--------------------------------
Returns ``(0, reason)`` to allow or ``(2, reason)`` to block.

* Not a ``Grep`` call .......................... allow
* ``ADG_GREP_GATE_BYPASS=1`` ................... allow (logged)
* ADG snapshot unusable ........................ allow + emit ``DEGRADED_FALLBACK:`` (§28)
* Literal / TODO / prose pattern ............... allow (never block a non-structural search)
* Deps-intent breadcrumb this turn + non-literal pattern + ADG healthy ... **BLOCK** (exit 2)
* Structural pattern only (no breadcrumb) + ADG healthy .................. allow + WARN (stderr)
* Otherwise .................................... allow

The breadcrumb (``artifacts/cursor/_grep_deps_intent_turn.flag``) is dropped by
``pre_user_prompt_grep_for_deps_warning.py`` when the user's prompt this turn asked a
dependency question ("who uses / what depends on / fan-in / fan-out / blast radius /
references to"). It is the high-precision signal: a structural grep *right after* a deps
question is almost certainly the dependency search we want routed to ADG.

Fail policy: OPEN — any unexpected error anywhere → allow (exit 0). A governance gate must
never be the reason a turn hangs or dies.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ADG_DIR = _REPO_ROOT / "artifacts" / "adg"
_BREADCRUMB = _REPO_ROOT / "artifacts" / "cursor" / "_grep_deps_intent_turn.flag"
_BYPASS_ENV = "ADG_GREP_GATE_BYPASS"

# A deps-intent breadcrumb older than this is treated as stale (a prior turn).
_BREADCRUMB_MAX_AGE_S: int = 1800  # 30 min — generous enough for a long working turn

# Patterns that are unmistakably structural (dependency/definition shaped).
_STRUCTURAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bimport\b", re.IGNORECASE),
    re.compile(r"\bfrom\s+\S+\s+import\b", re.IGNORECASE),
    re.compile(r"\b(class|def)\s+\w+", re.IGNORECASE),
    re.compile(r"\b(extends|implements)\b", re.IGNORECASE),
    re.compile(r"agentic_core\.", re.IGNORECASE),
    re.compile(r"apps_\w+\.", re.IGNORECASE),
)

# Patterns that are clearly NON-structural — never block these even mid-deps-turn.
_NONSTRUCTURAL_MARKERS: re.Pattern[str] = re.compile(
    r"\b(TODO|FIXME|HACK|XXX|NOTE|BUG|DEPRECATED)\b|(?:guardian|review):", re.IGNORECASE
)


def _is_structural_pattern(pattern: str) -> bool:
    return any(p.search(pattern) for p in _STRUCTURAL_PATTERNS)


def _is_clearly_nonstructural(pattern: str) -> bool:
    """True when the search is obviously a literal / comment / prose lookup.

    Used to keep literal greps flowing even when a deps-intent breadcrumb is present.
    """
    if not pattern.strip():
        return True
    if _NONSTRUCTURAL_MARKERS.search(pattern):
        return True
    # Long natural-language prose with no code-shaped tokens → treat as literal search.
    if len(pattern) > 60 and not re.search(r"[._(]|\\b", pattern):
        return True
    return False


def _latest_adg_snapshot() -> Path | None:
    try:
        snaps = sorted(
            _ADG_DIR.glob("adg_indexed_*.sqlite"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return None
    return snaps[0] if snaps else None


def _adg_healthy() -> bool:
    """Read-only probe of the latest snapshot for a populated ``nodes`` table.

    This is the exact signal that would have self-diagnosed the 2026-06-07 broken-stub
    incident (an empty 24 KB snapshot with no ``nodes`` table won the latest-resolver).
    """
    snap = _latest_adg_snapshot()
    if snap is None:
        return False
    try:
        con = sqlite3.connect(f"file:{snap}?mode=ro", uri=True, timeout=2.0)
        try:
            row = con.execute("SELECT count(*) FROM nodes").fetchone()
        finally:
            con.close()
        return bool(row) and int(row[0]) > 0
    except (sqlite3.Error, ValueError, TypeError):
        return False


def _breadcrumb_fresh() -> bool:
    try:
        if not _BREADCRUMB.is_file():
            return False
        age = time.time() - _BREADCRUMB.stat().st_mtime
        return age <= _BREADCRUMB_MAX_AGE_S
    except OSError:
        return False


def _extract_pattern(payload: dict) -> str:
    ti = payload.get("tool_input")
    if isinstance(ti, dict):
        pat = ti.get("pattern")
        if isinstance(pat, str):
            return pat
    pat = payload.get("pattern")
    return pat if isinstance(pat, str) else ""


def _extract_tool_name(payload: dict) -> str:
    tn = payload.get("tool_name") or payload.get("toolName")
    return tn if isinstance(tn, str) else ""


_REDIRECT = (
    "ADG-FIRST (§28): use the adg_sqlite MCP for dependency analysis instead of grep — "
    "fan-in → adg_edge_fanin · fan-out → adg_edge_fanout · blast radius → adg_blast_radius · "
    "who-uses/consumers → adg_nodes_by_file + adg_edge_fanin · layer → adg_nodes_by_layer. "
    "Literal/TODO/comment text searches are fine; this block fired because a dependency "
    f"question was asked this turn. Bypass: {_BYPASS_ENV}=1."
)


def evaluate(payload: dict) -> tuple[int, str]:
    """Pure decision function. Returns (exit_code, reason)."""
    if os.environ.get(_BYPASS_ENV, "").strip() == "1":
        return 0, f"allow: {_BYPASS_ENV}=1"

    if _extract_tool_name(payload) != "Grep":
        return 0, "allow: not a Grep call"

    pattern = _extract_pattern(payload)

    if not _adg_healthy():
        # Fail-open: ADG cannot serve, so grep is the legitimate fallback (§28).
        return 0, "DEGRADED_FALLBACK: reason=adg_snapshot_unusable (grep allowed)"

    if _is_clearly_nonstructural(pattern):
        return 0, "allow: literal/comment/prose search"

    if _breadcrumb_fresh():
        return 2, _REDIRECT

    if _is_structural_pattern(pattern):
        return (
            0,
            "WARN ADG-first: this grep looks structural — prefer adg_sqlite "
            "(adg_edge_fanin / adg_edge_fanout / adg_blast_radius).",
        )

    return 0, "allow: no deps-intent signal"


def main() -> int:
    if sys.stdin.isatty():
        return 0
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0

    try:
        code, reason = evaluate(payload)
    except Exception as exc:  # guardian: allow-broad-except -- gate must fail-open; never wedge a turn
        sys.stderr.write(f"[pre_grep_gate] internal error, failing open: {exc}\n")
        return 0

    if code == 2:
        # Block message goes to STDOUT so the thin hook can relay it as the block reason.
        sys.stdout.write(reason)
        return 2
    if reason and reason.startswith(("WARN", "DEGRADED_FALLBACK")):
        sys.stderr.write(f"[pre_grep_gate] {reason}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
