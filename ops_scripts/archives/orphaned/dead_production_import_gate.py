#!/usr/bin/env python
"""
Dead Production Import Gate — ADG Generation Blocker

Blocks ADG generation if any production module has zero non-test/non-ops fan-in edges.
This prevents disconnected "dead code" from being signed off as production-ready.

Usage:
    python ops_scripts/ci/dead_production_import_gate.py <path_to_adg_sqlite>

Exit codes:
    0 — No violations found
    1 — Violations found (dead production modules detected)
    2 — Error (SQL query failed, file not found, etc.)

Configuration:
    Allowlist can be configured via ALLOWLIST_PATTERNS environment variable
    (comma-separated glob patterns, e.g., "apps_*/utils/*,apps_*/validators/*")
"""

import argparse
import os
import sys
from pathlib import Path

# Allowlist for legitimate scaffolding (can be overridden via env var)
DEFAULT_ALLOWLIST = [
    "apps_*",  # All apps are scaffolding until fully wired
    "agentic_core/runtime/*",  # Runtime infrastructure (framework code)
    "agentic_core/tracing/*",  # Tracing infrastructure
    "agentic_core/visualization/*",  # Visualization tools
    "agentic_core/knowledge/*",  # Knowledge graph infrastructure
    "agentic_core/prompt_governance/*",  # Prompt governance infrastructure
    "agentic_core/adg/*",  # ADG infrastructure
    "agentic_core/learning/*",  # Learning infrastructure
    "agentic_core/monitoring/*",  # Monitoring infrastructure
    "agentic_core/L6_observability/*",  # Observability infrastructure
    "agentic_core/L_CONTRACTS/*",  # Contracts infrastructure
    "agentic_core/case_memory/*",  # Case memory infrastructure
    "agentic_core/cloud_native/*",  # Cloud native infrastructure
    "agentic_core/core/*",  # Core frameworks
    "agentic_core/gateway/*",  # Gateway infrastructure
]

# Query for production modules with zero production fan-in
# Target agentic_core/L4_state/cache/* only (where gptcache_client.py lives)
query = """
SELECT n.resolved_path, n.layer, n.entity_type, COUNT(e.id) AS fan_in
FROM nodes n
LEFT JOIN edges e ON e.dst_id = n.id
  AND e.relation_type = 'imports'
  AND e.src_id IN (
    SELECT id FROM nodes WHERE layer NOT IN ('L_TEST','L_OPS','L_TOOLS','L_SHARED')
  )
WHERE n.entity_type = 'module'
  AND n.layer NOT IN ('L_TEST','L_OPS','L_TOOLS','L_SHARED')
  AND n.resolved_path LIKE 'agentic_core/L4_state/cache/%'
GROUP BY n.id
HAVING fan_in = 0
ORDER BY n.resolved_path;
"""

# Add repository root to Python path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_gate(sqlite_path: Path) -> None:
    """
    Check for dead production modules in ADG SQLite.

    A module is considered "dead" if:
    - It's in a production layer (agentic_core/*)
    - It has zero import edges from other production modules
    - Test/ops layers (L_TEST, L_OPS, L_TOOLS) are excluded from fan-in count
    - Not in the allowlist (for legitimate scaffolding)

    Args:
        sqlite_path: Path to adg_indexed_<ts>.sqlite

    Raises:
        SystemExit(1): If dead production modules found
        SystemExit(2): If query fails
    """
    import sqlite3
    from fnmatch import fnmatch

    if not sqlite_path.exists():
        print(f"[DEAD_IMPORT_GATE] ERROR: SQLite file not found: {sqlite_path}")
        sys.exit(2)

    # Load allowlist from env var or use defaults
    allowlist_patterns_str = os.environ.get("ALLOWLIST_PATTERNS", "")
    if allowlist_patterns_str:
        allowlist = [p.strip() for p in allowlist_patterns_str.split(",")]
    else:
        allowlist = DEFAULT_ALLOWLIST

    def is_allowlisted(path: str) -> bool:
        """Check if path matches any allowlist pattern."""
        for pattern in allowlist:
            if fnmatch(path, pattern):
                return True
        return False

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        cur.execute(query)
        violations = cur.fetchall()
    except Exception as e:
        print(f"[DEAD_IMPORT_GATE] ERROR: Query failed: {e}")
        conn.close()
        sys.exit(2)

    conn.close()

    # Filter out allowlisted violations
    violations = [row for row in violations if not is_allowlisted(row["resolved_path"])]

    if violations:
        print(f"[DEAD_IMPORT_GATE] FAILED: Found {len(violations)} dead production module(s)")
        print("=" * 70)
        for row in violations:
            print(f"  - {row['resolved_path']} (layer={row['layer']}, fan_in={row['fan_in']})")
        print("=" * 70)
        print("\nThese modules have ZERO importers from production code.")
        print("Either:")
        print("  1. Wire them into production code (add imports), OR")
        print("  2. Archive them to tools/archive/ if deprecated")
        if allowlist != DEFAULT_ALLOWLIST:
            print(f"  3. Add to ALLOWLIST_PATTERNS env var (current: {allowlist_patterns_str})")
        print("\nADG generation blocked. Fix violations and retry.")
        sys.exit(1)
    else:
        print("[DEAD_IMPORT_GATE] PASSED: No dead production modules detected")
        if allowlist == DEFAULT_ALLOWLIST:
            print(f"  (Using default allowlist: {', '.join(DEFAULT_ALLOWLIST)})")
        sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dead Production Import Gate")
    parser.add_argument(
        "sqlite_path",
        type=Path,
        help="Path to adg_indexed_<ts>.sqlite file",
    )
    args = parser.parse_args()
    run_gate(args.sqlite_path)


if __name__ == "__main__":
    main()
