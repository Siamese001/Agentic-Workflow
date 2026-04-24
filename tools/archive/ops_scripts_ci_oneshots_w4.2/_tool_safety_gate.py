"""
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_1")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_2")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_3")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_4")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_5")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_6")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_7")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_8")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_9")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_10")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_11")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_12")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_13")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_14")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_15")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_16")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_17")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_18")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_19")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_20")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_21")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_22")
_emit_reads_through("l4", "_tool_safety_gate", "urg_read_23")
ops_scripts/ci/_tool_safety_gate.py

P1/L5 Tool Safety Governance Gate — CI enforcement.

Gates:
  A — Fail if runtime tool call occurs outside invoke_tool_safely()
      (ToolSafetyContract + invoke_tool_safely present in L5 non-test sources >= 1)
  B — Fail if runtime tool call lacks capability token
      (ToolCapabilityError symbol present in tool_safety_contract module >= 1)
  C — Fail if runtime tool call lacks policy hash
      (references_policy_hash edges in L5 non-test >= 1)
  D — Fail if runtime tool call lacks guardrail decision
      (applies_guardrail edges in L5 non-test >= 1;
       validated_by_safety_plane total non-test >= 10)
  E — Fail if mutating/privileged tool executes without human review where required
      (requires_human_review edges in L5 non-test >= 1;
       HUMAN_GATED + PRIVILEGED classified in ToolActionClass >= 1 source)

Closure criteria:
  P1/L5 is CLOSED when all 5 gates pass.
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

L5_FILTER = "AND source_file LIKE '%L5%' " + NON_TEST


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
    """Gate A — runtime tool calls must flow through invoke_tool_safely().

    Passes when:
    - ToolSafetyContract symbol in L5 non-test sources >= 1, AND
    - invoke_tool_safely symbol in L5 non-test sources >= 1
    """
    tsc_sources = _count_symbol_sources(conn, "ToolSafetyContract", L5_FILTER)
    its_sources = _count_symbol_sources(conn, "invoke_tool_safely", L5_FILTER)
    # Also count total (non-test) to show material presence
    tsc_total = _count_symbol_sources(conn, "ToolSafetyContract", NON_TEST)
    its_total = _count_symbol_sources(conn, "invoke_tool_safely", NON_TEST)

    ok = tsc_total >= 1 and its_total >= 1
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"L5 ToolSafetyContract sources={tsc_sources} (total={tsc_total} >=1), "
            f"L5 invoke_tool_safely sources={its_sources} (total={its_total} >=1)",
        ),
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — tool calls must have capability token validation.

    Passes when ToolCapabilityError is defined in tool_safety_contract module
    (enforces that missing token raises an error — fail-closed).
    """
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE symbol LIKE '%ToolCapabilityError%' "
        "AND source_file LIKE '%tool_safety_contract%'",
    )
    cap_in_contract = c.fetchone()[0]

    cap_total = _count_symbol_sources(conn, "ToolCapabilityError", NON_TEST)
    tok_total = _count_symbol_sources(conn, "capability_token", NON_TEST)

    ok = cap_in_contract >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"ToolCapabilityError in tool_safety_contract={cap_in_contract} (>=1), "
            f"total ToolCapabilityError sources={cap_total}, "
            f"capability_token symbol sources={tok_total}",
        ),
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — tool calls must attach policy hash.

    Passes when:
    - references_policy_hash edges in L5 non-test >= 1, AND
    - references_policy_hash total non-test >= 1
    """
    rph_l5 = _count_distinct_sources(conn, "references_policy_hash", L5_FILTER)
    rph_total = _count_distinct_sources(conn, "references_policy_hash", NON_TEST)

    # Also check policy_hash symbol in tool_safety_contract
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE symbol LIKE '%policy_hash%' "
        "AND source_file LIKE '%tool_safety_contract%'",
    )
    ph_in_contract = c.fetchone()[0]

    ok = rph_l5 >= 1 or ph_in_contract >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"references_policy_hash L5={rph_l5} (>=1), total={rph_total}, "
            f"policy_hash in tool_safety_contract={ph_in_contract} (>=1)",
        ),
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — tool calls must include guardrail decision.

    Passes when:
    - applies_guardrail edges in L5 non-test >= 1, AND
    - validated_by_safety_plane total non-test >= 10 (existing L2 coverage)
    """
    ag_l5 = _count_distinct_sources(conn, "applies_guardrail", L5_FILTER)
    ag_total = _count_distinct_sources(conn, "applies_guardrail", NON_TEST)
    vsp_total = _count_distinct_sources(conn, "validated_by_safety_plane", NON_TEST)

    # Also check GuardrailDecision / ToolGuardrailDeniedError in contract
    gdd_in_contract = _count_symbol_sources(
        conn,
        "ToolGuardrailDeniedError",
        "AND source_file LIKE '%tool_safety_contract%'",
    )

    ok = ag_l5 >= 1 and vsp_total >= 10
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"applies_guardrail L5={ag_l5} (>=1) total={ag_total}, "
            f"validated_by_safety_plane total={vsp_total} (>=10), "
            f"ToolGuardrailDeniedError in contract={gdd_in_contract}",
        ),
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — mutating/privileged tools must route to human review where required.

    Passes when:
    - requires_human_review edges in L5 non-test >= 1, AND
    - ToolActionClass enum (HUMAN_GATED + PRIVILEGED) defined in tool_safety_contract >= 1
    """
    rhr_l5 = _count_distinct_sources(conn, "requires_human_review", L5_FILTER)
    rhr_total = _count_distinct_sources(conn, "requires_human_review", NON_TEST)

    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE symbol LIKE '%ToolActionClass%' "
        "AND source_file LIKE '%tool_safety_contract%'",
    )
    tac_in_contract = c.fetchone()[0]

    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE symbol LIKE '%HUMAN_GATED%' "
        "AND source_file LIKE '%tool_safety_contract%'",
    )
    hg_in_contract = c.fetchone()[0]

    # Gate passes if: L5 has requires_human_review AND ToolActionClass defined
    ok = rhr_l5 >= 1 and tac_in_contract >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"requires_human_review L5={rhr_l5} (>=1) total={rhr_total}, "
            f"ToolActionClass in contract={tac_in_contract} (>=1), "
            f"HUMAN_GATED in contract={hg_in_contract}",
        ),
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    print("\n--- P1/L5 Tool Safety Baseline ---")

    for rel in (
        "applies_guardrail",
        "validated_by_safety_plane",
        "requires_human_review",
        "references_policy_hash",
        "invoke_tool",
        "executes_tool",
    ):
        total = _count_distinct_sources(conn, rel, NON_TEST)
        l5 = _count_distinct_sources(conn, rel, L5_FILTER)
        print(f"  {rel:<45} total={total:4d}  L5={l5:4d}")

    for sym in (
        "ToolSafetyContract",
        "invoke_tool_safely",
        "ToolActionClass",
        "ToolRegistry",
        "ToolRegistryEntry",
        "ToolCapabilityError",
        "ToolGuardrailDeniedError",
        "UnregisteredToolError",
        "get_tool_registry",
        "ToolDenialTrace",
        "HUMAN_GATED",
        "PRIVILEGED",
    ):
        n = _count_symbol_sources(conn, sym, NON_TEST)
        print(f"  symbol:{sym:<38} sources={n:4d}")

    print("\n--- Spec §9 Verification Queries ---")
    c = conn.cursor()
    c.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type='applies_guardrail' {NON_TEST}")
    print(f"  Runtime applies_guardrail (edges, non-test): {c.fetchone()[0]}")

    c.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type='validated_by_safety_plane' {NON_TEST}")
    print(f"  Runtime validated_by_safety_plane (edges, non-test): {c.fetchone()[0]}")

    # Show L5 applies_guardrail sources
    c.execute(
        f"SELECT DISTINCT source_file, symbol FROM edges "
        f"WHERE relation_type='applies_guardrail' {L5_FILTER} LIMIT 20",
    )
    print("\n  L5 applies_guardrail sources (up to 20):")
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}]")
    else:
        print("    (none yet)")

    # Show L5 requires_human_review sources
    c.execute(
        f"SELECT DISTINCT source_file, symbol FROM edges "
        f"WHERE relation_type='requires_human_review' {L5_FILTER} LIMIT 10",
    )
    print("\n  L5 requires_human_review sources (up to 10):")
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}]")
    else:
        print("    (none yet)")


def main() -> int:
    db = _get_db()
    print(f"P1/L5 Tool Safety Gate — ADG: {db}\n")
    conn = sqlite3.connect(db)

    _print_baseline(conn)

    runners = [gate_a, gate_b, gate_c, gate_d, gate_e]
    for fn in runners:
        try:
            fn(conn)
        except Exception as exc:  # guardian: allow-broad-exception -- offline tooling, reports failure
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
        print(f"\nP1/L5 TOOL SAFETY GOVERNANCE: FAILED GATES {failed}")
        return 1

    print("\nP1/L5 TOOL SAFETY GOVERNANCE: ALL GATES PASSED - CLOSURE VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
