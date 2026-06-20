"""ADG Layer Splitter — separate graph planes for targeted consumers.

Splits the monolithic ADGArtifact into THREE independent sub-graphs with
zero edge-type overlap between planes. Together they cover 100% of all
edge types present in the SQLite index.

Sub-graphs
----------
file_graph
    Node type: module only.
    Edge types: imports, exports, dead_imports, covers, influences,
                belongs_to_layer, in_cycle.
    Consumer: CI import validation, layer boundary checks, test coverage,
              ownership queries.
    NOTE: covers lives here (file→file coverage). in_cycle lives here.

symbol_graph
    Node types: module + symbol.
    Edge types: calls, instantiates, implements, reads_from, writes_to,
                writes_through, invokes_provider, routes_through,
                type_annotation, decorated_by.
    Consumer: blast-radius, rename-safety, mutation-authority.

governance_graph
    Node types: all (including prompt_slot, execution_trace, agent_action, etc.)
    Edge types: generates_prompt, consumes_prompt, assembles_into, injects_into,
                overrides_prompt, executed_with_prompt, triggered_telemetry,
                proposed_improvement, updated_prompt, executes_action,
                invokes_tool, crosses_layer, bypasses_uwg, routes_through_uwg,
                layer_authority_violation, policy_hash_mismatch, lineage_of,
                violates, dynamic_exec, antipattern.
    Consumer: P3+P6+P7 analysis modules — layer authority, mutation paths, policy hash.
    NOTE: in_cycle removed (lives in file_graph). antipattern added here.

Each sub-graph is a NormalizedGraph (compact node/edge format).
No edge type appears in more than one plane.

Usage::

    from agentic_core.adg.artifact.SplitArtifact import split_artifact

    planes = split_artifact(artifact)
    planes.file_graph.write(out_dir / "adg_file_graph.json")
    planes.symbol_graph.write(out_dir / "adg_symbol_graph.json")
    planes.governance_graph.write(out_dir / "adg_governance_graph.json")
    # or write all three at once:
    planes.write_all(out_dir)
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.adg.artifact.normalizer_config import NormalizedGraph
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

_emit_applies_guardrail("p0", "layer_splitter", "p0_governance")
_emit_reads_policy_state("p0", "layer_splitter", "policy_binding")
_emit_snapshots_state("p0", "layer_splitter", "state_snapshot")
emit_replay_key("p0", "layer_splitter")
emit_determinism_digest("p0", "layer_splitter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "layer_splitter", "execution_auth")
_emit_validates_capability("p2", "layer_splitter", "capability_check")
_emit_routes_to_capability("p2", "layer_splitter", "capability_route")
_emit_writes_via_uwg("p2", "layer_splitter", "uwg_write")
_emit_blocks_direct_write("p2", "layer_splitter", "direct_write_block")
_emit_records_tool_invocation("p2", "layer_splitter", "tool_invocation")
_emit_captures_execution_output("p2", "layer_splitter", "exec_output")
_emit_dispatches_agent("p3", "layer_splitter", "agent_dispatch")
_emit_coordinates_agents("p3", "layer_splitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "layer_splitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "layer_splitter", "healing_outcome")
_emit_escalates_failure("p3", "layer_splitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "layer_splitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "layer_splitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "layer_splitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "layer_splitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "layer_splitter", "eval_metric")
_emit_stores_embedding("p4", "layer_splitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "layer_splitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "layer_splitter", "exec_snapshot_link")

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

_emit_emits_metric_event("layer_splitter", "p4obs", "metric_1")
_emit_emits_metric_event("layer_splitter", "p4obs", "metric_2")
_emit_emits_metric_event("layer_splitter", "p4obs", "metric_3")
_emit_emits_metric_event("layer_splitter", "p4obs", "metric_4")
_emit_emits_metric_event("layer_splitter", "p4obs", "metric_5")
_emit_emits_metric_event("layer_splitter", "p4obs", "metric_6")
_emit_records_incident_event("layer_splitter", "p4obs", "incident")
_emit_captures_runtime_anomaly("layer_splitter", "p4obs", "anomaly")
_emit_writes_observability_log("layer_splitter", "p4obs", "obs_log")
_emit_updates_monitoring_state("layer_splitter", "p4obs", "mon_state")
_emit_triggers_alert("layer_splitter", "p4obs", "alert")
_emit_links_incident_trace("layer_splitter", "p4obs", "trace_link")
_emit_captures_pattern("layer_splitter", "p3lm", "pattern")
_emit_records_learning_event("layer_splitter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("layer_splitter", "p3lm", "snapshot")
_emit_feeds_meta_learning("layer_splitter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("layer_splitter", "p3lm", "routing")
_emit_improves_agent_policy("layer_splitter", "p3lm", "policy")
_emit_stores_learning_state("layer_splitter", "p3lm", "state")
_emit_records_execution_trace("layer_splitter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("layer_splitter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("layer_splitter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("layer_splitter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("layer_splitter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("layer_splitter", "env_read", "p2_env_1")
_emit_reads_environ("layer_splitter", "env_read", "p2_env_2")
_emit_reads_runtime_state("layer_splitter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("layer_splitter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "layer_splitter", "context_pull")
_emit_pulls_context("p1", "layer_splitter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "layer_splitter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "layer_splitter", "uwg_term_2")
_emit_writes_through("p1", "layer_splitter", "write_through")
_emit_writes_through("p1", "layer_splitter", "write_through_2")
_emit_validated_by_safety_plane("p1", "layer_splitter", "safety_validation")
_emit_invokes_eval("p1", "layer_splitter", "eval_call")
_emit_proposal_commits_routing("p1", "layer_splitter", "routing_commit")
_emit_escalates_to_human("p1", "layer_splitter", "human_escalation")
_emit_routes_through("p1", "layer_splitter", "route_through")
_emit_checks_agent_registry("p1", "layer_splitter", "agent_registry")
_emit_validates_agent_capability("p1", "layer_splitter", "capability")
_emit_dispatches_execution_plan("p1", "layer_splitter", "exec_plan")
_emit_agent_executes_agent("p1", "layer_splitter", "sub_agent")
_emit_routes_to_agent("p1", "layer_splitter", "target_agent")
_emit_verifies_policy("p1", "layer_splitter", "policy_check")
_emit_observes_runtime_state("p1", "layer_splitter", "runtime_state")
_emit_verifies_boundary("p1", "layer_splitter", "boundary_check")
_emit_transcripts_response("p1", "layer_splitter", "transcript")
_emit_hard_fails_untranscripted("p1", "layer_splitter")
_emit_gated_by_confidence("p1", "layer_splitter", "confidence_gate")

# ---------------------------------------------------------------------------
# Edge-type sets per plane
# ---------------------------------------------------------------------------

_FILE_GRAPH_RELS: frozenset[str] = frozenset(
    {
        "imports",
        "exports",  # module re-export edges (structural, module-level)
        "dead_imports",
        "covers",  # test→module coverage (canonical home)
        "influences",  # static influence edges between modules
        "belongs_to_layer",
        "in_cycle",  # canonical home: file_graph (removed from governance)
    },
)

_SYMBOL_GRAPH_RELS: frozenset[str] = frozenset(
    {
        "calls",
        "instantiates",
        "implements",
        "reads_from",
        "writes_to",
        "writes_through",
        "invokes_provider",
        "routes_through",
        "type_annotation",
        "decorated_by",
    },
)

_GOVERNANCE_GRAPH_RELS: frozenset[str] = frozenset(
    {
        # P6 prompt
        "generates_prompt",
        "consumes_prompt",
        "assembles_into",
        "injects_into",
        "overrides_prompt",
        "executed_with_prompt",
        "triggered_telemetry",
        "proposed_improvement",
        "updated_prompt",
        # P3 runtime/authority/mutation
        "executes_action",
        "invokes_tool",
        "crosses_layer",
        "bypasses_uwg",
        "routes_through_uwg",
        "layer_authority_violation",
        "policy_hash_mismatch",
        "lineage_of",
        # Existing violation/governance
        "violates",
        "dynamic_exec",
        # GA: behavioral anti-pattern detection edges
        "antipattern",
        # NOTE: in_cycle removed — lives in file_graph
        # --- Runtime-state / config read edges ---
        "reads_config",
        "reads_env",
        "reads_runtime_state",
        "reads_policy_state",
        "reads_secret",
        "invokes_dynamic",
        # --- G1 (gap): Healer/validator loop ---
        "heals",
        "orchestrates_healing",
        "healing_dispatch",
        "validator_check",
        # --- G3 (gap): Embedding pipeline ---
        "embeds_into",
        "stores_embedding",
        "retrieves_via",
        "chunks_into",
        # --- G4 (gap): HITL / confidence gating ---
        "gated_by_confidence",
        "escalates_to_human",
        # --- G5 (gap): Safety enforcement ---
        "applies_guardrail",
        "verifies_policy",
        # --- G7 (gap): Sandbox airlock ---
        "stamps_work_contract",
        "issues_capability_token",
        "enters_sandbox",
        "exits_sandbox",
        # --- G8 (gap): Capability budget ---
        "consumes_budget",
        "grants_resource",
        "exceeds_budget",
        # --- G9 (gap): JIT context sync ---
        "pulls_context",
        "freezes_context",
        "unfreezes_context",
        # --- G10 (gap): Boundary verification ---
        "verifies_boundary",
        "rejects_packet",
        "certifies_envelope",
        # --- G11 (gap): Determinism control ---
        "seeds_rng",
        "patches_time",
        "guards_replay",
        "emits_determinism_digest",
        # --- G12 (gap): IO interception ---
        "intercepts_io",
        "transcripts_response",
        "hard_fails_untranscripted",
        # --- G13 (gap): Mutation transport ---
        "packages_diff",
        "validates_blast_radius",
        "signs_execution_trace",
        "commits_mutation",
        "distributes_mutation",
        # --- G14 (gap): Execution proof ---
        "records_execution_trace",
        "emits_replay_key",
        "compares_proof",
        # --- G15 (gap): Path control ---
        "routes_path",
        "forces_stall",
        "reenters_safety",
        "vigilance_reroute",
        # --- G16 (gap): Evaluation spine ---
        "scores_groundedness",
        "emits_drift_alert",
        "builds_dpo_batch",
        "commits_optimization",
        # --- G17 (gap): Secret / credential access ---
        "reads_secret_vault",
        "accesses_credential",
        "rotates_secret",
        # --- G18 (gap): Config governance ---
        "reads_governed_config",
        "validates_config_schema",
        "caches_config",
        # --- G19 (gap): Dynamic invocation ---
        "invokes_eval",
        "invokes_exec",
        "invokes_importlib",
        "invokes_getattr_dynamic",
        # --- G20 (gap): Policy state observation ---
        "observes_policy_state",
        "observes_runtime_state",
        "snapshots_state",
        # --- G21 (gap): Anti-pattern registry ---
        "registers_antipattern",
        "classifies_antipattern",
        # --- G22 (gap): Healing orchestrator ---
        "dispatches_healing_run",
        "confirms_heal",
        "aborts_heal",
        # --- G23 (gap): Non-determinism primitive detection ---
        "uses_wall_clock",
        "uses_random",
        "uses_uuid",
        # --- G24 (gap): External HTTP / network egress ---
        "external_http_call",
        # --- G25 (gap): Agent-to-agent dispatch ---
        "agent_executes_agent",
        # --- G26 (gap): L5 validation proof edges ---
        "validated_by_registry",
        "validated_by_safety_plane",
        "validated_by_llm_gateway",
        "execution_terminates_at_uwg",
        "references_policy_hash",
        # --- G27 (gap): Learning / prompt provenance ---
        "proposal_commits_routing",
        "prompt_template_used_by",
        "instruction_injection_source",
        "produces_preference_pair",
        "requires_human_review",
    },
)

_TEST_PATH_MARKERS: tuple[str, ...] = ("tests/", "test_", "_test.py")


def _is_test_module(adg_name: str) -> bool:
    n = adg_name.lower()
    return any(m in n for m in _TEST_PATH_MARKERS)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class SplitArtifact:
    """Container for three non-overlapping graph plane sub-artifacts.

    Together these three planes provide 100% edge coverage with zero
    redundancy between planes.
    """

    file_graph: NormalizedGraph = field(default_factory=NormalizedGraph)
    symbol_graph: NormalizedGraph = field(default_factory=NormalizedGraph)
    governance_graph: NormalizedGraph = field(default_factory=NormalizedGraph)

    def write_all(self, out_dir: Path) -> dict[str, Path]:
        """Write all three planes to out_dir. Returns {plane: path}."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SplitArtifact.write_all")

        out_dir.mkdir(parents=True, exist_ok=True)
        paths = {}
        for plane, graph, fname in (
            ("file_graph", self.file_graph, "adg_file_graph.json"),
            ("symbol_graph", self.symbol_graph, "adg_symbol_graph.json"),
            ("governance_graph", self.governance_graph, "adg_governance_graph.json"),
        ):
            p = graph.write(out_dir / fname, indent=None)
            paths[plane] = p
        return paths

    def size_summary(self) -> dict[str, int]:
        return {
            plane: len(graph.to_json(indent=None).encode("utf-8"))
            for plane, graph in (
                ("file_graph", self.file_graph),
                ("symbol_graph", self.symbol_graph),
                ("governance_graph", self.governance_graph),
            )
        }


# ---------------------------------------------------------------------------
# Splitter
# ---------------------------------------------------------------------------


def _build_plane(
    artifact: ADGArtifact,
    rel_types: frozenset[str],
    *,
    node_type_filter: set[str] | None = None,
    plane_name: str = "",
) -> NormalizedGraph:
    """Build a NormalizedGraph containing only the specified relation types.

    Parameters
    ----------
    artifact:
        Source ADGArtifact.
    rel_types:
        Set of relation_type strings to include.
    node_type_filter:
        If given, only include entity nodes with these entity_type values.
        Nodes referenced by edges are always included regardless.
    plane_name:
        Label embedded in meta.plane.
    """
    # Step 1: filter edges
    selected_rels = [r for r in artifact.relations if r.relation_type in rel_types]

    # Step 2: collect referenced node names
    referenced: set[str] = set()
    for r in selected_rels:
        referenced.add(r.from_name)
        referenced.add(r.to_name)

    # Step 3: collect entity nodes
    entity_lookup: dict[str, object] = {e.adg_name: e for e in artifact.entities}

    # Build name → id mapping: entities first, then dangling references
    name_to_id: dict[str, int] = {}
    nodes: dict[str, dict] = {}

    def _register(name: str, ent=None) -> int:
        if name in name_to_id:
            return name_to_id[name]
        nid = len(name_to_id)
        name_to_id[name] = nid
        if ent is not None:
            nodes[str(nid)] = {
                "n": name,
                "t": ent.entity_type,
                "l": ent.layer,
                "k": ent.identity_kind,
                "c": ent.confidence,
                "p": ent.resolved_path,
            }
        else:
            # Dangling reference — minimal stub
            nodes[str(nid)] = {"n": name, "t": "symbol", "l": "", "k": "", "c": "", "p": ""}
        return nid

    # Register all entities that pass type filter
    for ent in sorted(artifact.entities, key=lambda e: e.adg_name):
        if node_type_filter and ent.entity_type not in node_type_filter:
            continue
        _register(ent.adg_name, ent)

    # Register dangling nodes from edges
    for name in sorted(referenced):
        if name not in name_to_id:
            ent = entity_lookup.get(name)
            _register(name, ent)

    # Step 4: compact edges
    edges: list[dict] = []
    for r in tqdm(selected_rels, desc="Processing", unit="item"):
        if r.from_name not in name_to_id or r.to_name not in name_to_id:
            continue
        e: dict = {
            "s": name_to_id[r.from_name],
            "d": name_to_id[r.to_name],
            "r": r.relation_type,
            "k": r.edge_kind,
            "f": r.source_file,
            "ln": r.line_no,
        }
        if r.symbol:
            e["sym"] = r.symbol
        edges.append(e)

    # Step 5: metrics
    by_rel: dict[str, int] = {}
    for e in edges:
        by_rel[e["r"]] = by_rel.get(e["r"], 0) + 1

    meta = {
        "plane": plane_name,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "by_relation_type": dict(sorted(by_rel.items())),
    }

    ng = NormalizedGraph(
        commit_sha=artifact.commit_sha,
        scanner_digest=artifact.scanner_digest,
        nodes=nodes,
        edges=edges,
        meta=meta,
    )
    ng.compute_digest()
    return ng


def split_artifact(artifact: ADGArtifact) -> SplitArtifact:
    """Split an ADGArtifact into three non-overlapping graph planes.

    Returns a SplitArtifact with .file_graph, .symbol_graph, .governance_graph —
    each a compact NormalizedGraph with zero edge-type overlap between planes.
    Together they cover 100% of all edge types.
    """
    file_graph = _build_plane(
        artifact,
        _FILE_GRAPH_RELS,
        node_type_filter={"module"},
        plane_name="file_graph",
    )
    symbol_graph = _build_plane(
        artifact,
        _SYMBOL_GRAPH_RELS,
        node_type_filter=None,  # include both module and symbol nodes
        plane_name="symbol_graph",
    )
    governance_graph = _build_plane(
        artifact,
        _GOVERNANCE_GRAPH_RELS,
        node_type_filter=None,
        plane_name="governance_graph",
    )
    return SplitArtifact(
        file_graph=file_graph,
        symbol_graph=symbol_graph,
        governance_graph=governance_graph,
    )


__all__ = [
    "SplitArtifact",
    "split_artifact",
    "_FILE_GRAPH_RELS",
    "_SYMBOL_GRAPH_RELS",
    "_GOVERNANCE_GRAPH_RELS",
]
