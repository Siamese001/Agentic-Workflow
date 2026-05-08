"""C0 Policy Migration — Background Contract Updater (Eager Migration)

W1 c0-policy-rectification-phase2-deferred-a3f7e2:
    Implements eager migration strategy for RouteContract instances
    lacking c0_policy field. Rewrites contracts with derived C0Policy
    based on legacy fields (grounding_required, route_id patterns).

Usage:
    python -m tools.c0_migration.background_contract_updater \
        --source-db contracts.db \
        --batch-size 100 \
        --dry-run

DS-5: Eager migration option for C0 policy rectification.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MigrationStats:
    """Statistics from a migration run."""

    total_contracts: int
    already_migrated: int
    needs_migration: int
    migrated_success: int
    migrated_failed: int
    dry_run: bool


def derive_c0_policy_from_legacy(contract: dict[str, Any]) -> dict[str, Any] | None:
    """Derive C0Policy from legacy RouteContract fields.

    W1 c0-policy-rectification-phase2-deferred-a3f7e2:
        Migration logic to backfill c0_policy for existing contracts.

    Derivation rules (match L0 routing logic):
    - R1_* routes: c0_mode=NOT_REQUIRED (preload routes)
    - R3_* routes: c0_mode=RETRIEVE_REQUIRED, evidence_contract_required=True
    - R4_* routes: c0_mode=BYPASS_PRELOADED_CONTEXT
    - R5_* routes: c0_mode=BYPASS_FALLBACK (or derived from grounding_required)
    - grounding_required=True: evidence_contract_required=True
    - grounding_required=False: evidence_contract_required=False
    """
    route_id = contract.get("route_id", "")
    grounding_required = contract.get("grounding_required", False)

    # Derive from route_id pattern (L0 routing logic)
    if route_id.startswith("R1_"):
        c0_mode = "NOT_REQUIRED"
        evidence_required = False
        decision_source = "L0_ROUTE_TOPOLOGY"
    elif route_id.startswith("R3_"):
        c0_mode = "RETRIEVE_REQUIRED"
        evidence_required = True
        decision_source = "L0_ROUTE_TOPOLOGY"
    elif route_id.startswith("R4_"):
        c0_mode = "BYPASS_PRELOADED_CONTEXT"
        evidence_required = False
        decision_source = "L0_ROUTE_TOPOLOGY"
    elif route_id.startswith("R5_"):
        c0_mode = "BYPASS_FALLBACK"
        evidence_required = False
        decision_source = "L0_ROUTE_TOPOLOGY"
    else:
        # Fallback: derive from grounding_required only
        c0_mode = "RETRIEVE_REQUIRED" if grounding_required else "NOT_REQUIRED"
        evidence_required = grounding_required
        decision_source = "L1_ADVISORY"

    return {
        "c0_mode": c0_mode,
        "evidence_contract_required": evidence_required,
        "decision_source": decision_source,
        "c0_mode_reason": f"MIGRATED:derived_from_{'route_id' if route_id else 'grounding_required'}",
    }


def migrate_contract(contract: dict[str, Any]) -> dict[str, Any] | None:
    """Migrate a single RouteContract, adding c0_policy if missing.

    Returns:
        Updated contract dict if migration applied, None if skipped.
    """
    # Skip if already has c0_policy
    if contract.get("c0_policy") is not None:
        return None

    # Derive C0 policy from legacy fields
    c0_policy = derive_c0_policy_from_legacy(contract)
    if c0_policy is None:
        return None

    # Create updated contract
    updated = dict(contract)
    updated["c0_policy"] = c0_policy
    updated["_migration_metadata"] = {
        "migrated_at": datetime.utcnow().isoformat(),
        "migration_tool": "background_contract_updater",
        "migration_version": "W1-phase2-a3f7e2",
    }
    return updated


def run_migration(
    db_path: str,
    batch_size: int = 100,
    dry_run: bool = True,
) -> MigrationStats:
    """Run eager migration on RouteContract database.

    Args:
        db_path: Path to SQLite database with contracts table
        batch_size: Number of contracts to process per batch
        dry_run: If True, don't write changes (preview only)

    Returns:
        MigrationStats with counts
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    stats = {
        "total": 0,
        "already_migrated": 0,
        "needs_migration": 0,
        "success": 0,
        "failed": 0,
    }

    try:
        cursor = conn.cursor()

        # Count total
        cursor.execute("SELECT COUNT(*) FROM route_contracts")
        stats["total"] = cursor.fetchone()[0]

        # Count already migrated
        cursor.execute(
            "SELECT COUNT(*) FROM route_contracts WHERE c0_policy IS NOT NULL"
        )
        stats["already_migrated"] = cursor.fetchone()[0]
        stats["needs_migration"] = stats["total"] - stats["already_migrated"]

        if dry_run:
            print(f"DRY RUN: Would migrate {stats['needs_migration']} contracts")
            return MigrationStats(
                total_contracts=stats["total"],
                already_migrated=stats["already_migrated"],
                needs_migration=stats["needs_migration"],
                migrated_success=0,
                migrated_failed=0,
                dry_run=True,
            )

        # Process in batches
        offset = 0
        while True:
            cursor.execute(
                "SELECT * FROM route_contracts WHERE c0_policy IS NULL LIMIT ? OFFSET ?",
                (batch_size, offset),
            )
            rows = cursor.fetchall()
            if not rows:
                break

            for row in rows:
                contract = dict(row)
                updated = migrate_contract(contract)

                if updated:
                    try:
                        cursor.execute(
                            "UPDATE route_contracts SET c0_policy = ? WHERE route_id = ?",
                            (json.dumps(updated["c0_policy"]), contract["route_id"]),
                        )
                        stats["success"] += 1
                    except Exception as e:
                        print(f"Failed to migrate {contract['route_id']}: {e}")
                        stats["failed"] += 1

            conn.commit()
            print(f"Migrated batch: offset={offset}, batch_size={batch_size}")
            offset += batch_size

    finally:
        conn.close()

    return MigrationStats(
        total_contracts=stats["total"],
        already_migrated=stats["already_migrated"],
        needs_migration=stats["needs_migration"],
        migrated_success=stats["success"],
        migrated_failed=stats["failed"],
        dry_run=False,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for background contract updater."""
    parser = argparse.ArgumentParser(
        description="C0 Policy Background Contract Updater (Eager Migration)"
    )
    parser.add_argument(
        "--source-db",
        required=True,
        help="Path to SQLite database with route_contracts table",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of contracts to process per batch",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without writing changes",
    )
    parser.add_argument(
        "--output-stats",
        help="Path to write migration stats JSON",
    )

    args = parser.parse_args(argv)

    if not Path(args.source_db).exists():
        print(f"Error: Database not found: {args.source_db}", file=sys.stderr)
        return 1

    print(f"Starting C0 Policy migration...")
    print(f"  Database: {args.source_db}")
    print(f"  Dry run: {args.dry_run}")
    print(f"  Batch size: {args.batch_size}")
    print()

    stats = run_migration(
        db_path=args.source_db,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )

    print("\nMigration complete!")
    print(f"  Total contracts: {stats.total_contracts}")
    print(f"  Already migrated: {stats.already_migrated}")
    print(f"  Needed migration: {stats.needs_migration}")
    print(f"  Migrated (success): {stats.migrated_success}")
    print(f"  Migrated (failed): {stats.migrated_failed}")

    if args.output_stats:
        stats_dict = {
            "total_contracts": stats.total_contracts,
            "already_migrated": stats.already_migrated,
            "needs_migration": stats.needs_migration,
            "migrated_success": stats.migrated_success,
            "migrated_failed": stats.migrated_failed,
            "dry_run": stats.dry_run,
            "completed_at": datetime.utcnow().isoformat(),
        }
        with open(args.output_stats, "w") as f:
            json.dump(stats_dict, f, indent=2)
        print(f"\nStats written to: {args.output_stats}")

    return 0 if stats.migrated_failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
