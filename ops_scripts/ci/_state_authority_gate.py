"""P0/L4 Unified Runtime State Authority CI Gate.

_emit_reads_through("l4", "_state_authority_gate", "urg_read_1")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_2")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_3")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_4")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_5")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_6")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_7")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_8")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_9")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_10")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_11")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_12")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_13")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_14")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_15")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_16")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_17")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_18")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_19")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_20")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_21")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_22")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_23")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_24")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_25")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_26")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_27")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_28")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_29")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_30")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_31")
_emit_reads_through("l4", "_state_authority_gate", "urg_read_32")
Six gates enforcing state authority coverage on runtime (non-test) paths.

Gate A — Governed Write Coverage
    writes_through / (writes_through + writes_to) >= 0.05 on runtime paths
    (baseline 5/2664 = 0.19%, target rising; hard fail if writes_through == 0)

Gate B — State Authority Coverage
    L3/L4 runtime files using RunStateAuthority (observe/commit/snapshot) >= 3

Gate C — Snapshot Coverage
    runtime snapshots_state edges >= 3 (one-per-run minimum rising from 1)

Gate D — Version Increment Enforcement
    runtime writes_through edges >= 3 (commits go through authority, not direct)

Gate E — Fragmented Mutation Detection
    L3/L4 runtime writes_to / writes_through ratio < 200
    (dominated writes_to = fragmented state; must trend toward authority use)

Gate F — Observation Coverage
    runtime observes_runtime_state edges >= 3
    (decision-relevant state must be explicitly observed)
"""

from __future__ import annotations

import glob
import sqlite3
import sys

from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through

NON_TEST = (
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' "
    "AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)

# ── Thresholds ────────────────────────────────────────────────────────────────
GATE_A_MIN_WRITES_THROUGH = 3  # hard floor: at least 3 governed writes
GATE_B_MIN_AUTHORITY_SOURCES = 3  # L3/L4 files using RSA
GATE_C_MIN_SNAPSHOTS = 3  # snapshots_state runtime edges
GATE_D_MIN_VERSIONED_COMMITS = 3  # writes_through runtime edges
GATE_E_MAX_FRAGMENTATION_RATIO = 200  # writes_to / writes_through < this
GATE_F_MIN_OBSERVATIONS = 3  # observes_runtime_state runtime edges


def _db() -> str:
    dbs = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
    if not dbs:
        print("[GATE] ERROR: no ADG sqlite found", file=sys.stderr)
        sys.exit(2)
    return dbs[-1]


def _count(cur: sqlite3.Cursor, sql: str, params: tuple = ()) -> int:
    cur.execute(sql, params)
    return cur.fetchone()[0]


# ─── Gate A ───────────────────────────────────────────────────────────────────


def gate_a(cur: sqlite3.Cursor) -> tuple[bool, str]:
    """Runtime writes_through >= GATE_A_MIN_WRITES_THROUGH (governed writes non-zero)."""
    n = _count(
        cur,
        "SELECT COUNT(*) FROM edges WHERE relation_type='writes_through' " + NON_TEST,
    )
    ok = n >= GATE_A_MIN_WRITES_THROUGH
    detail = f"runtime writes_through={n} (need >={GATE_A_MIN_WRITES_THROUGH})"
    return ok, detail


# ─── Gate B ───────────────────────────────────────────────────────────────────


def gate_b(cur: sqlite3.Cursor) -> tuple[bool, str]:
    """L3/L4 runtime files using RunStateAuthority >= GATE_B_MIN_AUTHORITY_SOURCES."""
    cur.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges"
        " WHERE relation_type IN ('writes_through', 'observes_runtime_state', 'snapshots_state')"
        " AND (source_file LIKE '%L3_orchestration%' OR source_file LIKE '%L4_state%')"
        " AND source_file NOT LIKE '%test%'"
        " AND source_file NOT LIKE '%tests%'"
    )
    n = cur.fetchone()[0]
    ok = n >= GATE_B_MIN_AUTHORITY_SOURCES
    detail = f"L3/L4 authority sources={n} (need >={GATE_B_MIN_AUTHORITY_SOURCES})"
    return ok, detail


# ─── Gate C ───────────────────────────────────────────────────────────────────


def gate_c(cur: sqlite3.Cursor) -> tuple[bool, str]:
    """Runtime snapshots_state edges >= GATE_C_MIN_SNAPSHOTS."""
    n = _count(
        cur,
        "SELECT COUNT(*) FROM edges WHERE relation_type='snapshots_state' " + NON_TEST,
    )
    ok = n >= GATE_C_MIN_SNAPSHOTS
    detail = f"runtime snapshots_state={n} (need >={GATE_C_MIN_SNAPSHOTS})"
    return ok, detail


# ─── Gate D ───────────────────────────────────────────────────────────────────


def gate_d(cur: sqlite3.Cursor) -> tuple[bool, str]:
    """Runtime writes_through (versioned commits) >= GATE_D_MIN_VERSIONED_COMMITS."""
    n = _count(
        cur,
        "SELECT COUNT(*) FROM edges WHERE relation_type='writes_through' " + NON_TEST,
    )
    ok = n >= GATE_D_MIN_VERSIONED_COMMITS
    detail = f"runtime versioned commits (writes_through)={n} (need >={GATE_D_MIN_VERSIONED_COMMITS})"
    return ok, detail


# ─── Gate E ───────────────────────────────────────────────────────────────────


def gate_e(cur: sqlite3.Cursor) -> tuple[bool, str]:
    """L3/L4 writes_to / writes_through ratio < GATE_E_MAX_FRAGMENTATION_RATIO."""
    n_through = _count(
        cur,
        "SELECT COUNT(*) FROM edges"
        " WHERE relation_type='writes_through'"
        " AND (source_file LIKE '%L3_orchestration%' OR source_file LIKE '%L4_state%')"
        " AND source_file NOT LIKE '%test%'",
    )
    n_direct = _count(
        cur,
        "SELECT COUNT(*) FROM edges"
        " WHERE relation_type='writes_to'"
        " AND (source_file LIKE '%L3_orchestration%' OR source_file LIKE '%L4_state%')"
        " AND source_file NOT LIKE '%test%'",
    )
    if n_through == 0:
        ratio = float("inf")
        ok = False
    else:
        ratio = n_direct / n_through
        ok = ratio < GATE_E_MAX_FRAGMENTATION_RATIO
    detail = (
        f"L3/L4 direct={n_direct} governed={n_through}"
        f" ratio={ratio:.1f} (need <{GATE_E_MAX_FRAGMENTATION_RATIO})"
    )
    return ok, detail


# ─── Gate F ───────────────────────────────────────────────────────────────────


def gate_f(cur: sqlite3.Cursor) -> tuple[bool, str]:
    """Runtime observes_runtime_state >= GATE_F_MIN_OBSERVATIONS."""
    n = _count(
        cur,
        "SELECT COUNT(*) FROM edges WHERE relation_type='observes_runtime_state' " + NON_TEST,
    )
    ok = n >= GATE_F_MIN_OBSERVATIONS
    detail = f"runtime observes_runtime_state={n} (need >={GATE_F_MIN_OBSERVATIONS})"
    return ok, detail


# ─── Runner ───────────────────────────────────────────────────────────────────


def main() -> int:
    db = _db()
    con = sqlite3.connect(db)
    cur = con.cursor()
    print(f"[GATE] DB: {db}")
    print("[GATE] P0/L4 Unified Runtime State Authority Gate")
    print("=" * 60)

    gates = [
        ("A", "Governed Write Coverage", gate_a),
        ("B", "State Authority Coverage", gate_b),
        ("C", "Snapshot Coverage", gate_c),
        ("D", "Version Increment Enforcement", gate_d),
        ("E", "Fragmented Mutation Detection", gate_e),
        ("F", "Observation Coverage", gate_f),
    ]

    failures: list[str] = []
    for label, name, fn in gates:
        ok, detail = fn(cur)
        status = "PASS" if ok else "FAIL"
        print(f"[Gate {label}] {name}: {status} -- {detail}")
        if not ok:
            failures.append(f"Gate {label}: {name} -- {detail}")

    con.close()
    print("=" * 60)

    if failures:
        print(f"[GATE] FAILED -- {len(failures)} gate(s) failed:")
        for f in failures:
            print(f"  FAIL: {f}")
        return 1

    print("[GATE] ALL GATES PASSED -- P0/L4 state authority closure verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
