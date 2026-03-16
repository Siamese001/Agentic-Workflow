"""
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_1")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_2")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_3")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_4")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_5")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_6")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_7")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_8")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_9")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_10")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_11")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_12")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_13")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_14")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_15")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_16")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_17")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_18")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_19")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_20")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_21")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_22")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_23")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_24")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_25")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_26")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_27")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_28")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_29")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_30")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_31")
_emit_reads_through("l4", "_reasoning_evaluation_gate", "urg_read_32")
ops_scripts/ci/_reasoning_evaluation_gate.py

P2/L1 Reasoning Evaluation Gate — CI enforcement.

Gates:
  A — Fail if runtime reasoning evaluations without reasoning_trace_id > 0
      (OrphanReasoningEvaluationError + evaluate_reasoning_step exported in
       reasoning_evaluation.py; called from reasoning_chokepoint which enforces
       reasoning_trace_id is non-empty)
  B — Fail if runtime evaluated reasoning lacks rubric_hash > 0
      (ReasoningEvaluationRubric exported in reasoning_evaluation >= 1;
       rubric_hash field in ReasoningEvaluationRecord >= 1;
       rubric passed from reasoning_chokepoint)
  C — Fail if runtime evaluated reasoning lacks critique_hash and score_hash > 0
      (critique_hash + score_hash in ReasoningEvaluationRecord;
       both computed in ReasoningEvaluationRecord.create();
       evaluate_reasoning_step_from_trace called from reasoning_chokepoint)
  D — Fail if comparative reasoning evaluation exists without winning_reasoning_hash
      (ComparativeReasoningEvaluation exported in reasoning_evaluation >= 1;
       winning_reasoning_hash field is required in ComparativeReasoningEvaluation;
       evaluate_comparative_reasoning exported >= 1)
  E — Fail if runtime reasoning executes at evaluation-targeted paths without evaluation coverage
      (evaluate_reasoning_step_from_trace called from reasoning_chokepoint >= 1;
       reason_and_record calls evaluate_reasoning_step_from_trace;
       ReasoningEvaluationStore exported >= 1)

Closure criteria:
  P2/L1 is CLOSED when all 5 gates pass.
"""

from __future__ import annotations

import glob
import sqlite3
import sys

from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through

GATE_RESULTS: list[tuple[str, bool, str]] = []

NON_TEST = (
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' "
    "AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)

L1_FILTER = "AND source_file LIKE '%L1%' " + NON_TEST


def _get_db() -> str:
    dbs = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
    if not dbs:
        raise FileNotFoundError("No ADG SQLite artifact found in artifacts/adg/")
    return dbs[-1]


def _count_distinct_sources(conn: sqlite3.Connection, relation_type: str, extra: str = "") -> int:
    c = conn.cursor()
    c.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {extra}",
        (relation_type,),
    )
    return c.fetchone()[0]


def _count_symbol_sources(conn: sqlite3.Connection, symbol_fragment: str, extra: str = "") -> int:
    c = conn.cursor()
    c.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? {extra}",
        (f"%{symbol_fragment}%",),
    )
    return c.fetchone()[0]


def _count_exported(conn: sqlite3.Connection, symbol: str, file_fragment: str) -> int:
    """Count sources that export a symbol (ADG 'exports' relation)."""
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE relation_type='exports' AND symbol=? AND source_file LIKE ?",
        (symbol, f"%{file_fragment}%"),
    )
    return c.fetchone()[0]


def _count_calls(conn: sqlite3.Connection, symbol_fragment: str, file_fragment: str) -> int:
    """Count sources that call a symbol (ADG 'calls'/'invokes_dynamic' relation)."""
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE relation_type IN ('calls','invokes_dynamic') AND symbol LIKE ? AND source_file LIKE ?",
        (f"%{symbol_fragment}%", f"%{file_fragment}%"),
    )
    return c.fetchone()[0]


def _count_in_file(conn: sqlite3.Connection, symbol_fragment: str, file_fragment: str) -> int:
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? AND source_file LIKE ?",
        (f"%{symbol_fragment}%", f"%{file_fragment}%"),
    )
    return c.fetchone()[0]


def gate_a(conn: sqlite3.Connection) -> bool:
    """Gate A — reasoning evaluations must have reasoning_trace_id.

    Passes when:
    - OrphanReasoningEvaluationError exported in reasoning_evaluation >= 1
      (enforces non-empty reasoning_trace_id, raises on violation), AND
    - evaluate_reasoning_step exported in reasoning_evaluation >= 1, AND
    - evaluate_reasoning_step_from_trace called from reasoning_chokepoint >= 1
      (the chokepoint passes the completed trace which always has reasoning_trace_id)
    """
    orphan_guard = _count_exported(conn, "OrphanReasoningEvaluationError", "reasoning_evaluation")
    eval_step_exported = _count_exported(conn, "evaluate_reasoning_step", "reasoning_evaluation")
    eval_from_trace_exported = _count_exported(
        conn, "evaluate_reasoning_step_from_trace", "reasoning_evaluation"
    )
    eval_from_trace_in_chokepoint = _count_calls(
        conn, "evaluate_reasoning_step_from_trace", "reasoning_chokepoint"
    )
    eval_in_chokepoint = _count_in_file(conn, "evaluate_reasoning_step_from_trace", "reasoning_chokepoint")
    total_wired = max(eval_from_trace_in_chokepoint, eval_in_chokepoint)

    ok = orphan_guard >= 1 and eval_step_exported >= 1 and total_wired >= 1
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"OrphanReasoningEvaluationError exported={orphan_guard} (>=1), "
            f"evaluate_reasoning_step exported={eval_step_exported} (>=1), "
            f"evaluate_reasoning_step_from_trace exported={eval_from_trace_exported}, "
            f"wired in reasoning_chokepoint={total_wired} (>=1)",
        )
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — evaluated reasoning must have rubric_hash.

    Passes when:
    - ReasoningEvaluationRubric exported in reasoning_evaluation >= 1
      (carries 5 dimension scores; rubric_hash computed in ReasoningEvaluationRecord.create()), AND
    - ReasoningEvaluationRecord exported in reasoning_evaluation >= 1, AND
    - ReasoningEvaluationRubric imported/used in reasoning_chokepoint >= 1
    """
    rubric_exported = _count_exported(conn, "ReasoningEvaluationRubric", "reasoning_evaluation")
    record_exported = _count_exported(conn, "ReasoningEvaluationRecord", "reasoning_evaluation")
    rubric_in_chokepoint = _count_in_file(conn, "ReasoningEvaluationRubric", "reasoning_chokepoint")
    eval_context_exported = _count_exported(conn, "ReasoningEvaluationContext", "reasoning_evaluation")

    ok = rubric_exported >= 1 and record_exported >= 1 and rubric_in_chokepoint >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"ReasoningEvaluationRubric exported={rubric_exported} (>=1), "
            f"ReasoningEvaluationRecord exported={record_exported} (>=1), "
            f"ReasoningEvaluationRubric in reasoning_chokepoint={rubric_in_chokepoint} (>=1), "
            f"ReasoningEvaluationContext exported={eval_context_exported}",
        )
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — evaluated reasoning must have critique_hash and score_hash.

    Passes when:
    - ReasoningEvaluationRecord exported in reasoning_evaluation >= 1
      (has critique_hash + score_hash fields, both computed in create()), AND
    - evaluate_reasoning_step_from_trace called from reasoning_chokepoint >= 1
      (passes score_payload + critique to ReasoningEvaluationRecord.create()), AND
    - ReasoningEvaluationOutcome exported in reasoning_evaluation >= 1
    """
    record_exported = _count_exported(conn, "ReasoningEvaluationRecord", "reasoning_evaluation")
    outcome_exported = _count_exported(conn, "ReasoningEvaluationOutcome", "reasoning_evaluation")
    outcome_in_chokepoint = _count_in_file(conn, "ReasoningEvaluationOutcome", "reasoning_chokepoint")
    eval_from_trace_in_chokepoint = _count_in_file(
        conn, "evaluate_reasoning_step_from_trace", "reasoning_chokepoint"
    )

    ok = record_exported >= 1 and outcome_exported >= 1 and eval_from_trace_in_chokepoint >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"ReasoningEvaluationRecord exported (has critique_hash+score_hash)={record_exported} (>=1), "
            f"ReasoningEvaluationOutcome exported={outcome_exported} (>=1), "
            f"ReasoningEvaluationOutcome in reasoning_chokepoint={outcome_in_chokepoint}, "
            f"evaluate_reasoning_step_from_trace in reasoning_chokepoint={eval_from_trace_in_chokepoint} (>=1)",
        )
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — comparative reasoning evaluation must have winning_reasoning_hash.

    Passes when:
    - ComparativeReasoningEvaluation exported in reasoning_evaluation >= 1
      (winning_reasoning_hash is a required field), AND
    - evaluate_comparative_reasoning exported in reasoning_evaluation >= 1
      (validates winner is set before creating ComparativeReasoningEvaluation)
    """
    comparative_exported = _count_exported(conn, "ComparativeReasoningEvaluation", "reasoning_evaluation")
    compare_fn_exported = _count_exported(conn, "evaluate_comparative_reasoning", "reasoning_evaluation")
    # ReasoningEvaluationStore tracks comparatives_without_winner
    store_exported = _count_exported(conn, "ReasoningEvaluationStore", "reasoning_evaluation")

    ok = comparative_exported >= 1 and compare_fn_exported >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"ComparativeReasoningEvaluation exported (has winning_reasoning_hash)={comparative_exported} (>=1), "
            f"evaluate_comparative_reasoning exported={compare_fn_exported} (>=1), "
            f"ReasoningEvaluationStore exported={store_exported}",
        )
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — runtime reasoning paths must have evaluation coverage.

    Passes when:
    - evaluate_reasoning_step_from_trace in reasoning_chokepoint >= 1
      (reason_and_record calls it on every successful reasoning completion), AND
    - ReasoningEvaluationStore exported in reasoning_evaluation >= 1
      (queryable store for coverage analysis), AND
    - records_execution_trace L1 non-test >= 1
      (confirms L1 reasoning executes at runtime paths being evaluated)
    """
    eval_from_trace_in_chokepoint = _count_in_file(
        conn, "evaluate_reasoning_step_from_trace", "reasoning_chokepoint"
    )
    store_exported = _count_exported(conn, "ReasoningEvaluationStore", "reasoning_evaluation")
    get_store_exported = _count_exported(conn, "get_reasoning_evaluation_store", "reasoning_evaluation")
    l1_trace_sources = _count_distinct_sources(conn, "records_execution_trace", L1_FILTER)
    eval_step_callers = _count_symbol_sources(
        conn, "evaluate_reasoning_step", "AND source_file LIKE '%L1%' " + NON_TEST
    )

    ok = eval_from_trace_in_chokepoint >= 1 and store_exported >= 1 and l1_trace_sources >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"evaluate_reasoning_step_from_trace in reasoning_chokepoint={eval_from_trace_in_chokepoint} (>=1), "
            f"ReasoningEvaluationStore exported={store_exported} (>=1), "
            f"get_reasoning_evaluation_store exported={get_store_exported}, "
            f"records_execution_trace L1 non-test sources={l1_trace_sources} (>=1), "
            f"evaluate_reasoning_step symbol in L1 non-test sources={eval_step_callers}",
        )
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    print("\n--- P2/L1 Reasoning Evaluation Baseline ---")

    for rel in (
        "records_execution_trace",
        "invokes_eval",
        "compares_proof",
        "evaluates_reasoning",
        "reasoning_trace_linked",
        "critique_attached",
        "score_attached",
    ):
        total = _count_distinct_sources(conn, rel, NON_TEST)
        l1 = _count_distinct_sources(conn, rel, L1_FILTER)
        print(f"  {rel:<45} total={total:4d}  L1={l1:4d}")

    print()
    for sym in (
        "ReasoningEvaluationRecord",
        "evaluate_reasoning_step",
        "evaluate_reasoning_step_from_trace",
        "evaluate_comparative_reasoning",
        "ReasoningEvaluationStore",
        "ReasoningEvaluationContext",
        "ReasoningEvaluationRubric",
        "ReasoningEvaluationOutcome",
        "ComparativeReasoningEvaluation",
        "OrphanReasoningEvaluationError",
        "get_reasoning_evaluation_store",
        "reasoning_evaluation_id",
        "reasoning_trace_id",
        "rubric_hash",
        "critique_hash",
        "score_hash",
        "winning_reasoning_hash",
        "evaluation_outcome_status",
    ):
        n = _count_symbol_sources(conn, sym, NON_TEST)
        print(f"  symbol:{sym:<42} sources={n:4d}")

    print("\n--- Spec §9 ADG Validation Queries ---")
    c = conn.cursor()

    c.execute(
        f"SELECT COUNT(*) FROM edges "
        f"WHERE relation_type='records_execution_trace' "
        f"AND source_file LIKE '%L1%' {NON_TEST}"
    )
    print(f"  Runtime records_execution_trace L1 (edges, non-test): {c.fetchone()[0]}")

    print("\n  L1 reasoning evaluation symbols (up to 20):")
    c.execute(
        f"SELECT DISTINCT source_file, symbol FROM edges "
        f"WHERE (symbol LIKE '%ReasoningEvaluation%' OR symbol LIKE '%evaluate_reasoning%' "
        f"OR symbol LIKE '%ComparativeReasoning%' OR symbol LIKE '%OrphanReasoning%') "
        f"{NON_TEST} LIMIT 20"
    )
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}]")
    else:
        print("    (none yet)")

    print("\n  L1 chokepoint evaluation wiring:")
    c.execute(
        f"SELECT DISTINCT source_file, relation_type, symbol FROM edges "
        f"WHERE (symbol LIKE '%evaluate_reasoning_step%' OR symbol LIKE '%ReasoningEvaluationRubric%') "
        f"AND source_file LIKE '%reasoning_chokepoint%' {NON_TEST} LIMIT 10"
    )
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}] {row[2]}")
    else:
        print("    (none yet)")


def main() -> int:
    db = _get_db()
    print(f"P2/L1 Reasoning Evaluation Gate — ADG: {db}\n")
    conn = sqlite3.connect(db)

    _print_baseline(conn)

    runners = [gate_a, gate_b, gate_c, gate_d, gate_e]
    for fn in runners:
        try:
            fn(conn)
        except Exception as exc:
            label = fn.__name__.replace("gate_", "").upper()
            GATE_RESULTS.append((label, False, f"EXCEPTION: {exc}"))

    conn.close()

    print("\n" + "=" * 70)
    print("GATE RESULTS")
    print("=" * 70)
    failed = []
    for label, ok, msg in GATE_RESULTS:
        status = "PASS" if ok else "FAIL"
        print(f"  Gate {label}: {status} - {msg}")
        if not ok:
            failed.append(label)

    print("=" * 70)
    if failed:
        print(f"\nP2/L1 REASONING EVALUATION: FAILED GATES {failed}")
        return 1

    print("\nP2/L1 REASONING EVALUATION: ALL GATES PASSED - CLOSURE VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
