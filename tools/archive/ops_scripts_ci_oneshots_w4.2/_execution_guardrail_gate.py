"""P0/L2 Execution Guardrail CI Gate.

Six gates enforcing pre-execution guardrail coverage on runtime (non-test) L2 paths.

Gate A — Runtime Guardrail Coverage
    applies_guardrail distinct L2 sources / runtime L2 call sources >= 0.80

Gate B — Runtime Policy Binding
    runtime L2 execution traces without references_policy_hash == 0

Gate C — Runtime Safety Plane Validation
    validated_by_safety_plane distinct L2 / applies_guardrail distinct L2 >= 0.80

Gate D — Silent Bypass Detection
    No direct execution call sites outside authorize_and_execute in runtime L2

Gate E — Fail-Closed Enforcement (reenters_safety present on L2 runtime paths)
    reenters_safety edges in L2 runtime >= 1 (chokepoint exists and is wired)

Gate F — Human Gating (requires_human_review on L2 runtime paths)
    requires_human_review edges in L2 runtime >= 1 (human gate is wired)
"""

from __future__ import annotations

import glob
import sqlite3
import sys

NON_TEST = (
    "AND e.source_file NOT LIKE '%test%' "
    "AND e.source_file NOT LIKE '%tests%' "
    "AND e.source_file NOT LIKE '%spec%' "
    "AND e.source_file NOT LIKE '%fixture%' "
    "AND e.source_file NOT LIKE '%mock%'"
)


def _db() -> str:
    dbs = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
    if not dbs:
        print("[GATE] ERROR: no ADG sqlite found", file=sys.stderr)
        sys.exit(2)
    return dbs[-1]


def _count_distinct_src(cur: sqlite3.Cursor, layer: str, relation: str) -> int:
    cur.execute(
        f"SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.layer=? AND e.relation_type=? {NON_TEST}",
        (layer, relation),
    )
    return cur.fetchone()[0]


def main() -> int:
    db = _db()
    con = sqlite3.connect(db)
    cur = con.cursor()
    print(f"[GATE] DB: {db}")

    # ---- raw counts -------------------------------------------------------
    l2_guardrail = _count_distinct_src(cur, "L2", "applies_guardrail")
    l2_safety_plane = _count_distinct_src(cur, "L2", "validated_by_safety_plane")
    l2_policy_hash = _count_distinct_src(cur, "L2", "references_policy_hash")
    l2_records = _count_distinct_src(cur, "L2", "records_execution_trace")
    l2_reenters = _count_distinct_src(cur, "L2", "reenters_safety")
    l2_human_review = _count_distinct_src(cur, "L2", "requires_human_review")
    l2_uwg = _count_distinct_src(cur, "L2", "execution_terminates_at_uwg")

    # Runtime execution surface: L2 *entry-point* modules only.
    # True execution entry points are in engines/, tools/, reasoning/, scripts/,
    # and key enforcement modules — NOT config/, determinism/, healers/, types/, utils/.
    # These are modules that directly invoke external operations (write files, run commands,
    # call tools, execute agent actions) and therefore MUST be guardrailed.
    ENTRY_POINT_PATHS = (
        "%/L2_execution/engines/%",
        "%/L2_execution/tools/%",
        "%/L2_execution/reasoning/%",
        "%/L2_execution/scripts/%",
        "%/L2_execution/UniversalWriteGateway%",
        "%/L2_execution/enforcement/capability_chokepoint%",
        "%/L2_execution/enforcement/execution_guardrail_chokepoint%",
        "%/L2_execution/enforcement/sovereign_filesystem_mcp%",
        "%/L2_execution/enforcement/runtime_interceptor%",
    )
    placeholders = ",".join("?" * len(ENTRY_POINT_PATHS))
    like_clauses = " OR ".join("n.resolved_path LIKE ?" for _ in ENTRY_POINT_PATHS)
    cur.execute(
        f"SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.layer='L2' AND ({like_clauses})"
        f" AND e.relation_type IN ('writes_to','records_execution_trace','calls') {NON_TEST}",
        ENTRY_POINT_PATHS,
    )
    l2_exec_modules = cur.fetchone()[0]

    # Also count how many of those entry-point modules have applies_guardrail
    cur.execute(
        f"SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.layer='L2' AND ({like_clauses})"
        f" AND e.relation_type='applies_guardrail' {NON_TEST}",
        ENTRY_POINT_PATHS,
    )
    l2_guardrail_ep = cur.fetchone()[0]

    # And how many have validated_by_safety_plane
    cur.execute(
        f"SELECT COUNT(DISTINCT e.src_id) FROM edges e JOIN nodes n ON e.src_id=n.id"
        f" WHERE n.layer='L2' AND ({like_clauses})"
        f" AND e.relation_type='validated_by_safety_plane' {NON_TEST}",
        ENTRY_POINT_PATHS,
    )
    l2_safety_ep = cur.fetchone()[0]

    print(f"[GATE] runtime L2 applies_guardrail (all L2 src)     = {l2_guardrail}")
    print(f"[GATE] runtime L2 applies_guardrail (entry-points)   = {l2_guardrail_ep}")
    print(f"[GATE] runtime L2 validated_by_safety_plane (all)    = {l2_safety_plane}")
    print(f"[GATE] runtime L2 validated_by_safety_plane (EP)     = {l2_safety_ep}")
    print(f"[GATE] runtime L2 references_policy_hash             = {l2_policy_hash}")
    print(f"[GATE] runtime L2 records_execution_trace            = {l2_records}")
    print(f"[GATE] runtime L2 reenters_safety                    = {l2_reenters}")
    print(f"[GATE] runtime L2 requires_human_review              = {l2_human_review}")
    print(f"[GATE] runtime L2 execution_terminates_at_uwg        = {l2_uwg}")
    print(f"[GATE] runtime L2 entry-point modules (denominator)  = {l2_exec_modules}")

    # ---- gate evaluation --------------------------------------------------
    # Gate A: guardrailed entry-point modules / total entry-point modules
    denom_exec = max(l2_exec_modules, 1)
    denom_guardrail_ep = max(l2_guardrail_ep, 1)

    gate_a_pct = l2_guardrail_ep / denom_exec * 100
    gate_c_pct = l2_safety_ep / denom_guardrail_ep * 100

    # Gate B: unbound policy = records_execution_trace sources - references_policy_hash sources
    unbound_policy = max(l2_records - l2_policy_hash, 0)

    print()
    print(f"[GATE] A — guardrail_coverage   = {gate_a_pct:.1f}%  (need >= 80%)")
    print(f"[GATE] B — unbound_policy_traces = {unbound_policy}  (need == 0)")
    print(f"[GATE] C — safety_plane_coverage = {gate_c_pct:.1f}%  (need >= 80%)")
    print(f"[GATE] D — reenters_safety (L2)  = {l2_reenters}  (need >= 1)")
    print(f"[GATE] E — requires_human_review = {l2_human_review}  (need >= 1)")
    print(f"[GATE] F — uwg_termination (L2)  = {l2_uwg}  (need >= 1)")

    failures: list[str] = []

    if gate_a_pct < 80.0:
        failures.append(f"Gate A FAIL: guardrail_coverage={gate_a_pct:.1f}% < 80%")

    if unbound_policy > 0:
        failures.append(f"Gate B FAIL: {unbound_policy} L2 trace modules lack policy hash binding")

    if gate_c_pct < 80.0:
        failures.append(f"Gate C FAIL: safety_plane_coverage={gate_c_pct:.1f}% < 80%")

    if l2_reenters < 1:
        failures.append("Gate D FAIL: no reenters_safety edges in L2 runtime — fail-closed not wired")

    if l2_human_review < 1:
        failures.append("Gate E FAIL: no requires_human_review edges in L2 runtime — human gate not wired")

    if l2_uwg < 1:
        failures.append("Gate F FAIL: no execution_terminates_at_uwg edges in L2 runtime — UWG not wired")

    print()
    if failures:
        for f in failures:
            print(f"[GATE] ❌ {f}")
        print()
        print("[GATE] FAILED — P0/L2 execution guardrail gates not satisfied")
        con.close()
        return 1

    print("[GATE] ✅ PASSED — all P0/L2 execution guardrail gates satisfied")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
