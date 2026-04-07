#!/usr/bin/env python3
"""
P4/L1 Reasoning Knowledge Base CI Gate

Enforces Gates A-E for reasoning knowledge base closure:
- Gate A: Pattern reused without validation
- Gate B: Reasoning pattern stored without evaluation score
- Gate C: Pattern version changes without version increment
- Gate D: Pattern lacks trace lineage
- Gate E: Reasoning pattern reused but outcome not recorded

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
    """Gate A — Pattern reused without validation.

    Passes when:
    - ReasoningKnowledgeRecord exported >= 1
      (reasoning knowledge record with 9 required fields), AND
    - capture_reasoning_pattern exported >= 1
      (mandatory pattern capture entrypoint), AND
    - reasoning_pattern_captured exported >= 1
      (ADG edge emitter for pattern capture), AND
    - pattern_validated exported >= 1
      (ADG edge emitter for pattern validation), AND
    - reuse_reasoning_pattern exported >= 1
      (reuse function with validation check), AND
    - validation_status exported >= 1
      (validation status field for validation tracking)
    """
    knowledge_record = _count_exported(conn, "ReasoningKnowledgeRecord", "reasoning_knowledge")
    capture_function = _count_exported(conn, "capture_reasoning_pattern", "knowledge_orchestrator")
    capture_emitter = _count_exported(conn, "reasoning_pattern_captured", "knowledge_orchestrator")
    validation_emitter = _count_exported(conn, "pattern_validated", "knowledge_orchestrator")
    reuse_function = _count_exported(conn, "reuse_reasoning_pattern", "knowledge_orchestrator")
    validation_status = _count_exported(conn, "validation_status", "reasoning_knowledge")

    ok = (
        knowledge_record >= 1
        and capture_function >= 1
        and capture_emitter >= 1
        and validation_emitter >= 1
        and reuse_function >= 1
        and validation_status >= 1
    )
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"ReasoningKnowledgeRecord exported={knowledge_record} (>=1), "
            f"capture_reasoning_pattern exported={capture_function} (>=1), "
            f"reasoning_pattern_captured exported={capture_emitter} (>=1), "
            f"pattern_validated exported={validation_emitter} (>=1), "
            f"reuse_reasoning_pattern exported={reuse_function} (>=1), "
            f"validation_status exported={validation_status} (>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — Reasoning pattern stored without evaluation score.

    Passes when:
    - ReasoningKnowledgeRecord exported >= 1
      (reasoning knowledge record for evaluation scoring), AND
    - outcome_quality_score exported >= 1
      (evaluation quality score field), AND
    - EvaluationResult exported >= 1
      (evaluation result context), AND
    - pattern_stored exported >= 1
      (ADG edge emitter for pattern storage), AND
    - capture_reasoning_pattern exported >= 1
      (capture function with evaluation scoring)
    """
    knowledge_record = _count_exported(conn, "ReasoningKnowledgeRecord", "reasoning_knowledge")
    quality_score = _count_exported(conn, "outcome_quality_score", "reasoning_knowledge")
    evaluation_result = _count_exported(conn, "EvaluationResult", "knowledge_orchestrator")
    storage_emitter = _count_exported(conn, "pattern_stored", "knowledge_orchestrator")
    capture_function = _count_exported(conn, "capture_reasoning_pattern", "knowledge_orchestrator")

    ok = (
        knowledge_record >= 1
        and quality_score >= 1
        and evaluation_result >= 1
        and storage_emitter >= 1
        and capture_function >= 1
    )
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"ReasoningKnowledgeRecord exported={knowledge_record} (>=1), "
            f"outcome_quality_score exported={quality_score} (>=1), "
            f"EvaluationResult exported={evaluation_result} (>=1), "
            f"pattern_stored exported={storage_emitter} (>=1), "
            f"capture_reasoning_pattern exported={capture_function} (>=1)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — Pattern version changes without version increment.

    Passes when:
    - ReasoningKnowledgeRecord exported >= 1
      (reasoning knowledge record for version tracking), AND
    - pattern_version exported >= 1
      (pattern version field for version tracking), AND
    - pattern_versioned exported >= 1
      (ADG edge emitter for versioning), AND
    - capture_reasoning_pattern exported >= 1
      (capture function with versioning), AND
    - reasoning_pattern_id exported >= 1
      (pattern ID for version tracking)
    """
    knowledge_record = _count_exported(conn, "ReasoningKnowledgeRecord", "reasoning_knowledge")
    pattern_version = _count_exported(conn, "pattern_version", "reasoning_knowledge")
    version_emitter = _count_exported(conn, "pattern_versioned", "knowledge_orchestrator")
    capture_function = _count_exported(conn, "capture_reasoning_pattern", "knowledge_orchestrator")
    pattern_id = _count_exported(conn, "reasoning_pattern_id", "reasoning_knowledge")

    ok = (
        knowledge_record >= 1
        and pattern_version >= 1
        and version_emitter >= 1
        and capture_function >= 1
        and pattern_id >= 1
    )
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"ReasoningKnowledgeRecord exported={knowledge_record} (>=1), "
            f"pattern_version exported={pattern_version} (>=1), "
            f"pattern_versioned exported={version_emitter} (>=1), "
            f"capture_reasoning_pattern exported={capture_function} (>=1), "
            f"reasoning_pattern_id exported={pattern_id} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — Pattern lacks trace lineage.

    Passes when:
    - ReasoningKnowledgeRecord exported >= 1
      (reasoning knowledge record for lineage), AND
    - originating_trace_id exported >= 1
      (originating trace ID for lineage), AND
    - records_execution_trace edges >= 1
      (execution trace linkage), AND
    - ReasoningTrace exported >= 1
      (reasoning trace context), AND
    - capture_reasoning_pattern exported >= 1
      (capture function with lineage tracking)
    """
    knowledge_record = _count_exported(conn, "ReasoningKnowledgeRecord", "reasoning_knowledge")
    trace_id = _count_exported(conn, "originating_trace_id", "reasoning_knowledge")
    trace_edges = _count_distinct_sources(conn, "records_execution_trace")
    reasoning_trace = _count_exported(conn, "ReasoningTrace", "knowledge_orchestrator")
    capture_function = _count_exported(conn, "capture_reasoning_pattern", "knowledge_orchestrator")

    ok = (
        knowledge_record >= 1
        and trace_id >= 1
        and trace_edges >= 1
        and reasoning_trace >= 1
        and capture_function >= 1
    )
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"ReasoningKnowledgeRecord exported={knowledge_record} (>=1), "
            f"originating_trace_id exported={trace_id} (>=1), "
            f"records_execution_trace sources={trace_edges} (>=1), "
            f"ReasoningTrace exported={reasoning_trace} (>=1), "
            f"capture_reasoning_pattern exported={capture_function} (>=1)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — Reasoning pattern reused but outcome not recorded.

    Passes when:
    - ReasoningKnowledgeRecord exported >= 1
      (reasoning knowledge record for reuse tracking), AND
    - reuse_count exported >= 1
      (reuse count field for tracking), AND
    - reuse_reasoning_pattern exported >= 1
      (reuse function with outcome recording), AND
    - reuse_outcome_recorded exported >= 1
      (ADG edge emitter for reuse outcome), AND
    - reasoning_pattern_reused exported >= 1
      (ADG edge emitter for pattern reuse)
    """
    knowledge_record = _count_exported(conn, "ReasoningKnowledgeRecord", "reasoning_knowledge")
    reuse_count = _count_exported(conn, "reuse_count", "reasoning_knowledge")
    reuse_function = _count_exported(conn, "reuse_reasoning_pattern", "knowledge_orchestrator")
    reuse_emitter = _count_exported(conn, "reuse_outcome_recorded", "knowledge_orchestrator")
    pattern_reuse_emitter = _count_exported(conn, "reasoning_pattern_reused", "knowledge_orchestrator")

    ok = (
        knowledge_record >= 1
        and reuse_count >= 1
        and reuse_function >= 1
        and reuse_emitter >= 1
        and pattern_reuse_emitter >= 1
    )
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"ReasoningKnowledgeRecord exported={knowledge_record} (>=1), "
            f"reuse_count exported={reuse_count} (>=1), "
            f"reuse_reasoning_pattern exported={reuse_function} (>=1), "
            f"reuse_outcome_recorded exported={reuse_emitter} (>=1), "
            f"reasoning_pattern_reused exported={pattern_reuse_emitter} (>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    """Print P4/L1 reasoning knowledge baseline for verification."""
    print("\n--- P4/L1 Reasoning Knowledge Baseline ---")

    for rel in (
        "invokes_eval",
        "records_execution_trace",
        "reasoning_pattern_captured",
        "reasoning_pattern_reused",
        "pattern_validated",
        "pattern_versioned",
        "pattern_stored",
        "reuse_outcome_recorded",
    ):
        total = _count_distinct_sources(conn, rel)
        print(f"  {rel:<45} total={total:4d}")

    print("\n--- Key L1 reasoning knowledge symbols (non-test) ---")
    for sym in (
        "ReasoningKnowledgeRecord",
        "capture_reasoning_pattern",
        "ReasoningKnowledgeError",
        "reasoning_pattern_id",
        "originating_trace_id",
        "reasoning_goal_hash",
        "reasoning_context_hash",
        "reasoning_steps_hash",
        "outcome_quality_score",
        "reuse_count",
        "pattern_version",
        "validation_status",
        "ReasoningTrace",
        "EvaluationResult",
        "ReasoningContext",
    ):
        count = _count_exported(conn, sym)
        print(f"  symbol:{sym:<40} sources={count:4d}")

    print("\n--- L1 reasoning knowledge module exports (non-test) ---")
    cursor = conn.execute(
        f"""
        SELECT DISTINCT source_file, symbol
        FROM edges
        WHERE source_file LIKE '%L1_cognition/knowledge%' {NON_TEST}
        ORDER BY source_file, symbol
        LIMIT 30
        """,
    )
    for source, symbol in cursor.fetchall():
        print(f"  {source:<60} [{symbol}]")


def main() -> int:
    """Run P4/L1 reasoning knowledge gates."""
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
        print("P4/L1 REASONING KNOWLEDGE: ALL GATES PASSED - CLOSURE VERIFIED")
    else:
        failed_gates = [gate for gate, ok, _ in GATE_RESULTS if not ok]
        print(f"P4/L1 REASONING KNOWLEDGE: FAILED GATES {failed_gates}")
    print("=" * 70)

    conn.close()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
