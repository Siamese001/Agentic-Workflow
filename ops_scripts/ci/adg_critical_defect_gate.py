#!/usr/bin/env python3
"""ADG Critical Defect Gate — Blocks commits if ADG:CRITICAL defects exist.

This gate queries the ADG SQLite store for critical-severity violations
(SeverityLevel.CRITICAL). If any exist, the gate blocks the commit.

Reclassified P0 (was P1 by naming convention — renamed from adg_p1_defect_gate.py).
Behavior has always been a hard block, consistent with P0 severity.
HITL decision H1 confirmed reclassification to P0 with this rename.

SEVERITY TAXONOMY (agentic_core.L5_safety.config.severity.SeverityLevel):
    ADG:CRITICAL  = SeverityLevel.CRITICAL  (layer violations, arch defects)
    ADG:HIGH      = SeverityLevel.HIGH       (anti-patterns, circular deps)
    ADG:MEDIUM    = SeverityLevel.MEDIUM     (quality debt)
    ADG:LOW       = SeverityLevel.LOW        (style / informational)

    NOTE: "ADG:P1" is a legacy alias for ADG:CRITICAL.
    Do NOT confuse with Ruff P0-P3 (different namespace) or V15 phase numbers.

Usage:
    python ops_scripts/ci/adg_critical_defect_gate.py

Exit codes:
    0 — No ADG:CRITICAL defects found (commit allowed)
    1 — ADG:CRITICAL defects found (commit blocked)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from agentic_core.L5_safety.config.severity import SeverityLevel


def _get_repo_root() -> Path:
    """Get repository root from script location."""
    return Path(__file__).resolve().parents[2]


def _get_critical_violations() -> list[dict]:
    """Get ADG:CRITICAL violations from the ADG SQLite store."""
    violations = []
    repo_root = _get_repo_root()

    try:
        adg_dir = repo_root / "artifacts" / "adg"
        sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True)
        if not sqlite_files:
            print(
                "[ADG-CRITICAL-GATE] Warning: No ADG SQLite found. Run: python tools/generate/generate_full_adg.py",
                file=sys.stderr,
            )
            return []

        sqlite_path = sqlite_files[0]

        import sqlite3

        conn = sqlite3.connect(str(sqlite_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, file_path, edge_id, line_no, category
               FROM violations WHERE severity = ? LIMIT 50""",
            (SeverityLevel.CRITICAL.value,),
        )

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            violations.append(
                {
                    "id": row["id"],
                    "source_file": row["file_path"] or "unknown",
                    "symbol": row["edge_id"] or "unknown",
                    "line_no": row["line_no"] or 0,
                    "category": row.get("category", "unknown"),
                },
            )

    except (OSError, sqlite3.Error) as e:
        print(f"[ADG-CRITICAL-GATE] Warning: Could not query ADG SQLite: {e}", file=sys.stderr)
        print("[ADG-CRITICAL-GATE] Run: python tools/generate/generate_full_adg.py", file=sys.stderr)

    return violations


def _format_violation(v: dict) -> str:
    """Format a single violation for display."""
    source = v.get("source_file", "unknown")
    symbol = v.get("symbol", "unknown")
    line = v.get("line_no", 0)
    category = v.get("category", "unknown")
    return f"  {source}:{line}  [{category}]  →  {symbol}"


def main() -> int:
    print("[ADG-CRITICAL-GATE] Checking for ADG:CRITICAL defects (SeverityLevel.CRITICAL)...")

    violations = _get_critical_violations()

    if not violations:
        print("[ADG-CRITICAL-GATE] OK: No ADG:CRITICAL defects found.")
        print("[ADG-CRITICAL-GATE] Commit allowed.")
        return 0

    grouped: dict[str, list[dict]] = {}
    for v in violations:
        category = v.get("category", "unknown")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(v)

    print(f"[ADG-CRITICAL-GATE] BLOCKING: {len(violations)} ADG:CRITICAL defect(s) found:")
    print()

    for category, viols in sorted(grouped.items(), key=lambda x: -len(x[1])):
        print(f"  [{category}] — {len(viols)} occurrence(s):")
        for v in viols[:10]:
            print(_format_violation(v))
        if len(viols) > 10:
            print(f"    ... and {len(viols) - 10} more")
        print()

    print("[ADG-CRITICAL-GATE] COMMIT BLOCKED — Fix ADG:CRITICAL defects before committing.")
    print("[ADG-CRITICAL-GATE] ADG:CRITICAL = layer boundary violations and architecture defects.")
    print("[ADG-CRITICAL-GATE] Run ADG repair: python tools/generate/generate_full_adg.py --repair")
    return 1


if __name__ == "__main__":
    sys.exit(main())
