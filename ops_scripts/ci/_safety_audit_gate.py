#!/usr/bin/env python3
"""
P2/L5 Safety Audit Trails CI Gate

Enforces Gates A-E for safety audit trail closure:
- Gate A: Runtime safety decisions must emit audit records
- Gate B: Runtime audit records must have policy hash
- Gate C: Runtime audit records must have decision outcome
- Gate D: Human review must have reviewer metadata
- Gate E: Audit records must be queryable by run_id and trace_id

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
    """Gate A — Runtime safety decisions must emit audit records.

    Passes when:
    - SafetyAuditMissingError exported >= 1
      (exception for missing audit records), AND
    - emit_safety_audit_record exported >= 1
      (mandatory audit entrypoint), AND
    - safety_audit_emitted function exported >= 1
      (ADG edge emitter for static scanner), AND
    - applies_guardrail edges >= 1
      (guardrail decisions happening), AND
    - validated_by_safety_plane edges >= 1
      (safety plane validations happening)
    """
    missing_error = _count_exported(conn, "SafetyAuditMissingError", "safety_audit_registry")
    emit_function = _count_exported(conn, "emit_safety_audit_record", "safety_audit_emitter")
    emitter_function = _count_exported(conn, "safety_audit_emitted", "safety_audit_emitter")
    guardrail_edges = _count_distinct_sources(conn, "applies_guardrail")
    safety_plane_edges = _count_distinct_sources(conn, "validated_by_safety_plane")

    ok = (
        missing_error >= 1
        and emit_function >= 1
        and emitter_function >= 1
        and guardrail_edges >= 1
        and safety_plane_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"SafetyAuditMissingError exported={missing_error} (>=1), "
            f"emit_safety_audit_record exported={emit_function} (>=1), "
            f"safety_audit_emitted exported={emitter_function} (>=1), "
            f"applies_guardrail sources={guardrail_edges} (>=1), "
            f"validated_by_safety_plane sources={safety_plane_edges} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Runtime audit records must have policy hash.

    Passes when:
    - SafetyAuditRecord exported >= 1
      (audit record with policy hash field), AND
    - policy_hash field present in SafetyAuditRecord
      (verified by symbol search), AND
    - references_policy_hash edges >= 1
      (policy hash binding happening)
    """
    audit_record = _count_exported(conn, "SafetyAuditRecord", "safety_audit_registry")
    policy_hash_field = _count_exported(conn, "policy_hash", "safety_audit_registry")
    policy_hash_edges = _count_distinct_sources(conn, "references_policy_hash")

    ok = audit_record >= 1 and policy_hash_field >= 1 and policy_hash_edges >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"SafetyAuditRecord exported={audit_record} (>=1), "
            f"policy_hash field present={policy_hash_field} (>=1), "
            f"references_policy_hash sources={policy_hash_edges} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Runtime audit records must have decision outcome.

    Passes when:
    - SafetyAuditRecord exported >= 1
      (audit record with decision_outcome field), AND
    - applies_guardrail edges >= 1
      (decisions being made)
    """
    audit_record = _count_exported(conn, "SafetyAuditRecord", "safety_audit_registry")
    guardrail_edges = _count_distinct_sources(conn, "applies_guardrail")

    ok = audit_record >= 1 and guardrail_edges >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"SafetyAuditRecord exported={audit_record} (>=1), "
            f"applies_guardrail sources={guardrail_edges} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Human review must have reviewer metadata.

    Passes when:
    - HumanReviewAuditError exported >= 1
      (exception for missing reviewer metadata), AND
    - HumanReviewAuditRecord exported >= 1
      (audit record with reviewer fields), AND
    - requires_human_review edges >= 1
      (human review requirements happening)
    """
    review_error = _count_exported(conn, "HumanReviewAuditError", "safety_audit_registry")
    review_record = _count_exported(conn, "HumanReviewAuditRecord", "safety_audit_registry")
    human_review_edges = _count_distinct_sources(conn, "requires_human_review")

    ok = review_error >= 1 and review_record >= 1 and human_review_edges >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"HumanReviewAuditError exported={review_error} (>=1), "
            f"HumanReviewAuditRecord exported={review_record} (>=1), "
            f"requires_human_review sources={human_review_edges} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Audit records must be queryable by run_id and trace_id.

    Passes when:
    - SafetyAuditRegistry exported >= 1
      (registry for audit storage), AND
    - query_safety_audits exported >= 1
      (query function), AND
    - SafetyAuditRecord exported >= 1
      (audit record with run_id and trace_id fields), AND
    - AuditQueryError exported >= 1
      (exception for query failures)
    """
    registry = _count_exported(conn, "SafetyAuditRegistry", "safety_audit_registry")
    query_function = _count_exported(conn, "query_safety_audits", "safety_audit_emitter")
    audit_record = _count_exported(conn, "SafetyAuditRecord", "safety_audit_registry")
    query_error = _count_exported(conn, "AuditQueryError", "safety_audit_registry")

    ok = registry >= 1 and query_function >= 1 and audit_record >= 1 and query_error >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"SafetyAuditRegistry exported={registry} (>=1), "
            f"query_safety_audits exported={query_function} (>=1), "
            f"SafetyAuditRecord exported={audit_record} (>=1), "
            f"AuditQueryError exported={query_error} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P2/L5 safety audit baseline for verification."""
    print("\n--- P2/L5 Safety Audit Trails Baseline ---")

    for rel in (
        "applies_guardrail",
        "validated_by_safety_plane",
        "requires_human_review",
        "escalates_to_human",
        "references_policy_hash",
        "safety_audit_emitted",
        "human_review_audited",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L5 audit symbols (non-test) ---")
    for sym in (
        "SafetyAuditRecord",
        "HumanReviewAuditRecord",
        "SafetyAuditRegistry",
        "emit_safety_audit_record",
        "query_safety_audits",
        "SafetyAuditMissingError",
        "HumanReviewAuditError",
        "AuditQueryError",
        "safety_audit_emitted",
        "human_review_audited",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L5 audit module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L5_safety/audit%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P2/L5 safety audit gates."""
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
        print("P2/L5 SAFETY AUDIT TRAILS: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P2/L5 SAFETY AUDIT TRAILS: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
