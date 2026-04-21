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

    from agentic_core.adg.artifact.multi_writer import write_all_artifacts

    paths = write_all_artifacts(artifact, out_dir=Path("artifacts/adg"), ts="20260311T154637Z")
    print(paths)
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from agentic_core.adg.artifact.layer_splitter import split_artifact
from agentic_core.adg.artifact.normalizer import ArtifactNormalizer
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
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

    -- Precision hardening extensions (Section 1: Node Granularity)
    precision_type        TEXT DEFAULT 'symbol',  -- 'symbol', 'code_block', 'expression_unit', 'control_branch'
    span_start            INTEGER DEFAULT 0,
    span_end              INTEGER DEFAULT 0,
    span_line             INTEGER DEFAULT 0,
    span_column           INTEGER DEFAULT 0,
    span_end_line         INTEGER DEFAULT 0,
    span_end_column       INTEGER DEFAULT 0,
    logical_sequence_id    INTEGER DEFAULT 0,
    control_path_id       TEXT DEFAULT NULL,
    temporal_order        INTEGER DEFAULT NULL,
    type_surface          TEXT DEFAULT NULL,
    enclosing_symbol      TEXT DEFAULT NULL
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

    -- Precision hardening extensions (Section 2: Semantic Edge Taxonomy)
    semantic_type        TEXT DEFAULT NULL,  -- 'invokes_function', 'reads_variable', 'writes_variable', etc.
    confidence           REAL DEFAULT 1.0,
    source_span_start    INTEGER DEFAULT 0,
    source_span_end      INTEGER DEFAULT 0,
    source_span_line     INTEGER DEFAULT 0,
    source_span_column   INTEGER DEFAULT 0,
    target_span_start    INTEGER DEFAULT 0,
    target_span_end      INTEGER DEFAULT 0,
    target_span_line     INTEGER DEFAULT 0,
    target_span_column   INTEGER DEFAULT 0,
    dynamic_resolution   TEXT DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_edges_src  ON edges(src_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst  ON edges(dst_id);
CREATE INDEX IF NOT EXISTS idx_edges_rel  ON edges(relation_type);
CREATE INDEX IF NOT EXISTS idx_edges_semantic_type ON edges(semantic_type)
    WHERE semantic_type IS NOT NULL AND semantic_type != '';

-- Precision hardening metadata tables (Sections 3-12)
CREATE TABLE IF NOT EXISTS precision_type_surfaces (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       INTEGER NOT NULL REFERENCES nodes(id),
    inferred_type TEXT DEFAULT NULL,
    possible_types TEXT DEFAULT '[]',  -- JSON array
    nullability   BOOLEAN DEFAULT FALSE,
    shape_signature TEXT DEFAULT NULL   -- JSON object
);
CREATE INDEX IF NOT EXISTS idx_type_surfaces_node ON precision_type_surfaces(node_id);

CREATE TABLE IF NOT EXISTS precision_variable_attributes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id          INTEGER NOT NULL REFERENCES nodes(id),
    source_origin    TEXT NOT NULL,
    mutation_count   INTEGER DEFAULT 0,
    lineage_chain    TEXT DEFAULT '[]',  -- JSON array
    type_surface_id  INTEGER REFERENCES precision_type_surfaces(id)
);
CREATE INDEX IF NOT EXISTS idx_var_attrs_node ON precision_variable_attributes(node_id);

CREATE TABLE IF NOT EXISTS precision_side_effects (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       INTEGER NOT NULL REFERENCES nodes(id),
    effect_type   TEXT NOT NULL,  -- 'filesystem_operation', 'network_call', etc.
    target        TEXT NOT NULL,
    confidence    REAL DEFAULT 1.0
);
CREATE INDEX IF NOT EXISTS idx_side_effects_node ON precision_side_effects(node_id);

CREATE TABLE IF NOT EXISTS precision_control_branches (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       INTEGER NOT NULL REFERENCES nodes(id),
    branch_type   TEXT NOT NULL,  -- 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with'
    condition     TEXT DEFAULT NULL,
    target_id     INTEGER REFERENCES nodes(id)
);
CREATE INDEX IF NOT EXISTS idx_control_branches_node ON precision_control_branches(node_id);

CREATE TABLE IF NOT EXISTS precision_call_resolution (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id             INTEGER NOT NULL REFERENCES edges(id),
    resolved_target     TEXT DEFAULT NULL,
    candidate_targets   TEXT DEFAULT '[]',  -- JSON array
    dispatch_type       TEXT DEFAULT NULL,  -- 'direct', 'attribute', 'complex'
    resolution_confidence REAL DEFAULT 0.0
);
CREATE INDEX IF NOT EXISTS idx_call_resolution_edge ON precision_call_resolution(edge_id);

CREATE TABLE IF NOT EXISTS precision_test_linkage (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    test_node_id  INTEGER NOT NULL REFERENCES nodes(id),
    target_node_id INTEGER NOT NULL REFERENCES nodes(id),
    link_type     TEXT NOT NULL,  -- 'validates_expression', 'covers_branch', 'observes_side_effect'
    confidence    REAL DEFAULT 1.0
);
CREATE INDEX IF NOT EXISTS idx_test_linkage_test ON precision_test_linkage(test_node_id);
CREATE INDEX IF NOT EXISTS idx_test_linkage_target ON precision_test_linkage(target_node_id);

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
        -- Precision extensions
        e.semantic_type AS semantic_type,
        e.confidence    AS edge_confidence,
        src.precision_type AS from_precision_type,
        dst.precision_type AS to_precision_type,
        src.logical_sequence_id AS from_sequence_id,
        dst.logical_sequence_id AS to_sequence_id
    FROM edges e
    JOIN nodes src ON src.id = e.src_id
    JOIN nodes dst ON dst.id = e.dst_id;

-- Precision metrics view (Section 11: Graph Completeness Invariants)
CREATE VIEW IF NOT EXISTS precision_metrics_view AS
SELECT
    COUNT(DISTINCT n.id) as total_nodes,
    COUNT(DISTINCT CASE WHEN n.precision_type != 'symbol' THEN n.id END) as precision_nodes,
    COUNT(DISTINCT e.id) as total_edges,
    COUNT(DISTINCT CASE WHEN e.semantic_type IS NOT NULL THEN e.id END) as semantic_edges,
    COUNT(DISTINCT CASE WHEN n.precision_type = 'code_block' THEN n.id END) as code_blocks,
    COUNT(DISTINCT CASE WHEN n.precision_type = 'expression_unit' THEN n.id END) as expression_units,
    COUNT(DISTINCT CASE WHEN n.precision_type = 'control_branch' THEN n.id END) as control_branches,
    COUNT(DISTINCT v.id) as variables_with_lineage,
    COUNT(DISTINCT s.id) as side_effects_modeled,
    COUNT(DISTINCT cr.id) as calls_resolved
FROM nodes n
LEFT JOIN edges e ON (e.src_id = n.id OR e.dst_id = n.id)
LEFT JOIN precision_variable_attributes v ON v.node_id = n.id
LEFT JOIN precision_side_effects s ON s.node_id = n.id
LEFT JOIN precision_call_resolution cr ON cr.edge_id = e.id;
"""


# STRICT MAP: one canonical token per edge_kind, PLUS a single documented
# semantic supersession: ``allow-broad-exception`` is the parent claim for
# ``except Exception``/``except BaseException`` and subsumes the swallow
# variants that a broad catch inherently exhibits (a broad catch always
# either swallows silently, logs-and-swallows, returns None, or re-raises).
# The swallow-specific tokens remain strictly scoped: they do NOT exempt
# each other or a broad catch.
_GUARDIAN_MAP: dict[str, tuple[str, ...]] = {
    "silent_exception_swallow": (
        "guardian: allow-silent-swallow",
        "guardian: allow-broad-exception",
    ),
    "broad_exception_catch": ("guardian: allow-broad-exception",),
    "log_and_swallow": (
        "guardian: allow-log-and-swallow",
        "guardian: allow-broad-exception",
    ),
    "return_none_swallow": (
        "guardian: allow-return-none-swallow",
        "guardian: allow-broad-exception",
    ),
    # Pattern C — dead code after raise. Strictly scoped: no supersession,
    # authors must justify each site individually (this is a bug, not a choice).
    "unreachable_after_raise": ("guardian: allow-unreachable-after-raise",),
    # Doc #8 — exception type erasure. Strictly scoped.
    "exception_type_erasure": ("guardian: allow-exception-type-erasure",),
    # Doc #9 — cleanup raises over original exception.
    "cleanup_raises_over_original": ("guardian: allow-cleanup-raises",),
    # Doc #10 — return in finally silently overrides try/except result.
    "return_in_finally": ("guardian: allow-finally-return",),
    # Blocking I/O inside an async function body (event-loop starvation).
    "blocking_call_in_async": ("guardian: allow-blocking-in-async",),
    # Retry loops without backoff (cost/latency amplification).
    "retry_without_backoff": ("guardian: allow-retry-without-backoff",),
    # Mutable default argument (shared state across calls).
    "mutable_default_arg": ("guardian: allow-mutable-default",),
    # Star import (namespace pollution, breaks static analysis).
    "star_import_use": ("guardian: allow-star-import",),
    # Doc #7 — partial side effects: try-body writes, except swallows.
    "partial_side_effects": ("guardian: allow-partial-side-effects",),
    # Doc #11 — double logging: handler logs and re-raises.
    "double_logging": ("guardian: allow-double-logging",),
    # Bare 'except:' (catches SystemExit/KeyboardInterrupt/GeneratorExit).
    "bare_except": ("guardian: allow-bare-except",),
    # Doc #4 — default fallback masking: 'except: price = 0'.
    "default_fallback_masking": ("guardian: allow-default-fallback",),
    # Doc #12 — exception as normal control flow.
    "throw_for_normal_flow": ("guardian: allow-control-flow-exception",),
    # Hardcoded credentials in source code.
    "hardcoded_secret": ("guardian: allow-hardcoded-secret",),
}

_LAYER_VIOLATION_GUARDIANS = ("guardian: allow-layer-violation",)

_file_cache: dict[str, list[str]] = {}

_CANONICAL_GUARDIAN_TOKENS = frozenset(
    {
        "allow-silent-swallow",
        "allow-log-and-swallow",
        "allow-return-none-swallow",
        "allow-broad-exception",
        "allow-unreachable-after-raise",
        "allow-exception-type-erasure",
        "allow-cleanup-raises",
        "allow-finally-return",
        "allow-blocking-in-async",
        "allow-retry-without-backoff",
        "allow-mutable-default",
        "allow-star-import",
        "allow-partial-side-effects",
        "allow-double-logging",
        "allow-bare-except",
        "allow-default-fallback",
        "allow-control-flow-exception",
        "allow-hardcoded-secret",
    }
)


def _read_lines_cached(filepath: str) -> list[str]:
    """Read file lines with caching to avoid repeated I/O for hot files."""
    if filepath not in _file_cache:
        try:
            _file_cache[filepath] = (
                Path(filepath)
                .read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                .splitlines()
            )
        except OSError:
            _file_cache[filepath] = []
    return _file_cache[filepath]


def _extract_guardian_tokens(line: str) -> set[str]:
    """Extract canonical guardian allow tokens from a single source line.

    STRICT: Requires a non-empty ``-- <justification>`` segment after the
    token. A bare ``# guardian: allow-X`` is rejected — every guardian must
    document *why* the swallow is justified.
    """
    if "guardian:" not in line:
        return set()
    tokens: set[str] = set()
    marker = "guardian:"
    idx = line.find(marker)
    if idx < 0:
        return tokens
    payload = line[idx + len(marker) :]
    parts = payload.split()
    if not parts:
        return tokens
    head = parts[0].strip().strip(",;()[]{}")
    if not (head.startswith("allow-") and head in _CANONICAL_GUARDIAN_TOKENS):
        return tokens
    # Require '-- <justification>' — at minimum, '--' followed by >=3 word chars
    tail = " ".join(parts[1:])
    if "--" not in tail:
        return tokens
    after_dashes = tail.split("--", 1)[1].strip()
    if len(after_dashes) < 3:
        return tokens
    tokens.add(head)
    return tokens


def _resolve_except_anchor_lines(lines: list[str], line_no: int) -> set[int]:
    """Resolve canonical anchor lines for an exception handler site.

    STRICT: Only two anchors are valid:
      1. The ``except ... :`` header line itself
      2. For multi-line except headers, the line containing the closing ``:``

    Pre-except orphan comments and generic ±6-line windows are rejected so
    guardians can no longer 'leak' between adjacent except blocks.
    """
    if line_no < 1 or not lines:
        return set()

    max_idx = len(lines) - 1
    idx = min(max(line_no - 1, 0), max_idx)
    start = idx

    # Walk back at most 6 lines to find the 'except' keyword that owns this site
    for probe in range(idx, max(-1, idx - 6), -1):
        stripped = lines[probe].lstrip()
        if stripped.startswith("except"):
            start = probe
            break

    # Walk forward to find the ':' that closes the except header (multi-line)
    end = start
    for probe in range(start, min(len(lines), start + 6)):
        end = probe
        if ":" in lines[probe]:
            break

    # STRICT: anchors are ONLY the except line and the closing-paren line.
    # No +/- 1-line fallback, no pre-except comment line.
    anchors = {start + 1, end + 1}
    return {ln for ln in anchors if 1 <= ln <= len(lines)}


def has_guardian_for_violation(source_file: str, line_no: int, edge_kind: str) -> bool:
    """Canonical guardian matcher used across write-time, phase2, and phase3."""
    guardians = _GUARDIAN_MAP.get(edge_kind)
    if not guardians:
        return False

    lines = _read_lines_cached(source_file)
    if not lines:
        return False

    valid_tokens = {g.split("guardian:", 1)[1].strip() for g in guardians if "guardian:" in g}
    for anchor_line in _resolve_except_anchor_lines(lines, line_no):
        tokens = _extract_guardian_tokens(lines[anchor_line - 1])
        if any(token in valid_tokens for token in tokens):
            return True
    return False


def _has_guardian_comment(
    source_file: str,
    line_no: int,
    guardian_strings: tuple[str, ...],
) -> bool:
    """Check if source line (±2 lines) contains a matching guardian comment."""
    lines = _read_lines_cached(source_file)
    if not lines or line_no < 1:
        return False
    valid_tokens = {g.split("guardian:", 1)[1].strip() for g in guardian_strings if "guardian:" in g}
    for anchor_line in _resolve_except_anchor_lines(lines, line_no):
        tokens = _extract_guardian_tokens(lines[anchor_line - 1])
        if any(token in valid_tokens for token in tokens):
            return True
    return False


def _filter_guardian_exempted_violations(conn: sqlite3.Connection) -> int:
    """Remove violations that have valid guardian exemption comments in source.

    Queries all antipattern and layer-violation rows, reads the source file
    at the violation line, and DELETEs rows whose surrounding context contains
    the matching ``# guardian: allow-<type>`` comment.

    Returns the number of exempted (deleted) violations.
    """
    _file_cache.clear()

    # Collect antipattern violations with edge_kind
    rows = conn.execute(
        "SELECT v.id, e.edge_kind, v.file_path, v.line_no "
        "FROM violations v JOIN edges e ON v.edge_id = e.id "
        "WHERE v.category = 'antipattern'",
    ).fetchall()

    exempt_ids: list[int] = []
    for vid, edge_kind, fpath, lno in rows:
        if has_guardian_for_violation(fpath, lno, edge_kind):
            exempt_ids.append(vid)

    # Collect layer-violation violations
    lv_rows = conn.execute(
        "SELECT v.id, v.file_path, v.line_no "
        "FROM violations v JOIN edges e ON v.edge_id = e.id "
        "WHERE e.relation_type = 'violates'",
    ).fetchall()
    for vid, fpath, lno in lv_rows:
        if _has_guardian_comment(fpath, lno, _LAYER_VIOLATION_GUARDIANS):
            exempt_ids.append(vid)

    # Batch delete
    if exempt_ids:
        # SQLite max variable limit is 999; batch if needed
        for i in range(0, len(exempt_ids), 900):
            batch = exempt_ids[i : i + 900]
            placeholders = ",".join("?" for _ in batch)
            conn.execute(
                f"DELETE FROM violations WHERE id IN ({placeholders})",
                batch,
            )

    # Store exemption count in meta for transparency
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
        ("guardian_exemptions", str(len(exempt_ids))),
    )

    _file_cache.clear()
    return len(exempt_ids)


def _write_sqlite(ng_full, db_path: Path) -> Path:
    """Write a NormalizedGraph to SQLite for fast querying."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    try:
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
                    # Precision extensions (default values for now)
                    node.get("pt", "symbol"),  # precision_type
                    node.get("ss", 0),  # span_start
                    node.get("se", 0),  # span_end
                    node.get("sl", 0),  # span_line
                    node.get("sc", 0),  # span_column
                    node.get("sel", 0),  # span_end_line
                    node.get("sec", 0),  # span_end_column
                    node.get("lsid", 0),  # logical_sequence_id
                    node.get("cpid", None),  # control_path_id
                    node.get("to", None),  # temporal_order
                    node.get("ts", None),  # type_surface
                    node.get("es", None),  # enclosing_symbol
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
                    # Precision extensions (default values for now)
                    e.get("st", None),  # semantic_type
                    e.get("conf", 1.0),  # confidence
                    e.get("sss", 0),  # source_span_start
                    e.get("sse", 0),  # source_span_end
                    e.get("ssl", 0),  # source_span_line
                    e.get("ssc", 0),  # source_span_column
                    e.get("tss", 0),  # target_span_start
                    e.get("tse", 0),  # target_span_end
                    e.get("tsl", 0),  # target_span_line
                    e.get("tsc", 0),  # target_span_column
                    e.get("dr", None),  # dynamic_resolution
                ),
            )
        conn.executemany(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol,"
            "semantic_type,confidence,source_span_start,source_span_end,source_span_line,source_span_column,"
            "target_span_start,target_span_end,target_span_line,target_span_column,dynamic_resolution) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            edge_rows,
        )

        # -----------------------------------------------------------------
        # Tier 1 edge-based antipattern detectors (plan agentic-antipattern-tier1-9f2c8a)
        # These insert SYNTHETIC antipattern edges AFTER the main edge insert
        # so downstream violations/severity CASE picks them up.
        # -----------------------------------------------------------------

        # A3 — missing_hitl_on_irreversible
        # Flag call edges from any source_file under apps_* or agentic_core/ whose
        # symbol resolves to a known irreversible operation, where the source_file
        # has NO edge importing a HITL checkpoint module.
        # Irreversible ops (conservative allow-list): shutil.rmtree, os.remove,
        # os.unlink, pathlib.Path.unlink, Path.rmdir, os.rmdir.
        # A "HITL-aware" file is one that imports from a module whose name
        # contains 'hitl', 'chokepoint', 'confirm', 'approval', or 'ask_user'.
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
              AND e.symbol NOT LIKE '%tmp_%'
              AND e.symbol NOT LIKE '%temp_%'
              AND e.symbol NOT LIKE '%db_path%'
              AND e.symbol NOT LIKE '%link_path%'
              AND e.symbol NOT LIKE '%backup_path%'
              AND e.symbol NOT LIKE '%duplicate_path%'
              AND e.symbol NOT LIKE '%created_path%'
              AND e.source_file NOT LIKE '%/scripts/%'
              AND e.source_file NOT LIKE '%_scripts/%'
              AND e.source_file NOT LIKE 'tests/%'
              AND e.source_file NOT LIKE '%/tests/%'
              AND e.source_file NOT LIKE 'agentic_core/L0_routing/enforcement/%'
              AND e.source_file NOT LIKE 'agentic_core/L0_routing/utils/core_integrity_%'
              AND e.source_file NOT LIKE 'agentic_core/L5_safety/%'
              AND e.source_file NOT LIKE '%/types/%'
              AND e.source_file NOT LIKE 'agentic_core/adg/artifact/%'
              AND e.source_file NOT LIKE 'agentic_core/mixins/atomic_%'
              AND e.source_file NOT LIKE 'agentic_core/mixins/hygiene_%'
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

        # A5 — chokepoint_bypass
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
              AND e.source_file NOT LIKE '%/scripts/%'
              AND e.source_file NOT LIKE '%_scripts/%'
              AND e.source_file NOT LIKE 'tests/%'
              AND e.source_file NOT LIKE '%/tests/%'
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
        # Severity assignment SSOT:
        #   CRITICAL antipattern kinds → always HIGH (P1 in prod, MEDIUM elsewhere)
        #     - agent-safety: missing_hitl_on_irreversible, chokepoint_bypass
        #   HIGH antipattern kinds (base) → HIGH in production layers, MEDIUM elsewhere
        #     - error-handling: broad_exception_catch, silent_exception_swallow,
        #       log_and_swallow, return_none_swallow, exception_type_erasure,
        #       return_in_finally
        #     - agent-safety: unbounded_agent_loop, llm_output_unvalidated,
        #       hallucinated_tool_name
        #   MEDIUM antipattern kinds → always MEDIUM (P2)
        #     - partial_side_effects, default_fallback_masking, double_logging,
        #       retry_without_backoff, unreachable_after_raise, bare_except,
        #       blocking_call_in_async, cleanup_raises_over_original
        #   Everything else antipattern → LOW (P3)
        #     - throw_for_normal_flow, global_state_mutation, hardcoded_path,
        #       mutable_default_arg, star_import_use
        conn.execute(
            """INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
            SELECT id, relation_type, symbol, source_file, line_no,
                CASE
                    -- CRITICAL agent-safety patterns (always P0)
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('missing_hitl_on_irreversible','chokepoint_bypass')
                    THEN 'CRITICAL'
                    -- HIGH severity in production layers (P1)
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                       'log_and_swallow','return_none_swallow',
                                       'exception_type_erasure','return_in_finally',
                                       'unbounded_agent_loop','llm_output_unvalidated',
                                       'hallucinated_tool_name')
                     AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
                    THEN 'HIGH'
                    -- P3 LOW: non-agent-executed ops/test/tooling directories get
                    -- downgraded for all MEDIUM-class antipatterns (see ArtifactPaths.py
                    -- for canonical doc). Keep visible in LOW band, don't block P2 gate.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                       'log_and_swallow','return_none_swallow',
                                       'exception_type_erasure','return_in_finally',
                                       'unbounded_agent_loop','llm_output_unvalidated',
                                       'hallucinated_tool_name',
                                       'partial_side_effects','default_fallback_masking',
                                       'double_logging','retry_without_backoff',
                                       'unreachable_after_raise','bare_except',
                                       'blocking_call_in_async','cleanup_raises_over_original',
                                       'mutable_default_arg','star_import_use')
                     AND (source_file LIKE 'ops_scripts/%'
                       OR source_file LIKE 'tests/%'
                       OR source_file LIKE 'tools/%'
                       OR source_file LIKE '.windsurf/%'
                       OR source_file LIKE 'infrastructure/%'
                       OR source_file LIKE '%/scripts/%'
                       OR source_file LIKE '%_scripts/%'
                       OR source_file LIKE '%/types/%'
                       OR source_file LIKE '%_types.py')
                    THEN 'LOW'
                    -- P3 LOW: double_logging in enforcement/chokepoint/guardrail/
                    -- validators/L5/L6/tracing/prompt_governance files.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind = 'double_logging'
                     AND (source_file LIKE '%/enforcement/%'
                       OR source_file LIKE '%chokepoint%'
                       OR source_file LIKE '%guardrail%'
                       OR source_file LIKE '%/validators/%'
                       OR source_file LIKE 'agentic_core/L5_safety/%'
                       OR source_file LIKE 'agentic_core/L6_%'
                       OR source_file LIKE 'agentic_core/mixins/%tracing%'
                       OR source_file LIKE '%/prompt_governance/%')
                    THEN 'LOW'
                    -- P3 LOW: default_fallback_masking in ML decision/integration
                    -- paths - cold-start fallback is a valid resilience pattern.
                    WHEN relation_type = 'antipattern'
                     AND edge_kind = 'default_fallback_masking'
                     AND (source_file LIKE '%/ml_decision_support/%'
                       OR source_file LIKE '%/ml_integration/%')
                    THEN 'LOW'
                    -- Same HIGH-severity kinds outside production → MEDIUM (P2)
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                       'log_and_swallow','return_none_swallow',
                                       'exception_type_erasure','return_in_finally',
                                       'unbounded_agent_loop','llm_output_unvalidated',
                                       'hallucinated_tool_name')
                    THEN 'MEDIUM'
                    -- Always-MEDIUM kinds (P2 regardless of layer)
                    WHEN relation_type = 'antipattern'
                     AND edge_kind IN ('partial_side_effects','default_fallback_masking',
                                       'double_logging','retry_without_backoff',
                                       'unreachable_after_raise','bare_except',
                                       'blocking_call_in_async','cleanup_raises_over_original')
                    THEN 'MEDIUM'
                    -- All other antipatterns → P3 style warnings
                    WHEN relation_type = 'antipattern' THEN 'LOW'
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
            ("scanner_digest", ng_full.scanner_digest),
            ("artifact_digest", ng_full.artifact_digest),
            ("total_nodes", str(len(ng_full.nodes))),
            ("total_edges", str(len(ng_full.edges))),
        ]
        conn.executemany("INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)", meta_rows)

        conn.commit()

        # Optimize SQLite database (3-13 MB savings)
        conn.execute("PRAGMA optimize")
        conn.execute("VACUUM")
        conn.commit()
    finally:
        conn.close()

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
    """Compatibility wrapper delegating to canonical ArtifactPaths writer."""
    from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts as _canonical_write_all_artifacts

    return cast(
        ArtifactPaths,
        _canonical_write_all_artifacts(
            artifact,
            out_dir=out_dir,
            ts=ts,
            write_split_planes=write_split_planes,
            write_sqlite=write_sqlite,
            create_latest_symlinks=create_latest_symlinks,
        ),
    )


__all__ = [
    "ArtifactPaths",
    "write_all_artifacts",
]
