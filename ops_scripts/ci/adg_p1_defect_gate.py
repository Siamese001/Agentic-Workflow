#!/usr/bin/env python3
"""ADG P1 Defect Gate — Blocks commits if P1 (critical) ADG defects exist.

This gate queries the ADG repair routes to check for critical (P1) severity defects.
If any P1 defects exist, the gate blocks the commit with exit code 1.

SEVERITY SSOT: Uses agentic_core.L5_safety.config.severity.SeverityLevel

Usage:
    python ops_scripts/ci/adg_p1_defect_gate.py

Exit codes:
    0 — No P1 defects found (commit allowed)
    1 — P1 defects found (commit blocked)
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
    """Get detailed critical violations from ADG SQLite."""
    violations = []
    repo_root = _get_repo_root()

    try:
        adg_dir = repo_root / "artifacts" / "adg"
        sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True)
        if not sqlite_files:
            return []

        sqlite_path = sqlite_files[0]

        import sqlite3

        conn = sqlite3.connect(str(sqlite_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query violations table for critical severity using SSOT
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
                }
            )

    except (OSError, sqlite3.Error) as e:
        print(f"[ADG-P1-GATE] Warning: Could not query ADG SQLite: {e}", file=sys.stderr)

    return violations


def _format_violation(v: dict) -> str:
    """Format a single violation for display."""
    source = v.get("source_file", "unknown")
    symbol = v.get("symbol", "unknown")
    line = v.get("line_no", 0)
    category = v.get("category", "unknown")
    return f"  {source}:{line}  [{category}]  →  {symbol}"


def main() -> int:
    print("[ADG-P1-GATE] Checking for P1 (critical) ADG defects...")

    # Get critical violations
    violations = _get_critical_violations()
    
    if not violations:
        print("[ADG-P1-GATE] OK: No P1 (critical) defects found in ADG.")
        print("[ADG-P1-GATE] Commit allowed.")
        return 0

    # Group by category
    grouped: dict[str, list[dict]] = {}
    for v in violations:
        category = v.get("category", "unknown")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(v)

    # Output summary
    print(f"[ADG-P1-GATE] BLOCKING: {len(violations)} P1 (critical) defect(s) found in ADG:")
    print()

    for category, viols in sorted(grouped.items(), key=lambda x: -len(x[1])):
        print(f"  [{category}] — {len(viols)} occurrence(s):")
        for v in viols[:10]:  # Show first 10 per category
            print(_format_violation(v))
        if len(viols) > 10:
            print(f"    ... and {len(viols) - 10} more")
        print()

    print("[ADG-P1-GATE] COMMIT BLOCKED - Fix P1 defects before committing.")
    print("[ADG-P1-GATE] P1 defects are critical layer violations that must be resolved.")
    print("[ADG-P1-GATE] Run ADG repair: python tools/generate/generate_full_adg.py --repair")
    return 1


if __name__ == "__main__":
    sys.exit(main())
