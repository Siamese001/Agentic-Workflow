#!/usr/bin/env python3
"""
P3/L5 Human Safety Escalation CI Gate

Enforces Gates A-E for human safety escalation closure:
- Gate A: Policy-designated human-gated action must have escalation record
- Gate B: Escalation must have reviewer queue assignment
- Gate C: Reviewer outcome must be present on completed escalated action
- Gate D: Escalated action must not auto-complete before review
- Gate E: Override must have explicit override flag and reason hash

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
    """Gate A — Policy-designated human-gated action must have escalation record.

    Passes when:
    - HumanEscalationError exported >= 1
      (exception for missing escalation record), AND
    - escalate_for_human_review exported >= 1
      (mandatory escalation entrypoint), AND
    - HumanEscalationRecord exported >= 1
      (escalation record with 11 required fields), AND
    - escalates_to_human function exported >= 1
      (ADG edge emitter for static scanner), AND
    - requires_human_review edges >= 1
      (policy-designated human-gated actions), AND
    - validated_by_safety_plane edges >= 1
      (policy outcomes triggering escalation)
    """
    escalation_error = _count_exported(conn, "HumanEscalationError", "human_escalation")
    escalate_function = _count_exported(conn, "escalate_for_human_review", "escalation_orchestrator")
    escalation_record = _count_exported(conn, "HumanEscalationRecord", "human_escalation")
    emitter_function = _count_exported(conn, "escalates_to_human", "escalation_orchestrator")
    review_edges = _count_distinct_sources(conn, "requires_human_review")
    safety_edges = _count_distinct_sources(conn, "validated_by_safety_plane")

    ok = (
        escalation_error >= 1
        and escalate_function >= 1
        and escalation_record >= 1
        and emitter_function >= 1
        and review_edges >= 1
        and safety_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"HumanEscalationError exported={escalation_error} (>=1), "
            f"escalate_for_human_review exported={escalate_function} (>=1), "
            f"HumanEscalationRecord exported={escalation_record} (>=1), "
            f"escalates_to_human exported={emitter_function} (>=1), "
            f"requires_human_review sources={review_edges} (>=1), "
            f"validated_by_safety_plane sources={safety_edges} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Escalation must have reviewer queue assignment.

    Passes when:
    - HumanEscalationRecord exported >= 1
      (escalation record with queue assignment field), AND
    - EscalationTriggerType exported >= 1
      (escalation trigger classification), AND
    - reviewer_queue_id exported >= 1
      (reviewer queue assignment field), AND
    - escalates_to_human function exported >= 1
      (ADG edge emitter with queue parameter), AND
    - requires_human_review edges >= 1
      (actions requiring queue assignment)
    """
    escalation_record = _count_exported(conn, "HumanEscalationRecord", "human_escalation")
    trigger_type = _count_exported(conn, "EscalationTriggerType", "human_escalation")
    queue_field = _count_exported(conn, "reviewer_queue_id", "human_escalation")
    emitter_function = _count_exported(conn, "escalates_to_human", "escalation_orchestrator")
    review_edges = _count_distinct_sources(conn, "requires_human_review")

    ok = (
        escalation_record >= 1
        and trigger_type >= 1
        and queue_field >= 1
        and emitter_function >= 1
        and review_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"HumanEscalationRecord exported={escalation_record} (>=1), "
            f"EscalationTriggerType exported={trigger_type} (>=1), "
            f"reviewer_queue_id exported={queue_field} (>=1), "
            f"escalates_to_human exported={emitter_function} (>=1), "
            f"requires_human_review sources={review_edges} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Reviewer outcome must be present on completed escalated action.

    Passes when:
    - HumanEscalationRecord exported >= 1
      (escalation record for outcome tracking), AND
    - ReviewerOutcome exported >= 1
      (reviewer outcome enumeration), AND
    - reviewer_outcome exported >= 1
      (reviewer outcome field), AND
    - reviewer_outcome_recorded function exported >= 1
      (ADG edge emitter for outcome recording), AND
    - escalates_to_human edges >= 1
      (escalated actions requiring outcomes)
    """
    escalation_record = _count_exported(conn, "HumanEscalationRecord", "human_escalation")
    outcome_enum = _count_exported(conn, "ReviewerOutcome", "human_escalation")
    outcome_field = _count_exported(conn, "reviewer_outcome", "human_escalation")
    outcome_emitter = _count_exported(conn, "reviewer_outcome_recorded", "escalation_orchestrator")
    escalation_edges = _count_distinct_sources(conn, "escalates_to_human")

    ok = (
        escalation_record >= 1
        and outcome_enum >= 1
        and outcome_field >= 1
        and outcome_emitter >= 1
        and escalation_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"HumanEscalationRecord exported={escalation_record} (>=1), "
            f"ReviewerOutcome exported={outcome_enum} (>=1), "
            f"reviewer_outcome exported={outcome_field} (>=1), "
            f"reviewer_outcome_recorded exported={outcome_emitter} (>=1), "
            f"escalates_to_human sources={escalation_edges} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Escalated action must not auto-complete before review.

    Passes when:
    - HumanEscalationRecord exported >= 1
      (escalation record for blocking tracking), AND
    - escalation_blocked function exported >= 1
      (ADG edge emitter for blocking), AND
    - DEFERRED status exported >= 1
      (deferred outcome for blocking), AND
    - ESCALATE_FURTHER status exported >= 1
      (further escalation for blocking), AND
    - escalates_to_human edges >= 1
      (escalated actions requiring blocking)
    """
    escalation_record = _count_exported(conn, "HumanEscalationRecord", "human_escalation")
    blocking_emitter = _count_exported(conn, "escalation_blocked", "escalation_orchestrator")
    deferred_status = _count_exported(conn, "DEFERRED", "human_escalation")
    further_status = _count_exported(conn, "ESCALATE_FURTHER", "human_escalation")
    escalation_edges = _count_distinct_sources(conn, "escalates_to_human")

    ok = (
        escalation_record >= 1
        and blocking_emitter >= 1
        and deferred_status >= 1
        and further_status >= 1
        and escalation_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"HumanEscalationRecord exported={escalation_record} (>=1), "
            f"escalation_blocked exported={blocking_emitter} (>=1), "
            f"DEFERRED exported={deferred_status} (>=1), "
            f"ESCALATE_FURTHER exported={further_status} (>=1), "
            f"escalates_to_human sources={escalation_edges} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Override must have explicit override flag and reason hash.

    Passes when:
    - HumanEscalationRecord exported >= 1
      (escalation record with override fields), AND
    - override_flag exported >= 1
      (override flag field), AND
    - final_decision_hash exported >= 1
      (override reason hash field), AND
    - override_executed function exported >= 1
      (ADG edge emitter for override), AND
    - requires_human_review edges >= 1
      (actions requiring override tracking)
    """
    escalation_record = _count_exported(conn, "HumanEscalationRecord", "human_escalation")
    override_field = _count_exported(conn, "override_flag", "human_escalation")
    hash_field = _count_exported(conn, "final_decision_hash", "human_escalation")
    override_emitter = _count_exported(conn, "override_executed", "escalation_orchestrator")
    review_edges = _count_distinct_sources(conn, "requires_human_review")

    ok = (
        escalation_record >= 1
        and override_field >= 1
        and hash_field >= 1
        and override_emitter >= 1
        and review_edges >= 1
    )
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"HumanEscalationRecord exported={escalation_record} (>=1), "
            f"override_flag exported={override_field} (>=1), "
            f"final_decision_hash exported={hash_field} (>=1), "
            f"override_executed exported={override_emitter} (>=1), "
            f"requires_human_review sources={review_edges} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P3/L5 human safety escalation baseline for verification."""
    print("\n--- P3/L5 Human Safety Escalation Baseline ---")

    for rel in (
        "requires_human_review",
        "escalates_to_human",
        "validated_by_safety_plane",
        "human_escalation_emitted",
        "escalation_recorded",
        "reviewer_outcome_recorded",
        "escalation_blocked",
        "override_executed",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L5 human escalation symbols (non-test) ---")
    for sym in (
        "HumanEscalationRecord",
        "escalate_for_human_review",
        "SafetyContext",
        "EscalationTriggerType",
        "ReviewerOutcome",
        "escalation_id",
        "run_id",
        "trace_id",
        "policy_hash",
        "action_class",
        "escalation_reason_hash",
        "escalation_trigger_type",
        "reviewer_queue_id",
        "reviewer_id",
        "reviewer_outcome",
        "override_flag",
        "final_decision_hash",
        "APPROVED",
        "DENIED",
        "MODIFIED",
        "ESCALATE_FURTHER",
        "DEFERRED",
        "HumanEscalationError",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L5 escalation module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L5_safety/escalation%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P3/L5 human safety escalation gates."""
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
        print("P3/L5 HUMAN SAFETY ESCALATION: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P3/L5 HUMAN SAFETY ESCALATION: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
