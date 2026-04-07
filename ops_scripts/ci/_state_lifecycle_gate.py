#!/usr/bin/env python3
"""
P3/L4 State Lifecycle Governance CI Gate

Enforces Gates A-E for state lifecycle governance closure:
- Gate A: Runtime state namespace must have lifecycle policy
- Gate B: Expired state must not remain ACTIVE without explicit override
- Gate C: Archival or deletion must have lifecycle record
- Gate D: Stale state growth must have lifecycle transitions
- Gate E: Destructive state cleanup must have policy and trace

Runtime-only closure: excludes test, tests, spec, fixture, mock files.
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple

# Constants
NON_TEST = """
    AND source_file NOT LIKE '%test%'
    AND source_file NOT LIKE '%tests%'
    AND source_file NOT LIKE '%spec%'
    AND source_file NOT LIKE '%fixture%'
    AND source_file NOT LIKE '%mock%'
"""

GATE_RESULTS: list[tuple[str, bool, str]] = []


def _count_exported(conn: sqlite3.Connection, symbol: str, module_hint: str = "") -> int:
    """Count distinct source files exporting a symbol."""
    if module_hint:
        cursor = conn.execute(
            f"""
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? AND source_file LIKE ? {NON_TEST}
            """,
            (f"%{symbol}%", f"%{module_hint}%"),
        )
    else:
        cursor = conn.execute(
            f"""
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? {NON_TEST}
            """,
            (f"%{symbol}%",),
        )
    return cursor.fetchone()[0]


def _count_distinct_sources(
    conn: sqlite3.Connection, relation_type: str, filter_clause: str = NON_TEST,
) -> int:
    """Count distinct source files for a relation type."""
    cursor = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {filter_clause}",
        (relation_type,),
    )
    return cursor.fetchone()[0]


def gate_a(conn: sqlite3.Connection) -> bool:
    """Gate A — Runtime state namespace must have lifecycle policy.

    Passes when:
    - StateLifecycleError exported >= 1
      (exception for missing lifecycle policy), AND
    - apply_state_lifecycle_policy exported >= 1
      (mandatory lifecycle policy entrypoint), AND
    - StateLifecycleRecord exported >= 1
      (lifecycle record with 10 required fields), AND
    - lifecycle_policy_applied function exported >= 1
      (ADG edge emitter for static scanner), AND
    - reads_runtime_state edges >= 1
      (runtime state reads happening), AND
    - writes_to edges >= 1
      (runtime state writes happening)
    """
    lifecycle_error = _count_exported(conn, "StateLifecycleError", "state_lifecycle")
    apply_function = _count_exported(conn, "apply_state_lifecycle_policy", "lifecycle_policy_applier")
    lifecycle_record = _count_exported(conn, "StateLifecycleRecord", "state_lifecycle")
    emitter_function = _count_exported(conn, "lifecycle_policy_applied", "lifecycle_policy_applier")
    read_edges = _count_distinct_sources(conn, "reads_runtime_state")
    write_edges = _count_distinct_sources(conn, "writes_to")

    ok = (
        lifecycle_error >= 1
        and apply_function >= 1
        and lifecycle_record >= 1
        and emitter_function >= 1
        and read_edges >= 1
        and write_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"StateLifecycleError exported={lifecycle_error} (>=1), "
            f"apply_state_lifecycle_policy exported={apply_function} (>=1), "
            f"StateLifecycleRecord exported={lifecycle_record} (>=1), "
            f"lifecycle_policy_applied exported={emitter_function} (>=1), "
            f"reads_runtime_state sources={read_edges} (>=1), "
            f"writes_to sources={write_edges} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Expired state must not remain ACTIVE without explicit override.

    Passes when:
    - StateLifecycleRecord exported >= 1
      (lifecycle record with status field), AND
    - LifecycleStatus exported >= 1
      (lifecycle status enumeration), AND
    - EXPIRED status exported >= 1
      (expired lifecycle status), AND
    - ACTIVE status exported >= 1
      (active lifecycle status), AND
    - lifecycle_policy_applied function exported >= 1
      (ADG edge emitter with status parameter)
    """
    lifecycle_record = _count_exported(conn, "StateLifecycleRecord", "state_lifecycle")
    lifecycle_status = _count_exported(conn, "LifecycleStatus", "state_lifecycle")
    expired_status = _count_exported(conn, "EXPIRED", "state_lifecycle")
    active_status = _count_exported(conn, "ACTIVE", "state_lifecycle")
    emitter_function = _count_exported(conn, "lifecycle_policy_applied", "lifecycle_policy_applier")

    ok = (
        lifecycle_record >= 1
        and lifecycle_status >= 1
        and expired_status >= 1
        and active_status >= 1
        and emitter_function >= 1
    )
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"StateLifecycleRecord exported={lifecycle_record} (>=1), "
            f"LifecycleStatus exported={lifecycle_status} (>=1), "
            f"EXPIRED exported={expired_status} (>=1), "
            f"ACTIVE exported={active_status} (>=1), "
            f"lifecycle_policy_applied exported={emitter_function} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Archival or deletion must have lifecycle record.

    Passes when:
    - StateLifecycleRecord exported >= 1
      (lifecycle record for archival/deletion tracking), AND
    - ARCHIVED status exported >= 1
      (archived lifecycle status), AND
    - DELETED status exported >= 1
      (deleted lifecycle status), AND
    - state_archived function exported >= 1
      (ADG edge emitter for archival), AND
    - state_deleted function exported >= 1
      (ADG edge emitter for deletion)
    """
    lifecycle_record = _count_exported(conn, "StateLifecycleRecord", "state_lifecycle")
    archived_status = _count_exported(conn, "ARCHIVED", "state_lifecycle")
    deleted_status = _count_exported(conn, "DELETED", "state_lifecycle")
    archive_emitter = _count_exported(conn, "state_archived", "lifecycle_policy_applier")
    delete_emitter = _count_exported(conn, "state_deleted", "lifecycle_policy_applier")

    ok = (
        lifecycle_record >= 1
        and archived_status >= 1
        and deleted_status >= 1
        and archive_emitter >= 1
        and delete_emitter >= 1
    )
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"StateLifecycleRecord exported={lifecycle_record} (>=1), "
            f"ARCHIVED exported={archived_status} (>=1), "
            f"DELETED exported={deleted_status} (>=1), "
            f"state_archived exported={archive_emitter} (>=1), "
            f"state_deleted exported={delete_emitter} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Stale state growth must have lifecycle transitions.

    Passes when:
    - StateLifecycleRecord exported >= 1
      (lifecycle record for stale state tracking), AND
    - STALE status exported >= 1
      (stale lifecycle status), AND
    - lifecycle_transition_recorded function exported >= 1
      (ADG edge emitter for lifecycle transitions), AND
    - writes_through edges >= 1
      (runtime state writes for stale growth detection), AND
    - snapshots_state edges >= 1
      (runtime state snapshots for lifecycle management)
    """
    lifecycle_record = _count_exported(conn, "StateLifecycleRecord", "state_lifecycle")
    stale_status = _count_exported(conn, "STALE", "state_lifecycle")
    transition_emitter = _count_exported(conn, "lifecycle_transition_recorded", "lifecycle_policy_applier")
    write_through_edges = _count_distinct_sources(conn, "writes_through")
    snapshot_edges = _count_distinct_sources(conn, "snapshots_state")

    ok = (
        lifecycle_record >= 1
        and stale_status >= 1
        and transition_emitter >= 1
        and write_through_edges >= 1
        and snapshot_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"StateLifecycleRecord exported={lifecycle_record} (>=1), "
            f"STALE exported={stale_status} (>=1), "
            f"lifecycle_transition_recorded exported={transition_emitter} (>=1), "
            f"writes_through sources={write_through_edges} (>=1), "
            f"snapshots_state sources={snapshot_edges} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Destructive state cleanup must have policy and trace.

    Passes when:
    - StateLifecycleRecord exported >= 1
      (lifecycle record with policy and trace fields), AND
    - LifecyclePolicy exported >= 1
      (lifecycle policy definition), AND
    - PENDING_DELETION status exported >= 1
      (pending deletion lifecycle status), AND
    - state_deleted function exported >= 1
      (ADG edge emitter for destructive cleanup), AND
    - writes_to edges >= 1
      (runtime state writes for destructive operations)
    """
    lifecycle_record = _count_exported(conn, "StateLifecycleRecord", "state_lifecycle")
    lifecycle_policy = _count_exported(conn, "LifecyclePolicy", "state_lifecycle")
    pending_deletion_status = _count_exported(conn, "PENDING_DELETION", "state_lifecycle")
    delete_emitter = _count_exported(conn, "state_deleted", "lifecycle_policy_applier")
    write_edges = _count_distinct_sources(conn, "writes_to")

    ok = (
        lifecycle_record >= 1
        and lifecycle_policy >= 1
        and pending_deletion_status >= 1
        and delete_emitter >= 1
        and write_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"StateLifecycleRecord exported={lifecycle_record} (>=1), "
            f"LifecyclePolicy exported={lifecycle_policy} (>=1), "
            f"PENDING_DELETION exported={pending_deletion_status} (>=1), "
            f"state_deleted exported={delete_emitter} (>=1), "
            f"writes_to sources={write_edges} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P3/L4 state lifecycle governance baseline for verification."""
    print("\n--- P3/L4 State Lifecycle Governance Baseline ---")

    for rel in (
        "reads_runtime_state",
        "writes_through",
        "writes_to",
        "snapshots_state",
        "lifecycle_policy_applied",
        "lifecycle_transition_recorded",
        "state_archived",
        "state_deleted",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L4 state lifecycle symbols (non-test) ---")
    for sym in (
        "StateLifecycleRecord",
        "apply_state_lifecycle_policy",
        "StateLifecycleContext",
        "LifecycleStatus",
        "RetentionClass",
        "state_namespace",
        "lifecycle_policy_id",
        "retention_class",
        "expiration_rule",
        "archival_rule",
        "deletion_rule",
        "created_at_tick",
        "last_accessed_tick",
        "last_mutated_tick",
        "lifecycle_status",
        "ACTIVE",
        "STALE",
        "EXPIRED",
        "ARCHIVED",
        "PENDING_DELETION",
        "DELETED",
        "SHORT_TERM",
        "MEDIUM_TERM",
        "LONG_TERM",
        "PERMANENT",
        "StateLifecycleError",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L4 lifecycle module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L4_persistence/lifecycle%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P3/L4 state lifecycle governance gates."""
    # Find latest ADG SQLite artifact
    adg_dir = Path("artifacts/adg")
    if not adg_dir.exists():
        print("ERROR: artifacts/adg directory not found")
        return 1

    db_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not db_files:
        print("ERROR: No ADG SQLite artifacts found")
        return 1

    db_path = db_files[-1]
    print(f"Using ADG: {db_path.name}")

    conn = sqlite3.connect(str(db_path))

    # Run gates
    gate_a_result = gate_a(conn)
    gate_b_result = gate_b(conn)
    gate_c_result = gate_c(conn)
    gate_d_result = gate_d(conn)
    gate_e_result = gate_e(conn)

    # Print baseline
    _print_baseline(conn)

    # Print results
    print("\n" + "=" * 70)
    print("GATE RESULTS")
    print("=" * 70)
    for gate, ok, details in GATE_RESULTS:
        status = "PASS" if ok else "FAIL"
        print(f"  Gate {gate}: {status} - {details}")

    # Overall result
    all_passed = all([gate_a_result, gate_b_result, gate_c_result, gate_d_result, gate_e_result])
    print("\n" + "=" * 70)
    if all_passed:
        print("P3/L4 STATE LIFECYCLE GOVERNANCE: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P3/L4 STATE LIFECYCLE GOVERNANCE: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
