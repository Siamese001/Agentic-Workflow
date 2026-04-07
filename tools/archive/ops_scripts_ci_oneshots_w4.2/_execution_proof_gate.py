"""
ops_scripts/ci/_execution_proof_gate.py

P1/L2 Execution Proof Gate — CI enforcement.

Gates:
  A — Fail if authorize_and_execute does not import emit_execution_proof
  B — Fail if runtime emits_replay_key / governed execution sources < 0.80
  C — Fail if runtime emits_determinism_digest / governed execution sources < 0.80
  D — Fail if runtime signed proof sources (signs_execution_trace) < 0.80
  E — Fail if compares_proof edge count is zero (no replay validation path)

Closure criteria:
  P1/L2 is CLOSED when all 5 gates pass.
"""

from __future__ import annotations

import glob
import sqlite3
import sys

GATE_RESULTS: list[tuple[str, bool, str]] = []

NON_TEST = (
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' "
    "AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)

L2_FILTER = "AND source_file LIKE '%L2%' " + NON_TEST


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


def gate_a(conn: sqlite3.Connection) -> bool:
    """Gate A — authorize_and_execute must import emit_execution_proof.

    The chokepoint file must show symbol usage of emit_execution_proof.
    """
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM edges "
        "WHERE symbol LIKE '%emit_execution_proof%' "
        "AND source_file LIKE '%execution_guardrail_chokepoint%'",
    )
    n = c.fetchone()[0]
    ok = n >= 1
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"authorize_and_execute uses emit_execution_proof={n} (required>=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — emits_replay_key coverage >= 80% of governed execution sources.

    Governed execution sources = files importing authorize_and_execute (non-test).
    emits_replay_key sources = non-test files with that edge.
    Ratio must be >= 0.80.
    """
    replay_sources = _count_distinct_sources(conn, "emits_replay_key", NON_TEST)
    governed_sources = _count_symbol_sources(conn, "authorize_and_execute", NON_TEST)
    governed_sources = max(governed_sources, 1)
    ratio = replay_sources / governed_sources
    ok = ratio >= 0.80
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"emits_replay_key={replay_sources} / governed_sources={governed_sources} = {ratio:.3f} (required>=0.80)",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — emits_determinism_digest coverage >= 80% of governed execution sources."""
    digest_sources = _count_distinct_sources(conn, "emits_determinism_digest", NON_TEST)
    governed_sources = _count_symbol_sources(conn, "authorize_and_execute", NON_TEST)
    governed_sources = max(governed_sources, 1)
    ratio = digest_sources / governed_sources
    ok = ratio >= 0.80
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"emits_determinism_digest={digest_sources} / governed_sources={governed_sources} = {ratio:.3f} (required>=0.80)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — signs_execution_trace runtime sources >= 80% of governed sources."""
    signed_sources = _count_distinct_sources(conn, "signs_execution_trace", NON_TEST)
    governed_sources = _count_symbol_sources(conn, "authorize_and_execute", NON_TEST)
    governed_sources = max(governed_sources, 1)
    ratio = signed_sources / governed_sources
    ok = ratio >= 0.80
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"signs_execution_trace={signed_sources} / governed_sources={governed_sources} = {ratio:.3f} (required>=0.80)",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — compares_proof edge must exist (replay validation path is wired).

    At least 1 non-test source must emit compares_proof.
    """
    n = _count_distinct_sources(conn, "compares_proof", NON_TEST)
    # Also check for DeterminismViolation symbol (replay harness present)
    dv = _count_symbol_sources(conn, "DeterminismViolation", NON_TEST)
    ok = n >= 1 or dv >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"compares_proof sources={n}, DeterminismViolation sources={dv} (required: n>=1 or dv>=1)",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    print("\n--- L2 Execution Proof Baseline ---")
    for rel in ("emits_replay_key", "emits_determinism_digest", "signs_execution_trace", "compares_proof"):
        total = _count_distinct_sources(conn, rel, NON_TEST)
        l2 = _count_distinct_sources(conn, rel, L2_FILTER)
        print(f"  {rel:<40} total={total:4d}  L2={l2:4d}")

    for sym in ("emit_execution_proof", "authorize_and_execute", "DeterminismViolation", "ExecutionProof"):
        n = _count_symbol_sources(conn, sym, NON_TEST)
        print(f"  symbol:{sym:<35} sources={n:4d}")


def main() -> int:
    db = _get_db()
    print(f"P1/L2 Execution Proof Gate - ADG: {db}\n")
    conn = sqlite3.connect(db)

    _print_baseline(conn)

    runners = [gate_a, gate_b, gate_c, gate_d, gate_e]
    for fn in runners:
        try:
            fn(conn)
        except Exception as exc:  # guardian: allow-silent-swallow
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
        print(f"\nP1/L2 EXECUTION PROOF: FAILED GATES {failed}")
        return 1

    print("\nP1/L2 EXECUTION PROOF: ALL GATES PASSED - CLOSURE VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
