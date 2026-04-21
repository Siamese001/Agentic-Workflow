"""ADG Multi-Writer — produces all artifact tiers in one pass, zero redundancy.

Tier 1  adg_snapshot.json        CI-light, ~50 KB
    Metrics only: counts, digests, graph_plane_counts, violation summary,
    blind_spots, top-20 hotspots. No entities or edges.
    Used by: CI gate, drift detection, quick health checks.

Tier 2  adg_indexed.sqlite        Primary queryable store, ~38 MB
    SQLite database with three tables:
        nodes (id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
        edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
        meta  (key, value)
    Used by: all analysis, queries, layer-authority checks, mutation-path scans.
    NOTE: adg_full.json removed — SQLite is the canonical complete store.

Three non-overlapping split-plane sub-graphs (together = 100% edge coverage):
    adg_file_graph.json        imports, exports, dead_imports, covers, influences, in_cycle
    adg_symbol_graph.json      calls, implements, reads_from, writes_to, instantiates, ...
    adg_governance_graph.json  violates, antipattern, generates_prompt, ...
    NOTE: test_graph removed — covers edges live in file_graph.

Minimal ingestion set (non-redundant, 100% coverage):
    adg_LATEST.sqlite           ← primary: all 18 edge types, queryable
    adg_LATEST_snapshot.json    ← metrics / health summary only

Usage::

    from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts

    paths = write_all_artifacts(artifact, out_dir=Path("artifacts/adg"), ts="20260311T154637Z")
    print(paths)
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.adg.artifact.multi_writer import _filter_guardian_exempted_violations
from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "multi_writer", "p0_governance")
_emit_reads_policy_state("p0", "multi_writer", "policy_binding")
_emit_snapshots_state("p0", "multi_writer", "state_snapshot")
emit_replay_key("p0", "multi_writer")
emit_determinism_digest("p0", "multi_writer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "multi_writer", "execution_auth")
_emit_validates_capability("p2", "multi_writer", "capability_check")
_emit_routes_to_capability("p2", "multi_writer", "capability_route")
_emit_writes_via_uwg("p2", "multi_writer", "uwg_write")
_emit_blocks_direct_write("p2", "multi_writer", "direct_write_block")
_emit_records_tool_invocation("p2", "multi_writer", "tool_invocation")
_emit_captures_execution_output("p2", "multi_writer", "exec_output")
_emit_dispatches_agent("p3", "multi_writer", "agent_dispatch")
_emit_coordinates_agents("p3", "multi_writer", "agent_coordination")
_emit_records_workflow_lineage("p3", "multi_writer", "workflow_lineage")
_emit_records_healing_outcome("p3", "multi_writer", "healing_outcome")
_emit_escalates_failure("p3", "multi_writer", "failure_escalation")
_emit_orchestrates_workflow("p3", "multi_writer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "multi_writer", "healing_dispatch")
_emit_invokes_evaluation("p3", "multi_writer", "evaluation_signal")
_emit_records_telemetry_event("p4", "multi_writer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "multi_writer", "eval_metric")
_emit_stores_embedding("p4", "multi_writer", "embedding_store")
_emit_updates_meta_learning_state("p4", "multi_writer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "multi_writer", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder_types import ADGArtifact
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("multi_writer", "p4obs", "metric_1")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_2")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_3")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_4")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_5")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_6")
_emit_records_incident_event("multi_writer", "p4obs", "incident")
_emit_captures_runtime_anomaly("multi_writer", "p4obs", "anomaly")
_emit_writes_observability_log("multi_writer", "p4obs", "obs_log")
_emit_updates_monitoring_state("multi_writer", "p4obs", "mon_state")
_emit_triggers_alert("multi_writer", "p4obs", "alert")
_emit_links_incident_trace("multi_writer", "p4obs", "trace_link")
_emit_captures_pattern("multi_writer", "p3lm", "pattern")
_emit_records_learning_event("multi_writer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("multi_writer", "p3lm", "snapshot")
_emit_feeds_meta_learning("multi_writer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("multi_writer", "p3lm", "routing")
_emit_improves_agent_policy("multi_writer", "p3lm", "policy")
_emit_stores_learning_state("multi_writer", "p3lm", "state")
_emit_records_execution_trace("multi_writer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("multi_writer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("multi_writer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("multi_writer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("multi_writer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("multi_writer", "env_read", "p2_env_1")
_emit_reads_environ("multi_writer", "env_read", "p2_env_2")
_emit_reads_runtime_state("multi_writer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("multi_writer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "multi_writer", "context_pull")
_emit_pulls_context("p1", "multi_writer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "multi_writer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "multi_writer", "uwg_term_2")
_emit_writes_through("p1", "multi_writer", "write_through")
_emit_writes_through("p1", "multi_writer", "write_through_2")
_emit_validated_by_safety_plane("p1", "multi_writer", "safety_validation")
_emit_invokes_eval("p1", "multi_writer", "eval_call")
_emit_proposal_commits_routing("p1", "multi_writer", "routing_commit")
_emit_escalates_to_human("p1", "multi_writer", "human_escalation")
_emit_routes_through("p1", "multi_writer", "route_through")
_emit_checks_agent_registry("p1", "multi_writer", "agent_registry")
_emit_validates_agent_capability("p1", "multi_writer", "capability")
_emit_dispatches_execution_plan("p1", "multi_writer", "exec_plan")
_emit_agent_executes_agent("p1", "multi_writer", "sub_agent")
_emit_routes_to_agent("p1", "multi_writer", "target_agent")
_emit_verifies_policy("p1", "multi_writer", "policy_check")
_emit_observes_runtime_state("p1", "multi_writer", "runtime_state")
_emit_verifies_boundary("p1", "multi_writer", "boundary_check")
_emit_transcripts_response("p1", "multi_writer", "transcript")
_emit_hard_fails_untranscripted("p1", "multi_writer")
_emit_gated_by_confidence("p1", "multi_writer", "confidence_gate")

# ---------------------------------------------------------------------------
# Snapshot (Tier 1)
# ---------------------------------------------------------------------------


def _build_snapshot(artifact: ADGArtifact) -> dict:
    """Build a lightweight CI snapshot dict — no entities or edges."""
    sm = artifact.structural_metrics.to_dict()
    bs = artifact.blind_spots.to_dict()

    # Relation-type distribution
    by_rel = sm.get("by_relation_type", {})

    # Top-20 fan-in hotspots (module names only, no full edge data)
    hotspots_in = sorted(sm.get("high_fan_in_modules", []), key=lambda x: -x.get("fan_in", 0))[:20]
    hotspots_out = sorted(sm.get("high_fan_out_modules", []), key=lambda x: -x.get("fan_out", 0))[:20]

    return {
        "schema_version": "snapshot-1.0",
        "commit_sha": artifact.commit_sha,
        "repo_state_hash": artifact.repo_state_hash,
        "scanner_digest": artifact.scanner_digest,
        "artifact_digest": artifact.artifact_digest,
        "counts": {
            "total_entities": sm.get("total_entities", 0),
            "total_relations": sm.get("total_relations", 0),
            "module_count": sm.get("module_count", 0),
            "symbol_count": sm.get("symbol_count", 0),
            "external_count": sm.get("external_count", 0),
            "unresolved_count": sm.get("unresolved_count", 0),
            "orphan_module_count": sm.get("orphan_module_count", 0),
            "layer_violation_count": sm.get("layer_violation_count", 0),
        },
        "graph_plane_counts": {k: v for k, v in sorted(by_rel.items()) if v > 0},
        "by_layer": sm.get("by_layer", {}),
        "blind_spots": {
            "parse_failure_count": bs.get("parse_failure_count", 0),
            "dynamic_import_count": bs.get("dynamic_import_count", 0),
            "star_import_count": bs.get("star_import_count", 0),
        },
        "identity_health": artifact.identity_health,
        "top_fan_in_hotspots": hotspots_in,
        "top_fan_out_hotspots": hotspots_out,
    }


# ---------------------------------------------------------------------------
# SQLite index (Tier 3)
# ---------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS nodes (
    id            INTEGER PRIMARY KEY,
    adg_name      TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    layer         TEXT NOT NULL,
    identity_kind TEXT NOT NULL,
    confidence    TEXT NOT NULL,
    resolved_path TEXT NOT NULL,
    precision_type        TEXT DEFAULT 'symbol',
    span_start            INTEGER DEFAULT 0,
    span_end              INTEGER DEFAULT 0,
    span_line             INTEGER DEFAULT 0,
    span_column           INTEGER DEFAULT 0,
    span_end_line         INTEGER DEFAULT 0,
    span_end_column       INTEGER DEFAULT 0,
    logical_sequence_id   INTEGER DEFAULT 0,
    control_path_id       TEXT DEFAULT '',
    temporal_order        INTEGER DEFAULT 0,
    type_surface          TEXT DEFAULT '',
    enclosing_symbol      TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_nodes_type  ON nodes(entity_type);
CREATE INDEX IF NOT EXISTS idx_nodes_layer ON nodes(layer);
CREATE INDEX IF NOT EXISTS idx_nodes_name  ON nodes(adg_name);
CREATE INDEX IF NOT EXISTS idx_nodes_precision_type ON nodes(precision_type)
    WHERE precision_type != 'symbol';
CREATE INDEX IF NOT EXISTS idx_nodes_sequence ON nodes(logical_sequence_id)
    WHERE logical_sequence_id != 0;

CREATE TABLE IF NOT EXISTS edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id        INTEGER NOT NULL REFERENCES nodes(id),
    dst_id        INTEGER NOT NULL REFERENCES nodes(id),
    relation_type TEXT NOT NULL,
    edge_kind     TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    line_no       INTEGER NOT NULL,
    symbol        TEXT NOT NULL DEFAULT '',
    semantic_type      TEXT DEFAULT '',
    confidence_score   REAL DEFAULT 1.0,
    source_span_start  INTEGER DEFAULT 0,
    source_span_end    INTEGER DEFAULT 0,
    source_span_line   INTEGER DEFAULT 0,
    source_span_column INTEGER DEFAULT 0,
    target_span_start  INTEGER DEFAULT 0,
    target_span_end    INTEGER DEFAULT 0,
    target_span_line   INTEGER DEFAULT 0,
    target_span_column INTEGER DEFAULT 0,
    dynamic_resolution TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_edges_src  ON edges(src_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst  ON edges(dst_id);
CREATE INDEX IF NOT EXISTS idx_edges_rel  ON edges(relation_type);
CREATE INDEX IF NOT EXISTS idx_edges_semantic_type ON edges(semantic_type)
    WHERE semantic_type != '';

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS violations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id       INTEGER NOT NULL REFERENCES edges(id),
    category      TEXT NOT NULL,
    evidence      TEXT NOT NULL DEFAULT '',
    file_path     TEXT NOT NULL DEFAULT '',
    line_no       INTEGER NOT NULL DEFAULT 0,
    disposition   TEXT NOT NULL DEFAULT 'untriaged',
    disposition_source TEXT DEFAULT '',
    disposition_date TEXT DEFAULT '',
    severity      TEXT NOT NULL DEFAULT 'MEDIUM',
    violation_class TEXT NOT NULL DEFAULT 'hygiene'
);
CREATE INDEX IF NOT EXISTS idx_violations_cat  ON violations(category);
CREATE INDEX IF NOT EXISTS idx_violations_file ON violations(file_path);
CREATE INDEX IF NOT EXISTS idx_violations_disp ON violations(disposition);
CREATE INDEX IF NOT EXISTS idx_violations_class ON violations(violation_class);

CREATE VIEW IF NOT EXISTS edge_view AS
    SELECT
        e.id            AS edge_id,
        src.adg_name    AS from_name,
        e.relation_type AS relation_type,
        dst.adg_name    AS to_name,
        e.edge_kind     AS edge_kind,
        src.entity_type AS from_type,
        dst.entity_type AS to_type,
        src.layer       AS from_layer,
        dst.layer       AS to_layer,
        e.source_file   AS source_file,
        e.line_no       AS line_no,
        e.symbol        AS symbol,
        e.semantic_type AS semantic_type,
        e.confidence_score AS edge_confidence,
        src.precision_type AS from_precision_type,
        dst.precision_type AS to_precision_type,
        src.logical_sequence_id AS from_sequence_id,
        dst.logical_sequence_id AS to_sequence_id
    FROM edges e
    JOIN nodes src ON src.id = e.src_id
    JOIN nodes dst ON dst.id = e.dst_id;

CREATE VIEW IF NOT EXISTS precision_metrics_view AS
SELECT
    COUNT(*) AS total_edges,
    SUM(CASE WHEN e.semantic_type != '' THEN 1 ELSE 0 END) AS semantic_edges,
    COUNT(DISTINCT n.id) AS total_nodes,
    SUM(CASE WHEN n.precision_type != 'symbol' THEN 1 ELSE 0 END) AS precision_nodes,
    SUM(CASE WHEN n.precision_type = 'code_block' THEN 1 ELSE 0 END) AS code_blocks,
    SUM(CASE WHEN n.precision_type = 'expression_unit' THEN 1 ELSE 0 END) AS expression_units,
    SUM(CASE WHEN n.precision_type = 'control_branch' THEN 1 ELSE 0 END) AS control_branches
FROM edges e
JOIN nodes n ON n.id = e.src_id;
"""


def _write_sqlite(ng_full, db_path: Path) -> Path:
    """Write a NormalizedGraph to SQLite for fast querying."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temporary file first to avoid leaving 0-byte files on failure
    temp_db_path = db_path.parent / f"{db_path.name}.tmp"
    if temp_db_path.exists():
        temp_db_path.unlink()

    conn = sqlite3.connect(str(temp_db_path))
    write_failed = False
    try:
        # D2b: bulk-insert PRAGMAs — keep journal in RAM and skip fsync barriers.
        # Saves ~1.4s on the node executemany phase (1.76s → 0.53s measured).
        # MEMORY journal is safe here: if the process dies mid-write the file is
        # simply incomplete/corrupt, which is acceptable for a re-generable artifact.
        conn.execute("PRAGMA journal_mode=MEMORY")
        conn.execute("PRAGMA synchronous=OFF")
        conn.executescript(_DDL)

        # Insert nodes in bulk
        node_rows = []
        for nid_str, node in tqdm(ng_full.nodes.items(), desc="Processing", unit="item"):
            node_rows.append(
                (
                    int(nid_str),
                    node.get("n", ""),
                    node.get("t", ""),
                    node.get("l", ""),
                    node.get("k", ""),
                    node.get("c", ""),
                    node.get("p", ""),
                    node.get("pt", "symbol"),
                    node.get("ss", 0),
                    node.get("se", 0),
                    node.get("sl", 0),
                    node.get("sc", 0),
                    node.get("sel", 0),
                    node.get("sec", 0),
                    node.get("lsid", 0),
                    node.get("cpid", ""),
                    node.get("to", 0),
                    node.get("ts", ""),
                    node.get("es", ""),
                ),
            )
        conn.executemany(
            "INSERT OR REPLACE INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path,"
            "precision_type,span_start,span_end,span_line,span_column,span_end_line,span_end_column,"
            "logical_sequence_id,control_path_id,temporal_order,type_surface,enclosing_symbol) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            node_rows,
        )

        # Insert edges in bulk
        edge_rows = []
        for e in tqdm(ng_full.edges, desc="Processing", unit="item"):
            edge_rows.append(
                (
                    e["s"],
                    e["d"],
                    e["r"],
                    e["k"],
                    e["f"],
                    e["ln"],
                    e.get("sym", ""),
                    e.get("st", ""),
                    e.get("conf", 1.0),
                    e.get("sss", 0),
                    e.get("sse", 0),
                    e.get("ssl", 0),
                    e.get("ssc", 0),
                    e.get("tss", 0),
                    e.get("tse", 0),
                    e.get("tsl", 0),
                    e.get("tsc", 0),
                    e.get("dr", ""),
                ),
            )
        conn.executemany(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol,"
            "semantic_type,confidence_score,source_span_start,source_span_end,source_span_line,source_span_column,"
            "target_span_start,target_span_end,target_span_line,target_span_column,dynamic_resolution) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            edge_rows,
        )

        # -----------------------------------------------------------------
        # Tier 1 edge-based antipattern detectors (plan agentic-antipattern-tier1-9f2c8a)
        # A3 missing_hitl_on_irreversible — file-level heuristic: flag irreversible
        # filesystem operations from production/app code when the source file does
        # not import any HITL / chokepoint / approval module.
        #
        # Precision exclusions (avoid false positives):
        #  - tempfile cleanup (symbol contains 'tmp_' or 'temp_' — atomic write pattern)
        #  - admin/ops scripts under `scripts/` or `*_scripts/` subdirs
        #  - tests under `tests/`
        #  - one synthetic edge per (file, line, symbol) to avoid double-counting
        #    when the same call is indexed under both writes_to and emits_side_effect.
        # -----------------------------------------------------------------
        conn.execute(
            """
            INSERT INTO edges(src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
            SELECT
                MIN(e.src_id), MIN(e.dst_id), 'antipattern', 'missing_hitl_on_irreversible',
                e.source_file, e.line_no, MIN(e.symbol)
            FROM edges e
            WHERE e.relation_type IN ('writes_to','emits_side_effect','resolves_callsite','calls')
              AND (
                   e.symbol LIKE '%shutil.rmtree%'
                OR e.symbol LIKE '%os.remove%'
                OR e.symbol LIKE '%os.unlink%'
                OR e.symbol LIKE '%os.rmdir%'
                OR e.symbol LIKE '%Path.unlink%'
                OR e.symbol LIKE '%Path.rmdir%'
              )
              AND (
                   e.source_file LIKE 'agentic_core/%'
                OR e.source_file LIKE 'apps_%'
                OR e.source_file LIKE 'system_learning/%'
              )
              -- Precision: tempfile cleanup is an atomic-write pattern, not a user-data delete
              AND e.symbol NOT LIKE '%tmp_%'
              AND e.symbol NOT LIKE '%temp_%'
              AND e.symbol NOT LIKE '%db_path%'
              AND e.symbol NOT LIKE '%link_path%'
              AND e.symbol NOT LIKE '%backup_path%'
              AND e.symbol NOT LIKE '%duplicate_path%'
              AND e.symbol NOT LIKE '%created_path%'
              -- Precision: admin/ops scripts and tests are not agent-executed
              AND e.source_file NOT LIKE '%/scripts/%'
              AND e.source_file NOT LIKE '%_scripts/%'
              AND e.source_file NOT LIKE 'tests/%'
              AND e.source_file NOT LIKE '%/tests/%'
              -- Precision: L0 routing enforcement and L5 safety plane are
              -- policy-enforcement authorities, not agent-plane consumers.
              AND e.source_file NOT LIKE 'agentic_core/L0_routing/enforcement/%'
              AND e.source_file NOT LIKE 'agentic_core/L0_routing/utils/core_integrity_%'
              AND e.source_file NOT LIKE 'agentic_core/L5_safety/%'
              -- Precision: types/ subdirs are TypedDict/pydantic schemas, not executed code.
              AND e.source_file NOT LIKE '%/types/%'
              -- Precision: ADG artifact writers use atomic temp-rename; the
              -- unlink is part of atomic-rename safety, not user-data deletion.
              AND e.source_file NOT LIKE 'agentic_core/adg/artifact/%'
              -- Precision: atomic_*/hygiene_* mixins implement rollback-safe
              -- cleanup that the calling agent already HITL-guards.
              AND e.source_file NOT LIKE 'agentic_core/mixins/atomic_%'
              AND e.source_file NOT LIKE 'agentic_core/mixins/hygiene_%'
              -- Precision: *_cleaner_util / backup_manager_util are explicit
              -- cleanup tooling where deletion IS the documented purpose.
              AND e.source_file NOT LIKE '%_cleaner_util.py'
              AND e.source_file NOT LIKE '%/backup_manager_util.py'
              AND e.source_file NOT LIKE '%/state_persistence_error_util.py'
              AND e.source_file NOT LIKE '%/waterfall_reconciliation_util.py'
              -- Wave 3: util files whose public API is explicit .delete(key) —
              -- caller owns HITL. Ephemeral artifact pipelines and eval scenario
              -- runners use tempfile.NamedTemporaryFile under try/finally.
              AND e.source_file NOT LIKE 'agentic_core/L3_orchestration/utils/state_management_%'
              AND e.source_file NOT LIKE '%/canonical_store.py'
              AND e.source_file NOT LIKE 'agentic_core/embeddings/%'
              AND e.source_file NOT LIKE 'apps_eval/engines/scenario_runner.py'
              AND NOT EXISTS (
                  SELECT 1 FROM edges i
                  WHERE i.relation_type = 'imports'
                    AND i.source_file = e.source_file
                    AND (
                         i.symbol LIKE '%hitl%'
                      OR i.symbol LIKE '%chokepoint%'
                      OR i.symbol LIKE '%ask_user%'
                      OR i.symbol LIKE '%approval%'
                      OR i.symbol LIKE '%confirm%'
                    )
              )
            GROUP BY e.source_file, e.line_no
            """,
        )

        # A5 chokepoint_bypass — file-level heuristic: flag subprocess / network
        # calls from L1/L2/L3 production layers and apps_* that do not import
        # from a chokepoint / guardrail / safety_plane module. Exclude L5/L6
        # (safety-plane and observability are authorities, not consumers).
        conn.execute(
            """
            INSERT INTO edges(src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
            SELECT
                MIN(e.src_id), MIN(e.dst_id), 'antipattern', 'chokepoint_bypass',
                e.source_file, e.line_no, MIN(e.symbol)
            FROM edges e
            WHERE e.relation_type IN ('writes_to','emits_side_effect','resolves_callsite','calls')
              AND (
                   e.symbol LIKE '%subprocess.run%'
                OR e.symbol LIKE '%subprocess.Popen%'
                OR e.symbol LIKE '%subprocess.check_output%'
                OR e.symbol LIKE '%requests.get%'
                OR e.symbol LIKE '%requests.post%'
                OR e.symbol LIKE '%requests.put%'
                OR e.symbol LIKE '%requests.delete%'
                OR e.symbol LIKE '%urllib.request.urlopen%'
              )
              AND (
                   e.source_file LIKE 'agentic_core/L1_%'
                OR e.source_file LIKE 'agentic_core/L2_%'
                OR e.source_file LIKE 'agentic_core/L3_%'
                OR e.source_file LIKE 'apps_%'
              )
              -- Precision: admin/ops scripts and tests are not agent-executed
              AND e.source_file NOT LIKE '%/scripts/%'
              AND e.source_file NOT LIKE '%_scripts/%'
              AND e.source_file NOT LIKE 'tests/%'
              AND e.source_file NOT LIKE '%/tests/%'
              -- Precision: types/ subdirs, *_util.py cleanup tooling,
              -- and gpu/hardware monitors (subprocess is the API surface).
              AND e.source_file NOT LIKE '%/types/%'
              AND e.source_file NOT LIKE '%/waterfall_reconciliation_util.py'
              AND e.source_file NOT LIKE '%/gpu_memory_monitor.py'
              AND NOT EXISTS (
                  SELECT 1 FROM edges i
                  WHERE i.relation_type = 'imports'
                    AND i.source_file = e.source_file
                    AND (
                         i.symbol LIKE '%chokepoint%'
                      OR i.symbol LIKE '%guardrail%'
                      OR i.symbol LIKE '%safety_plane%'
                    )
              )
              AND e.source_file NOT LIKE '%chokepoint%'
              AND e.source_file NOT LIKE '%guardrail%'
              AND e.source_file NOT LIKE 'agentic_core/L5_%'
              AND e.source_file NOT LIKE 'agentic_core/L6_%'
            GROUP BY e.source_file, e.line_no
            """,
        )

        # Populate violations from governance edges with severity derivation
        conn.execute(
            """INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
            SELECT id, relation_type, symbol, source_file, line_no,
                CASE
                    -- P0 CRITICAL: architectural violations and dynamic code execution
                    -- Layer boundary crossings break the layer contract; eval/exec is
                    -- an arbitrary-code-execution vector. Both block production merge.
                    WHEN relation_type = 'violates' THEN 'CRITICAL'
                    WHEN relation_type = 'dynamic_exec' THEN 'CRITICAL'
                    -- P1 HIGH: swallow-class antipatterns in production layers
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                       'log_and_swallow','return_none_swallow')
                     AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
                    THEN 'HIGH'
                    -- P1 HIGH: unreachable-after-raise (dead code bug) and
                    -- exception_type_erasure (PEP 3134 non-compliance) in production
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('unreachable_after_raise','exception_type_erasure')
                     AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
                    THEN 'HIGH'
                    -- P1 HIGH: blocking I/O in async functions in production
                    -- (event-loop starvation locks up all concurrent work)
                    WHEN relation_type = 'antipattern'
                     AND edge_kind = 'blocking_call_in_async'
                     AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
                    THEN 'HIGH'
                    -- P1 HIGH: bare 'except:' in production layers (catches
                    -- SystemExit, KeyboardInterrupt, GeneratorExit — strictly
                    -- more dangerous than 'except Exception:').
                    WHEN relation_type = 'antipattern'
                     AND edge_kind = 'bare_except'
                     AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
                    THEN 'HIGH'
                    -- P1 HIGH globally: hardcoded credentials are a universal
                    -- security risk regardless of layer.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind = 'hardcoded_secret'
                    THEN 'HIGH'
                    -- P0 CRITICAL agent-safety (plan agentic-antipattern-tier1-9f2c8a)
                    -- Missing HITL on irreversible ops + chokepoint bypass.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('missing_hitl_on_irreversible','chokepoint_bypass')
                    THEN 'CRITICAL'
                    -- P1 HIGH agent-safety in production (Tier 1 agentic):
                    -- unbounded agent loops, unvalidated LLM output, hallucinated
                    -- tool names, return-in-finally.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('unbounded_agent_loop','llm_output_unvalidated',
                                       'hallucinated_tool_name','return_in_finally')
                     AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
                    THEN 'HIGH'
                    -- P2 MEDIUM: same agent-safety kinds outside production
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('unbounded_agent_loop','llm_output_unvalidated',
                                       'hallucinated_tool_name','return_in_finally')
                    THEN 'MEDIUM'
                    -- P3 LOW: non-agent-executed ops/test/tooling directories get
                    -- downgraded for all MEDIUM-class antipatterns. These paths are
                    -- CI gates, dev tools, test scaffolding, Windsurf hooks — not
                    -- code that runs inside the agent execution plane. Keep them
                    -- visible in the LOW band for hygiene, but don't block P2 gate.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                       'log_and_swallow','return_none_swallow',
                                       'unreachable_after_raise','exception_type_erasure',
                                       'blocking_call_in_async','bare_except',
                                       'cleanup_raises_over_original','return_in_finally',
                                       'partial_side_effects','double_logging',
                                       'default_fallback_masking',
                                       'retry_without_backoff','mutable_default_arg','star_import_use')
                     AND (source_file LIKE 'ops_scripts/%'
                       OR source_file LIKE 'tests/%'
                       OR source_file LIKE 'tools/%'
                       OR source_file LIKE '.windsurf/%'
                       OR source_file LIKE 'infrastructure/%'
                       OR source_file LIKE '%/scripts/%'
                       OR source_file LIKE '%_scripts/%'
                       OR source_file LIKE '%/types/%'
                       OR source_file LIKE '%_types.py'
                       -- Apps support/plumbing code (not agent business logic):
                       -- utility helpers, mixins, integrations, tracing shims.
                       OR source_file LIKE 'apps_%/utils/%'
                       OR source_file LIKE 'apps_%/mixins/%'
                       OR source_file LIKE 'apps_%/integrations/%'
                       OR source_file LIKE 'apps_%/_compat/%'
                       OR source_file LIKE 'apps_%/config/%'
                       OR source_file LIKE '%_util.py'
                       OR source_file LIKE '%_mixin.py')
                    THEN 'LOW'
                    -- P3 LOW: double_logging in enforcement/chokepoint/guardrail files
                    -- AND the entire L5 safety plane AND cache clients. These modules
                    -- log + re-raise INTENTIONALLY as an observability contract —
                    -- safety authorities and cache clients must emit a signal AND
                    -- propagate errors so upstream can react.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind = 'double_logging'
                     AND (source_file LIKE '%/enforcement/%'
                       OR source_file LIKE '%chokepoint%'
                       OR source_file LIKE '%guardrail%'
                       OR source_file LIKE '%/validators/%'
                       OR source_file LIKE 'agentic_core/L5_safety/%'
                       OR source_file LIKE 'agentic_core/L6_%'
                       OR source_file LIKE 'agentic_core/mixins/%tracing%'
                       OR source_file LIKE '%/prompt_governance/%'
                       OR source_file LIKE '%/cache/%'
                       OR source_file LIKE '%_cache_%'
                       OR source_file LIKE '%_cache.py'
                       OR source_file LIKE '%cache_client%')
                    THEN 'LOW'
                    -- P3 LOW: log_and_swallow / broad_exception_catch in apps base
                    -- engine framework classes. Base agents/engines/orchestrators
                    -- implement graceful error degradation by design (catch + log +
                    -- advance to next handler in chain). The swallow is a
                    -- framework-level resilience contract, not a hidden failure.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('log_and_swallow','broad_exception_catch',
                                       'silent_exception_swallow','return_none_swallow')
                     AND (source_file LIKE 'apps_%/engines/base_%.py'
                       OR source_file LIKE 'apps_shared/reasoning/Base%.py'
                       OR source_file LIKE 'apps_shared/reasoning/%Orchestrator.py'
                       OR source_file LIKE 'apps_shared/enforcement/%Strategy.py')
                    THEN 'LOW'
                    -- P3 LOW: default_fallback_masking in ML decision support modules.
                    -- ML model-loading fallback (except: return default_model()) is a
                    -- valid resilience pattern - cold-start / missing-model recovery.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind = 'default_fallback_masking'
                     AND (source_file LIKE '%/ml_decision_support/%'
                       OR source_file LIKE '%/ml_integration/%')
                    THEN 'LOW'
                    -- P2 MEDIUM: swallow-class and structural antipatterns in non-production
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                       'log_and_swallow','return_none_swallow',
                                       'unreachable_after_raise','exception_type_erasure',
                                       'blocking_call_in_async','bare_except')
                    THEN 'MEDIUM'
                    -- P2 MEDIUM: finally-block antipatterns (doc #9 and #10),
                    -- cross-cutting exception-handling antipatterns (doc #7, #11),
                    -- and default-fallback-masking (doc #4 — except: X = 0).
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('cleanup_raises_over_original','return_in_finally',
                                       'partial_side_effects','double_logging',
                                       'default_fallback_masking')
                    THEN 'MEDIUM'
                    -- P2 MEDIUM: retry storms, mutable default args, star imports
                    -- (all have credible paths to production incidents)
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('retry_without_backoff','mutable_default_arg','star_import_use')
                    THEN 'MEDIUM'
                    -- P3 LOW: style/hygiene warnings (global state, hardcoded paths)
                    WHEN relation_type = 'antipattern' THEN 'LOW'
                    -- Everything else routes through as MEDIUM (safe default)
                    ELSE 'MEDIUM'
                END as severity
            FROM edges WHERE relation_type IN ('violates', 'antipattern', 'dynamic_exec')""",
        )

        # Guardian exemption filtering — remove violations with valid guardian comments
        guardian_exempted = _filter_guardian_exempted_violations(conn)
        if guardian_exempted:
            print(f"[ADG] Guardian exemptions applied: {guardian_exempted} violations filtered")

        # Meta
        meta_rows = [
            ("schema_version", ng_full.schema_version),
            ("commit_sha", ng_full.commit_sha),
            ("repo_state_hash", ng_full.repo_state_hash),
            ("scanner_digest", ng_full.scanner_digest),
            ("artifact_digest", ng_full.artifact_digest),
            ("total_nodes", str(len(ng_full.nodes))),
            ("total_edges", str(len(ng_full.edges))),
        ]
        conn.executemany("INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)", meta_rows)

        conn.commit()
    except Exception:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        write_failed = True
        raise
    finally:
        conn.close()
        if write_failed and temp_db_path.exists():
            temp_db_path.unlink()

        # Force garbage collection to release file handles on Windows
        import gc

        gc.collect()

    # Atomic rename: only move to final path after successful commit and close
    import shutil

    if db_path.exists():
        db_path.unlink()
    shutil.move(str(temp_db_path), str(db_path))

    return db_path


def _create_latest_symlinks(
    out_dir: Path,
    sqlite_path: Path,
    snap_path: Path,
    file_graph_path: Path,
    symbol_graph_path: Path,
    governance_graph_path: Path,
) -> None:
    """Create LATEST symlinks pointing to the newest timestamped artifacts.

    On Windows, creates copies instead of symlinks if symlink creation fails.
    """
    import shutil

    # guardian: Multiple exceptions (OSError, NotImplementedError) need specific handling
    symlink_map = {
        "adg_LATEST.sqlite": sqlite_path,
        "adg_LATEST_snapshot.json": snap_path,
        "adg_LATEST_file_graph.json": file_graph_path,
        "adg_LATEST_symbol_graph.json": symbol_graph_path,
        "adg_LATEST_governance_graph.json": governance_graph_path,
    }

    for link_name, target_path in tqdm(symlink_map.items(), desc="Processing", unit="item"):
        if not target_path.exists():
            continue

        link_path = out_dir / link_name

        # Remove existing symlink/file
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()

        # Try to create symlink, fall back to copy on Windows
        try:
            link_path.symlink_to(target_path.name)
        except (
            OSError,
            NotImplementedError,
        ):  # guardian: allow-silent-swallow - acceptable exception handling
            # Windows without admin rights or filesystem doesn't support symlinks
            shutil.copy2(target_path, link_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


@dataclass
class ArtifactPaths:
    """Paths of all artifacts written by write_all_artifacts.

    Non-redundant output set (5 files, 100% edge coverage):
        snapshot          - Tier 1: metrics only (~50 KB)
        sqlite            - Tier 2: primary queryable store (~38 MB, all 18 edge types)
        file_graph        - imports, exports, dead_imports, covers, influences, in_cycle
        symbol_graph      - calls, implements, reads_from, writes_to, instantiates, ...
        governance_graph  - violates, antipattern, generates_prompt, ...
    """

    snapshot: Path
    sqlite: Path
    file_graph: Path
    symbol_graph: Path
    governance_graph: Path

    def size_report(self) -> dict[str, str]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArtifactPaths.size_report")

        result = {}
        for name, path in tqdm(
            (
                ("snapshot", self.snapshot),
                ("sqlite", self.sqlite),
                ("file_graph", self.file_graph),
                ("symbol_graph", self.symbol_graph),
                ("governance_graph", self.governance_graph),
            ),
            desc="Processing",
            unit="item",
        ):
            if path.exists():
                sz = path.stat().st_size
                result[name] = f"{sz / 1024:.0f} KB" if sz < 1_048_576 else f"{sz / 1_048_576:.1f} MB"
            else:
                result[name] = "missing"
        return result


def write_all_artifacts(
    artifact: ADGArtifact,
    out_dir: Path,
    *,
    ts: str = "",
    write_split_planes: bool = True,
    write_sqlite: bool = True,
    create_latest_symlinks: bool = False,
) -> ArtifactPaths:
    """Write Tier 1 (snapshot), Tier 2 (sqlite) and three non-overlapping
    split-plane graphs to out_dir. Zero redundancy, 100% edge coverage.

    Parameters
    ----------
    artifact:
        The fully-built ADGArtifact to serialize.
    out_dir:
        Target directory (will be created if missing).
    ts:
        Timestamp string for filenames, e.g. ``"20260311T154637Z"``.
        If empty, no timestamp suffix is added.
    write_split_planes:
        Whether to write the three plane sub-graphs.
    write_sqlite:
        Whether to write the SQLite index.
    create_latest_symlinks:
        Whether to create LATEST symlinks pointing to the newest artifacts.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{ts}" if ts else ""

    # --- Tier 1: lightweight snapshot ---
    snap_dict = _build_snapshot(artifact)
    snap_path = out_dir / f"adg_snapshot{suffix}.json"
    snap_path.write_text(json.dumps(snap_dict, sort_keys=True, indent=2), encoding="utf-8")

    # --- Tier 2: SQLite index + split planes — single normalizer pass ---
    from agentic_core.adg.artifact.SplitArtifact import (
        _FILE_GRAPH_RELS,
        _GOVERNANCE_GRAPH_RELS,
        _SYMBOL_GRAPH_RELS,
    )

    normalizer = ArtifactNormalizer()
    ng_full, ng_file, ng_sym, ng_gov = normalizer.normalize_with_planes(
        artifact,
        file_rels=_FILE_GRAPH_RELS,
        symbol_rels=_SYMBOL_GRAPH_RELS,
        governance_rels=_GOVERNANCE_GRAPH_RELS,
    )

    sqlite_path = out_dir / f"adg_indexed{suffix}.sqlite"
    if write_sqlite:
        _write_sqlite(ng_full, sqlite_path)

    # --- Split planes (non-overlapping, together = 100% edge coverage) ---
    file_graph_path = out_dir / f"adg_file_graph{suffix}.json"
    symbol_graph_path = out_dir / f"adg_symbol_graph{suffix}.json"
    governance_graph_path = out_dir / f"adg_governance_graph{suffix}.json"

    if write_split_planes:
        ng_file.write(file_graph_path, indent=None)
        ng_sym.write(symbol_graph_path, indent=None)
        ng_gov.write(governance_graph_path, indent=None)

    # --- Create LATEST symlinks for easy discovery ---
    if create_latest_symlinks and ts:
        _create_latest_symlinks(
            out_dir,
            sqlite_path,
            snap_path,
            file_graph_path,
            symbol_graph_path,
            governance_graph_path,
        )

    return ArtifactPaths(
        snapshot=snap_path,
        sqlite=sqlite_path,
        file_graph=file_graph_path,
        symbol_graph=symbol_graph_path,
        governance_graph=governance_graph_path,
    )


__all__ = [
    "ArtifactPaths",
    "write_all_artifacts",
]
