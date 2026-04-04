#!/usr/bin/env python3
"""
Memory Health CI Gate

Checks memory graph for bloat conditions:
- Entity count > 500
- Oldest non-protected entity age > 14 days

Exit codes:
- 0: Healthy
- 1: Warning (bloat detected)
- 2: Error (database unavailable)
"""

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
MEMORY_DB = REPO_ROOT / "artifacts" / "memory" / "knowledge_graph.sqlite"

# Health thresholds
MAX_ENTITIES = 500
MAX_ENTITY_AGE_DAYS = 14

# Protected types never purged
PROTECTED_TYPES = {"ArchitectureLayer", "ProjectContext", "ConstitutionalRule"}


def get_db_connection() -> sqlite3.Connection:
    """Get connection to memory database."""
    if not MEMORY_DB.exists():
        print(f"ERROR: Memory database not found at {MEMORY_DB}", file=sys.stderr)
        sys.exit(2)
    return sqlite3.connect(MEMORY_DB)


def check_entity_count(conn: sqlite3.Connection) -> tuple[bool, int]:
    """Check if entity count is within threshold."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM entities")
    count = cursor.fetchone()[0]
    healthy = count <= MAX_ENTITIES
    return healthy, count


def check_oldest_entity_age(conn: sqlite3.Connection) -> tuple[bool, int | None]:
    """Check age of oldest non-protected entity."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT created_at FROM entities
        WHERE entity_type NOT IN (?, ?, ?)
        ORDER BY created_at ASC
        LIMIT 1
    """, tuple(PROTECTED_TYPES))

    row = cursor.fetchone()
    if not row or not row[0]:
        return True, None

    try:
        oldest_dt = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - oldest_dt).days
        healthy = age_days <= MAX_ENTITY_AGE_DAYS
        return healthy, age_days
    except (ValueError, AttributeError):
        return True, None


def get_breakdown(conn: sqlite3.Connection) -> dict:
    """Get entity count breakdown by type."""
    cursor = conn.cursor()
    cursor.execute("SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type")
    return {row[0]: row[1] for row in cursor.fetchall()}


def main():
    """Run memory health checks."""
    conn = get_db_connection()

    # Run checks
    entity_count_ok, count = check_entity_count(conn)
    age_ok, age_days = check_oldest_entity_age(conn)
    breakdown = get_breakdown(conn)
    conn.close()

    # Report results
    print("Memory Health Check")
    print("=" * 40)
    print(f"Entity count:       {count} (threshold: {MAX_ENTITIES}) {'✓' if entity_count_ok else '✗'}")
    if age_days is not None:
        print(f"Oldest entity age:  {age_days} days (threshold: {MAX_ENTITY_AGE_DAYS}) {'✓' if age_ok else '✗'}")
    else:
        print(f"Oldest entity age:  N/A (no non-protected entities)")

    print("\nEntity breakdown:")
    for etype, etype_count in sorted(breakdown.items(), key=lambda x: -x[1]):
        protected_marker = " [P]" if etype in PROTECTED_TYPES else ""
        print(f"  {etype}: {etype_count}{protected_marker}")

    # Determine exit code
    if entity_count_ok and age_ok:
        print("\nStatus: HEALTHY ✓")
        return 0
    else:
        print("\nStatus: WARNING — Memory purge sync recommended")
        print(f"  Run: python {REPO_ROOT}/tools/memory/purge_sync.py --full-sync")
        return 1


if __name__ == "__main__":
    sys.exit(main())
