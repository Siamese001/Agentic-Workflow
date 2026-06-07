#!/usr/bin/env python3
"""Gate G-RUNTIME-TRACE-TOPOLOGY — runtime evidence is more than row shape.

Plan: ``.claude/plans/adg-three-graph-harness-e57cc7.md`` (W2.P2).

Sister gate to ``check_runtime_proof_view_well_formed.py``. That gate checks
ROW SHAPE (closed-enum status, non-empty fields, attesting_trace_count >= 1).
This gate checks TOPOLOGY:

  T1. Every AUTHORITATIVE_RUNTIME ``v_runtime_proof`` row maps to raw OTel
      span refs (``latest_span_id`` non-empty AND evidence_refs cite spans).
  T2. parent_span_id chain is continuous within each trace (no orphans
      mid-trace; every non-root span has a parent that exists in the same
      trace).
  T3. Each trace has exactly one root span (parent_span_id = NULL or empty).
  T4. Timestamps within a trace are monotonic (parent.start <= child.start
      for every (parent,child) pair).
  T5. Required fields exist on every span: trace_id, span_id, parent_span_id
      (may be empty for root), policy_hash, blueprint_hash, registry_digest.
  T6. ``app_id`` exists for spans on app paths (src/dst contains apps_*).
  T7. ``route_id`` exists for spans on routed paths (relation_type ==
      'routes_through' or 'flows_to').
  T8. ``scenario_id`` exists for proof scenarios (trace_id starts with
      'scenario-').
  T9. Synthetic fixtures (``trace_id`` starts with ``synth-``) are ALLOWED
      to populate ``v_runtime_proof`` for harness bring-up, but they
      CANNOT satisfy ``--require-production`` mode. In that mode, any
      AUTHORITATIVE_RUNTIME row with synthetic trace_id is a hard FAIL.

Reads
-----
* Primary: ``v_runtime_proof`` (latest_trace_id, latest_span_id,
  evidence_refs, static_edge_id).
* Optional: ``agentic_core/L4_state/memory/runtime_adg/<trace_id>/spans.json``
  when the per-trace store is reachable. Span topology checks (T2/T3/T4)
  require these JSON files; without them, the gate emits SKIP for those
  invariants.

Failure codes
-------------
T1_FAIL_NO_RAW_SPAN_REF
T2_FAIL_BROKEN_PARENT_CHAIN
T3_FAIL_NO_ROOT_OR_MULTI_ROOT
T4_FAIL_NON_MONOTONIC_TIMESTAMPS
T5_FAIL_MISSING_REQUIRED_FIELD
T6_FAIL_MISSING_APP_ID
T7_FAIL_MISSING_ROUTE_ID
T8_FAIL_MISSING_SCENARIO_ID
T9_FAIL_SYNTHETIC_IN_PRODUCTION_MODE

Bypass: ``RUNTIME_TOPOLOGY_BYPASS=1``.
"""

from __future__ import annotations

# Reads v_runtime_proof and the runtime store directly. Proof-grade.
__adg_consumer_mode__ = "proof"

import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.ci.gate_result import GateResult  # noqa: E402

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "adg"
RUNTIME_STORE_DIR = REPO_ROOT / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
REPORT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "runtime_trace_topology.json"
SAMPLE_LIMIT = 10

REQUIRED_SPAN_FIELDS = (
    "trace_id",
    "span_id",
    "parent_span_id",
    "policy_hash",
    "blueprint_hash",
    "registry_digest",
)


def _latest_snapshot() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def _load_evidence(refs_json: str | None) -> dict[str, Any] | list[Any]:
    if not refs_json:
        return {}
    try:
        return json.loads(refs_json)
    except json.JSONDecodeError:
        return {}


def _load_trace_spans(trace_id: str) -> list[dict[str, Any]] | None:
    """Best-effort load of per-trace span list from the runtime store.

    The runtime store layout is
    ``agentic_core/L4_state/memory/runtime_adg/<trace_id>/spans.json``.
    Returns ``None`` if the file is unreachable. The caller treats absence
    as "topology checks SKIP for this trace".
    """
    if not trace_id:
        return None
    candidate = RUNTIME_STORE_DIR / trace_id / "spans.json"
    if not candidate.is_file():
        return None
    try:
        data = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(data, list):
        return [s for s in data if isinstance(s, dict)]
    if isinstance(data, dict) and isinstance(data.get("spans"), list):
        return [s for s in data["spans"] if isinstance(s, dict)]
    return None


def _check_t1_raw_span_ref(con: sqlite3.Connection) -> tuple[list[str], list[dict]]:
    """T1 — every NON-SYNTHETIC AUTHORITATIVE_RUNTIME row maps to raw OTel span refs.

    Synthetic seed rows (trace_id LIKE 'synth-%') are intentionally exempt;
    they are the harness's own bring-up scaffolding and do not carry raw
    span topology. T9 is the dedicated synthetic-discriminator.
    """
    failures: list[str] = []
    samples: list[dict[str, Any]] = []

    rows = con.execute(
        """
        SELECT id, src_name, dst_name, latest_trace_id, latest_span_id,
               evidence_refs, attesting_trace_count
          FROM v_runtime_proof
         WHERE authority_status='AUTHORITATIVE_RUNTIME'
           AND latest_trace_id NOT LIKE 'synth-%'
        """
    ).fetchall()
    miss = 0
    for r in rows:
        ev = _load_evidence(r[5])
        # Pass criterion: latest_span_id is non-empty AND evidence_refs is
        # a non-empty container (any of run_ids / spans / trace_id / span_id
        # is enough — the runtime store layout uses run_ids as the canonical
        # multi-trace pointer).
        has_span = bool(r[4])
        ev_has_span = False
        if isinstance(ev, list):
            ev_has_span = bool(ev)
        elif isinstance(ev, dict):
            ev_has_span = bool(
                ev.get("run_ids")
                or ev.get("trace_id")
                or ev.get("span_id")
                or ev.get("spans")
                or ev.get("trace_ids")
            )
        if not (has_span and ev_has_span):
            miss += 1
            if len(samples) < SAMPLE_LIMIT:
                samples.append({
                    "code": "T1_FAIL_NO_RAW_SPAN_REF",
                    "row_id": r[0],
                    "src_name": r[1],
                    "dst_name": r[2],
                    "trace_id": r[3],
                    "latest_span_id": r[4],
                    "has_evidence_refs_pointer": ev_has_span,
                })
    if miss:
        failures.append("T1_FAIL_NO_RAW_SPAN_REF")

    return failures, samples


def _check_t2345_chain(
    con: sqlite3.Connection, trace_ids: list[str]
) -> tuple[list[str], list[dict[str, Any]], dict[str, int]]:
    """T2/T3/T4/T5 — chain continuity, root, timestamps, required fields.

    Requires per-trace ``spans.json`` files; when the store is unavailable,
    each invariant emits SKIP for that trace. Aggregate counts surface as
    ``traces_with_topology_check`` so callers can tell whether a PASS is
    earned or blank.
    """
    failures: list[str] = []
    samples: list[dict[str, Any]] = []
    counts = {
        "traces_total": len(trace_ids),
        "traces_with_topology_check": 0,
        "traces_passing_topology": 0,
        "traces_with_broken_chain": 0,
        "traces_with_no_root": 0,
        "traces_with_multi_root": 0,
        "traces_with_non_monotonic": 0,
        "spans_with_missing_fields": 0,
    }

    for trace_id in trace_ids:
        spans = _load_trace_spans(trace_id)
        if spans is None:
            continue
        counts["traces_with_topology_check"] += 1

        ids_in_trace = {s.get("span_id") for s in spans if s.get("span_id")}
        roots = [s for s in spans if not s.get("parent_span_id")]

        # T3 — root invariant.
        if not roots:
            counts["traces_with_no_root"] += 1
            if len(samples) < SAMPLE_LIMIT:
                samples.append({
                    "code": "T3_FAIL_NO_ROOT_OR_MULTI_ROOT",
                    "trace_id": trace_id,
                    "issue": "no root span (no parent_span_id == empty)",
                })
            continue
        if len(roots) > 1:
            counts["traces_with_multi_root"] += 1
            if len(samples) < SAMPLE_LIMIT:
                samples.append({
                    "code": "T3_FAIL_NO_ROOT_OR_MULTI_ROOT",
                    "trace_id": trace_id,
                    "issue": f"{len(roots)} root spans (expected 1)",
                })
            continue

        # T2 — every non-root span's parent must exist in the trace.
        broken = [
            s for s in spans
            if s.get("parent_span_id") and s.get("parent_span_id") not in ids_in_trace
        ]
        if broken:
            counts["traces_with_broken_chain"] += 1
            if len(samples) < SAMPLE_LIMIT:
                samples.append({
                    "code": "T2_FAIL_BROKEN_PARENT_CHAIN",
                    "trace_id": trace_id,
                    "broken_span_count": len(broken),
                    "sample_orphan_span_id": broken[0].get("span_id"),
                    "sample_missing_parent_id": broken[0].get("parent_span_id"),
                })

        # T4 — monotonic timestamps. Build span_id -> start_time map.
        starts: dict[str, float] = {}
        for s in spans:
            sid = s.get("span_id")
            t = s.get("start_time") or s.get("startTime") or s.get("start")
            if sid and t is not None:
                try:
                    starts[sid] = float(t)
                except (TypeError, ValueError):
                    pass
        non_mono = 0
        for s in spans:
            parent = s.get("parent_span_id")
            sid = s.get("span_id")
            if parent and sid and parent in starts and sid in starts:
                if starts[sid] < starts[parent]:
                    non_mono += 1
        if non_mono:
            counts["traces_with_non_monotonic"] += 1
            if len(samples) < SAMPLE_LIMIT:
                samples.append({
                    "code": "T4_FAIL_NON_MONOTONIC_TIMESTAMPS",
                    "trace_id": trace_id,
                    "non_monotonic_pair_count": non_mono,
                })

        # T5 — required fields.
        for s in spans:
            for fld in REQUIRED_SPAN_FIELDS:
                # parent_span_id is allowed to be empty for the root span only.
                if fld == "parent_span_id" and not s.get("parent_span_id"):
                    if not s.get("is_root") and s == roots[0]:
                        # root span — empty parent is legitimate
                        continue
                if fld != "parent_span_id" and not s.get(fld):
                    counts["spans_with_missing_fields"] += 1
                    if len(samples) < SAMPLE_LIMIT:
                        samples.append({
                            "code": "T5_FAIL_MISSING_REQUIRED_FIELD",
                            "trace_id": trace_id,
                            "span_id": s.get("span_id"),
                            "missing_field": fld,
                        })
                    break  # one example per span

        if (
            broken == []
            and non_mono == 0
            and len(roots) == 1
        ):
            counts["traces_passing_topology"] += 1

    if counts["traces_with_broken_chain"]:
        failures.append("T2_FAIL_BROKEN_PARENT_CHAIN")
    if counts["traces_with_no_root"] or counts["traces_with_multi_root"]:
        failures.append("T3_FAIL_NO_ROOT_OR_MULTI_ROOT")
    if counts["traces_with_non_monotonic"]:
        failures.append("T4_FAIL_NON_MONOTONIC_TIMESTAMPS")
    if counts["spans_with_missing_fields"]:
        failures.append("T5_FAIL_MISSING_REQUIRED_FIELD")

    return failures, samples, counts


def _check_t9_synthetic_in_production(
    con: sqlite3.Connection, *, require_production: bool
) -> tuple[list[str], list[dict[str, Any]], int]:
    """T9 — synthetic trace_ids cannot satisfy production runtime proof."""
    failures: list[str] = []
    samples: list[dict[str, Any]] = []
    rows = con.execute(
        """
        SELECT COUNT(*) FROM v_runtime_proof
         WHERE authority_status='AUTHORITATIVE_RUNTIME'
           AND latest_trace_id LIKE 'synth-%'
        """
    ).fetchone()
    synthetic_count = rows[0] if rows else 0

    if synthetic_count and require_production:
        failures.append("T9_FAIL_SYNTHETIC_IN_PRODUCTION_MODE")
        sample_rows = con.execute(
            """
            SELECT id, src_name, dst_name, latest_trace_id
              FROM v_runtime_proof
             WHERE authority_status='AUTHORITATIVE_RUNTIME'
               AND latest_trace_id LIKE 'synth-%'
             LIMIT ?
            """,
            (SAMPLE_LIMIT,),
        ).fetchall()
        for r in sample_rows:
            samples.append({
                "code": "T9_FAIL_SYNTHETIC_IN_PRODUCTION_MODE",
                "row_id": r[0],
                "src_name": r[1],
                "dst_name": r[2],
                "trace_id": r[3],
            })

    return failures, samples, synthetic_count


def _check_t678_path_fields(
    con: sqlite3.Connection,
    trace_ids: list[str],
    *,
    require_production: bool,
) -> tuple[list[str], list[dict[str, Any]], dict[str, int]]:
    """T6/T7/T8 — app_id / route_id / scenario_id presence per path semantics.

    These checks look at v_runtime_proof rows directly (not span-level)
    because the path-classification is derived from src_name/dst_name and
    relation_type, not from the per-span attributes. In default harness
    mode they are ADVISORY (counts only). With ``--require-production``,
    missing fields become FAIL.
    """
    failures: list[str] = []
    warns: list[str] = []
    samples: list[dict[str, Any]] = []
    counts = {
        "app_path_rows": 0,
        "missing_app_id": 0,
        "routed_path_rows": 0,
        "missing_route_id": 0,
        "scenario_rows": 0,
        "missing_scenario_id": 0,
    }

    # Skip synthetic rows — same exemption as T1.
    rows = con.execute(
        """
        SELECT id, src_name, dst_name, relation_type, latest_trace_id, evidence_refs
          FROM v_runtime_proof
         WHERE authority_status='AUTHORITATIVE_RUNTIME'
           AND latest_trace_id NOT LIKE 'synth-%'
        """
    ).fetchall()

    for r in rows:
        rid, src, dst, rel, tid, ev_json = r
        ev = _load_evidence(ev_json)
        ev_dict = ev if isinstance(ev, dict) else {}

        # T6 — app_id required when src or dst is on an app path.
        is_app_path = "apps_" in (src or "") or "apps_" in (dst or "")
        if is_app_path:
            counts["app_path_rows"] += 1
            if not ev_dict.get("app_id"):
                counts["missing_app_id"] += 1
                if len(samples) < SAMPLE_LIMIT:
                    samples.append({
                        "code": "T6_FAIL_MISSING_APP_ID",
                        "row_id": rid,
                        "src_name": src,
                        "dst_name": dst,
                    })

        # T7 — route_id required for routed relations.
        if rel in ("routes_through", "flows_to"):
            counts["routed_path_rows"] += 1
            if not ev_dict.get("route_id"):
                counts["missing_route_id"] += 1
                if len(samples) < SAMPLE_LIMIT:
                    samples.append({
                        "code": "T7_FAIL_MISSING_ROUTE_ID",
                        "row_id": rid,
                        "relation_type": rel,
                    })

        # T8 — scenario_id required for proof-scenario traces.
        if (tid or "").startswith("scenario-"):
            counts["scenario_rows"] += 1
            if not ev_dict.get("scenario_id"):
                counts["missing_scenario_id"] += 1
                if len(samples) < SAMPLE_LIMIT:
                    samples.append({
                        "code": "T8_FAIL_MISSING_SCENARIO_ID",
                        "row_id": rid,
                        "trace_id": tid,
                    })

    target = failures if require_production else warns
    if counts["missing_app_id"]:
        target.append("T6_FAIL_MISSING_APP_ID")
    if counts["missing_route_id"]:
        target.append("T7_FAIL_MISSING_ROUTE_ID")
    if counts["missing_scenario_id"]:
        target.append("T8_FAIL_MISSING_SCENARIO_ID")

    return failures, samples, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--require-production",
        action="store_true",
        help=(
            "Activate T9: synthetic trace_ids (synth-*) cannot satisfy "
            "AUTHORITATIVE_RUNTIME. Default: synthetic is OK (harness mode)."
        ),
    )
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    bypass_active = os.environ.get("RUNTIME_TOPOLOGY_BYPASS") == "1"

    snapshot = args.snapshot or _latest_snapshot()
    snapshot_id = snapshot.stem if snapshot else ""
    started = datetime.now(timezone.utc)

    base = {
        "gate_id": "runtime.trace_topology",
        "bucket": "runtime",
        "evidence_mode": "proof",
        "enforcement_mode": "strict",
        "snapshot_id": snapshot_id,
        "input_refs": [
            "v_runtime_proof (latest_trace_id, latest_span_id, evidence_refs)",
            "agentic_core/L4_state/memory/runtime_adg/<trace>/spans.json (when present)",
        ],
        "bypass_env_detected": ["RUNTIME_TOPOLOGY_BYPASS"] if bypass_active else [],
    }

    if bypass_active:
        result = GateResult(**base, status="SKIP", actual_fail_reason="").finalize()
        _emit(result, args.json_out)
        print("[runtime_topology] BYPASS via RUNTIME_TOPOLOGY_BYPASS=1")
        return 0

    if snapshot is None or not snapshot.exists():
        result = GateResult(**base, status="SKIP", actual_fail_reason="").finalize()
        _emit(result, args.json_out)
        print("[runtime_topology] SKIP: no snapshot")
        return 0

    con = sqlite3.connect(str(snapshot))
    try:
        # Verify v_runtime_proof exists; if not, SKIP entire gate.
        if not con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='v_runtime_proof'"
        ).fetchone():
            result = GateResult(**base, status="SKIP", actual_fail_reason="").finalize()
            _emit(result, args.json_out)
            print("[runtime_topology] SKIP: v_runtime_proof not present")
            return 0

        t1_fails, t1_samples = _check_t1_raw_span_ref(con)
        trace_id_rows = con.execute(
            """
            SELECT DISTINCT latest_trace_id
              FROM v_runtime_proof
             WHERE authority_status='AUTHORITATIVE_RUNTIME'
               AND latest_trace_id IS NOT NULL AND latest_trace_id != ''
            """
        ).fetchall()
        trace_ids = [r[0] for r in trace_id_rows]

        t_chain_fails, t_chain_samples, t_chain_counts = _check_t2345_chain(con, trace_ids)
        t_path_fails, t_path_samples, t_path_counts = _check_t678_path_fields(
            con, trace_ids, require_production=args.require_production
        )
        t9_fails, t9_samples, synth_count = _check_t9_synthetic_in_production(
            con, require_production=args.require_production
        )
    finally:
        con.close()

    failures = t1_fails + t_chain_fails + t_path_fails + t9_fails
    counts = {
        "synthetic_count": synth_count,
        **t_chain_counts,
        **t_path_counts,
        "fail_codes_count": len(failures),
    }

    duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    # If most invariants couldn't run because the runtime store wasn't
    # reachable, mark WARN — the gate ran but the most expensive checks
    # were SKIP-equivalent at the per-trace level.
    if failures:
        status = "FAIL"
        actual_fail = failures[0]
    elif t_chain_counts.get("traces_with_topology_check", 0) == 0 and trace_ids:
        # Topology not verifiable. Surface clearly without claiming PASS.
        status = "WARN"
        actual_fail = ""
    else:
        status = "PASS"
        actual_fail = ""

    result = GateResult(
        **base,
        status=status,
        actual_fail_reason=actual_fail,
        counts=counts,
        sample_failures=(t1_samples + t_chain_samples + t_path_samples + t9_samples)[:10],
        duration_ms=duration_ms,
    ).finalize()
    _emit(result, args.json_out)

    print(
        f"[runtime_topology] status={status} traces={len(trace_ids)} "
        f"topology_checked={t_chain_counts['traces_with_topology_check']} "
        f"synthetic={synth_count} fails={len(failures)}"
    )
    if failures:
        print(f"[runtime_topology] failure codes: {', '.join(failures)}")

    return 1 if status == "FAIL" else 0


def _emit(result: GateResult, custom_out: Path | None) -> None:
    out_path = custom_out or REPORT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_json(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
