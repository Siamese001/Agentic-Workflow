#!/usr/bin/env python3
"""
Memory Graph Purge Sync Tool

Purge stale entities from the memory graph.
Protected types (ArchitectureLayer, ProjectContext, ConstitutionalRule, EpisodicEvent,
ProceduralPattern, ArchitecturalDecision) are never deleted.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent
MEMORY_DB = REPO_ROOT / "artifacts" / "memory" / "knowledge_graph.sqlite"
TELEMETRY_DIR = REPO_ROOT / "docs" / "reports" / "telemetry"

PROTECTED_TYPES = {
    "ArchitectureLayer",
    "ProjectContext",
    "ConstitutionalRule",
    "EpisodicEvent",
    "ProceduralPattern",
    "ArchitecturalDecision",
}


def get_db_connection() -> sqlite3.Connection:
    """Get connection to memory database."""
    if not MEMORY_DB.exists():
        print(f"Error: Memory database not found at {MEMORY_DB}", file=sys.stderr)
        sys.exit(1)
    return sqlite3.connect(MEMORY_DB)



def get_current_stats(conn: sqlite3.Connection) -> Dict:
    """Get current memory graph statistics."""
    cursor = conn.cursor()

    # Total entities
    cursor.execute("SELECT COUNT(*) FROM entities")
    total_entities = cursor.fetchone()[0]

    # Entities by type
    cursor.execute("SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type")
    by_type = {row[0]: row[1] for row in cursor.fetchall()}

    # Total observations
    cursor.execute("SELECT COUNT(*) FROM observations")
    total_observations = cursor.fetchone()[0]

    # Total relations
    cursor.execute("SELECT COUNT(*) FROM relations")
    total_relations = cursor.fetchone()[0]

    # Oldest entity age
    cursor.execute("SELECT MIN(created_at) FROM entities")
    oldest = cursor.fetchone()[0]
    oldest_days = None
    if oldest:
        try:
            oldest_dt = datetime.fromisoformat(oldest.replace("Z", "+00:00"))
            oldest_days = (datetime.now(timezone.utc) - oldest_dt).days
        except (ValueError, AttributeError):
            pass

    return {
        "total_entities": total_entities,
        "by_type": by_type,
        "total_observations": total_observations,
        "total_relations": total_relations,
        "oldest_entity_days": oldest_days,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def get_stale_entities(conn: sqlite3.Connection, older_than_days: int) -> List[str]:
    """Get entity names that are stale (older than threshold) and not protected."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, entity_type, created_at FROM entities
        WHERE entity_type NOT IN ({})
    """.format(",".join("'" + t + "'" for t in PROTECTED_TYPES)))

    stale = []
    for name, _, created_at in cursor.fetchall():
        if not created_at:
            continue
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - created_dt).days
            if age_days > older_than_days:
                stale.append(name)
        except (ValueError, AttributeError):
            pass

    return stale


def purge_entities(conn: sqlite3.Connection, entity_names: List[str], dry_run: bool = False) -> int:
    """Purge entities and cascade-delete their observations and relations."""
    if not entity_names:
        return 0

    cursor = conn.cursor()
    count = 0

    for name in entity_names:
        if dry_run:
            print(f"  [DRY-RUN] Would delete: {name}")
            count += 1
        else:
            cursor.execute("DELETE FROM relations WHERE from_entity = ? OR to_entity = ?", (name, name))
            cursor.execute("DELETE FROM observations WHERE entity_name = ?", (name,))
            cursor.execute("DELETE FROM entities WHERE name = ?", (name,))
            count += 1

    if not dry_run:
        conn.commit()

    return count



def write_evidence(before: Dict, after: Dict, purged_count: int) -> Path:
    """Write telemetry evidence artifact."""
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    evidence_file = TELEMETRY_DIR / f"memory_purge_{timestamp}.json"

    evidence = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "before": before,
        "after": after,
        "purged_count": purged_count,
        "reduction_percent": round(
            (before["total_entities"] - after["total_entities"]) / max(before["total_entities"], 1) * 100, 1,
        ) if before["total_entities"] > 0 else 0,
    }

    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    return evidence_file


def cmd_stats(_args):
    """Show current memory graph statistics."""
    conn = get_db_connection()
    stats = get_current_stats(conn)
    conn.close()

    print("Memory Graph Statistics")
    print(f"  Total entities:      {stats['total_entities']}")
    print(f"  Total observations:  {stats['total_observations']}")
    print(f"  Total relations:     {stats['total_relations']}")
    if stats['oldest_entity_days'] is not None:
        print(f"  Oldest entity age:   {stats['oldest_entity_days']} days")

    print("\nEntity types:")
    for etype, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        protected = " [PROTECTED]" if etype in PROTECTED_TYPES else ""
        print(f"  {etype}: {count}{protected}")

    return 0


def cmd_purge(args):
    """Purge stale entities."""
    conn = get_db_connection()

    stale = get_stale_entities(conn, args.older_than_days)
    print(f"Found {len(stale)} stale entities (>{args.older_than_days} days)")

    if stale and args.dry_run:
        print("Dry-run mode — no changes made")

    count = purge_entities(conn, stale, dry_run=args.dry_run)
    conn.close()

    if args.dry_run:
        print(f"\n[DRY-RUN] Would purge {count} entities")
    else:
        print(f"\nPurged {count} entities")

    return 0



def cmd_full_sync(args):
    """Execute full purge sync workflow."""
    conn = get_db_connection()

    # Pre-purge stats
    print("=== Pre-Purge Stats ===")
    before = get_current_stats(conn)
    print(f"Entities: {before['total_entities']}")
    print(f"Observations: {before['total_observations']}")
    print(f"Relations: {before['total_relations']}")
    conn.close()

    # Purge
    print("\n=== Purging (>" + str(args.older_than_days) + " days) ===")
    conn = get_db_connection()
    stale = get_stale_entities(conn, args.older_than_days)
    print(f"Stale entities found: {len(stale)}")
    purged = purge_entities(conn, stale, dry_run=False)
    print(f"Purged: {purged}")
    conn.close()

    # Post-purge stats
    print("\n=== Post-Purge Stats ===")
    conn = get_db_connection()
    after = get_current_stats(conn)
    print(f"Entities: {after['total_entities']} ({before['total_entities'] - after['total_entities']} removed)")
    print(f"Observations: {after['total_observations']}")
    print(f"Relations: {after['total_relations']}")

    # Verify protected entities
    protected_ok = all(
        after['by_type'].get(pt, 0) > 0 for pt in PROTECTED_TYPES
    )
    print(f"\nProtected entities: {'✓' if protected_ok else '✗'}")
    conn.close()

    # Write evidence
    if args.evidence:
        evidence_path = write_evidence(before, after, purged)
        print(f"\nEvidence written: {evidence_path}")

    # Health check
    if after['total_entities'] > 500:
        print(f"\nWarning: Entity count ({after['total_entities']}) exceeds recommended threshold (500)", file=sys.stderr)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Memory Graph Purge Sync Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --stats                    Show current statistics
  %(prog)s --purge --dry-run          Preview what would be purged
  %(prog)s --purge --older-than-days=7  Purge entities >7 days old
  %(prog)s --full-sync --evidence      Full sync with evidence artifact
        """,
    )

    parser.add_argument("--stats", action="store_true", help="Show memory graph statistics")
    parser.add_argument("--purge", action="store_true", help="Purge stale entities")
    parser.add_argument("--older-than-days", type=int, default=7, help="Purge threshold in days (default: 7)")
    parser.add_argument("--dry-run", action="store_true", help="Preview purge without deleting")
    parser.add_argument("--full-sync", action="store_true", help="Execute full purge sync workflow")
    parser.add_argument("--evidence", action="store_true", help="Write evidence artifact (with --full-sync)")

    args = parser.parse_args()

    if not any([args.stats, args.purge, args.full_sync]):
        parser.print_help()
        return 0

    if args.stats:
        return cmd_stats(args)
    elif args.purge:
        return cmd_purge(args)
    elif args.full_sync:
        return cmd_full_sync(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
