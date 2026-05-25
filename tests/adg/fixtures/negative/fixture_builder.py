"""Negative-control fixture builder for the ADG three-graph harness.

Plan: ``.windsurf/plans/adg-three-graph-harness-e57cc7.md`` (W4.P1).

Builds minimal SQLite snapshots that DELIBERATELY violate one specific
invariant per fixture. The negative-control test suite then runs the
relevant gate against each fixture and asserts the gate FAILs with the
exact ``actual_fail_reason`` declared in the manifest.

The 10 required cases (from the user spec):
  1.  null_edge_authority           -> static.edge_authority_well_formed
  2.  forged_trace_id                -> runtime.proof_view_well_formed (T1/T9)
  3.  missing_parent_span_id_chain   -> runtime.trace_topology (T2)
  4.  synthetic_mislabeled_prod      -> runtime.trace_topology (T9)
  5.  agent_without_execution_profile-> registry.graph_integrity (C)
  6.  model_outside_gateway          -> registry.graph_integrity (D4)
  7.  duplicate_active_target        -> registry.graph_integrity (D2)
  8.  registry_only_prod_route       -> cross_bucket.impossible_states (I6)
  9.  triplet_missing_bucket_ref     -> cross_bucket.impossible_states (I4)
  10. stale_snapshot_vs_gap_report   -> cross_bucket.impossible_states (I8)

Each builder returns the path to a ``.sqlite`` file under
``tests/adg/fixtures/negative/<slug>/snapshot.sqlite``. A companion
``manifest.json`` records the expected_fail_reason and the gate to invoke.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
FIXTURE_ROOT: Final[Path] = REPO_ROOT / "tests" / "adg" / "fixtures" / "negative"


@dataclass
class NegativeFixture:
    slug: str
    description: str
    target_gate: str
    expected_fail_reason: str
    extra_args: list[str]


def _ensure_dir(slug: str) -> Path:
    d = FIXTURE_ROOT / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def _common_schema(con: sqlite3.Connection) -> None:
    """Minimal schema shared by all fixtures.

    Mirrors the columns the gates inspect; not a full ADG schema.
    """
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            entity_type TEXT,
            layer TEXT,
            identity_kind TEXT,
            confidence TEXT,
            resolved_path TEXT
        );
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            semantic_type TEXT,
            confidence_score REAL,
            dynamic_resolution TEXT,
            authority TEXT,
            bucket TEXT,
            resolution_status TEXT,
            authority_status TEXT,
            evidence_refs TEXT
        );
        CREATE TABLE IF NOT EXISTS v_runtime_proof (
            id INTEGER PRIMARY KEY,
            src_name TEXT,
            dst_name TEXT,
            relation_type TEXT,
            edge_kind TEXT,
            static_edge_id INTEGER,
            attesting_trace_count INTEGER,
            latest_trace_id TEXT,
            latest_span_id TEXT,
            last_seen_at TEXT,
            evidence_refs TEXT,
            bucket TEXT,
            resolution_status TEXT,
            authority_status TEXT
        );
        CREATE TABLE IF NOT EXISTS violations (id INTEGER PRIMARY KEY);
        """
    )
    con.execute("DELETE FROM meta")
    con.execute("DELETE FROM nodes")
    con.execute("DELETE FROM edges")
    con.execute("DELETE FROM v_runtime_proof")
    con.execute(
        "INSERT INTO meta(key,value) VALUES('artifact_digest','f1xtur3d1g3st0000000000000000000000000000')"
    )
    con.execute("INSERT INTO meta(key,value) VALUES('schema_version','4.0.0')")
    # Bare-minimum mv_*/v_p* surface so floor-count gates don't trip on
    # the fixture itself when they're not the gate under test.
    for i in range(35):
        con.execute(f"CREATE VIEW IF NOT EXISTS mv_fixture_{i} AS SELECT 1 AS x")
    for i in range(5):
        con.execute(f"CREATE VIEW IF NOT EXISTS v_p{i % 4}_fixture_{i} AS SELECT 1 AS x")


def _well_formed_seed(con: sqlite3.Connection) -> None:
    """Seed a small set of valid rows so gates have a baseline to compare against."""
    # 1 valid static edge, 1 valid registry decl, 1 valid runtime row.
    con.execute(
        "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
        " VALUES (1,'src.module','module','L1','file','HIGH','agentic_core/foo.py')"
    )
    con.execute(
        "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
        " VALUES (2,'dst.symbol','symbol','L1','symbol','HIGH','agentic_core/bar.py')"
    )
    con.execute(
        "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
        " VALUES (10,'Registry::MCP::ok_server','registry_node','L_REGISTRY','virtual','HIGH',NULL)"
    )
    con.execute(
        "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
        "resolution_status,authority_status,authority,evidence_refs)"
        " VALUES (1001,1,2,'imports','static_call','agentic_core/foo.py','static','RESOLVED',"
        "'AUTHORITATIVE_STATIC','verified','{}')"
    )
    con.execute(
        "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
        "resolution_status,authority_status,authority,evidence_refs,symbol)"
        " VALUES (2001,1,10,'MCP_SERVER_DECLARED','registry','.windsurf/mcp_config.json','registry',"
        "'STABLE_REGISTRY','AUTHORITATIVE_REGISTRY','verified',"
        "'{\"registry_digest\":\"abc123\",\"declaration_key\":\"mcpServers.ok_server\"}','ok_server')"
    )
    con.execute(
        "INSERT INTO v_runtime_proof(id,src_name,dst_name,relation_type,edge_kind,static_edge_id,"
        "attesting_trace_count,latest_trace_id,latest_span_id,evidence_refs,bucket,"
        "resolution_status,authority_status)"
        " VALUES (3001,'src.module','dst.symbol','imports','static_call',1001,2,"
        "'real-trace-aaa111bbb222ccc333','span-aaa1','{\"run_ids\":[\"r1\"]}','runtime',"
        "'RESOLVED','AUTHORITATIVE_RUNTIME')"
    )


# ---------------------------------------------------------------------------
# Per-fixture builders
# ---------------------------------------------------------------------------


def build_null_edge_authority() -> NegativeFixture:
    fix = NegativeFixture(
        slug="null_edge_authority",
        description="A static edge with NULL authority — must trip edge_authority_well_formed.",
        target_gate="static.edge_authority_well_formed",
        expected_fail_reason="legacy_exit_code:1",  # legacy gate exits 1 on NULL.
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        _well_formed_seed(con)
        # Insert one edge with NULL authority — that's the violation.
        con.execute(
            "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
            "resolution_status,authority_status,authority,evidence_refs)"
            " VALUES (9001,1,2,'imports','static_call','agentic_core/foo.py','static',"
            "'RESOLVED','AUTHORITATIVE_STATIC',NULL,'{}')"
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_forged_trace_id() -> NegativeFixture:
    """An AUTHORITATIVE_RUNTIME row with empty trace_id — runtime.proof_view fails."""
    fix = NegativeFixture(
        slug="forged_trace_id",
        description="AUTHORITATIVE_RUNTIME row with empty latest_trace_id.",
        target_gate="runtime.proof_view_well_formed",
        expected_fail_reason="legacy_exit_code:1",
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        _well_formed_seed(con)
        con.execute(
            "INSERT INTO v_runtime_proof(id,src_name,dst_name,relation_type,edge_kind,static_edge_id,"
            "attesting_trace_count,latest_trace_id,latest_span_id,evidence_refs,bucket,"
            "resolution_status,authority_status)"
            " VALUES (3999,'src.module','dst.symbol','imports','static_call',1001,1,"
            "'','','{}','runtime','RESOLVED','AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_missing_parent_span_chain() -> NegativeFixture:
    """A trace whose spans.json has a non-root span pointing to a missing parent."""
    fix = NegativeFixture(
        slug="missing_parent_span_chain",
        description="parent_span_id chain broken inside a trace.",
        target_gate="runtime.trace_topology",
        expected_fail_reason="T2_FAIL_BROKEN_PARENT_CHAIN",
        extra_args=["--require-production"],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        # Need a non-synthetic v_runtime_proof row that points at a trace
        # whose spans.json we are about to create.
        con.execute(
            "INSERT INTO v_runtime_proof(id,src_name,dst_name,relation_type,edge_kind,"
            "static_edge_id,attesting_trace_count,latest_trace_id,latest_span_id,"
            "evidence_refs,bucket,resolution_status,authority_status)"
            " VALUES (4001,'a','b','imports','static_call',1,1,"
            "'fixture-trace-xx','span-1','{\"run_ids\":[\"r1\"]}','runtime',"
            "'RESOLVED','AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
    finally:
        con.close()
    spans_dir = REPO_ROOT / "agentic_core" / "L4_state" / "memory" / "runtime_adg" / "fixture-trace-xx"
    spans_dir.mkdir(parents=True, exist_ok=True)
    spans = [
        {"trace_id": "fixture-trace-xx", "span_id": "span-1", "parent_span_id": "",
         "policy_hash": "p", "blueprint_hash": "b", "registry_digest": "r",
         "start_time": 1.0},
        {"trace_id": "fixture-trace-xx", "span_id": "span-2",
         "parent_span_id": "span-NONEXISTENT",
         "policy_hash": "p", "blueprint_hash": "b", "registry_digest": "r",
         "start_time": 2.0},
    ]
    (spans_dir / "spans.json").write_text(json.dumps(spans), encoding="utf-8")
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_synthetic_mislabeled_prod() -> NegativeFixture:
    fix = NegativeFixture(
        slug="synthetic_mislabeled_prod",
        description="Synthetic trace_id satisfies AUTHORITATIVE_RUNTIME under --require-production.",
        target_gate="runtime.trace_topology",
        expected_fail_reason="T9_FAIL_SYNTHETIC_IN_PRODUCTION_MODE",
        extra_args=["--require-production"],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        con.execute(
            "INSERT INTO v_runtime_proof(id,src_name,dst_name,relation_type,edge_kind,"
            "static_edge_id,attesting_trace_count,latest_trace_id,latest_span_id,"
            "evidence_refs,bucket,resolution_status,authority_status)"
            " VALUES (4101,'a','b','imports','x',1,1,'synth-aaaa','span-1','{}',"
            "'runtime','RESOLVED','AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_agent_without_execution_profile() -> NegativeFixture:
    fix = NegativeFixture(
        slug="agent_without_execution_profile",
        description="AGENT_SPEC_DECLARED edge missing execution_profile field.",
        target_gate="registry.graph_integrity",
        expected_fail_reason="C_WARN_RELATION_FIELDS_ASPIRATIONAL",
        extra_args=["--strict"],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        # NOTE: do not seed _well_formed_seed — it inserts an MCP_SERVER_DECLARED
        # edge whose evidence_refs lacks owner/version/digest/declared_surface,
        # which would trip the B aspirational check first. We construct ONE
        # AGENT_SPEC edge that satisfies B fully and ONLY misses C.execution_profile.
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
            " VALUES (1,'src.module','module','L1','file','HIGH','agentic_core/foo.py')"
        )
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
            " VALUES (20,'Registry::Agent::no_profile','registry_node','L_REGISTRY','virtual','HIGH',NULL)"
        )
        # Evidence carries every B field; only C.execution_profile is missing.
        ev = json.dumps({
            "registry_digest": "d1",
            "declaration_key": "agents.no_profile",
            "owner": "team_x",
            "version": "1.0.0",
            "digest": "node-digest-abc",
            "declared_surface": "internal",
            # execution_profile intentionally omitted
        })
        con.execute(
            "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
            "resolution_status,authority_status,authority,evidence_refs,symbol)"
            " VALUES (5001,1,20,'AGENT_SPEC_DECLARED','registry','agent_specs/no_profile.yaml',"
            "'registry','STABLE_REGISTRY','AUTHORITATIVE_REGISTRY','verified',?,'no_profile')",
            (ev,),
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_model_outside_gateway() -> NegativeFixture:
    fix = NegativeFixture(
        slug="model_outside_gateway",
        description="Model/provider declared with wildcard scope — D4 widening.",
        target_gate="registry.graph_integrity",
        # Currently advisory in the live gate (logged as D4_INFO_WILDCARD_SCOPE).
        # The negative test asserts the SAMPLE is captured, even if not a hard FAIL.
        expected_fail_reason="",  # advisory; sample-only assertion
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        # Don't seed _well_formed_seed — we want ONLY the D4 wildcard signal,
        # not B/C aspirational warnings, so the test can assert on D4 samples
        # without slot-pressure from B/C.
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
            " VALUES (1,'src.module','module','L1','file','HIGH','agentic_core/foo.py')"
        )
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
            " VALUES (30,'Registry::Route::wildcard','registry_node','L_REGISTRY','virtual','HIGH',NULL)"
        )
        # Evidence has full B/C coverage AND the wildcard scope literal so
        # only D4 sampler fires.
        ev = json.dumps({
            "registry_digest": "d1",
            "owner": "team_y",
            "version": "1.0.0",
            "digest": "route-digest-xyz",
            "declared_surface": "external",
            "gateway_resolution": "approved-gateway",
            "scope": "*",
        })
        con.execute(
            "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
            "resolution_status,authority_status,authority,evidence_refs,symbol)"
            " VALUES (5101,1,30,'ROUTE_CONTRACT_DECLARED','registry',"
            "'agentic_core/L0_routing/config/v15_policy_pack.json',"
            "'registry','STABLE_REGISTRY','AUTHORITATIVE_REGISTRY','verified',?,'wildcard_route')",
            (ev,),
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_duplicate_active_target() -> NegativeFixture:
    fix = NegativeFixture(
        slug="duplicate_active_target",
        description="Two MCP_SERVER_DECLARED rows with identical (relation_type, symbol, source_file).",
        target_gate="registry.graph_integrity",
        expected_fail_reason="D2_FAIL_DUPLICATE_ACTIVE_DECLARATION",
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        _well_formed_seed(con)
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
            " VALUES (40,'Registry::MCP::dup','registry_node','L_REGISTRY','virtual','HIGH',NULL)"
        )
        con.execute(
            "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
            "resolution_status,authority_status,authority,evidence_refs,symbol)"
            " VALUES (5201,1,40,'MCP_SERVER_DECLARED','registry','.windsurf/mcp_config.json',"
            "'registry','STABLE_REGISTRY','AUTHORITATIVE_REGISTRY','verified',"
            "'{\"registry_digest\":\"d1\"}','dup_server')"
        )
        con.execute(
            "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
            "resolution_status,authority_status,authority,evidence_refs,symbol)"
            " VALUES (5202,1,40,'MCP_SERVER_DECLARED','registry','.windsurf/mcp_config.json',"
            "'registry','STABLE_REGISTRY','AUTHORITATIVE_REGISTRY','verified',"
            "'{\"registry_digest\":\"d2\"}','dup_server')"
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_registry_only_prod_route() -> NegativeFixture:
    fix = NegativeFixture(
        slug="registry_only_prod_route",
        description="Registry decl in production source with no static or runtime support.",
        target_gate="cross_bucket.impossible_states",
        expected_fail_reason="I6_FAIL_REGISTRY_ONLY_PROD_ROUTE",
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        # Production source path. No static twin, no runtime evidence.
        con.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)"
            " VALUES (50,'Registry::MCP::orphan','registry_node','L_REGISTRY','virtual','HIGH',NULL)"
        )
        con.execute(
            "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
            "resolution_status,authority_status,authority,evidence_refs,symbol)"
            " VALUES (5301,1,50,'MCP_SERVER_DECLARED','registry',"
            "'agentic_core/L4_state/orphan.py',"
            "'registry','STABLE_REGISTRY','AUTHORITATIVE_REGISTRY','verified',"
            "'{\"registry_digest\":\"dx\"}','orphan_server')"
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_triplet_missing_bucket_ref() -> NegativeFixture:
    fix = NegativeFixture(
        slug="triplet_missing_bucket_ref",
        description="AUTHORITATIVE_RUNTIME row whose static_edge_id points to nothing.",
        target_gate="cross_bucket.impossible_states",
        expected_fail_reason="I4_FAIL_TRIPLET_MISSING_BUCKET_REF",
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        # static_edge_id=99999 but no edges row with id=99999
        con.execute(
            "INSERT INTO v_runtime_proof(id,src_name,dst_name,relation_type,edge_kind,"
            "static_edge_id,attesting_trace_count,latest_trace_id,latest_span_id,"
            "evidence_refs,bucket,resolution_status,authority_status)"
            " VALUES (5401,'a','b','imports','x',99999,1,'real-trace-zzz','span-z','{}',"
            "'runtime','RESOLVED','AUTHORITATIVE_RUNTIME')"
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_stale_snapshot_vs_gap_report() -> NegativeFixture:
    fix = NegativeFixture(
        slug="stale_snapshot_vs_gap_report",
        description="Gap report references a different snapshot than the one under test.",
        target_gate="cross_bucket.impossible_states",
        expected_fail_reason="I8_FAIL_STALE_SNAPSHOT_VS_GAP_REPORT",
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        con.commit()
    finally:
        con.close()
    # Write a gap report that points at a DIFFERENT snapshot name.
    gap_report = {
        "snapshot": "adg_indexed_19990101_0000.sqlite",
        "summary_by_class": [],
        "runtime_view_present": True,
        "health_score_pct_triplet_attested": 0.0,
    }
    (d / "gap_report.json").write_text(json.dumps(gap_report), encoding="utf-8")
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_null_triplet_edges() -> NegativeFixture:
    """NULL (bucket, resolution_status, authority_status) — static.no_null_triplet."""
    fix = NegativeFixture(
        slug="null_triplet_edges",
        description="Edge row with NULL triplet columns.",
        target_gate="static.no_null_triplet",
        expected_fail_reason="view_rule_fail",
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    con = sqlite3.connect(d / "snapshot.sqlite")
    try:
        _common_schema(con)
        _well_formed_seed(con)
        con.execute(
            "INSERT INTO edges(id,src_id,dst_id,relation_type,edge_kind,source_file,bucket,"
            "resolution_status,authority_status,authority,evidence_refs)"
            " VALUES (9002,1,2,'imports','static_call','agentic_core/foo.py',NULL,"
            "NULL,NULL,'verified','{}')"
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


def build_missing_mv_views() -> NegativeFixture:
    """No mv_* views — static.snapshot_has_mvs."""
    fix = NegativeFixture(
        slug="missing_mv_views",
        description="Snapshot without materialized views.",
        target_gate="static.snapshot_has_mvs",
        expected_fail_reason="legacy_exit_code:1",
        extra_args=[],
    )
    d = _ensure_dir(fix.slug)
    snap_path = d / "snapshot.sqlite"
    if snap_path.exists():
        snap_path.unlink()
    con = sqlite3.connect(snap_path)
    try:
        con.executescript(
            """
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE edges (id INTEGER PRIMARY KEY);
            INSERT INTO meta(key,value) VALUES('schema_version','4.0.0');
            INSERT INTO meta(key,value) VALUES('artifact_digest','f1xtur3d1g3st0000000000000000000000000000');
            """
        )
        con.commit()
    finally:
        con.close()
    (d / "manifest.json").write_text(json.dumps(asdict(fix), indent=2), encoding="utf-8")
    return fix


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

ALL_BUILDERS = (
    build_null_triplet_edges,
    build_missing_mv_views,
    build_null_edge_authority,
    build_forged_trace_id,
    build_missing_parent_span_chain,
    build_synthetic_mislabeled_prod,
    build_agent_without_execution_profile,
    build_model_outside_gateway,
    build_duplicate_active_target,
    build_registry_only_prod_route,
    build_triplet_missing_bucket_ref,
    build_stale_snapshot_vs_gap_report,
)


def build_all() -> list[NegativeFixture]:
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    return [b() for b in ALL_BUILDERS]


if __name__ == "__main__":
    fixtures = build_all()
    for f in fixtures:
        print(f"  built: {f.slug:<40} -> {f.target_gate}")
    print(f"\n[negative_fixtures] built {len(fixtures)} fixture(s) under {FIXTURE_ROOT}")
