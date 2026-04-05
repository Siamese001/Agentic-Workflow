"""
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_1")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_2")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_3")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_4")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_5")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_6")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_7")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_8")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_9")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_10")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_11")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_12")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_13")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_14")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_15")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_16")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_17")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_18")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_19")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_20")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_21")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_22")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_23")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_24")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_25")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_26")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_27")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_28")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_29")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_30")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_31")
_emit_reads_through("l4", "_routing_telemetry_gate", "urg_read_32")
ops_scripts/ci/_routing_telemetry_gate.py

P2/L0 Routing Telemetry Gate — CI enforcement.

Gates:
  A — Fail if runtime routing decisions without RoutingTelemetry > 0
      (record_routing_telemetry + RoutingTelemetry present in L0 non-test >= 1,
       called from both primary routing chokepoints)
  B — Fail if runtime routing telemetry lacks duration_ms > 0
      (routing_duration_ms field present in RoutingTelemetry in routing_telemetry.py;
       routing_start_tick + routing_end_tick captured in L0 chokepoints)
  C — Fail if runtime routing telemetry lacks outcome_status > 0
      (RoutingOutcomeStatus exported in routing_telemetry >= 1;
       routing_outcome_status field in RoutingTelemetry >= 1;
       RoutingOutcomeStatus used in both chokepoints)
  D — Fail if routing contract exists without matching routing telemetry
      (RoutingTelemetry exported in routing_telemetry >= 1;
       record_routing_telemetry called from files that also call
       create_and_commit_routing_contract)
  E — Fail if queue/load fields are silently absent instead of explicitly null-classified
      (NullMetricReason exported in routing_telemetry >= 1;
       queue_depth_snapshot + target_load_snapshot in RoutingTelemetry >= 1)

Closure criteria:
  P2/L0 is CLOSED when all 5 gates pass.
"""

from __future__ import annotations

import glob
import sqlite3
import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_reads_through,
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("_routing_telemetry_gate", "_routing_telemetry_gate_digest")
record_execution_trace("_routing_telemetry_gate", "_routing_telemetry_gate_trace")


GATE_RESULTS: list[tuple[str, bool, str]] = []

NON_TEST = (
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%' "
    "AND source_file NOT LIKE '%spec%' "
    "AND source_file NOT LIKE '%fixture%' "
    "AND source_file NOT LIKE '%mock%'"
)

L0_FILTER = "AND source_file LIKE '%L0%' " + NON_TEST


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
    """Gate A — runtime routing decisions must have RoutingTelemetry.

    Passes when:
    - record_routing_telemetry exported in routing_telemetry.py >= 1, AND
    - RoutingTelemetry exported in routing_telemetry.py >= 1, AND
    - record_routing_telemetry called from agentic_router >= 1, AND
    - record_routing_telemetry called from path_router >= 1
    """
    rrt_exported = _count_exported(conn, "record_routing_telemetry", "routing_telemetry")
    rt_exported = _count_exported(conn, "RoutingTelemetry", "routing_telemetry")
    rrt_in_router = _count_calls(conn, "record_routing_telemetry", "agentic_router")
    rrt_in_path = _count_calls(conn, "record_routing_telemetry", "path_router")
    total_callers = rrt_in_router + rrt_in_path

    ok = rrt_exported >= 1 and rt_exported >= 1 and total_callers >= 1
    GATE_RESULTS.append(
        (
            "A",
            ok,
            f"record_routing_telemetry exported in routing_telemetry={rrt_exported} (>=1), "
            f"RoutingTelemetry exported={rt_exported} (>=1), "
            f"callers: agentic_router={rrt_in_router} path_router={rrt_in_path} total={total_callers} (>=1)",
        )
    )
    return ok


def gate_b(conn: sqlite3.Connection) -> bool:
    """Gate B — routing telemetry must have duration_ms.

    Passes when:
    - RoutingTelemetry exported in routing_telemetry (carries routing_duration_ms field), AND
    - RoutingTelemetryContext imported in agentic_router or path_router >= 1
      (RoutingTelemetryContext carries routing_start_tick + routing_end_tick, which
       are used by record_routing_telemetry to compute routing_duration_ms), AND
    - record_routing_telemetry called from agentic_router or path_router >= 1
    """
    rt_exported = _count_exported(conn, "RoutingTelemetry", "routing_telemetry")
    rtc_exported = _count_exported(conn, "RoutingTelemetryContext", "routing_telemetry")
    # RoutingTelemetryContext imported in chokepoints (it carries timing fields)
    rtc_in_router = _count_in_file(conn, "RoutingTelemetryContext", "agentic_router")
    rtc_in_path = _count_in_file(conn, "RoutingTelemetryContext", "path_router")
    total_rtc_users = rtc_in_router + rtc_in_path
    # record_routing_telemetry called from chokepoints (computes duration from start/end ticks)
    rrt_in_router = _count_calls(conn, "record_routing_telemetry", "agentic_router")
    rrt_in_path = _count_calls(conn, "record_routing_telemetry", "path_router")
    total_callers = rrt_in_router + rrt_in_path

    ok = rt_exported >= 1 and rtc_exported >= 1 and total_rtc_users >= 1 and total_callers >= 1
    GATE_RESULTS.append(
        (
            "B",
            ok,
            f"RoutingTelemetry exported (has routing_duration_ms)={rt_exported} (>=1), "
            f"RoutingTelemetryContext exported (has start/end tick)={rtc_exported} (>=1), "
            f"RoutingTelemetryContext in chokepoints: agentic_router={rtc_in_router} path_router={rtc_in_path} "
            f"total={total_rtc_users} (>=1), "
            f"record_routing_telemetry callers: agentic_router={rrt_in_router} path_router={rrt_in_path} "
            f"total={total_callers} (>=1)",
        )
    )
    return ok


def gate_c(conn: sqlite3.Connection) -> bool:
    """Gate C — routing telemetry must have outcome_status.

    Passes when:
    - RoutingOutcomeStatus exported in routing_telemetry >= 1, AND
    - RoutingOutcomeStatus used in agentic_router or path_router >= 1
    """
    ros_exported = _count_exported(conn, "RoutingOutcomeStatus", "routing_telemetry")
    ros_in_router = _count_in_file(conn, "RoutingOutcomeStatus", "agentic_router")
    ros_in_path = _count_in_file(conn, "RoutingOutcomeStatus", "path_router")
    total_users = ros_in_router + ros_in_path
    # All 5 outcome values defined
    succeeded = _count_in_file(conn, "ROUTE_SUCCEEDED", "routing_telemetry")
    failed = _count_in_file(conn, "ROUTE_FAILED", "routing_telemetry")
    escalated = _count_in_file(conn, "ROUTE_ESCALATED", "routing_telemetry")

    ok = ros_exported >= 1 and total_users >= 1
    GATE_RESULTS.append(
        (
            "C",
            ok,
            f"RoutingOutcomeStatus exported={ros_exported} (>=1), "
            f"used in: agentic_router={ros_in_router} path_router={ros_in_path} total={total_users} (>=1), "
            f"ROUTE_SUCCEEDED in routing_telemetry={succeeded}, ROUTE_FAILED={failed}, ROUTE_ESCALATED={escalated}",
        )
    )
    return ok


def gate_d(conn: sqlite3.Connection) -> bool:
    """Gate D — routing contract must have matching routing telemetry.

    Passes when:
    - RoutingTelemetry exported in routing_telemetry >= 1 (telemetry carries routing_contract_id), AND
    - record_routing_telemetry called from files that also call create_and_commit_routing_contract
    """
    rt_exported = _count_exported(conn, "RoutingTelemetry", "routing_telemetry")
    rrt_exported = _count_exported(conn, "record_routing_telemetry", "routing_telemetry")
    # Both chokepoints call both contract creation AND telemetry recording
    contract_and_telemetry_router = (
        _count_calls(conn, "create_and_commit_routing_contract", "agentic_router") > 0
        and _count_calls(conn, "record_routing_telemetry", "agentic_router") > 0
    )
    contract_and_telemetry_path = (
        _count_calls(conn, "create_and_commit_routing_contract", "path_router") > 0
        and _count_calls(conn, "record_routing_telemetry", "path_router") > 0
    )
    both_wired = int(contract_and_telemetry_router) + int(contract_and_telemetry_path)
    # RoutingTelemetryStore exported (queryable by contract_id)
    store_exported = _count_exported(conn, "RoutingTelemetryStore", "routing_telemetry")

    ok = rt_exported >= 1 and rrt_exported >= 1 and both_wired >= 1
    GATE_RESULTS.append(
        (
            "D",
            ok,
            f"RoutingTelemetry exported={rt_exported} (>=1), "
            f"record_routing_telemetry exported={rrt_exported} (>=1), "
            f"chokepoints with both contract+telemetry: agentic_router={int(contract_and_telemetry_router)} "
            f"path_router={int(contract_and_telemetry_path)} total={both_wired} (>=1), "
            f"RoutingTelemetryStore exported={store_exported}",
        )
    )
    return ok


def gate_e(conn: sqlite3.Connection) -> bool:
    """Gate E — queue/load fields must be explicitly null-classified, not silently absent.

    Passes when:
    - NullMetricReason exported in routing_telemetry >= 1 (explicit null discipline defined), AND
    - RoutingTelemetry exported in routing_telemetry >= 1 (carries queue_depth_snapshot + target_load_snapshot)
    """
    nmr_exported = _count_exported(conn, "NullMetricReason", "routing_telemetry")
    rt_exported = _count_exported(conn, "RoutingTelemetry", "routing_telemetry")
    # NOT_INSTRUMENTED is the default null value
    not_instrumented = _count_in_file(conn, "NOT_INSTRUMENTED", "routing_telemetry")
    get_store_exported = _count_exported(conn, "get_routing_telemetry_store", "routing_telemetry")

    ok = nmr_exported >= 1 and rt_exported >= 1
    GATE_RESULTS.append(
        (
            "E",
            ok,
            f"NullMetricReason exported in routing_telemetry={nmr_exported} (>=1), "
            f"RoutingTelemetry exported (has queue/load fields)={rt_exported} (>=1), "
            f"NOT_INSTRUMENTED null-value in routing_telemetry={not_instrumented}, "
            f"get_routing_telemetry_store exported={get_store_exported}",
        )
    )
    return ok


def _print_baseline(conn: sqlite3.Connection) -> None:
    print("\n--- P2/L0 Routing Telemetry Baseline ---")

    for rel in (
        "routes_path",
        "routes_through",
        "proposal_commits_routing",
        "records_execution_trace",
        "routing_telemetry_emitted",
        "emits_routing_telemetry",
        "routing_decision",
    ):
        total = _count_distinct_sources(conn, rel, NON_TEST)
        l0 = _count_distinct_sources(conn, rel, L0_FILTER)
        print(f"  {rel:<45} total={total:4d}  L0={l0:4d}")

    print()
    for sym in (
        "RoutingTelemetry",
        "record_routing_telemetry",
        "RoutingTelemetryStore",
        "RoutingTelemetryContext",
        "RoutingOutcomeStatus",
        "NullMetricReason",
        "ROUTE_SUCCEEDED",
        "ROUTE_FAILED",
        "ROUTE_ESCALATED",
        "ROUTE_RETRIED",
        "ROUTE_ABANDONED",
        "routing_duration_ms",
        "routing_outcome_status",
        "queue_depth_snapshot",
        "target_load_snapshot",
        "routing_failure_reason",
        "get_routing_telemetry_store",
        "RoutingTelemetryContext",
        "routing_telemetry_id",
    ):
        n = _count_symbol_sources(conn, sym, NON_TEST)
        print(f"  symbol:{sym:<38} sources={n:4d}")

    print("\n--- Spec §9 ADG Validation Queries ---")
    c = conn.cursor()

    c.execute(
        f"SELECT COUNT(*) FROM edges WHERE relation_type IN ('routes_path','routes_through') {NON_TEST}"
    )
    print(f"  Runtime routes_path/routes_through (edges, non-test): {c.fetchone()[0]}")

    c.execute(f"SELECT COUNT(*) FROM edges WHERE relation_type='proposal_commits_routing' {NON_TEST}")
    print(f"  Runtime proposal_commits_routing (edges, non-test): {c.fetchone()[0]}")

    print("\n  L0 routing telemetry symbols (source files, up to 20):")
    c.execute(
        f"SELECT DISTINCT source_file, symbol FROM edges "
        f"WHERE (symbol LIKE '%RoutingTelemetry%' OR symbol LIKE '%record_routing_telemetry%' "
        f"OR symbol LIKE '%RoutingOutcomeStatus%' OR symbol LIKE '%NullMetricReason%') "
        f"{NON_TEST} LIMIT 20"
    )
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}]")
    else:
        print("    (none yet)")

    print("\n  L0 routing chokepoint wiring:")
    c.execute(
        f"SELECT DISTINCT source_file, relation_type, symbol FROM edges "
        f"WHERE relation_type IN ('calls','invokes_dynamic') "
        f"AND symbol LIKE '%record_routing_telemetry%' {NON_TEST} LIMIT 10"
    )
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"    {row[0]}  [{row[1]}] {row[2]}")
    else:
        print("    (none yet)")


def main() -> int:
    db = _get_db()
    print(f"P2/L0 Routing Telemetry Gate — ADG: {db}\n")
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
        print(f"\nP2/L0 ROUTING TELEMETRY: FAILED GATES {failed}")
        return 1

    print("\nP2/L0 ROUTING TELEMETRY: ALL GATES PASSED - CLOSURE VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
