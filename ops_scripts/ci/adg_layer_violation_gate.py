#!/usr/bin/env python3
"""ADG Layer Violation Gate — Reports layer boundary violations from ADG.

This gate queries the ADG for 'violates' edges (layer boundary violations) and
reports them. Runs in warning mode by default (--warn) for visibility without
blocking commits.

Usage:
    python ops_scripts/ci/adg_layer_violation_gate.py [--warn]

Exit codes:
    0 — Always exits 0 in --warn mode (non-blocking)
    1 — Exits 1 if violations found and not in --warn mode
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _get_repo_root() -> Path:
    """Get repository root from script location."""
    return Path(__file__).resolve().parents[2]


def _load_adg_violations() -> list[dict]:
    """Load violations from ADG SQLite directly."""
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

        cursor.execute(
            """SELECT id, source_file, relation_type, symbol, line_no
               FROM edges WHERE relation_type = 'violates' LIMIT ?""",
            (100,),
        )

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            violations.append(
                {
                    "id": row["id"],
                    "source_file": row["source_file"] or "unknown",
                    "symbol": row["symbol"] or "unknown",
                    "line_no": row["line_no"] or 0,
                    "relation_type": row["relation_type"],
                }
            )

    except (OSError, json.JSONDecodeError, sqlite3.Error) as e:
        print(f"[ADG-LAYER-GATE] Warning: Could not query ADG: {e}", file=sys.stderr)

    return violations


def _format_violation(v: dict) -> str:
    """Format a single violation for display."""
    source = v.get("source_file", "unknown")
    symbol = v.get("symbol", "unknown")
    line = v.get("line_no", 0)
    return f"  {source}:{line}  →  {symbol}"


def main() -> int:
    parser = argparse.ArgumentParser(description="ADG Layer Violation Gate")
    parser.add_argument("--warn", action="store_true", help="Warning mode (non-blocking, exit 0)")
    args = parser.parse_args()

    violations = _load_adg_violations()

    if not violations:
        print("[ADG-LAYER-GATE] ✅ No layer boundary violations found in ADG.")
        return 0

    # Group by violation symbol (e.g., L0->L4)
    grouped: dict[str, list[dict]] = {}
    for v in violations:
        symbol = v.get("symbol", "unknown")
        if symbol not in grouped:
            grouped[symbol] = []
        grouped[symbol].append(v)

    # Output summary
    print(f"[ADG-LAYER-GATE] {'⚠️ ' if args.warn else '🚫 '} {len(violations)} layer violation(s) in ADG:")
    print()

    for symbol, viols in sorted(grouped.items(), key=lambda x: -len(x[1])):
        print(f"  [{symbol}] — {len(viols)} occurrence(s):")
        for v in viols[:5]:  # Show first 5 per category
            print(_format_violation(v))
        if len(viols) > 5:
            print(f"    ... and {len(viols) - 5} more")
        print()

    if args.warn:
        print("[ADG-LAYER-GATE] Warning mode — violations logged but not blocking commit.")
        print("                 Remove --warn flag or fix violations to enforce blocking mode.")
        return 0
    else:
        print("[ADG-LAYER-GATE] Blocking mode — fix violations or use --warn for non-blocking.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
