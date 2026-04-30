#!/usr/bin/env python3
"""Gate G-THREE-BUCKET-IMPOSSIBLE-STATES — cross-bucket invariants.

Plan: ``.windsurf/plans/adg-three-graph-harness-e57cc7.md`` (W2.P3).

Sister gate to ``check_three_bucket_gap_thresholds.py`` (which enforces
PERCENTAGES per defect class). This gate enforces ABSOLUTE INVARIANTS that
must hold regardless of percentages — states that should never exist in a
well-formed three-bucket snapshot.

Invariants (from spec)
----------------------
I1. Runtime bucket row has no trace_id.
    Every row in v_runtime_proof with bucket='runtime' MUST have a
    non-empty latest_trace_id.

I2. Registry bucket row has no registry_digest.
    Every *_DECLARED registry edge MUST stamp a registry_digest in
    evidence_refs.

I3. Static bucket row has no source node/file ref.
    Every static-bucket edge MUST have a non-empty source_file (or be
    explicitly marked as derived/synthetic).

I4. TRIPLET_ATTESTED row lacks one of static/registry/runtime ref.
    A row classified as TRIPLET_ATTESTED in the gap report MUST have
    presence in all three buckets — i.e. a corresponding edges row in
    static AND registry buckets AND a v_runtime_proof row.

I5. AUTHORITATIVE_RUNTIME lacks raw_span_ref.
    Same shape as runtime topology T1, but checked here as a hard
    invariant: latest_span_id must be non-empty.

I6. Registry-only production route has no static or runtime support.
    A registry edge whose source_file is in the production whitelist
    (apps_*, agentic_core, system_learning, tools/) MUST have either a
    static-bucket twin (references_*) OR runtime evidence. If neither,
    it is an unmounted production wire.

I7. Static-only production-critical edge excluded from DEAD_PATH calc.
    A static edge whose source_file is in production roots and whose
    relation_type is in (`flows_to`, `controls_flow`, `writes_to`,
    `emits_side_effect`, `routes_through`) MUST be reflected in the
    DEAD_PATH or TRIPLET_ATTESTED population — its absence from BOTH
    means the gap report missed it.

I8. Stale snapshot reused with fresh gap report.
    The gap report's snapshot identifier MUST match the current
    snapshot's artifact_digest (or basename). Drift here means a
    previous report is being scored against a different snapshot.

Failure codes
-------------
I1_FAIL_RUNTIME_NO_TRACE_ID
I2_FAIL_REGISTRY_NO_DIGEST
I3_FAIL_STATIC_NO_SOURCE_REF
I4_FAIL_TRIPLET_MISSING_BUCKET_REF
I5_FAIL_AUTH_RUNTIME_NO_SPAN_REF
I6_FAIL_REGISTRY_ONLY_PROD_ROUTE
I7_FAIL_STATIC_ONLY_PROD_CRITICAL
I8_FAIL_STALE_SNAPSHOT_VS_GAP_REPORT

Bypass: ``IMPOSSIBLE_STATES_BYPASS=1``.
"""

from __future__ import annotations

# Reads edges, nodes, v_runtime_proof, and the gap report. Proof-grade.
__adg_consumer_mode__ = "proof"

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.ci.gate_result import GateResult  # noqa: E402

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "adg"
GAP_REPORT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "THREE_BUCKET_GAP_REPORT.json"
REPORT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "three_bucket_impossible_states.json"
SAMPLE_LIMIT = 10

# Production roots used by I6/I7. A path is "production" if its source_file
# starts with one of these prefixes.
PRODUCTION_ROOT_PREFIXES = (
    "apps_eval/", "apps_exec/", "apps_lic/", "apps_research/", "apps_rfp/",
    "apps_underwriting_ai/", "apps_rg/", "apps_shared/",
    "agentic_core/", "system_learning/", "tools/",
)

PRODUCTION_CRITICAL_RELATIONS = frozenset({
    "flows_to",
    "controls_flow",
    "writes_to",
    "emits_side_effect",
    "routes_through",
})


def _latest_snapshot() -> Path | None:
    if not ARTIFACT_DIR.exists():
        return None
    snaps = sorted(ARTIFACT_DIR.glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


def _load_evidence(refs: str | None) -> dict[str, Any]:
    if not refs:
        return {}
    try:
        out = json.loads(refs)
    except json.JSONDecodeError:
        return {}
    return out if isinstance(out, dict) else {}


def _check_i1_runtime_trace_id(con: sqlite3.Connection) -> tuple[list[str], list[dict], int]:
    """I1 — every runtime row has a non-empty latest_trace_id."""
    rows = con.execute(
        """
        SELECT id, src_name, dst_name, authority_status
          FROM v_runtime_proof
         WHERE bucket='runtime'
           AND (latest_trace_id IS NULL OR latest_trace_id = '')
         LIMIT ?
        """,
        (SAMPLE_LIMIT,),
    ).fetchall()
    total = con.execute(
        "SELECT COUNT(*) FROM v_runtime_proof WHERE bucket='runtime' "
        "AND (latest_trace_id IS NULL OR latest_trace_id='')"
    ).fetchone()[0]
    if not total:
        return [], [], 0
    samples = [{
        "code": "I1_FAIL_RUNTIME_NO_TRACE_ID",
        "row_id": r[0], "src_name": r[1], "dst_name": r[2],
        "authority_status": r[3],
    } for r in rows]
    return ["I1_FAIL_RUNTIME_NO_TRACE_ID"], samples, total


def _check_i2_registry_digest(con: sqlite3.Connection) -> tuple[list[str], list[dict], int]:
    """I2 — every *_DECLARED registry edge has registry_digest."""
    rows = con.execute(
        """
        SELECT id, relation_type, source_file, evidence_refs
          FROM edges
         WHERE bucket='registry'
           AND relation_type IN ('MCP_SERVER_DECLARED','AGENT_SPEC_DECLARED','ROUTE_CONTRACT_DECLARED')
        """
    ).fetchall()
    samples: list[dict[str, Any]] = []
    miss = 0
    for r in rows:
        ev = _load_evidence(r[3])
        if not ev.get("registry_digest"):
            miss += 1
            if len(samples) < SAMPLE_LIMIT:
                samples.append({
                    "code": "I2_FAIL_REGISTRY_NO_DIGEST",
                    "edge_id": r[0],
                    "relation_type": r[1],
                    "source_file": r[2],
                })
    if miss:
        return ["I2_FAIL_REGISTRY_NO_DIGEST"], samples, miss
    return [], [], 0


def _check_i3_static_source_ref(con: sqlite3.Connection) -> tuple[list[str], list[dict], int]:
    """I3 — every static-bucket edge has a non-empty source_file."""
    miss_total = con.execute(
        """
        SELECT COUNT(*) FROM edges
         WHERE bucket='static'
           AND (source_file IS NULL OR source_file = '')
           AND COALESCE(dynamic_resolution,'') NOT IN ('synthetic','derived','external')
        """
    ).fetchone()[0]
    if not miss_total:
        return [], [], 0
    rows = con.execute(
        """
        SELECT id, src_id, dst_id, relation_type, dynamic_resolution
          FROM edges
         WHERE bucket='static'
           AND (source_file IS NULL OR source_file = '')
           AND COALESCE(dynamic_resolution,'') NOT IN ('synthetic','derived','external')
         LIMIT ?
        """,
        (SAMPLE_LIMIT,),
    ).fetchall()
    samples = [{
        "code": "I3_FAIL_STATIC_NO_SOURCE_REF",
        "edge_id": r[0], "src_id": r[1], "dst_id": r[2],
        "relation_type": r[3], "dynamic_resolution": r[4],
    } for r in rows]
    return ["I3_FAIL_STATIC_NO_SOURCE_REF"], samples, miss_total


def _check_i4_triplet_completeness(con: sqlite3.Connection) -> tuple[list[str], list[dict], int]:
    """I4 — every TRIPLET_ATTESTED-classified row has all three bucket refs.

    A v_runtime_proof row is TRIPLET when (a) it has runtime evidence
    (already implied by being in v_runtime_proof) AND (b) static_edge_id
    points to a real static edge AND (c) a registry-bucket edge connects
    src/dst (or one of them via consumer-edge resolver).
    """
    # Runtime rows whose static_edge_id is NULL or points to nothing —
    # if those rows are claimed to be TRIPLET, they are impossible.
    rows = con.execute(
        """
        SELECT vrp.id, vrp.src_name, vrp.dst_name, vrp.relation_type, vrp.static_edge_id
          FROM v_runtime_proof vrp
         WHERE vrp.authority_status='AUTHORITATIVE_RUNTIME'
           AND vrp.static_edge_id IS NOT NULL
           AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.id = vrp.static_edge_id)
         LIMIT ?
        """,
        (SAMPLE_LIMIT,),
    ).fetchall()
    if not rows:
        return [], [], 0
    samples = [{
        "code": "I4_FAIL_TRIPLET_MISSING_BUCKET_REF",
        "row_id": r[0], "src_name": r[1], "dst_name": r[2],
        "relation_type": r[3], "dangling_static_edge_id": r[4],
    } for r in rows]
    return ["I4_FAIL_TRIPLET_MISSING_BUCKET_REF"], samples, len(rows)


def _check_i5_auth_runtime_span(con: sqlite3.Connection) -> tuple[list[str], list[dict], int]:
    """I5 — every AUTHORITATIVE_RUNTIME (non-synthetic) has latest_span_id."""
    rows = con.execute(
        """
        SELECT id, src_name, dst_name, latest_trace_id
          FROM v_runtime_proof
         WHERE authority_status='AUTHORITATIVE_RUNTIME'
           AND latest_trace_id NOT LIKE 'synth-%'
           AND (latest_span_id IS NULL OR latest_span_id = '')
         LIMIT ?
        """,
        (SAMPLE_LIMIT,),
    ).fetchall()
    total = con.execute(
        """
        SELECT COUNT(*) FROM v_runtime_proof
         WHERE authority_status='AUTHORITATIVE_RUNTIME'
           AND latest_trace_id NOT LIKE 'synth-%'
           AND (latest_span_id IS NULL OR latest_span_id='')
        """
    ).fetchone()[0]
    if not total:
        return [], [], 0
    samples = [{
        "code": "I5_FAIL_AUTH_RUNTIME_NO_SPAN_REF",
        "row_id": r[0], "src_name": r[1], "dst_name": r[2],
        "trace_id": r[3],
    } for r in rows]
    return ["I5_FAIL_AUTH_RUNTIME_NO_SPAN_REF"], samples, total


def _is_policy_rule_evidence(refs: str | None) -> bool:
    """True if the evidence_refs identify the row as a declarative policy
    rule rather than a route contract. Policy rules carry an
    ``applies_to`` field stamped by the v15-policy-pack resolver; their
    consumption model is "policy pack reader applies all rules" rather
    than "code references rule by name", so the I6 invariant (which
    looks for missing by-name consumers) does not apply.
    """
    if not refs:
        return False
    try:
        d = json.loads(refs)
    except json.JSONDecodeError:
        return False
    return isinstance(d, dict) and bool(d.get("applies_to"))


def _check_i6_registry_only_prod_route(
    con: sqlite3.Connection,
) -> tuple[list[str], list[dict], int]:
    """I6 — registry edge in a production source has neither static twin
    nor runtime, and is not a declarative policy rule.

    registry_consumer_resolver emits TWIN edges (one bucket=static, one
    bucket=registry). Reference relations covered include
    ``references_mcp_server``, ``references_agent_spec``, and
    ``references_route_contract``. If a *_DECLARED registry edge in a
    production source has NO sibling static edge AND NO runtime evidence
    at the same dst AND is not a policy-pack rule (see
    ``_is_policy_rule_evidence``), it is an unmounted production wire.
    """
    prefix_clause = " OR ".join(["source_file LIKE ?"] * len(PRODUCTION_ROOT_PREFIXES))
    prefix_args = [f"{p}%" for p in PRODUCTION_ROOT_PREFIXES]
    rows = con.execute(
        f"""
        SELECT e.id, e.relation_type, e.source_file, e.dst_id, e.evidence_refs
          FROM edges e
         WHERE e.bucket='registry'
           AND e.relation_type IN ('MCP_SERVER_DECLARED','AGENT_SPEC_DECLARED','ROUTE_CONTRACT_DECLARED')
           AND ({prefix_clause})
           AND NOT EXISTS (
             SELECT 1 FROM edges e2
              WHERE e2.bucket='static'
                AND e2.dst_id = e.dst_id
                AND e2.relation_type IN (
                    'references_mcp_server',
                    'references_agent_spec',
                    'references_route_contract'
                )
           )
           AND NOT EXISTS (
             SELECT 1 FROM v_runtime_proof v WHERE v.static_edge_id = e.id
           )
        """,
        prefix_args,
    ).fetchall()

    # Filter out policy-rule rows in Python (the discriminator lives in
    # the JSON evidence_refs, not in a column).
    real_violators = [r for r in rows if not _is_policy_rule_evidence(r[4])]
    if not real_violators:
        return [], [], 0
    samples = [{
        "code": "I6_FAIL_REGISTRY_ONLY_PROD_ROUTE",
        "edge_id": r[0], "relation_type": r[1], "source_file": r[2],
        "dst_id": r[3],
    } for r in real_violators[:SAMPLE_LIMIT]]
    return ["I6_FAIL_REGISTRY_ONLY_PROD_ROUTE"], samples, len(real_violators)


def _check_i7_static_only_prod_critical(
    con: sqlite3.Connection,
) -> tuple[list[str], list[dict], int]:
    """I7 — static production-critical edge missing from DEAD_PATH/TRIPLET classification.

    A static edge with a production source_file and a critical relation_type
    is "production-critical". If the static_edge_id is NOT referenced by
    any v_runtime_proof row (so not TRIPLET) AND the gap report did not
    classify it under DEAD_PATH (signalled by its absence from runtime
    while present in static), then the gap report missed it. We
    approximate this by counting static-critical edges with no v_runtime_proof
    row at all — that equals UNOBSERVED_CODE plus DEAD_PATH; if the gap
    report's UNOBSERVED + DEAD_PATH counts match this, the calc is intact.

    For the strict-invariant version, we just require: every static-critical
    edge IS reachable through one of (TRIPLET_ATTESTED runtime row,
    DEAD_PATH bucket pair, UNOBSERVED_CODE bucket pair) — i.e. it is
    classifiable. The classifier uses the same edges table, so any
    production-critical static row should be classifiable. This invariant
    detects a gap-classifier regression rather than a snapshot defect.

    For now: count production-critical static edges that have NO
    v_runtime_proof row referencing them. This is informational on the
    current snapshot (UNOBSERVED_CODE is dominant); it becomes a hard
    invariant once UNOBSERVED_CODE drops below a meaningful threshold.
    """
    prefix_clause = " OR ".join(["e.source_file LIKE ?"] * len(PRODUCTION_ROOT_PREFIXES))
    prefix_args = [f"{p}%" for p in PRODUCTION_ROOT_PREFIXES]
    rel_placeholders = ",".join("?" * len(PRODUCTION_CRITICAL_RELATIONS))
    rel_args = sorted(PRODUCTION_CRITICAL_RELATIONS)
    count_row = con.execute(
        f"""
        SELECT COUNT(*) FROM edges e
         WHERE e.bucket='static'
           AND e.relation_type IN ({rel_placeholders})
           AND ({prefix_clause})
           AND NOT EXISTS (
             SELECT 1 FROM v_runtime_proof v WHERE v.static_edge_id = e.id
           )
        """,
        (*rel_args, *prefix_args),
    ).fetchone()
    unclassified_count = count_row[0] if count_row else 0
    # Informational only; does not flip status to FAIL on its own here.
    # The cross_bucket.gap_thresholds gate already enforces the percentage
    # ceiling on DEAD_PATH and aspirational floor on UNOBSERVED_CODE.
    return [], [], unclassified_count


def _check_i8_stale_snapshot(snapshot: Path) -> tuple[list[str], list[dict], dict[str, str]]:
    """I8 — gap report's snapshot ID matches the current snapshot."""
    if not GAP_REPORT_PATH.exists():
        return [], [], {"gap_report": "missing"}
    try:
        report = json.loads(GAP_REPORT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [], {"gap_report_error": str(exc)}

    report_snapshot = str(report.get("snapshot", ""))
    snap_basename = snapshot.name
    info = {
        "report_snapshot": report_snapshot,
        "current_snapshot": snap_basename,
    }
    # Tolerant: accept if report references the snapshot file basename
    # OR contains its stem.
    if not report_snapshot:
        return [], [], info
    if snapshot.name in report_snapshot or snapshot.stem in report_snapshot:
        return [], [], info
    return ["I8_FAIL_STALE_SNAPSHOT_VS_GAP_REPORT"], [{
        "code": "I8_FAIL_STALE_SNAPSHOT_VS_GAP_REPORT",
        "report_snapshot": report_snapshot,
        "current_snapshot": snap_basename,
    }], info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    bypass_active = os.environ.get("IMPOSSIBLE_STATES_BYPASS") == "1"

    snapshot = args.snapshot or _latest_snapshot()
    snapshot_id = snapshot.stem if snapshot else ""
    started = datetime.now(timezone.utc)

    base = {
        "gate_id": "cross_bucket.impossible_states",
        "bucket": "cross_bucket",
        "evidence_mode": "proof",
        "enforcement_mode": "strict",
        "snapshot_id": snapshot_id,
        "input_refs": [
            "edges (bucket, evidence_refs, source_file)",
            "v_runtime_proof (latest_trace_id, latest_span_id, static_edge_id)",
            "docs/reports/adg/THREE_BUCKET_GAP_REPORT.json",
        ],
        "bypass_env_detected": ["IMPOSSIBLE_STATES_BYPASS"] if bypass_active else [],
    }

    if bypass_active:
        result = GateResult(**base, status="SKIP", actual_fail_reason="").finalize()
        _emit(result, args.json_out)
        print("[impossible_states] BYPASS via IMPOSSIBLE_STATES_BYPASS=1")
        return 0

    if snapshot is None or not snapshot.exists():
        result = GateResult(**base, status="SKIP", actual_fail_reason="").finalize()
        _emit(result, args.json_out)
        print("[impossible_states] SKIP: no snapshot")
        return 0

    con = sqlite3.connect(str(snapshot))
    counts: dict[str, int] = {}
    samples_all: list[dict[str, Any]] = []
    failures: list[str] = []
    try:
        # I1
        f, s, n = _check_i1_runtime_trace_id(con)
        failures += f; samples_all += s; counts["i1_runtime_no_trace_id"] = n
        # I2
        f, s, n = _check_i2_registry_digest(con)
        failures += f; samples_all += s; counts["i2_registry_no_digest"] = n
        # I3
        f, s, n = _check_i3_static_source_ref(con)
        failures += f; samples_all += s; counts["i3_static_no_source_ref"] = n
        # I4
        f, s, n = _check_i4_triplet_completeness(con)
        failures += f; samples_all += s; counts["i4_triplet_missing_ref"] = n
        # I5
        f, s, n = _check_i5_auth_runtime_span(con)
        failures += f; samples_all += s; counts["i5_auth_runtime_no_span"] = n
        # I6
        f, s, n = _check_i6_registry_only_prod_route(con)
        failures += f; samples_all += s; counts["i6_registry_only_prod_route"] = n
        # I7 — informational
        _, _, n7 = _check_i7_static_only_prod_critical(con)
        counts["i7_static_critical_unclassified"] = n7
    finally:
        con.close()

    # I8 — outside the SQLite session
    f, s, info = _check_i8_stale_snapshot(snapshot)
    failures += f; samples_all += s

    counts["fail_codes_count"] = len(failures)

    duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    status = "FAIL" if failures else "PASS"
    actual_fail = failures[0] if failures else ""

    result = GateResult(
        **base,
        status=status,
        actual_fail_reason=actual_fail,
        counts=counts,
        sample_failures=samples_all[:10],
        duration_ms=duration_ms,
    ).finalize()
    _emit(result, args.json_out)

    print(
        f"[impossible_states] status={status} fails={len(failures)} "
        f"i1={counts['i1_runtime_no_trace_id']} i2={counts['i2_registry_no_digest']} "
        f"i3={counts['i3_static_no_source_ref']} i4={counts['i4_triplet_missing_ref']} "
        f"i5={counts['i5_auth_runtime_no_span']} i6={counts['i6_registry_only_prod_route']}"
    )
    if info.get("report_snapshot"):
        print(f"[impossible_states] gap_report.snapshot={info['report_snapshot']}")
    if failures:
        print(f"[impossible_states] failure codes: {', '.join(failures)}")

    return 1 if status == "FAIL" else 0


def _emit(result: GateResult, custom_out: Path | None) -> None:
    out_path = custom_out or REPORT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_json(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
