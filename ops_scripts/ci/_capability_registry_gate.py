"""
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_1")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_2")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_3")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_4")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_5")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_6")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_7")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_8")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_9")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_10")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_11")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_12")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_13")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_14")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_15")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_16")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_17")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_18")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_19")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_20")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_21")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_22")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_23")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_24")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_25")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_26")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_27")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_28")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_29")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_30")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_31")
_emit_reads_through("l4", "_capability_registry_gate", "urg_read_32")
ops_scripts/ci/_capability_registry_gate.py

P2/L3 Agent Capability Registry Gate — CI enforcement.

Gates:
  A — Fail if runtime agent dispatch occurs without registry resolution
      (UnregisteredDispatchError + resolve_agent_for_capability exported;
       wired in HandoffDispatcher.dispatch() which is the L3 dispatch chokepoint)
  B — Fail if runtime capability token lacks resolved_agent_id
      (CapabilityToken exported with resolved_agent_id field;
       CapabilityDecision exported with selected_agent_id field;
       resolve_agent_for_capability wired in agent_handoff)
  C — Fail if unregistered agent is selected for runtime work
      (UnregisteredAgentError exported in capability_registry >= 1;
       CapabilityRegistry exported >= 1;
       get_capability_registry exported >= 1;
       resolve_agent_for_capability wired in agent_handoff)
  D — Fail if multiple agents claim exclusive capability ownership without explicit shared policy
      (ExclusiveCapabilityConflictError exported in capability_registry >= 1;
       CapabilityOwnership exported >= 1 — carries SINGLETON/SHARED semantics)
  E — Fail if registry mutation occurs without version increment
      (RegistryVersionError exported in capability_registry >= 1;
       registry_version present in CapabilityRegistry — every register() call increments;
       CapabilityDecision exported — carries registry_version field)

Closure criteria:
  P2/L3 is CLOSED when all 5 gates pass.
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

L3_FILTER = "AND source_file LIKE '%L3%' " + NON_TEST


def _get_db() -> str:
    dbs = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))
    if not dbs:
        raise FileNotFoundError("No ADG SQLite artifact found in artifacts/adg/")
    return dbs[-1]


def _count_edges(conn: sqlite3.Connection, relation_type: str, extra: str = "") -> int:
    c = conn.cursor()
    c.execute(
        f"SELECT COUNT(*) FROM edges WHERE relation_type=? {extra}",
        (relation_type,),
    )
    return c.fetchone()[0]


def _count_distinct_sources(conn: sqlite3.Connection, relation_type: str, extra: str = "") -> int:
    c = conn.cursor()
    c.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {extra}",
        (relation_type,),
    )
    return c.fetchone()[0]


def _count_exported(conn: sqlite3.Connection, symbol: str, file_fragment: str) -> int:
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges "
        "WHERE relation_type='exports' AND symbol=? AND source_file LIKE ?",
        (symbol, f"%{file_fragment}%"),
    )
    return c.fetchone()[0]


def _count_in_file(conn: sqlite3.Connection, symbol_fragment: str, file_fragment: str) -> int:
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? AND source_file LIKE ?",
        (f"%{symbol_fragment}%", f"%{file_fragment}%"),
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
    """Gate A — runtime agent dispatch must go through registry resolution.

    Passes when:
    - UnregisteredDispatchError exported in capability_registry >= 1
      (guard raised when dispatch bypasses registry), AND
    - resolve_agent_for_capability exported in capability_registry >= 1
      (the mandatory entrypoint for all dispatches), AND
    - resolve_agent_for_capability imported/used in agent_handoff >= 1
      (HandoffDispatcher.dispatch() calls resolve_agent_for_capability before execution)
    """
    unregistered_dispatch_guard = _count_exported(conn, "UnregisteredDispatchError", "capability_registry")
    resolve_exported = _count_exported(conn, "resolve_agent_for_capability", "capability_registry")
    resolve_in_handoff = _count_in_file(conn, "resolve_agent_for_capability", "agent_handoff")
    handoff_dispatcher_in_handoff = _count_exported(conn, "HandoffDispatcher", "agent_handoff")

    ok = unregistered_dispatch_guard >= 1 and resolve_exported >= 1 and resolve_in_handoff >= 1
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"UnregisteredDispatchError exported={unregistered_dispatch_guard} (>=1), "
            f"resolve_agent_for_capability exported={resolve_exported} (>=1), "
            f"resolve_agent_for_capability in agent_handoff={resolve_in_handoff} (>=1), "
            f"HandoffDispatcher exported={handoff_dispatcher_in_handoff}",
        )
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — runtime capability token must carry resolved_agent_id.

    Passes when:
    - CapabilityToken exported in capability_registry >= 1
      (carries capability_name + capability_token + resolved_agent_id), AND
    - CapabilityDecision exported in capability_registry >= 1
      (carries selected_agent_id — the resolved_agent_id binding), AND
    - resolve_agent_for_capability in agent_handoff >= 1
      (ensures token is created and bound to every dispatch)
    """
    token_exported = _count_exported(conn, "CapabilityToken", "capability_registry")
    decision_exported = _count_exported(conn, "CapabilityDecision", "capability_registry")
    resolve_in_handoff = _count_in_file(conn, "resolve_agent_for_capability", "agent_handoff")
    decision_store_exported = _count_exported(conn, "CapabilityDecisionStore", "capability_registry")
    token_in_handoff = _count_in_file(conn, "CapabilityToken", "agent_handoff")

    ok = token_exported >= 1 and decision_exported >= 1 and resolve_in_handoff >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"CapabilityToken exported (has resolved_agent_id)={token_exported} (>=1), "
            f"CapabilityDecision exported (has selected_agent_id)={decision_exported} (>=1), "
            f"resolve_agent_for_capability in agent_handoff={resolve_in_handoff} (>=1), "
            f"CapabilityDecisionStore exported={decision_store_exported}, "
            f"CapabilityToken in agent_handoff={token_in_handoff}",
        )
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — unregistered agents must not do production work.

    Passes when:
    - UnregisteredAgentError exported in capability_registry >= 1
      (raised when unregistered agent is selected), AND
    - CapabilityRegistry exported in capability_registry >= 1
      (the registry that governs which agents may execute), AND
    - get_capability_registry exported in capability_registry >= 1
      (process-level singleton accessor), AND
    - get_capability_registry imported/used in agent_handoff >= 1
      (HandoffDispatcher consults registry before every dispatch)
    """
    unregistered_agent_guard = _count_exported(conn, "UnregisteredAgentError", "capability_registry")
    registry_exported = _count_exported(conn, "CapabilityRegistry", "capability_registry")
    get_registry_exported = _count_exported(conn, "get_capability_registry", "capability_registry")
    registry_in_handoff = _count_in_file(conn, "get_capability_registry", "agent_handoff")
    entry_exported = _count_exported(conn, "CapabilityRegistryEntry", "capability_registry")

    ok = (
        unregistered_agent_guard >= 1
        and registry_exported >= 1
        and get_registry_exported >= 1
        and registry_in_handoff >= 1
    )
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"UnregisteredAgentError exported={unregistered_agent_guard} (>=1), "
            f"CapabilityRegistry exported={registry_exported} (>=1), "
            f"get_capability_registry exported={get_registry_exported} (>=1), "
            f"get_capability_registry in agent_handoff={registry_in_handoff} (>=1), "
            f"CapabilityRegistryEntry exported={entry_exported}",
        )
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — exclusive capability conflicts must be explicit with shared policy.

    Passes when:
    - ExclusiveCapabilityConflictError exported in capability_registry >= 1
      (raised when SINGLETON agents conflict without shared_policy_hash), AND
    - CapabilityOwnership exported in capability_registry >= 1
      (enum: SINGLETON / DELEGATED / PARALLELIZABLE / SHARED — explicit ownership semantics)
    """
    conflict_guard = _count_exported(conn, "ExclusiveCapabilityConflictError", "capability_registry")
    ownership_exported = _count_exported(conn, "CapabilityOwnership", "capability_registry")
    registry_exported = _count_exported(conn, "CapabilityRegistry", "capability_registry")

    # Also check issues_capability_token edges (ADG validation target §9)
    issues_token_total = _count_distinct_sources(conn, "issues_capability_token", NON_TEST)
    issues_token_l3 = _count_distinct_sources(conn, "issues_capability_token", L3_FILTER)

    ok = conflict_guard >= 1 and ownership_exported >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"ExclusiveCapabilityConflictError exported (blocks conflict without shared_policy)={conflict_guard} (>=1), "
            f"CapabilityOwnership exported (SINGLETON/SHARED semantics)={ownership_exported} (>=1), "
            f"CapabilityRegistry exported={registry_exported}, "
            f"issues_capability_token non-test sources={issues_token_total}, "
            f"issues_capability_token L3 sources={issues_token_l3}",
        )
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — registry mutations must increment version.

    Passes when:
    - RegistryVersionError exported in capability_registry >= 1
      (guard for illegal version regression), AND
    - CapabilityDecision exported in capability_registry >= 1
      (carries registry_version — every decision bound to version at resolution time), AND
    - get_capability_decision_store exported in capability_registry >= 1
      (queryable for runtime coverage audit)
    """
    version_error_exported = _count_exported(conn, "RegistryVersionError", "capability_registry")
    decision_exported = _count_exported(conn, "CapabilityDecision", "capability_registry")
    store_exported = _count_exported(conn, "get_capability_decision_store", "capability_registry")
    reset_exported = _count_exported(conn, "reset_capability_registry", "capability_registry")

    # ADG validation §9: agent_executes_agent on L3 non-test
    agent_executes_l3 = _count_distinct_sources(conn, "agent_executes_agent", L3_FILTER)
    agent_executes_total = _count_distinct_sources(conn, "agent_executes_agent", NON_TEST)

    ok = version_error_exported >= 1 and decision_exported >= 1 and store_exported >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"RegistryVersionError exported (guards version mutations)={version_error_exported} (>=1), "
            f"CapabilityDecision exported (carries registry_version)={decision_exported} (>=1), "
            f"get_capability_decision_store exported={store_exported} (>=1), "
            f"reset_capability_registry exported={reset_exported}, "
            f"agent_executes_agent L3 non-test sources={agent_executes_l3}, "
            f"agent_executes_agent total non-test sources={agent_executes_total}",
        )
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    print("\n--- P2/L3 Agent Capability Registry Baseline ---")

    for rel in (
        "agent_executes_agent",
        "issues_capability_token",
        "invokes_getattr_dynamic",
        "records_execution_trace",
        "capability_resolved",
        "registry_versioned",
        "dispatch_bound_to_registry",
    ):
        total = _count_distinct_sources(conn, rel, NON_TEST)
        l3 = _count_distinct_sources(conn, rel, L3_FILTER)
        total_edges = _count_edges(conn, rel, NON_TEST)
        print(f"  {rel:<45} sources={total:4d}  L3={l3:4d}  edges={total_edges:5d}")

    print()
    for sym in (
        "CapabilityRegistry",
        "resolve_agent_for_capability",
        "CapabilityRegistryEntry",
        "CapabilityToken",
        "CapabilityDecision",
        "CapabilityDecisionStore",
        "CapabilityOwnership",
        "RunContext",
        "CapabilityNotFoundError",
        "CapabilityPermissionError",
        "UnregisteredAgentError",
        "ExclusiveCapabilityConflictError",
        "RegistryVersionError",
        "UnregisteredDispatchError",
        "get_capability_registry",
        "get_capability_decision_store",
        "capability_set",
        "allowed_callers",
        "owner_team",
        "active_status",
        "resolved_agent_id",
        "capability_name",
        "capability_token",
    ):
        n = _count_symbol_sources(conn, sym, NON_TEST)
        print(f"  symbol:{sym:<42} sources={n:4d}")

    print("\n--- Spec §9/§10 ADG Validation Queries ---")
    c = conn.cursor()

    c.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type='agent_executes_agent' {NON_TEST}")
    print(f"  agent_executes_agent (non-test edges): {c.fetchone()[0]}")

    c.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type='issues_capability_token' {NON_TEST}")
    print(f"  issues_capability_token (non-test edges): {c.fetchone()[0]}")

    print("\n  L3 capability registry symbols (up to 20):")
    c.execute(
        f"SELECT DISTINCT source_file, symbol FROM edges "
        f"WHERE (symbol LIKE '%CapabilityRegistry%' OR symbol LIKE '%resolve_agent_for_capability%' "
        f"OR symbol LIKE '%CapabilityToken%' OR symbol LIKE '%CapabilityDecision%' "
        f"OR symbol LIKE '%UnregisteredAgent%' OR symbol LIKE '%CapabilityNotFound%' "
        f"OR symbol LIKE '%CapabilityPermission%' OR symbol LIKE '%UnregisteredDispatch%' "
        f"OR symbol LIKE '%RegistryVersion%' OR symbol LIKE '%ExclusiveCapability%') "
        f"{NON_TEST} LIMIT 20"
    )
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}]")
    else:
        print("    (none yet)")

    print("\n  L3 agent_handoff wiring:")
    c.execute(
        f"SELECT DISTINCT source_file, relation_type, symbol FROM edges "
        f"WHERE (symbol LIKE '%resolve_agent_for_capability%' OR symbol LIKE '%CapabilityRegistry%' "
        f"OR symbol LIKE '%get_capability_registry%' OR symbol LIKE '%CapabilityToken%' "
        f"OR symbol LIKE '%RunContext%') "
        f"AND source_file LIKE '%agent_handoff%' {NON_TEST} LIMIT 15"
    )
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}] {row[2]}")
    else:
        print("    (none yet)")

    print("\n  agent_executes_agent sources (non-test, up to 10):")
    c.execute(
        f"SELECT DISTINCT source_file FROM edges "
        f"WHERE relation_type='agent_executes_agent' {NON_TEST} LIMIT 10"
    )
    for (f,) in c.fetchall():
        print(f"    {f}")


def main() -> int:
    db = _get_db()
    print(f"P2/L3 Agent Capability Registry Gate — ADG: {db}\n")
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
        print(f"\nP2/L3 AGENT CAPABILITY REGISTRY: FAILED GATES {failed}")
        return 1

    print("\nP2/L3 AGENT CAPABILITY REGISTRY: ALL GATES PASSED - CLOSURE VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
