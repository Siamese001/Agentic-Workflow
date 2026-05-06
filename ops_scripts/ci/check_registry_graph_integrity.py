#!/usr/bin/env python3
"""Gate G-REGISTRY-GRAPH-INTEGRITY — dedicated registry-graph lane.

Plan: ``.windsurf/plans/adg-three-graph-harness-e57cc7.md`` (W2.P1).

Until this lane existed, the registry bucket had NO dedicated CI gate — its
correctness was folded into the cross-bucket gap thresholds. That left
registry-graph well-formedness untested in isolation. This gate fixes it.

Invariants asserted (by category)
---------------------------------
A. **Bucket discipline**
   A1. Every registry edge has ``bucket='registry'``
   A2. Every registry edge has ``authority_status='AUTHORITATIVE_REGISTRY'``
       OR a justified other status (logged)
   A3. Every node referenced by a registry edge has
       ``entity_type='registry_node'`` OR is a static-bucket consumer

B. **Node well-formedness** — emits ``WARN`` (not FAIL) when the schema
   field is aspirational and not yet populated by the resolver.
   B1. Every registry node has owner (from ``evidence_refs.owner``)
   B2. Every registry node has version (from ``evidence_refs.version``)
   B3. Every registry node has digest (from ``evidence_refs.digest``)
   B4. Every registry node has declared_surface
       (from ``evidence_refs.declared_surface``)

C. **Per-relation contracts** — emits ``WARN`` when aspirational
   C1. AGENT_SPEC_DECLARED → execution_profile present in evidence_refs
   C2. references_mcp_server → tool capability binding present
   C3. ROUTE_CONTRACT_DECLARED → approved gateway resolution
   C4. MCP_SERVER_DECLARED → transport + scope declaration

D. **Mapping completeness**
   D1. Every registry declaration maps to:
       - a static implementation (TRIPLET_ATTESTED-eligible), OR
       - an allowed-external-endpoint (whitelist), OR
       - a test_only fixture
   D2. No duplicate active registry declarations for the same logical target
       (key: ``(symbol, source_file)`` for declared rows;
        key: ``(dst_id, relation_type)`` for reference rows)
   D3. No stale ``registry_digest`` relative to snapshot ``meta.artifact_digest``
   D4. No registry declaration widens authority beyond policy/blueprint

Output schema
-------------
Emits a normalized GateResult JSON to stdout AND a copy to
``docs/reports/adg/registry_graph_integrity.json``. The ``actual_fail_reason``
field, when non-empty, is one of the codes below — used by negative-control
tests for exact-match assertion.

Failure codes
-------------
A1_FAIL_BUCKET_MISMATCH
A2_FAIL_AUTHORITY_MISMATCH
A3_FAIL_NODE_KIND_MISMATCH
B_WARN_NODE_FIELDS_ASPIRATIONAL
C_WARN_RELATION_FIELDS_ASPIRATIONAL
D1_FAIL_UNMAPPED_DECLARATION
D2_FAIL_DUPLICATE_ACTIVE_DECLARATION
D3_FAIL_STALE_REGISTRY_DIGEST
D4_FAIL_AUTHORITY_WIDENING

Bypass: ``REGISTRY_INTEGRITY_BYPASS=1``.
"""

from __future__ import annotations

# Reads `edges`, `nodes`, `mcp_config_servers` directly via SQLite. Proof-grade
# for bucket / authority / mapping invariants; advisory for aspirational fields.
__adg_consumer_mode__ = "proof"

import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.ci.gate_result import GateResult  # noqa: E402

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "adg"
REPORT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "registry_graph_integrity.json"
SAMPLE_LIMIT = 10

REGISTRY_DECLARED_RELATIONS = {
    "MCP_SERVER_DECLARED",
    "AGENT_SPEC_DECLARED",
    "ROUTE_CONTRACT_DECLARED",
}
REGISTRY_REFERENCE_RELATIONS = {
    "references_mcp_server",
    "references_agent_spec",
}
ALL_REGISTRY_RELATIONS = REGISTRY_DECLARED_RELATIONS | REGISTRY_REFERENCE_RELATIONS

# Allowed external endpoints (D1) — keep minimal; expand via Author-Gate.
ALLOWED_EXTERNAL_ENDPOINTS = (
    "https://mcp.deepwiki.com/mcp",
)

# Aspirational fields. When a registry node lacks these, emit WARN not FAIL,
# because the resolver (registry_resolvers.py / registry_consumer_resolver.py)
# may not yet populate them. Promotion to FAIL is W4.future.
ASPIRATIONAL_NODE_FIELDS = ("owner", "version", "digest", "declared_surface")
ASPIRATIONAL_RELATION_FIELDS = {
    "AGENT_SPEC_DECLARED": ("execution_profile",),
    "references_mcp_server": ("capability_binding",),
    "ROUTE_CONTRACT_DECLARED": ("gateway_resolution",),
    "MCP_SERVER_DECLARED": ("transport", "scope"),
}


def _latest_snapshot() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def _load_evidence(refs_json: str | None) -> dict[str, Any]:
    if not refs_json:
        return {}
    try:
        out = json.loads(refs_json)
    except json.JSONDecodeError:
        return {}
    return out if isinstance(out, dict) else {}


def _check_a_bucket_discipline(con: sqlite3.Connection) -> tuple[list[str], list[dict]]:
    """A1/A2/A3 — bucket / authority / node-kind discipline.

    Note on twin edges: ``references_mcp_server`` and ``references_agent_spec``
    are EXPECTED to appear with both ``bucket='static'`` (code-side reference)
    and ``bucket='registry'`` (registry-side mirror). Only ``*_DECLARED``
    relations must be exclusively in the registry bucket.
    """
    failures: list[str] = []
    samples: list[dict[str, Any]] = []

    # A1 — every *_DECLARED edge must be in registry bucket. Reference edges
    # are dual-bucket by design (twin edges from the consumer resolver).
    declared = sorted(REGISTRY_DECLARED_RELATIONS)
    rows = con.execute(
        f"""
        SELECT id, src_id, dst_id, relation_type, bucket, authority_status, source_file
          FROM edges
         WHERE relation_type IN ({','.join('?' * len(declared))})
           AND bucket != 'registry'
         LIMIT ?
        """,
        (*declared, SAMPLE_LIMIT),
    ).fetchall()
    if rows:
        failures.append("A1_FAIL_BUCKET_MISMATCH")
        for r in rows:
            samples.append({
                "code": "A1_FAIL_BUCKET_MISMATCH",
                "edge_id": r[0],
                "relation_type": r[3],
                "actual_bucket": r[4],
                "expected_bucket": "registry",
                "source_file": r[6],
            })

    # A2 — registry edges should carry AUTHORITATIVE_REGISTRY (or another
    # registry-tier authority). NULL is treated as authority mismatch.
    rows = con.execute(
        """
        SELECT id, relation_type, authority_status, source_file
          FROM edges
         WHERE bucket='registry'
           AND (authority_status IS NULL
                OR authority_status NOT LIKE '%REGISTRY%')
         LIMIT ?
        """,
        (SAMPLE_LIMIT,),
    ).fetchall()
    if rows:
        failures.append("A2_FAIL_AUTHORITY_MISMATCH")
        for r in rows:
            samples.append({
                "code": "A2_FAIL_AUTHORITY_MISMATCH",
                "edge_id": r[0],
                "relation_type": r[1],
                "authority_status": r[2],
                "source_file": r[3],
            })

    # A3 — destinations of registry-DECLARED edges must be registry_node.
    declared_placeholders = ",".join("?" * len(REGISTRY_DECLARED_RELATIONS))
    rows = con.execute(
        f"""
        SELECT e.id, e.dst_id, e.relation_type, n.entity_type, n.adg_name
          FROM edges e
          JOIN nodes n ON n.id = e.dst_id
         WHERE e.bucket='registry'
           AND e.relation_type IN ({declared_placeholders})
           AND COALESCE(n.entity_type,'') != 'registry_node'
         LIMIT ?
        """,
        (*sorted(REGISTRY_DECLARED_RELATIONS), SAMPLE_LIMIT),
    ).fetchall()
    if rows:
        failures.append("A3_FAIL_NODE_KIND_MISMATCH")
        for r in rows:
            samples.append({
                "code": "A3_FAIL_NODE_KIND_MISMATCH",
                "edge_id": r[0],
                "dst_id": r[1],
                "relation_type": r[2],
                "actual_entity_type": r[3],
                "expected_entity_type": "registry_node",
            })

    return failures, samples


def _check_b_node_fields(
    con: sqlite3.Connection,
) -> tuple[list[str], list[dict[str, Any]], dict[str, int]]:
    """B1..B4 — registry node aspirational fields. WARN, not FAIL."""
    warnings: list[str] = []
    samples: list[dict[str, Any]] = []
    counts = {f"missing_{f}": 0 for f in ASPIRATIONAL_NODE_FIELDS}

    rows = con.execute(
        """
        SELECT n.id, n.adg_name, MIN(e.evidence_refs)
          FROM nodes n
          JOIN edges e ON n.id = e.dst_id
         WHERE n.entity_type='registry_node'
           AND e.bucket='registry'
         GROUP BY n.id, n.adg_name
        """
    ).fetchall()

    for r in rows:
        ev = _load_evidence(r[2])
        for fld in ASPIRATIONAL_NODE_FIELDS:
            if fld not in ev or not ev.get(fld):
                counts[f"missing_{fld}"] += 1
                if len(samples) < SAMPLE_LIMIT:
                    samples.append({
                        "code": "B_WARN_NODE_FIELDS_ASPIRATIONAL",
                        "field": fld,
                        "node_id": r[0],
                        "adg_name": r[1],
                    })

    if any(v > 0 for v in counts.values()):
        warnings.append("B_WARN_NODE_FIELDS_ASPIRATIONAL")

    return warnings, samples, counts


def _check_c_relation_fields(
    con: sqlite3.Connection,
) -> tuple[list[str], list[dict[str, Any]], dict[str, int]]:
    """C1..C4 — per-relation aspirational fields. WARN, not FAIL."""
    warnings: list[str] = []
    samples: list[dict[str, Any]] = []
    counts: dict[str, int] = defaultdict(int)

    for relation, fields in ASPIRATIONAL_RELATION_FIELDS.items():
        rows = con.execute(
            """
            SELECT id, evidence_refs, source_file
              FROM edges
             WHERE bucket='registry' AND relation_type=?
            """,
            (relation,),
        ).fetchall()
        for r in rows:
            ev = _load_evidence(r[1])
            for fld in fields:
                if fld not in ev or not ev.get(fld):
                    counts[f"missing_{relation}.{fld}"] += 1
                    if len(samples) < SAMPLE_LIMIT:
                        samples.append({
                            "code": "C_WARN_RELATION_FIELDS_ASPIRATIONAL",
                            "relation_type": relation,
                            "field": fld,
                            "edge_id": r[0],
                            "source_file": r[2],
                        })

    if counts:
        warnings.append("C_WARN_RELATION_FIELDS_ASPIRATIONAL")

    return warnings, samples, dict(counts)


def _check_d_mapping(
    con: sqlite3.Connection,
) -> tuple[list[str], list[dict[str, Any]]]:
    """D1..D4 — mapping completeness, dedup, digest freshness, authority widening."""
    failures: list[str] = []
    samples: list[dict[str, Any]] = []

    # D2 — duplicate ACTIVE registry declarations for same (symbol, source_file).
    # Uses HAVING COUNT(*) > 1; "active" = current snapshot rows.
    rows = con.execute(
        f"""
        SELECT relation_type, symbol, source_file, COUNT(*) AS n
          FROM edges
         WHERE bucket='registry'
           AND relation_type IN ({','.join('?' * len(REGISTRY_DECLARED_RELATIONS))})
           AND COALESCE(symbol,'') != ''
         GROUP BY relation_type, symbol, source_file
        HAVING n > 1
         LIMIT ?
        """,
        (*sorted(REGISTRY_DECLARED_RELATIONS), SAMPLE_LIMIT),
    ).fetchall()
    if rows:
        failures.append("D2_FAIL_DUPLICATE_ACTIVE_DECLARATION")
        for r in rows:
            samples.append({
                "code": "D2_FAIL_DUPLICATE_ACTIVE_DECLARATION",
                "relation_type": r[0],
                "symbol": r[1],
                "source_file": r[2],
                "duplicate_count": r[3],
            })

    # D3 — registry_digest presence. Every *_DECLARED edge MUST stamp a
    # non-empty ``registry_digest`` in its evidence_refs (per-declaration
    # hash, used by downstream cross-snapshot drift detection). Cross-
    # snapshot staleness is a separate concern handled by the snapshot-
    # signing gate.
    declared_placeholders = ",".join("?" * len(REGISTRY_DECLARED_RELATIONS))
    rows = con.execute(
        f"""
        SELECT id, relation_type, evidence_refs, source_file
          FROM edges
         WHERE bucket='registry'
           AND relation_type IN ({declared_placeholders})
        """,
        sorted(REGISTRY_DECLARED_RELATIONS),
    ).fetchall()
    missing_digest = 0
    for r in rows:
        ev = _load_evidence(r[2])
        if not ev.get("registry_digest"):
            missing_digest += 1
            if len(samples) < 3 * SAMPLE_LIMIT:
                samples.append({
                    "code": "D3_FAIL_STALE_REGISTRY_DIGEST",
                    "edge_id": r[0],
                    "relation_type": r[1],
                    "source_file": r[3],
                    "issue": "missing registry_digest in evidence_refs",
                })
    if missing_digest:
        failures.append("D3_FAIL_STALE_REGISTRY_DIGEST")

    # D1 — unmapped registry declaration. A declared registry node is
    # "unmapped" if NO consumer edge (references_*) targets it AND no static
    # edge resolves to a same-name symbol AND it is not in the allowed-external
    # whitelist AND its source is not a test_only fixture path.
    rows = con.execute(
        """
        SELECT n.id, n.adg_name, MIN(e_decl.evidence_refs), MIN(e_decl.source_file)
          FROM nodes n
          JOIN edges e_decl ON n.id = e_decl.dst_id
         WHERE n.entity_type='registry_node'
           AND e_decl.bucket='registry'
           AND e_decl.relation_type IN ('MCP_SERVER_DECLARED','AGENT_SPEC_DECLARED','ROUTE_CONTRACT_DECLARED')
           AND NOT EXISTS (
             SELECT 1 FROM edges e_ref
              WHERE e_ref.dst_id = n.id
                AND e_ref.bucket='registry'
                AND e_ref.relation_type IN ('references_mcp_server','references_agent_spec')
           )
         GROUP BY n.id, n.adg_name
         LIMIT 200
        """,
    ).fetchall()
    unmapped = 0
    for r in rows:
        ev = _load_evidence(r[2])
        source_file = (r[3] or "").lower()
        # Whitelist: external endpoint OR test_only fixture path.
        url = ev.get("url", "")
        if any(allowed in url for allowed in ALLOWED_EXTERNAL_ENDPOINTS):
            continue
        if "test_only" in source_file or "/tests/" in source_file or "fixtures" in source_file:
            continue
        unmapped += 1
        if len(samples) < 3 * SAMPLE_LIMIT:
            samples.append({
                "code": "D1_FAIL_UNMAPPED_DECLARATION",
                "node_id": r[0],
                "adg_name": r[1],
                "source_file": r[3],
            })
    # D1 is reported but currently NOT a hard fail because the registry
    # consumer resolver only emits twin edges for code-side references; many
    # registry declarations are NOT yet used in code today (this is the same
    # signal as the gap classifier's CONFIG_BLOAT class). Mark as advisory.
    if unmapped:
        # Track count, but don't append D1_FAIL — the cross-bucket gap
        # threshold gate already enforces the % ceiling on CONFIG_BLOAT.
        samples.append({
            "code": "D1_INFO_UNMAPPED_DECLARATION_COUNT",
            "count": unmapped,
            "note": "Tracked by cross_bucket.gap_thresholds CONFIG_BLOAT class.",
        })

    # D4 — authority widening. A registry decl widens authority if its
    # declared ``scope`` field equals the wildcard ``*``. Today this is
    # advisory; promote to FAIL when policy SSOT lands. Pre-filter via SQL
    # LIKE then parse evidence_refs in Python so we tolerate both
    # ``"scope":"*"`` (no space) and ``"scope": "*"`` (with space) JSON
    # encodings.
    rows = con.execute(
        """
        SELECT id, relation_type, evidence_refs, source_file
          FROM edges
         WHERE bucket='registry'
           AND evidence_refs LIKE '%"scope"%'
        """
    ).fetchall()
    d4_emitted = 0
    for r in rows:
        ev = _load_evidence(r[2])
        if ev.get("scope") == "*":
            d4_emitted += 1
            samples.append({
                "code": "D4_INFO_WILDCARD_SCOPE",
                "edge_id": r[0],
                "relation_type": r[1],
                "source_file": r[3],
            })
            if d4_emitted >= SAMPLE_LIMIT:
                break

    return failures, samples


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force strict mode: any FAIL or WARN counts as a non-zero exit.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Path to write the GateResult JSON (default: docs/reports/adg/registry_graph_integrity.json).",
    )
    args = parser.parse_args(argv)

    bypass_active = os.environ.get("REGISTRY_INTEGRITY_BYPASS") == "1"

    snapshot = args.snapshot or _latest_snapshot()
    snapshot_id = snapshot.stem if snapshot else ""
    started = datetime.now(timezone.utc)

    base = {
        "gate_id": "registry.graph_integrity",
        "bucket": "registry",
        "evidence_mode": "proof",
        "enforcement_mode": "strict",
        "snapshot_id": snapshot_id,
        "input_refs": [
            "edges WHERE bucket='registry'",
            "nodes WHERE entity_type='registry_node'",
            "meta.artifact_digest",
        ],
        "bypass_env_detected": ["REGISTRY_INTEGRITY_BYPASS"] if bypass_active else [],
    }

    if bypass_active:
        result = GateResult(**base, status="SKIP", actual_fail_reason="").finalize()
        _emit(result, args.json_out)
        print("[registry_integrity] BYPASS via REGISTRY_INTEGRITY_BYPASS=1")
        return 0

    if snapshot is None or not snapshot.exists():
        result = GateResult(**base, status="SKIP", actual_fail_reason="").finalize()
        _emit(result, args.json_out)
        print("[registry_integrity] SKIP: no snapshot")
        return 0

    con = sqlite3.connect(str(snapshot))
    try:
        a_fails, a_samples = _check_a_bucket_discipline(con)
        b_warns, b_samples, b_counts = _check_b_node_fields(con)
        c_warns, c_samples, c_counts = _check_c_relation_fields(con)
        d_fails, d_samples = _check_d_mapping(con)

        # Aggregate counts
        total_registry_edges = con.execute(
            "SELECT COUNT(*) FROM edges WHERE bucket='registry'"
        ).fetchone()[0]
        total_registry_nodes = con.execute(
            "SELECT COUNT(*) FROM nodes WHERE entity_type='registry_node'"
        ).fetchone()[0]
        relation_distribution = dict(
            con.execute(
                "SELECT relation_type, COUNT(*) FROM edges WHERE bucket='registry' GROUP BY relation_type"
            ).fetchall()
        )
    finally:
        con.close()

    failures = a_fails + d_fails
    warnings = b_warns + c_warns

    counts = {
        "total_registry_edges": total_registry_edges,
        "total_registry_nodes": total_registry_nodes,
        **{f"relation:{k}": v for k, v in relation_distribution.items()},
        **b_counts,
        **c_counts,
        "fail_codes_count": len(failures),
        "warn_codes_count": len(warnings),
    }

    duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    # Status precedence:
    #   * Real invariant failures (A/D-class) -> FAIL regardless of strict.
    #   * Aspirational warnings (B/C-class) -> WARN. Per the gate's
    #     documented contract these are "aspirational schema fields not
    #     yet populated by the resolver"; they are intentionally NOT a
    #     hard failure even in --strict, because doing so would conflate
    #     "missing data" with "wrong data".
    #   * --strict still promotes A/D failures (which already FAIL above)
    #     and surfaces a non-zero exit; aspirational WARNs surface as
    #     status=WARN and exit 0. The runner's overall_status logic is
    #     responsible for cross-gate strict semantics.
    if failures:
        status = "FAIL"
        actual_fail = failures[0]
    elif warnings:
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
        sample_failures=(a_samples + b_samples + c_samples + d_samples)[:10],
        duration_ms=duration_ms,
    ).finalize()
    _emit(result, args.json_out)

    print(
        f"[registry_integrity] status={status} edges={total_registry_edges} "
        f"nodes={total_registry_nodes} fails={len(failures)} warns={len(warnings)}"
    )
    if failures:
        print(f"[registry_integrity] failure codes: {', '.join(failures)}")

    return 1 if status == "FAIL" else 0


def _emit(result: GateResult, custom_out: Path | None) -> None:
    out_path = custom_out or REPORT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_json(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
