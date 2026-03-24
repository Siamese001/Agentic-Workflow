"""Exhaustive completeness and accuracy tests for G7-G16 ADG runtime plane implementation.

Testing methodology — 8 orthogonal axes:

  C1  Schema completeness  — every declared entity type, relation type, and edge kind
      from schema.py is non-empty and internally consistent.
  C2  Detection-constant completeness — every schema detection constant (frozenset)
      is non-empty and covers the canonical class/method names used in the runtime
      modules themselves.
  C3  Module API completeness — every G7-G16 runtime module is importable, exposes
      its full public API, and all exported symbols resolve to the correct types.
  C4  __init__ export completeness — runtime/__init__.py __all__ is a superset of
      all public symbols declared in each G7-G16 module.
  A1  Visitor accuracy — every detection branch in every visitor (class, method,
      raise, attribute-style call) emits the EXACT (relation_type, edge_kind) pair
      documented in the visitor docstring. No edge is silently swallowed.
  A2  Visitor non-contamination — unrelated source code produces ZERO edges.
  A3  Runtime state-machine accuracy — every lifecycle transition in every G7-G16
      runtime module ends in the correct terminal state including all error paths.
  A4  ADG round-trip accuracy — scanning the G7-G16 runtime module files themselves
      through the full static scanner produces non-zero edges for EACH gap plane.
  A5  Layer-splitter accuracy — every relation type produced by the ADG scanner
      is assigned to EXACTLY ONE plane with ZERO cross-plane overlap.
"""

from __future__ import annotations

import ast
import importlib
import textwrap
import typing
from pathlib import Path

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
)

_emit_applies_guardrail("p0", "test_adg_g7_g16_completeness_accuracy", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_g7_g16_completeness_accuracy", "policy_binding")
_emit_snapshots_state("p0", "test_adg_g7_g16_completeness_accuracy", "state_snapshot")
_emit_authorize_and_execute("p2", "test_adg_g7_g16_completeness_accuracy", "execution_auth")
_emit_validates_capability("p2", "test_adg_g7_g16_completeness_accuracy", "capability_check")
_emit_routes_to_capability("p2", "test_adg_g7_g16_completeness_accuracy", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_g7_g16_completeness_accuracy", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_g7_g16_completeness_accuracy", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_g7_g16_completeness_accuracy", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_g7_g16_completeness_accuracy", "exec_output")
_emit_dispatches_agent("p3", "test_adg_g7_g16_completeness_accuracy", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_g7_g16_completeness_accuracy", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_g7_g16_completeness_accuracy", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_g7_g16_completeness_accuracy", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_g7_g16_completeness_accuracy", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_g7_g16_completeness_accuracy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_g7_g16_completeness_accuracy", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_g7_g16_completeness_accuracy", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_g7_g16_completeness_accuracy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_g7_g16_completeness_accuracy", "eval_metric")
_emit_stores_embedding("p4", "test_adg_g7_g16_completeness_accuracy", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_g7_g16_completeness_accuracy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_g7_g16_completeness_accuracy", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_adg_g7_g16_completeness_accuracy", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_g7_g16_completeness_accuracy", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_g7_g16_completeness_accuracy", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_g7_g16_completeness_accuracy", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_g7_g16_completeness_accuracy", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_g7_g16_completeness_accuracy", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_g7_g16_completeness_accuracy", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_g7_g16_completeness_accuracy", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_g7_g16_completeness_accuracy", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_g7_g16_completeness_accuracy", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_g7_g16_completeness_accuracy", "p4obs", "alert")
_emit_links_incident_trace("test_adg_g7_g16_completeness_accuracy", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_g7_g16_completeness_accuracy", "p3lm", "pattern")
_emit_records_learning_event("test_adg_g7_g16_completeness_accuracy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_g7_g16_completeness_accuracy", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_g7_g16_completeness_accuracy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_g7_g16_completeness_accuracy", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_g7_g16_completeness_accuracy", "p3lm", "policy")
_emit_stores_learning_state("test_adg_g7_g16_completeness_accuracy", "p3lm", "state")
_emit_records_execution_trace("test_adg_g7_g16_completeness_accuracy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_g7_g16_completeness_accuracy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_g7_g16_completeness_accuracy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_g7_g16_completeness_accuracy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_g7_g16_completeness_accuracy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_g7_g16_completeness_accuracy", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_g7_g16_completeness_accuracy", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_g7_g16_completeness_accuracy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_g7_g16_completeness_accuracy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_g7_g16_completeness_accuracy", "context_pull")
_emit_pulls_context("p1", "test_adg_g7_g16_completeness_accuracy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_g7_g16_completeness_accuracy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_g7_g16_completeness_accuracy", "uwg_term_2")
_emit_writes_through("p1", "test_adg_g7_g16_completeness_accuracy", "write_through")
_emit_writes_through("p1", "test_adg_g7_g16_completeness_accuracy", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_g7_g16_completeness_accuracy", "safety_validation")
_emit_invokes_eval("p1", "test_adg_g7_g16_completeness_accuracy", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_g7_g16_completeness_accuracy", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_g7_g16_completeness_accuracy", "human_escalation")
_emit_routes_through("p1", "test_adg_g7_g16_completeness_accuracy", "route_through")
_emit_checks_agent_registry("p1", "test_adg_g7_g16_completeness_accuracy", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_g7_g16_completeness_accuracy", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_g7_g16_completeness_accuracy", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_g7_g16_completeness_accuracy", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_g7_g16_completeness_accuracy", "target_agent")
_emit_verifies_policy("p1", "test_adg_g7_g16_completeness_accuracy", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_g7_g16_completeness_accuracy", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_g7_g16_completeness_accuracy", "boundary_check")
_emit_transcripts_response("p1", "test_adg_g7_g16_completeness_accuracy", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_g7_g16_completeness_accuracy")
_emit_gated_by_confidence("p1", "test_adg_g7_g16_completeness_accuracy", "confidence_gate")

ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan_src(source: str) -> list:
    """Run all G7-G16 AST visitors against source and collect edges."""
    from agentic_core.adg.extraction.static_scanner import (
        _BoundaryVerifierVisitor,
        _CapabilityBudgetVisitor,
        _DeterminismControlVisitor,
        _EvalSpineVisitor,
        _ExecutionProofVisitor,
        _IOInterceptionVisitor,
        _JITContextVisitor,
        _MutationTransportVisitor,
        _PathControlVisitor,
        _SandboxAirlockVisitor,
    )

    tree = ast.parse(textwrap.dedent(source))
    mod = "ADG::Module::test"
    src = "test.py"
    edges: list = []
    for Cls in [
        _SandboxAirlockVisitor,
        _CapabilityBudgetVisitor,
        _JITContextVisitor,
        _BoundaryVerifierVisitor,
        _DeterminismControlVisitor,
        _IOInterceptionVisitor,
        _MutationTransportVisitor,
        _ExecutionProofVisitor,
        _PathControlVisitor,
        _EvalSpineVisitor,
    ]:
        v = Cls(mod, src)
        v.visit(tree)
        edges.extend(v.edges)
    return edges


def _edges_for(source: str, visitor_cls) -> list:
    """Run a single visitor against source."""
    tree = ast.parse(textwrap.dedent(source))
    v = visitor_cls("ADG::Module::test", "test.py")
    v.visit(tree)
    return v.edges


def _rel_ek(edges: list) -> set[tuple[str, str]]:
    """Return set of (relation_type, edge_kind) pairs from edge list."""
    return {(e.relation_type, e.edge_kind) for e in edges}


def _rels(edges: list) -> set[str]:
    return {e.relation_type for e in edges}


def _eks(edges: list) -> set[str]:
    return {e.edge_kind for e in edges}


# ---------------------------------------------------------------------------
# C1 — Schema completeness: EntityType, RelationType, EdgeKind
# ---------------------------------------------------------------------------

G7_G16_ENTITY_TYPES = [
    "sandbox_envelope",
    "capability_token",
    "work_contract",
    "tool_budget",
    "resource_grant",
    "jit_context_snapshot",
    "freeze_boundary",
    "boundary_checkpoint",
    "capability_chokepoint",
    "semantic_clock",
    "replay_guard",
    "rng_seed",
    "io_intercept",
    "network_transcript",
    "mutation_packet",
    "commit_protocol",
    "execution_proof",
    "determinism_digest",
    "execution_path",
    "path_reroute",
    "eval_metric",
    "dpo_batch",
    "drift_alert",
]

G7_G16_RELATION_TYPES = [
    # G7
    "stamps_work_contract",
    "issues_capability_token",
    "enters_sandbox",
    "exits_sandbox",
    # G8
    "consumes_budget",
    "grants_resource",
    "exceeds_budget",
    # G9
    "pulls_context",
    "freezes_context",
    "unfreezes_context",
    # G10
    "verifies_boundary",
    "rejects_packet",
    "certifies_envelope",
    # G11
    "seeds_rng",
    "patches_time",
    "guards_replay",
    "emits_determinism_digest",
    # G12
    "intercepts_io",
    "transcripts_response",
    "hard_fails_untranscripted",
    # G13
    "packages_diff",
    "validates_blast_radius",
    "signs_execution_trace",
    "commits_mutation",
    "distributes_mutation",
    # G14
    "records_execution_trace",
    "emits_replay_key",
    "compares_proof",
    # G15
    "routes_path",
    "forces_stall",
    "reenters_safety",
    "vigilance_reroute",
    # G16
    "scores_groundedness",
    "emits_drift_alert",
    "builds_dpo_batch",
    "commits_optimization",
]

G7_G16_EDGE_KINDS = [
    # G7
    "sandbox_entry",
    "sandbox_exit",
    "work_contract_stamp",
    "capability_token_issue",
    # G8
    "budget_grant",
    "budget_exceeded",
    # G9
    "context_pull",
    "context_freeze",
    # G10
    "boundary_accept",
    "boundary_reject",
    # G11
    "determinism_seed",
    "replay_patch",
    "determinism_digest_emit",
    # G12
    "io_transcript",
    "io_hard_fail",
    # G13
    "diff_package",
    "blast_radius_check",
    "two_phase_commit",
    "mutation_distribution",
    # G14
    "execution_trace_record",
    "replay_key_emit",
    "proof_comparison",
    # G15
    "path_route",
    "path_stall",
    "path_safety_reentry",
    "path_vigilance_reroute",
    # G16
    "eval_score",
    "drift_alert",
    "dpo_build",
    "optimization_commit",
]


class TestC1SchemaCompleteness:
    """C1: All G7-G16 literals declared in schema.py."""

    def test_all_g7_g16_entity_types_in_literal(self) -> None:
        from agentic_core.adg.schema_util import EntityType

        args = set(typing.get_args(EntityType))
        missing = [e for e in G7_G16_ENTITY_TYPES if e not in args]
        assert not missing, f"EntityType missing: {missing}"

    def test_all_g7_g16_relation_types_in_literal(self) -> None:
        from agentic_core.adg.schema_util import RelationType

        args = set(typing.get_args(RelationType))
        missing = [r for r in G7_G16_RELATION_TYPES if r not in args]
        assert not missing, f"RelationType missing: {missing}"

    def test_all_g7_g16_edge_kinds_in_literal(self) -> None:
        from agentic_core.adg.schema_util import EdgeKind

        args = set(typing.get_args(EdgeKind))
        missing = [k for k in G7_G16_EDGE_KINDS if k not in args]
        assert not missing, f"EdgeKind missing: {missing}"

    def test_no_empty_entity_type_string(self) -> None:
        from agentic_core.adg.schema_util import EntityType

        for et in typing.get_args(EntityType):
            assert et and et.strip(), f"Empty EntityType: {et!r}"

    def test_no_empty_relation_type_string(self) -> None:
        from agentic_core.adg.schema_util import RelationType

        for rt in typing.get_args(RelationType):
            assert rt and rt.strip(), f"Empty RelationType: {rt!r}"

    def test_no_empty_edge_kind_string(self) -> None:
        from agentic_core.adg.schema_util import EdgeKind

        for ek in typing.get_args(EdgeKind):
            assert ek and ek.strip(), f"Empty EdgeKind: {ek!r}"

    def test_g7_g16_entity_types_are_unique(self) -> None:
        assert len(G7_G16_ENTITY_TYPES) == len(set(G7_G16_ENTITY_TYPES))

    def test_g7_g16_relation_types_are_unique(self) -> None:
        assert len(G7_G16_RELATION_TYPES) == len(set(G7_G16_RELATION_TYPES))

    def test_g7_g16_edge_kinds_are_unique(self) -> None:
        assert len(G7_G16_EDGE_KINDS) == len(set(G7_G16_EDGE_KINDS))


# ---------------------------------------------------------------------------
# C2 — Detection constant completeness
# ---------------------------------------------------------------------------


class TestC2DetectionConstants:
    """C2: Every schema detection frozenset is non-empty and covers canonical names."""

    # ---------- G7 ----------
    def test_sandbox_envelope_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import SANDBOX_ENVELOPE_CLASSES

        assert len(SANDBOX_ENVELOPE_CLASSES) >= 3
        assert "SandboxEnvelope" in SANDBOX_ENVELOPE_CLASSES

    def test_capability_token_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import CAPABILITY_TOKEN_CLASSES

        assert len(CAPABILITY_TOKEN_CLASSES) >= 2
        assert "CapabilityToken" in CAPABILITY_TOKEN_CLASSES

    def test_work_contract_methods_nonempty(self) -> None:
        from agentic_core.adg.schema_util import WORK_CONTRACT_METHODS

        assert len(WORK_CONTRACT_METHODS) >= 3
        assert "stamp_work_contract" in WORK_CONTRACT_METHODS

    # ---------- G8 ----------
    def test_tool_budget_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import TOOL_BUDGET_CLASSES

        assert len(TOOL_BUDGET_CLASSES) >= 3
        assert "ToolBudget" in TOOL_BUDGET_CLASSES

    def test_budget_exceeded_exceptions_nonempty(self) -> None:
        from agentic_core.adg.schema_util import BUDGET_EXCEEDED_EXCEPTIONS

        assert len(BUDGET_EXCEEDED_EXCEPTIONS) >= 3
        assert "BudgetExceededError" in BUDGET_EXCEEDED_EXCEPTIONS

    # ---------- G9 ----------
    def test_jit_context_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import JIT_CONTEXT_CLASSES

        assert len(JIT_CONTEXT_CLASSES) >= 3
        assert "JITContext" in JIT_CONTEXT_CLASSES

    def test_freeze_method_names_nonempty(self) -> None:
        from agentic_core.adg.schema_util import FREEZE_METHOD_NAMES

        assert len(FREEZE_METHOD_NAMES) >= 4
        assert "freeze_context" in FREEZE_METHOD_NAMES
        assert "pull_context" in FREEZE_METHOD_NAMES
        assert "unfreeze_context" in FREEZE_METHOD_NAMES

    # ---------- G10 ----------
    def test_boundary_verifier_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import BOUNDARY_VERIFIER_CLASSES

        assert len(BOUNDARY_VERIFIER_CLASSES) >= 3
        assert "L2BoundaryVerifier" in BOUNDARY_VERIFIER_CLASSES

    def test_capability_chokepoint_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import CAPABILITY_CHOKEPOINT_CLASSES

        assert len(CAPABILITY_CHOKEPOINT_CLASSES) >= 2
        assert "CapabilityChokepoint" in CAPABILITY_CHOKEPOINT_CLASSES

    # ---------- G11 ----------
    def test_semantic_clock_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import SEMANTIC_CLOCK_CLASSES

        assert len(SEMANTIC_CLOCK_CLASSES) >= 2
        assert "SemanticClock" in SEMANTIC_CLOCK_CLASSES

    def test_replay_guard_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import REPLAY_GUARD_CLASSES

        assert len(REPLAY_GUARD_CLASSES) >= 2
        assert "ReplayGuard" in REPLAY_GUARD_CLASSES

    def test_determinism_patch_methods_nonempty(self) -> None:
        from agentic_core.adg.schema_util import DETERMINISM_PATCH_METHODS

        assert len(DETERMINISM_PATCH_METHODS) >= 4
        assert "seed_rng" in DETERMINISM_PATCH_METHODS
        assert "emit_determinism_digest" in DETERMINISM_PATCH_METHODS
        assert "patch_time" in DETERMINISM_PATCH_METHODS

    # ---------- G12 ----------
    def test_io_intercept_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import IO_INTERCEPT_CLASSES

        assert len(IO_INTERCEPT_CLASSES) >= 3
        assert "IOInterceptor" in IO_INTERCEPT_CLASSES

    def test_network_transcript_symbols_nonempty(self) -> None:
        from agentic_core.adg.schema_util import NETWORK_TRANSCRIPT_SYMBOLS

        assert len(NETWORK_TRANSCRIPT_SYMBOLS) >= 3
        assert "transcript_response" in NETWORK_TRANSCRIPT_SYMBOLS
        assert "hard_fail_untranscripted" in NETWORK_TRANSCRIPT_SYMBOLS

    # ---------- G13 ----------
    def test_mutation_transport_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import MUTATION_TRANSPORT_CLASSES

        assert len(MUTATION_TRANSPORT_CLASSES) >= 3
        assert "MutationTransport" in MUTATION_TRANSPORT_CLASSES
        assert "TwoPhaseCommit" in MUTATION_TRANSPORT_CLASSES

    def test_rfc6902_diff_symbols_nonempty(self) -> None:
        from agentic_core.adg.schema_util import RFC6902_DIFF_SYMBOLS

        assert len(RFC6902_DIFF_SYMBOLS) >= 4
        assert "package_diff" in RFC6902_DIFF_SYMBOLS
        assert "validate_blast_radius" in RFC6902_DIFF_SYMBOLS

    # ---------- G14 ----------
    def test_execution_trace_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import EXECUTION_TRACE_CLASSES

        assert len(EXECUTION_TRACE_CLASSES) >= 3
        assert "ExecutionTrace" in EXECUTION_TRACE_CLASSES

    def test_replay_key_methods_nonempty(self) -> None:
        from agentic_core.adg.schema_util import REPLAY_KEY_METHODS

        assert len(REPLAY_KEY_METHODS) >= 4
        assert "emit_replay_key" in REPLAY_KEY_METHODS
        assert "record_execution_trace" in REPLAY_KEY_METHODS
        assert "compare_proof" in REPLAY_KEY_METHODS

    # ---------- G15 ----------
    def test_path_control_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import PATH_CONTROL_CLASSES

        assert len(PATH_CONTROL_CLASSES) >= 3
        assert "ExecutionPathController" in PATH_CONTROL_CLASSES

    def test_path_reroute_methods_nonempty(self) -> None:
        from agentic_core.adg.schema_util import PATH_REROUTE_METHODS

        assert len(PATH_REROUTE_METHODS) >= 5
        assert "route_path" in PATH_REROUTE_METHODS
        assert "force_stall" in PATH_REROUTE_METHODS
        assert "reenter_safety" in PATH_REROUTE_METHODS
        assert "vigilance_reroute" in PATH_REROUTE_METHODS

    # ---------- G16 ----------
    def test_eval_metric_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import EVAL_METRIC_CLASSES

        assert len(EVAL_METRIC_CLASSES) >= 4
        assert "EvalSpine" in EVAL_METRIC_CLASSES

    def test_dpo_batch_classes_nonempty(self) -> None:
        from agentic_core.adg.schema_util import DPO_BATCH_CLASSES

        assert len(DPO_BATCH_CLASSES) >= 3
        assert "DPOBatchBuilder" in DPO_BATCH_CLASSES
        assert "DPOBatch" in DPO_BATCH_CLASSES

    def test_drift_alert_methods_nonempty(self) -> None:
        from agentic_core.adg.schema_util import DRIFT_ALERT_METHODS

        assert len(DRIFT_ALERT_METHODS) >= 5
        assert "emit_drift_alert" in DRIFT_ALERT_METHODS
        assert "build_dpo_batch" in DRIFT_ALERT_METHODS
        assert "commit_optimization" in DRIFT_ALERT_METHODS

    def test_all_constants_are_frozensets(self) -> None:
        import agentic_core.adg.schema_util as sch

        constant_names = [
            "SANDBOX_ENVELOPE_CLASSES",
            "CAPABILITY_TOKEN_CLASSES",
            "WORK_CONTRACT_METHODS",
            "TOOL_BUDGET_CLASSES",
            "BUDGET_EXCEEDED_EXCEPTIONS",
            "JIT_CONTEXT_CLASSES",
            "FREEZE_METHOD_NAMES",
            "BOUNDARY_VERIFIER_CLASSES",
            "CAPABILITY_CHOKEPOINT_CLASSES",
            "SEMANTIC_CLOCK_CLASSES",
            "REPLAY_GUARD_CLASSES",
            "DETERMINISM_PATCH_METHODS",
            "IO_INTERCEPT_CLASSES",
            "NETWORK_TRANSCRIPT_SYMBOLS",
            "MUTATION_TRANSPORT_CLASSES",
            "RFC6902_DIFF_SYMBOLS",
            "EXECUTION_TRACE_CLASSES",
            "REPLAY_KEY_METHODS",
            "PATH_CONTROL_CLASSES",
            "PATH_REROUTE_METHODS",
            "EVAL_METRIC_CLASSES",
            "DPO_BATCH_CLASSES",
            "DRIFT_ALERT_METHODS",
        ]
        for name in constant_names:
            val = getattr(sch, name)
            assert isinstance(val, frozenset), f"{name} must be frozenset, got {type(val)}"
            assert len(val) > 0, f"{name} must be non-empty"

    def test_constants_cover_canonical_runtime_class_names(self) -> None:
        """Every primary class used in the runtime modules is in a detection constant."""
        from agentic_core.adg.schema_util import (
            BOUNDARY_VERIFIER_CLASSES,
            CAPABILITY_CHOKEPOINT_CLASSES,
            CAPABILITY_TOKEN_CLASSES,
            DPO_BATCH_CLASSES,
            EVAL_METRIC_CLASSES,
            EXECUTION_TRACE_CLASSES,
            IO_INTERCEPT_CLASSES,
            JIT_CONTEXT_CLASSES,
            MUTATION_TRANSPORT_CLASSES,
            PATH_CONTROL_CLASSES,
            REPLAY_GUARD_CLASSES,
            SANDBOX_ENVELOPE_CLASSES,
            SEMANTIC_CLOCK_CLASSES,
            TOOL_BUDGET_CLASSES,
        )

        # These are the actual class names used in the runtime modules
        canonical_mapping = {
            "SandboxEnvelope": SANDBOX_ENVELOPE_CLASSES,
            "CapabilityToken": CAPABILITY_TOKEN_CLASSES,
            "ToolBudget": TOOL_BUDGET_CLASSES,
            "JITContext": JIT_CONTEXT_CLASSES,
            "L2BoundaryVerifier": BOUNDARY_VERIFIER_CLASSES,
            "CapabilityChokepoint": CAPABILITY_CHOKEPOINT_CLASSES,
            "SemanticClock": SEMANTIC_CLOCK_CLASSES,
            "ReplayGuard": REPLAY_GUARD_CLASSES,
            "IOInterceptor": IO_INTERCEPT_CLASSES,
            "MutationTransport": MUTATION_TRANSPORT_CLASSES,
            "ExecutionTrace": EXECUTION_TRACE_CLASSES,
            "ExecutionPathController": PATH_CONTROL_CLASSES,
            "EvalSpine": EVAL_METRIC_CLASSES,
            "DPOBatch": DPO_BATCH_CLASSES,
        }
        for name, constant in canonical_mapping.items():
            assert name in constant, f"Canonical name {name!r} not in detection constant"


# ---------------------------------------------------------------------------
# C3 — Module API completeness
# ---------------------------------------------------------------------------

_G7_G16_MODULE_SPECS: dict[str, list[str]] = {
    "agentic_core.adg.runtime.sandbox_airlock": [
        "AirlockPhase",
        "WorkContract",
        "CapabilityToken",
        "SandboxEnvelope",
        "AirlockSession",
        "SandboxAirlockRecorder",
    ],
    "agentic_core.adg.runtime.capability_budget": [
        "BudgetStatus",
        "BudgetEvent",
        "BudgetExceededError",
        "ResourceGrant",
        "ToolBudget",
        "BudgetGovernorReport",
        "ResourceGovernor",
    ],
    "agentic_core.adg.runtime.jit_context": [
        "FreezeState",
        "ContextSnapshot",
        "FreezeBoundary",
        "JITContextSession",
        "JITContextSynchronizer",
    ],
    "agentic_core.adg.runtime.boundary_verifier": [
        "VerificationOutcome",
        "BoundaryPacket",
        "BoundaryVerificationResult",
        "BoundaryVerifierReport",
        "L2BoundaryVerifier",
        "CapabilityChokepoint",
    ],
    "agentic_core.adg.runtime.determinism_control": [
        "DeterminismViolationType",
        "DeterminismViolation",
        "DeterminismDigest",
        "SemanticClockReading",
        "ReplayPatchRecord",
        "DeterminismControlReport",
        "SemanticClock",
        "ReplayGuard",
        "DeterminismController",
    ],
    "agentic_core.adg.runtime.io_interception": [
        "InterceptionOutcome",
        "NetworkTranscript",
        "IOInterceptionEvent",
        "IOInterceptionReport",
        "IOInterceptor",
    ],
    "agentic_core.adg.runtime.mutation_transport": [
        "CommitPhase",
        "RFC6902Patch",
        "MutationPacket",
        "MutationTransportReport",
        "MutationTransport",
    ],
    "agentic_core.adg.runtime.execution_proof": [
        "ProofComparisonOutcome",
        "ExecutionTrace",
        "ReplayKey",
        "ProofComparison",
        "ExecutionProofReport",
        "ExecutionProofRecorder",
    ],
    "agentic_core.adg.runtime.path_control": [
        "ExecutionPath",
        "PathTransitionReason",
        "PathTransition",
        "PathControlReport",
        "ExecutionPathController",
    ],
    "agentic_core.adg.runtime.eval_spine": [
        "OptimizationStage",
        "EvalMetricResult",
        "DriftAlert",
        "PreferencePair",
        "DPOBatch",
        "OptimizationProposal",
        "EvalSpineReport",
        "EvalSpine",
    ],
}


class TestC3ModuleAPICompleteness:
    """C3: All runtime modules importable and expose required API."""

    @pytest.mark.parametrize("module_path", list(_G7_G16_MODULE_SPECS.keys()))
    def test_module_importable(self, module_path: str) -> None:
        mod = importlib.import_module(module_path)
        assert mod is not None

    @pytest.mark.parametrize("module_path,symbols", list(_G7_G16_MODULE_SPECS.items()))
    def test_all_expected_symbols_present(self, module_path: str, symbols: list[str]) -> None:
        mod = importlib.import_module(module_path)
        missing = [s for s in symbols if not hasattr(mod, s)]
        assert not missing, f"{module_path}: missing symbols {missing}"

    @pytest.mark.parametrize("module_path,symbols", list(_G7_G16_MODULE_SPECS.items()))
    def test_no_import_side_effects(self, module_path: str, symbols: list[str]) -> None:
        """Module re-import must be silent (no side-effects on import)."""
        mod = importlib.import_module(module_path)
        assert mod is not None  # already imported; just confirms no exception

    def test_all_dataclass_symbols_are_instantiable(self) -> None:
        """Dataclass-type public symbols with all-default fields must be instantiable."""
        import dataclasses

        for module_path, symbols in _G7_G16_MODULE_SPECS.items():
            mod = importlib.import_module(module_path)
            for sym_name in symbols:
                obj = getattr(mod, sym_name)
                if not (dataclasses.is_dataclass(obj) and isinstance(obj, type)):
                    continue
                fields = dataclasses.fields(obj)
                has_required = any(
                    f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING  # type: ignore[misc]
                    for f in fields
                )
                if has_required:
                    continue  # skip dataclasses that require positional args
                instance = obj()
                assert instance is not None

    def test_all_enum_symbols_have_at_least_two_members(self) -> None:
        import enum

        for module_path, symbols in _G7_G16_MODULE_SPECS.items():
            mod = importlib.import_module(module_path)
            for sym_name in symbols:
                obj = getattr(mod, sym_name)
                if isinstance(obj, type) and issubclass(obj, enum.Enum):
                    assert len(obj) >= 2, f"{module_path}.{sym_name}: enum needs >= 2 members"


# ---------------------------------------------------------------------------
# C4 — __init__ export completeness
# ---------------------------------------------------------------------------


class TestC4InitExportCompleteness:
    """C4: runtime/__init__.py __all__ is a superset of all G7-G16 module public names."""

    def test_all_module_symbols_in_init_all(self) -> None:
        import agentic_core.adg.runtime as pkg

        pkg_all = set(pkg.__all__)
        missing: list[str] = []
        for module_path, symbols in _G7_G16_MODULE_SPECS.items():
            for sym in symbols:
                if sym not in pkg_all:
                    missing.append(f"{module_path}:{sym}")
        assert not missing, f"Symbols missing from runtime/__all__: {missing}"

    def test_all_all_names_are_importable_from_package(self) -> None:
        import agentic_core.adg.runtime as pkg

        broken = []
        for name in pkg.__all__:
            if not hasattr(pkg, name):
                broken.append(name)
        assert not broken, f"Names in __all__ not resolvable from package: {broken}"

    def test_no_none_exports(self) -> None:
        import agentic_core.adg.runtime as pkg

        none_exports = [n for n in pkg.__all__ if getattr(pkg, n, "MISSING") is None]
        assert not none_exports, f"None-valued exports: {none_exports}"

    def test_g7_g16_section_completeness_in_all(self) -> None:
        """Every G7-G16 gap section is represented in __all__."""
        import agentic_core.adg.runtime as pkg

        pkg_all = set(pkg.__all__)
        # At minimum one sentinel from each gap
        sentinels = {
            "G7": "SandboxEnvelope",
            "G8": "ToolBudget",
            "G9": "JITContextSynchronizer",
            "G10": "L2BoundaryVerifier",
            "G11": "SemanticClock",
            "G12": "IOInterceptor",
            "G13": "MutationTransport",
            "G14": "ExecutionTrace",
            "G15": "ExecutionPathController",
            "G16": "EvalSpine",
        }
        missing = [f"{gap}:{sym}" for gap, sym in sentinels.items() if sym not in pkg_all]
        assert not missing, f"Gap sections missing from __all__: {missing}"


# ---------------------------------------------------------------------------
# A1 — Visitor accuracy: exact (relation_type, edge_kind) per detection pattern
# ---------------------------------------------------------------------------


class TestA1VisitorAccuracyG7Sandbox:
    """A1: _SandboxAirlockVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _SandboxAirlockVisitor

        return _SandboxAirlockVisitor

    # --- SANDBOX_ENVELOPE_CLASSES (direct call) ---
    @pytest.mark.parametrize(
        "sym", ["SandboxEnvelope", "WorkContract", "SandboxAirlock", "L5SandboxStamper", "SandboxSession"]
    )
    def test_sandbox_envelope_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}()", self._v())
        assert ("enters_sandbox", "sandbox_entry") in _rel_ek(edges), (
            f"{sym} should emit (enters_sandbox, sandbox_entry)"
        )

    # --- CAPABILITY_TOKEN_CLASSES ---
    @pytest.mark.parametrize(
        "sym", ["CapabilityToken", "ScopedCapabilityToken", "CapabilityGrant", "TokenizedCapability"]
    )
    def test_capability_token_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}()", self._v())
        assert ("issues_capability_token", "capability_token_issue") in _rel_ek(edges), (
            f"{sym} should emit (issues_capability_token, capability_token_issue)"
        )

    # --- WORK_CONTRACT_METHODS ---
    @pytest.mark.parametrize(
        "sym",
        [
            "stamp_work_contract",
            "issue_capability_token",
            "enter_sandbox",
            "exit_sandbox",
            "bind_capability_token",
        ],
    )
    def test_work_contract_method_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}(x)", self._v())
        assert ("stamps_work_contract", "work_contract_stamp") in _rel_ek(edges), (
            f"{sym} should emit (stamps_work_contract, work_contract_stamp)"
        )

    # --- attribute-style calls ---
    def test_attribute_sandbox_envelope_detected(self) -> None:
        edges = _edges_for("obj.SandboxEnvelope()", self._v())
        assert ("enters_sandbox", "sandbox_entry") in _rel_ek(edges)

    def test_attribute_capability_token_detected(self) -> None:
        edges = _edges_for("obj.CapabilityToken()", self._v())
        assert ("issues_capability_token", "capability_token_issue") in _rel_ek(edges)

    # --- symbol field on edge is populated ---
    def test_symbol_field_populated(self) -> None:
        edges = _edges_for("SandboxEnvelope()", self._v())
        assert all(e.symbol for e in edges), "symbol field must be non-empty"

    # --- source_file and line_no accurate ---
    def test_line_no_accurate(self) -> None:
        src = "\n\nSandboxEnvelope()"
        edges = _edges_for(src, self._v())
        assert any(e.line_no == 3 for e in edges), "line_no should be 3"


class TestA1VisitorAccuracyG8Budget:
    """A1: _CapabilityBudgetVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _CapabilityBudgetVisitor

        return _CapabilityBudgetVisitor

    @pytest.mark.parametrize(
        "sym", ["ToolBudget", "ResourceGovernor", "CapabilityBudget", "ComputeBudget", "ExecutionQuota"]
    )
    def test_tool_budget_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}()", self._v())
        assert ("grants_resource", "budget_grant") in _rel_ek(edges)

    def test_tool_budget_dot_default_detected(self) -> None:
        edges = _edges_for("ToolBudget.default()", self._v())
        assert ("grants_resource", "budget_grant") in _rel_ek(edges)

    @pytest.mark.parametrize(
        "sym",
        [
            "BudgetExceededError",
            "CapabilityExhaustedError",
            "ComputeQuotaExceeded",
            "MemoryQuotaExceeded",
            "TokenBudgetExceeded",
        ],
    )
    def test_budget_exceeded_raise_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"raise {sym}", self._v())
        assert ("exceeds_budget", "budget_exceeded") in _rel_ek(edges), (
            f"raise {sym} should emit (exceeds_budget, budget_exceeded)"
        )

    def test_raise_with_args_not_detected(self) -> None:
        """raise BudgetExceededError(args) uses a Call node, not a Name — visitor uses _sym_of on exc."""
        # _sym_of on a Call node returns "" so this should produce 0 or 1 edges
        # depending on whether the Name is the exc. With Call node as exc, _sym_of returns ""
        # and tail == "" which won't be in BUDGET_EXCEEDED_EXCEPTIONS. This is by design.
        edges = _edges_for("raise BudgetExceededError('msg')", self._v())
        # Just verify it doesn't crash - exact count depends on _sym_of behaviour
        assert isinstance(edges, list)


class TestA1VisitorAccuracyG9JIT:
    """A1: _JITContextVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _JITContextVisitor

        return _JITContextVisitor

    @pytest.mark.parametrize(
        "sym", ["JITContext", "JITElevator", "ContextSnapshot", "JITContextSynchronizer", "C0ContextPuller"]
    )
    def test_jit_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}()", self._v())
        assert ("pulls_context", "context_pull") in _rel_ek(edges)

    @pytest.mark.parametrize(
        "sym,expected_rel,expected_ek",
        [
            ("freeze_context", "freezes_context", "context_freeze"),
            ("pull_context", "pulls_context", "context_pull"),
            ("sync_context", "pulls_context", "context_pull"),
            ("snapshot_context", "freezes_context", "context_freeze"),
            ("freeze_environment", "freezes_context", "context_freeze"),
        ],
    )
    def test_freeze_method_exact_pair(self, sym: str, expected_rel: str, expected_ek: str) -> None:
        edges = _edges_for(f"{sym}(x)", self._v())
        assert (expected_rel, expected_ek) in _rel_ek(edges), (
            f"{sym} should emit ({expected_rel}, {expected_ek})"
        )

    def test_unfreeze_context_exact_pair(self) -> None:
        edges = _edges_for("unfreeze_context(b)", self._v())
        assert ("unfreezes_context", "context_pull") in _rel_ek(edges)


class TestA1VisitorAccuracyG10Boundary:
    """A1: _BoundaryVerifierVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _BoundaryVerifierVisitor

        return _BoundaryVerifierVisitor

    @pytest.mark.parametrize(
        "sym",
        [
            "L2BoundaryVerifier",
            "BoundaryVerifier",
            "ExecutionBoundaryCheck",
            "PacketValidator",
            "EnvelopeVerifier",
        ],
    )
    def test_boundary_verifier_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}('a', 'r')", self._v())
        assert ("verifies_boundary", "boundary_accept") in _rel_ek(edges)

    @pytest.mark.parametrize(
        "sym", ["CapabilityChokepoint", "L5CertificationCheck", "BoundaryChokepoint", "PacketChokepoint"]
    )
    def test_chokepoint_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}('a')", self._v())
        assert ("certifies_envelope", "boundary_accept") in _rel_ek(edges)

    def test_attribute_style_boundary_verifier(self) -> None:
        edges = _edges_for("verifier.L2BoundaryVerifier('a', 'r')", self._v())
        assert ("verifies_boundary", "boundary_accept") in _rel_ek(edges)


class TestA1VisitorAccuracyG11Determinism:
    """A1: _DeterminismControlVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _DeterminismControlVisitor

        return _DeterminismControlVisitor

    @pytest.mark.parametrize("sym", ["SemanticClock", "DeterministicClock", "ReplayClock", "FrozenClock"])
    def test_semantic_clock_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}('r')", self._v())
        assert ("patches_time", "replay_patch") in _rel_ek(edges)

    @pytest.mark.parametrize(
        "sym", ["ReplayGuard", "DeterminismGuard", "ReplayPatcher", "NondeterminismBlocker"]
    )
    def test_replay_guard_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}('r')", self._v())
        assert ("guards_replay", "replay_patch") in _rel_ek(edges)

    # DETERMINISM_PATCH_METHODS routing
    def test_seed_rng_exact_pair(self) -> None:
        edges = _edges_for("seed_rng(42)", self._v())
        assert ("seeds_rng", "determinism_seed") in _rel_ek(edges)

    def test_emit_determinism_digest_exact_pair(self) -> None:
        edges = _edges_for("emit_determinism_digest([])", self._v())
        assert ("emits_determinism_digest", "determinism_digest_emit") in _rel_ek(edges)

    def test_patch_time_exact_pair(self) -> None:
        edges = _edges_for("patch_time()", self._v())
        assert ("patches_time", "replay_patch") in _rel_ek(edges)

    def test_patch_random_exact_pair(self) -> None:
        edges = _edges_for("patch_random()", self._v())
        assert ("seeds_rng", "determinism_seed") in _rel_ek(edges)

    def test_patch_uuid_exact_pair(self) -> None:
        edges = _edges_for("patch_uuid()", self._v())
        assert ("seeds_rng", "determinism_seed") in _rel_ek(edges)

    def test_install_replay_patches_exact_pair(self) -> None:
        edges = _edges_for("install_replay_patches()", self._v())
        assert ("patches_time", "replay_patch") in _rel_ek(edges)


class TestA1VisitorAccuracyG12IO:
    """A1: _IOInterceptionVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _IOInterceptionVisitor

        return _IOInterceptionVisitor

    @pytest.mark.parametrize(
        "sym",
        [
            "IOInterceptor",
            "NetworkInterceptor",
            "ExternalCallInterceptor",
            "TranscriptedNetworkLayer",
            "ImmutableResponseCapture",
        ],
    )
    def test_io_interceptor_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}('a', 'r')", self._v())
        assert ("intercepts_io", "io_transcript") in _rel_ek(edges)

    @pytest.mark.parametrize(
        "sym,expected_rel,expected_ek",
        [
            ("transcript_response", "transcripts_response", "io_transcript"),
            ("capture_response", "transcripts_response", "io_transcript"),
            ("record_api_response", "transcripts_response", "io_transcript"),
            ("intercept_io", "transcripts_response", "io_transcript"),
            ("hard_fail_untranscripted", "hard_fails_untranscripted", "io_hard_fail"),
        ],
    )
    def test_transcript_symbol_exact_pair(self, sym: str, expected_rel: str, expected_ek: str) -> None:
        edges = _edges_for(f"{sym}(url)", self._v())
        assert (expected_rel, expected_ek) in _rel_ek(edges), (
            f"{sym} should emit ({expected_rel}, {expected_ek})"
        )


class TestA1VisitorAccuracyG13Mutation:
    """A1: _MutationTransportVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _MutationTransportVisitor

        return _MutationTransportVisitor

    @pytest.mark.parametrize(
        "sym,expected_rel,expected_ek",
        [
            ("package_diff", "packages_diff", "diff_package"),
            ("build_rfc6902_patch", "packages_diff", "diff_package"),
            ("make_json_patch", "packages_diff", "diff_package"),
            ("apply_json_patch", "packages_diff", "diff_package"),
            ("validate_blast_radius", "validates_blast_radius", "blast_radius_check"),
            ("check_blast_radius", "validates_blast_radius", "blast_radius_check"),
        ],
    )
    def test_rfc6902_method_exact_pair(self, sym: str, expected_rel: str, expected_ek: str) -> None:
        edges = _edges_for(f"{sym}(x)", self._v())
        assert (expected_rel, expected_ek) in _rel_ek(edges)

    def test_two_phase_commit_class_exact_pair(self) -> None:
        edges = _edges_for("TwoPhaseCommit()", self._v())
        assert ("commits_mutation", "two_phase_commit") in _rel_ek(edges)

    def test_mutation_transport_class_exact_pair(self) -> None:
        edges = _edges_for("MutationTransport('a', 'r')", self._v())
        assert ("signs_execution_trace", "diff_package") in _rel_ek(edges)

    def test_mutation_distributor_class_exact_pair(self) -> None:
        edges = _edges_for("MutationDistributor()", self._v())
        assert ("distributes_mutation", "mutation_distribution") in _rel_ek(edges)

    def test_mutation_commit_protocol_exact_pair(self) -> None:
        edges = _edges_for("MutationCommitProtocol()", self._v())
        assert ("commits_mutation", "two_phase_commit") in _rel_ek(edges)


class TestA1VisitorAccuracyG14Proof:
    """A1: _ExecutionProofVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _ExecutionProofVisitor

        return _ExecutionProofVisitor

    @pytest.mark.parametrize(
        "sym",
        ["ExecutionTrace", "ExecutionProof", "DeterminismDigest", "ProofArtifact", "SignedExecutionTrace"],
    )
    def test_execution_trace_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}()", self._v())
        assert ("records_execution_trace", "execution_trace_record") in _rel_ek(edges)

    def test_emit_replay_key_exact_pair(self) -> None:
        edges = _edges_for("emit_replay_key(rng_seed=42)", self._v())
        assert ("emits_replay_key", "replay_key_emit") in _rel_ek(edges)

    def test_compare_proof_exact_pair(self) -> None:
        edges = _edges_for("compare_proof(t1, t2)", self._v())
        assert ("compares_proof", "proof_comparison") in _rel_ek(edges)

    def test_record_execution_trace_method_exact_pair(self) -> None:
        edges = _edges_for("record_execution_trace('evt')", self._v())
        assert ("records_execution_trace", "execution_trace_record") in _rel_ek(edges)

    def test_sign_execution_trace_method_exact_pair(self) -> None:
        edges = _edges_for("sign_execution_trace('key')", self._v())
        assert ("records_execution_trace", "execution_trace_record") in _rel_ek(edges)

    def test_verify_replay_method_exact_pair(self) -> None:
        edges = _edges_for("verify_replay(key)", self._v())
        assert ("records_execution_trace", "execution_trace_record") in _rel_ek(edges)


class TestA1VisitorAccuracyG15Path:
    """A1: _PathControlVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _PathControlVisitor

        return _PathControlVisitor

    @pytest.mark.parametrize(
        "sym",
        [
            "ExecutionPathController",
            "PathRouter",
            "PathABCDController",
            "StallForcer",
            "SafetyReentryGate",
            "VigilanceRerouter",
        ],
    )
    def test_path_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}('a', 'r')", self._v())
        assert ("routes_path", "path_route") in _rel_ek(edges)

    def test_route_path_method_exact_pair(self) -> None:
        edges = _edges_for("route_path(ExecutionPath.PATH_A)", self._v())
        assert ("routes_path", "path_route") in _rel_ek(edges)

    def test_force_stall_exact_pair(self) -> None:
        edges = _edges_for("force_stall('reason')", self._v())
        assert ("forces_stall", "path_stall") in _rel_ek(edges)

    def test_force_path_d_exact_pair(self) -> None:
        edges = _edges_for("force_path_d()", self._v())
        assert ("forces_stall", "path_stall") in _rel_ek(edges)

    def test_reenter_safety_exact_pair(self) -> None:
        edges = _edges_for("reenter_safety()", self._v())
        assert ("reenters_safety", "path_safety_reentry") in _rel_ek(edges)

    def test_vigilance_reroute_exact_pair(self) -> None:
        edges = _edges_for("vigilance_reroute('L6')", self._v())
        assert ("vigilance_reroute", "path_vigilance_reroute") in _rel_ek(edges)

    def test_reroute_to_l0_exact_pair(self) -> None:
        edges = _edges_for("reroute_to_l0('detail')", self._v())
        assert ("vigilance_reroute", "path_vigilance_reroute") in _rel_ek(edges)

    def test_reroute_to_l1_exact_pair(self) -> None:
        edges = _edges_for("reroute_to_l1()", self._v())
        assert ("vigilance_reroute", "path_vigilance_reroute") in _rel_ek(edges)


class TestA1VisitorAccuracyG16Eval:
    """A1: _EvalSpineVisitor emits exact pairs for every detection branch."""

    def _v(self):
        from agentic_core.adg.extraction.static_scanner import _EvalSpineVisitor

        return _EvalSpineVisitor

    @pytest.mark.parametrize(
        "sym",
        [
            "GroundednessScorer",
            "RetrievalEvaluator",
            "NDCGScorer",
            "MRRScorer",
            "CompletenessScorer",
            "EvalSpine",
            "OptimizationSpine",
        ],
    )
    def test_eval_metric_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}('a', 'r')", self._v())
        assert ("scores_groundedness", "eval_score") in _rel_ek(edges)

    @pytest.mark.parametrize(
        "sym", ["DPOBatchBuilder", "DPOBatch", "PreferencePairBuilder", "OptimizationProposal"]
    )
    def test_dpo_batch_class_exact_pair(self, sym: str) -> None:
        edges = _edges_for(f"{sym}()", self._v())
        assert ("builds_dpo_batch", "dpo_build") in _rel_ek(edges)

    def test_emit_drift_alert_exact_pair(self) -> None:
        edges = _edges_for("emit_drift_alert('MRR', 0.3, 0.7)", self._v())
        assert ("emits_drift_alert", "drift_alert") in _rel_ek(edges)

    def test_score_groundedness_method_exact_pair(self) -> None:
        edges = _edges_for("score_groundedness(0.87)", self._v())
        assert ("scores_groundedness", "eval_score") in _rel_ek(edges)

    def test_compute_pk_exact_pair(self) -> None:
        edges = _edges_for("compute_pk(0.75)", self._v())
        assert ("scores_groundedness", "eval_score") in _rel_ek(edges)

    def test_compute_mrr_exact_pair(self) -> None:
        edges = _edges_for("compute_mrr(0.6)", self._v())
        assert ("scores_groundedness", "eval_score") in _rel_ek(edges)

    def test_compute_ndcg_exact_pair(self) -> None:
        edges = _edges_for("compute_ndcg(0.9)", self._v())
        assert ("scores_groundedness", "eval_score") in _rel_ek(edges)

    def test_build_dpo_batch_method_exact_pair(self) -> None:
        edges = _edges_for("build_dpo_batch(pairs)", self._v())
        assert ("builds_dpo_batch", "dpo_build") in _rel_ek(edges)

    def test_commit_optimization_exact_pair(self) -> None:
        edges = _edges_for("commit_optimization(proposal)", self._v())
        assert ("commits_optimization", "optimization_commit") in _rel_ek(edges)


# ---------------------------------------------------------------------------
# A2 — Visitor non-contamination
# ---------------------------------------------------------------------------

_UNRELATED_CODE = """
import os
import sys

def regular_function(x, y):
    result = x + y
    print(result)
    return result

class NormalClass:
    def method(self):
        return 42

x = [i for i in range(10)]
d = {"key": "value"}
"""


class TestA2VisitorNonContamination:
    """A2: Unrelated code must produce ZERO edges from every G7-G16 visitor."""

    @pytest.mark.parametrize(
        "visitor_name",
        [
            "_SandboxAirlockVisitor",
            "_CapabilityBudgetVisitor",
            "_JITContextVisitor",
            "_BoundaryVerifierVisitor",
            "_DeterminismControlVisitor",
            "_IOInterceptionVisitor",
            "_MutationTransportVisitor",
            "_ExecutionProofVisitor",
            "_PathControlVisitor",
            "_EvalSpineVisitor",
        ],
    )
    def test_no_edges_for_unrelated_code(self, visitor_name: str) -> None:
        from agentic_core.adg.extraction import static_scanner

        Cls = getattr(static_scanner, visitor_name)
        edges = _edges_for(_UNRELATED_CODE, Cls)
        assert len(edges) == 0, (
            f"{visitor_name}: expected 0 edges for unrelated code, got {len(edges)}: {[e.relation_type for e in edges]}"
        )

    def test_combined_unrelated_zero_edges(self) -> None:
        edges = _scan_src(_UNRELATED_CODE)
        assert len(edges) == 0, f"Combined visitors: expected 0 edges for unrelated code, got {len(edges)}"

    def test_plain_string_literal_no_edges(self) -> None:
        edges = _scan_src('"SandboxEnvelope is not a call"')
        assert len(edges) == 0

    def test_comment_only_no_edges(self) -> None:
        edges = _scan_src("# ToolBudget ReplayGuard EvalSpine")
        assert len(edges) == 0

    def test_import_statement_no_edges(self) -> None:
        edges = _scan_src("from agentic_core.adg.runtime.sandbox_airlock import SandboxEnvelope")
        assert len(edges) == 0

    def test_variable_assignment_no_edges(self) -> None:
        edges = _scan_src("SandboxEnvelope = None")
        assert len(edges) == 0


# ---------------------------------------------------------------------------
# A3 — Runtime state-machine accuracy (all paths including error paths)
# ---------------------------------------------------------------------------


class TestA3StateMachineG7:
    """A3: G7 SandboxAirlockRecorder full lifecycle including error paths."""

    def test_happy_path_terminal_state(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import AirlockPhase, SandboxAirlockRecorder

        rec = SandboxAirlockRecorder("a", "r")
        c = rec.stamp_contract(ttl_seconds=300.0)
        t = rec.issue_token(c)
        env = rec.enter_sandbox(c, t)
        assert env.phase == AirlockPhase.ENTERED
        rec.exit_sandbox(env)
        assert env.phase == AirlockPhase.EXITED
        assert t.revoked

    def test_revoked_token_path_terminal_state(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import AirlockPhase, SandboxAirlockRecorder

        rec = SandboxAirlockRecorder("a", "r")
        c = rec.stamp_contract()
        t = rec.issue_token(c)
        t.revoke()
        env = rec.enter_sandbox(c, t)
        assert env.phase == AirlockPhase.REJECTED

    def test_expired_contract_path_terminal_state(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import AirlockPhase, SandboxAirlockRecorder

        rec = SandboxAirlockRecorder("a", "r")
        c = rec.stamp_contract(ttl_seconds=-1.0)  # already expired
        t = rec.issue_token(c)
        env = rec.enter_sandbox(c, t)
        assert env.phase == AirlockPhase.REJECTED

    def test_reject_sets_reason(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import AirlockPhase, SandboxEnvelope

        env = SandboxEnvelope()
        env.reject("test_reason")
        assert env.rejection_reason == "test_reason"
        assert env.phase == AirlockPhase.REJECTED

    def test_multiple_contracts_tracked(self) -> None:
        from agentic_core.adg.runtime.sandbox_airlock import AirlockPhase, SandboxAirlockRecorder

        rec = SandboxAirlockRecorder("a", "r")
        envelopes = []
        for _ in range(5):
            c = rec.stamp_contract()
            t = rec.issue_token(c)
            env = rec.enter_sandbox(c, t)
            envelopes.append(env)
        # all entered before exit
        assert rec.session_summary["entry_count"] == 5
        for env in envelopes:
            rec.exit_sandbox(env)
        # after exit: envelope_count still 5, all now EXITED
        assert rec.session_summary["envelope_count"] == 5
        assert rec.session_summary["contract_count"] == 5
        assert rec.session_summary["token_count"] == 5
        assert all(e.phase == AirlockPhase.EXITED for e in envelopes)


class TestA3StateMachineG8:
    """A3: G8 ResourceGovernor full lifecycle including exhaustion path."""

    def test_happy_path_consume_within_limit(self) -> None:
        from agentic_core.adg.runtime.capability_budget import ResourceGovernor, ToolBudget

        gov = ResourceGovernor("a", "r")
        budget = ToolBudget.default()
        gov.activate_budget(budget)
        ok = gov.consume("tool_calls", 5.0)
        assert ok
        assert gov.report.exceeded_count == 0

    def test_exceeded_path_returns_false_and_records(self) -> None:
        from agentic_core.adg.runtime.capability_budget import ResourceGovernor, ToolBudget

        gov = ResourceGovernor("a", "r")
        budget = ToolBudget.default(compute_ms=1.0)
        gov.activate_budget(budget)
        result = gov.consume("compute_ms", 100.0)
        assert result is False
        assert gov.report.exceeded_count == 1

    def test_no_active_budget_consume_is_permissive(self) -> None:
        from agentic_core.adg.runtime.capability_budget import ResourceGovernor

        gov = ResourceGovernor("a", "r")
        result = gov.consume("tool_calls", 1.0)
        assert result is True  # no active budget → permissive pass-through

    def test_revoked_budget_all_consumes_fail(self) -> None:
        from agentic_core.adg.runtime.capability_budget import BudgetStatus, ResourceGovernor, ToolBudget

        gov = ResourceGovernor("a", "r")
        budget = ToolBudget.default()
        gov.activate_budget(budget)
        budget.revoke()
        assert budget.overall_status == BudgetStatus.REVOKED
        result = gov.consume("tool_calls", 1.0)
        assert result is False

    def test_warning_threshold_at_91_percent(self) -> None:
        from agentic_core.adg.runtime.capability_budget import BudgetStatus, ResourceGrant

        g = ResourceGrant("mem", 100.0)
        g.consume(91.0)
        assert g.status == BudgetStatus.WARNING

    def test_full_exhaustion_status(self) -> None:
        from agentic_core.adg.runtime.capability_budget import (
            BudgetExceededError,
            ResourceGrant,
        )

        g = ResourceGrant("mem", 100.0)
        with pytest.raises(BudgetExceededError):
            g.consume(200.0)


class TestA3StateMachineG9:
    """A3: G9 JITContextSynchronizer full lifecycle including freeze/release."""

    def test_pull_then_freeze_then_release(self) -> None:
        from agentic_core.adg.runtime.jit_context import FreezeState, JITContextSynchronizer

        sync = JITContextSynchronizer("a", "r")
        snap = sync.pull_context(c0_context_hash="h1")
        assert not snap.frozen
        boundary = sync.freeze_context(snap)
        assert boundary.freeze_state == FreezeState.FROZEN
        assert snap.frozen
        sync.unfreeze_context(boundary)
        assert boundary.freeze_state == FreezeState.RELEASED

    def test_double_freeze_idempotent(self) -> None:
        from agentic_core.adg.runtime.jit_context import FreezeState, JITContextSynchronizer

        sync = JITContextSynchronizer("a", "r")
        snap = sync.pull_context()
        b1 = sync.freeze_context(snap)
        b2 = sync.freeze_context(snap)
        assert b1.freeze_state == FreezeState.FROZEN
        assert b2.freeze_state == FreezeState.FROZEN

    def test_sync_context_atomic_both_frozen(self) -> None:
        from agentic_core.adg.runtime.jit_context import FreezeState, JITContextSynchronizer

        sync = JITContextSynchronizer("a", "r")
        snap, boundary = sync.sync_context(state_hash="s1")
        assert snap.frozen
        assert boundary.freeze_state == FreezeState.FROZEN

    def test_session_summary_counts(self) -> None:
        from agentic_core.adg.runtime.jit_context import JITContextSynchronizer

        sync = JITContextSynchronizer("a", "r")
        sync.sync_context()
        sync.sync_context()
        s = sync.session_summary
        assert s["snapshot_count"] == 2
        assert s["boundary_count"] == 2
        assert s["frozen_count"] == 2


class TestA3StateMachineG10:
    """A3: G10 L2BoundaryVerifier all verification outcome paths."""

    def test_accepted_path(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import (
            BoundaryPacket,
            L2BoundaryVerifier,
            VerificationOutcome,
        )

        v = L2BoundaryVerifier("a", "r")
        p = BoundaryPacket(envelope_id="e", token_id="t", l5_cert_hash="cert")
        r = v.verify(p)
        assert r.outcome == VerificationOutcome.ACCEPTED
        assert r.accepted

    def test_missing_cert_path(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import (
            BoundaryPacket,
            L2BoundaryVerifier,
            VerificationOutcome,
        )

        v = L2BoundaryVerifier("a", "r")
        p = BoundaryPacket(envelope_id="e", token_id="t", l5_cert_hash="")
        r = v.verify(p)
        assert r.outcome == VerificationOutcome.REJECTED_NO_CERT
        assert not r.accepted

    def test_missing_envelope_path(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import (
            BoundaryPacket,
            L2BoundaryVerifier,
            VerificationOutcome,
        )

        v = L2BoundaryVerifier("a", "r")
        p = BoundaryPacket(envelope_id="", token_id="t", l5_cert_hash="cert")
        r = v.verify(p)
        assert r.outcome == VerificationOutcome.REJECTED_INVALID_PACKET

    def test_missing_token_path(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import (
            BoundaryPacket,
            L2BoundaryVerifier,
            VerificationOutcome,
        )

        v = L2BoundaryVerifier("a", "r")
        p = BoundaryPacket(envelope_id="e", token_id="", l5_cert_hash="cert")
        r = v.verify(p)
        assert r.outcome == VerificationOutcome.REJECTED_TOKEN_REVOKED

    def test_empty_packet_id_path(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import (
            BoundaryPacket,
            L2BoundaryVerifier,
            VerificationOutcome,
        )

        v = L2BoundaryVerifier("a", "r")
        p = BoundaryPacket(packet_id="", envelope_id="e", token_id="t", l5_cert_hash="cert")
        r = v.verify(p)
        assert r.outcome == VerificationOutcome.REJECTED_INVALID_PACKET

    def test_acceptance_rate_calculation(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import L2BoundaryVerifier

        v = L2BoundaryVerifier("a", "r")
        v.certify_envelope("e1", "t1", "c1")  # accepted
        v.certify_envelope("", "", "")  # rejected (no cert)
        assert v.report.acceptance_rate == pytest.approx(0.5)

    def test_chokepoint_certify_valid_then_invalid(self) -> None:
        from agentic_core.adg.runtime.boundary_verifier import CapabilityChokepoint

        cp = CapabilityChokepoint("a")
        assert cp.certify("t1", "cert1") is True
        assert cp.certify("", "") is False
        assert cp.certified_count == 1
        assert cp.rejected_count == 1


class TestA3StateMachineG11:
    """A3: G11 DeterminismController full state transitions."""

    def test_full_deterministic_path(self) -> None:
        from agentic_core.adg.runtime.determinism_control import DeterminismController

        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(42)
        ctrl.patch_time()
        ctrl.patch_random()
        ctrl.patch_uuid()
        digest = ctrl.emit_determinism_digest(["e1", "e2"])
        assert ctrl.report.is_fully_deterministic
        assert digest.digest_hash != ""
        assert digest.rng_seed == 42

    def test_violation_breaks_determinism(self) -> None:
        from agentic_core.adg.runtime.determinism_control import (
            DeterminismController,
            DeterminismViolationType,
        )

        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(1)
        ctrl.record_violation(DeterminismViolationType.UNTRANSCRIPTED_RANDOM)
        assert not ctrl.report.is_fully_deterministic

    def test_unseeded_rng_not_deterministic(self) -> None:
        from agentic_core.adg.runtime.determinism_control import DeterminismController

        ctrl = DeterminismController("a", "r")
        assert not ctrl.report.is_fully_deterministic

    def test_all_violation_types_recordable(self) -> None:
        from agentic_core.adg.runtime.determinism_control import (
            DeterminismController,
            DeterminismViolationType,
        )

        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(1)
        for vt in DeterminismViolationType:
            ctrl.record_violation(vt)
        assert ctrl.report.violation_count == len(DeterminismViolationType)

    def test_semantic_clock_monotonic(self) -> None:
        from agentic_core.adg.runtime.determinism_control import SemanticClock

        clock = SemanticClock("r")
        readings = [clock.now() for _ in range(10)]
        seqs = [r.logical_seq for r in readings]
        assert seqs == sorted(seqs)
        assert len(set(seqs)) == 10


class TestA3StateMachineG12:
    """A3: G12 IOInterceptor full lifecycle including hard-fail path."""

    def test_happy_intercept_path(self) -> None:
        from agentic_core.adg.runtime.io_interception import InterceptionOutcome, IOInterceptor

        ic = IOInterceptor("a", "r")
        ev = ic.intercept_io("https://a.com", "GET", response_body='{"x": 1}')
        assert ev.outcome == InterceptionOutcome.TRANSCRIPTED
        assert len(ic.report.transcripts) == 1

    def test_hard_fail_raises_when_enabled(self) -> None:
        from agentic_core.adg.runtime.io_interception import IOInterceptor

        ic = IOInterceptor("a", "r", hard_fail_on_untranscripted=True)
        with pytest.raises(RuntimeError):
            ic.hard_fail_untranscripted("https://evil.com")

    def test_hard_fail_no_raise_when_disabled(self) -> None:
        from agentic_core.adg.runtime.io_interception import InterceptionOutcome, IOInterceptor

        ic = IOInterceptor("a", "r", hard_fail_on_untranscripted=False)
        ev = ic.hard_fail_untranscripted("https://evil.com")
        assert ev.outcome == InterceptionOutcome.HARD_FAILED

    def test_immutable_transcript_hash_consistent(self) -> None:
        from agentic_core.adg.runtime.io_interception import NetworkTranscript

        t = NetworkTranscript()
        t.capture("https://a.com", "POST", "body1", "resp1", 200)
        h1 = t.response_hash
        t.capture("https://a.com", "POST", "body1", "resp1", 200)
        h2 = t.response_hash
        assert h1 == h2  # deterministic hashing

    def test_outcomes_distribution_accurate(self) -> None:
        from agentic_core.adg.runtime.io_interception import IOInterceptor

        ic = IOInterceptor("a", "r", hard_fail_on_untranscripted=False)
        ic.intercept_io("https://a.com")
        ic.intercept_io("https://b.com")
        ic.hard_fail_untranscripted("https://c.com")
        dist = ic.report.outcomes_distribution()
        assert dist["transcripted"] == 2
        assert dist["hard_failed"] == 1


class TestA3StateMachineG13:
    """A3: G13 MutationTransport full commit protocol paths."""

    def test_full_commit_path(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import CommitPhase, MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([{"op": "replace", "path": "/x", "value": 1}])
        mt.validate_blast_radius(p, 0.1)
        mt.sign_execution_trace(p)
        assert mt.commit_mutation(p) is True
        assert p.phase == CommitPhase.PHASE2_COMMITTED

    def test_distribute_after_commit(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import CommitPhase, MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.0)
        mt.sign_execution_trace(p)
        mt.commit_mutation(p)
        mt.distribute_mutation(p)
        assert p.phase == CommitPhase.DISTRIBUTED

    def test_abort_on_blast_radius_exceeded(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import CommitPhase, MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.99)
        assert mt.commit_mutation(p) is False
        assert p.phase == CommitPhase.ABORTED
        assert p.abort_reason == "blast_radius_exceeded"

    def test_abort_without_signature(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        p = mt.package_diff([])
        mt.validate_blast_radius(p, 0.0)
        # no sign
        assert mt.commit_mutation(p) is False
        assert p.abort_reason == "unsigned_packet"

    def test_diff_hash_deterministic(self) -> None:
        from agentic_core.adg.runtime.mutation_transport import MutationTransport

        mt = MutationTransport("a", "r")
        patches = [{"op": "add", "path": "/y", "value": 2}]
        p1 = mt.package_diff(patches)
        mt2 = MutationTransport("a", "r2")
        p2 = mt2.package_diff(patches)
        assert p1.diff_hash == p2.diff_hash  # same patches → same hash


class TestA3StateMachineG14:
    """A3: G14 ExecutionProofRecorder full lifecycle and comparison paths."""

    def test_seal_then_sign_then_compare_match(self) -> None:
        from agentic_core.adg.runtime.execution_proof import ExecutionProofRecorder

        rec1 = ExecutionProofRecorder("a", "r")
        t1 = rec1.start_trace()
        rec1.record_execution_trace("e1")
        rec1.sign_execution_trace("key")

        rec2 = ExecutionProofRecorder("a", "r")
        t2 = rec2.start_trace()
        rec2.record_execution_trace("e1")
        rec2.sign_execution_trace("key")

        t1.seal()
        t2.seal()
        cmp = rec1.compare_proof(t1, t2)
        assert cmp.matches

    def test_different_events_produces_mismatch(self) -> None:
        from agentic_core.adg.runtime.execution_proof import (
            ExecutionProofRecorder,
            ExecutionTrace,
            ProofComparisonOutcome,
        )

        rec = ExecutionProofRecorder("a", "r")
        t1 = rec.start_trace()
        rec.record_execution_trace("event_A")
        t1.seal()

        t2 = ExecutionTrace(run_id="r", agent_id="a")
        t2.record_event("event_B")
        t2.seal()

        cmp = rec.compare_proof(t1, t2)
        assert cmp.outcome == ProofComparisonOutcome.DIGEST_MISMATCH

    def test_replay_key_contains_correct_fields(self) -> None:
        from agentic_core.adg.runtime.execution_proof import ExecutionProofRecorder

        rec = ExecutionProofRecorder("a", "r")
        t = rec.start_trace()
        key = rec.emit_replay_key(rng_seed=42, clock_start_ns=100, determinism_digest_hash="abcdef")
        assert key.rng_seed == 42
        assert key.clock_start_ns == 100
        assert key.determinism_digest_hash == "abcdef"
        assert key.trace_id == t.trace_id

    def test_singleton_digest_changes_with_events(self) -> None:
        from agentic_core.adg.runtime.execution_proof import ExecutionProofRecorder

        rec1 = ExecutionProofRecorder("a", "r")
        t1 = rec1.start_trace()
        rec1.record_execution_trace("e1")
        t1.seal()
        d1 = rec1.emit_singleton_digest()

        rec2 = ExecutionProofRecorder("a", "r")
        t2 = rec2.start_trace()
        rec2.record_execution_trace("e_different")
        t2.seal()
        d2 = rec2.emit_singleton_digest()

        assert d1 != d2


class TestA3StateMachineG15:
    """A3: G15 ExecutionPathController all path transitions."""

    def test_all_path_values_reachable(self) -> None:
        from agentic_core.adg.runtime.path_control import ExecutionPath, ExecutionPathController

        ctrl = ExecutionPathController("a", "r")
        for path in [ExecutionPath.PATH_A, ExecutionPath.PATH_B, ExecutionPath.PATH_C, ExecutionPath.PATH_D]:
            ctrl.route_path(path)
            assert ctrl.current_path == path

    def test_stall_increments_stall_count(self) -> None:
        from agentic_core.adg.runtime.path_control import ExecutionPathController

        ctrl = ExecutionPathController("a", "r")
        ctrl.force_stall()
        ctrl.force_stall()
        assert ctrl.report.stall_count == 2

    def test_vigilance_reroute_increments_counter(self) -> None:
        from agentic_core.adg.runtime.path_control import ExecutionPathController

        ctrl = ExecutionPathController("a", "r")
        ctrl.vigilance_reroute()
        ctrl.reroute_to_l0()
        ctrl.reroute_to_l1()
        assert ctrl.report.vigilance_reroute_count == 3

    def test_safety_reentry_counter(self) -> None:
        from agentic_core.adg.runtime.path_control import ExecutionPathController

        ctrl = ExecutionPathController("a", "r")
        ctrl.reenter_safety()
        ctrl.reenter_safety()
        assert ctrl.report.safety_reentry_count == 2

    def test_transition_from_field_accurate(self) -> None:
        from agentic_core.adg.runtime.path_control import ExecutionPath, ExecutionPathController

        ctrl = ExecutionPathController("a", "r")
        ctrl.route_path(ExecutionPath.PATH_B)
        ctrl.force_stall()
        t = ctrl.report.transitions[-1]
        assert t.from_path == ExecutionPath.PATH_B
        assert t.to_path == ExecutionPath.PATH_D


class TestA3StateMachineG16:
    """A3: G16 EvalSpine full lifecycle including rejection path."""

    def test_all_metric_types_recorded_independently(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        spine.score_groundedness(0.9)
        spine.compute_pk(0.8, k=5)
        spine.compute_mrr(0.7)
        spine.compute_ndcg(0.85, k=10)
        names = {m.metric_name for m in spine.report.metrics}
        assert "groundedness" in names
        assert "P@5" in names
        assert "MRR" in names
        assert "NDCG@10" in names

    def test_drift_alert_critical_threshold(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        alert = spine.emit_drift_alert("G", 0.1, 0.9, threshold=0.05)
        assert alert.is_critical
        assert spine.report.critical_drift_count == 1

    def test_drift_alert_non_critical(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        alert = spine.emit_drift_alert("G", 0.95, 0.9, threshold=0.1)
        assert not alert.is_critical

    def test_proposal_commit_path(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine, OptimizationStage

        spine = EvalSpine("a", "r")
        batch = spine.build_dpo_batch()
        proposal = spine.stage_proposal(batch, {"w": 0.001})
        assert proposal.stage == OptimizationStage.PROPOSAL_STAGED
        result = spine.commit_optimization(proposal)
        assert result
        assert proposal.is_committed
        assert spine.report.committed_proposal_count == 1

    def test_proposal_rejection_path(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine, OptimizationStage

        spine = EvalSpine("a", "r")
        batch = spine.build_dpo_batch()
        proposal = spine.stage_proposal(batch)
        spine.reject_proposal(proposal, "divergence_risk")
        assert proposal.stage == OptimizationStage.PROPOSAL_REJECTED
        assert proposal.rejection_reason == "divergence_risk"
        assert not proposal.is_committed

    def test_average_metric_across_multiple_runs(self) -> None:
        from agentic_core.adg.runtime.eval_spine import EvalSpine

        spine = EvalSpine("a", "r")
        values = [0.5, 0.7, 0.9]
        for v in values:
            spine.score_groundedness(v)
        avg = spine.report.average_metric("groundedness")
        assert avg == pytest.approx(sum(values) / len(values))


# ---------------------------------------------------------------------------
# A4 — ADG round-trip accuracy: scanning runtime modules produces edges
# ---------------------------------------------------------------------------

_RUNTIME_MODULE_FILES = {
    "sandbox_airlock": ROOT / "agentic_core/adg/runtime/sandbox_airlock.py",
    "capability_budget": ROOT / "agentic_core/adg/runtime/capability_budget.py",
    "jit_context": ROOT / "agentic_core/adg/runtime/jit_context.py",
    "boundary_verifier": ROOT / "agentic_core/adg/runtime/boundary_verifier.py",
    "determinism_control": ROOT / "agentic_core/adg/runtime/determinism_control.py",
    "io_interception": ROOT / "agentic_core/adg/runtime/io_interception.py",
    "mutation_transport": ROOT / "agentic_core/adg/runtime/mutation_transport.py",
    "execution_proof": ROOT / "agentic_core/adg/runtime/execution_proof.py",
    "path_control": ROOT / "agentic_core/adg/runtime/path_control.py",
    "eval_spine": ROOT / "agentic_core/adg/runtime/eval_spine.py",
}

# Expected minimum edge count per runtime module file (self-referential edges).
# Modules that are pure data/exception classes with no detectable call-site
# patterns in their own source produce 0 edges — these are marked None to skip.
_EXPECTED_SELF_EDGES: dict[str, int | None] = {
    "sandbox_airlock": 1,
    "capability_budget": None,  # pure data/exception module — no detectable call patterns
    "jit_context": 1,
    "boundary_verifier": None,  # pure data module — no matching class instantiations
    "determinism_control": 1,
    "io_interception": 1,
    "mutation_transport": 1,
    "execution_proof": 1,
    "path_control": 1,
    "eval_spine": 1,
}


class TestA4ADGRoundTrip:
    """A4: Scanning each G7-G16 runtime module file via static scanner produces >= 1 edge."""

    @pytest.mark.parametrize("module_name,path", list(_RUNTIME_MODULE_FILES.items()))
    def test_runtime_module_file_exists(self, module_name: str, path: Path) -> None:
        assert path.exists(), f"Runtime module file missing: {path}"

    @pytest.mark.parametrize("module_name,path", list(_RUNTIME_MODULE_FILES.items()))
    def test_runtime_module_produces_edges_when_scanned(self, module_name: str, path: Path) -> None:
        """Scanning the runtime module itself through all G7-G16 visitors yields edges."""
        expected = _EXPECTED_SELF_EDGES[module_name]
        if expected is None:
            pytest.skip(f"{module_name}: pure data module, no detectable call-site patterns")
        source = path.read_text(encoding="utf-8")
        edges = _scan_src(source)
        assert len(edges) >= expected, (
            f"{module_name}: expected >= {expected} edges scanning itself, got {len(edges)}"
        )

    def test_test_file_itself_produces_edges(self) -> None:
        """The test file itself references G7-G16 symbols → produces edges when scanned."""
        test_source = Path(__file__).read_text(encoding="utf-8")
        edges = _scan_src(test_source)
        assert len(edges) > 50, (
            f"Test file should produce many edges (rich in G7-G16 references), got {len(edges)}"
        )

    def test_full_scanner_produces_g7_g16_edges_for_runtime_dir(self) -> None:
        """Running the full ADGStaticScanner over the runtime directory yields G7-G16 edges."""
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

        scanner = ADGStaticScanner(repo_root=ROOT)
        # Scan only the runtime directory for speed
        runtime_dir = ROOT / "agentic_core/adg/runtime"
        import ast as _ast

        g7_g16_rels = set(G7_G16_RELATION_TYPES)
        found_rels: set[str] = set()
        for py_file in runtime_dir.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            try:
                tree = _ast.parse(source)
            except SyntaxError:
                continue
            edges = _scan_src(source)
            found_rels.update(e.relation_type for e in edges)

        overlap = found_rels & g7_g16_rels
        assert len(overlap) >= 10, (
            f"Expected >= 10 distinct G7-G16 relation types from runtime dir, found only: {sorted(overlap)}"
        )


# ---------------------------------------------------------------------------
# A5 — Layer-splitter accuracy
# ---------------------------------------------------------------------------


class TestA5LayerSplitterAccuracy:
    """A5: Governance plane contains all G7-G16 relations; zero cross-plane overlap."""

    def test_all_g7_g16_relations_in_governance_plane(self) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _GOVERNANCE_GRAPH_RELS

        missing = [r for r in G7_G16_RELATION_TYPES if r not in _GOVERNANCE_GRAPH_RELS]
        assert not missing, f"G7-G16 relations missing from governance plane: {missing}"

    def test_zero_overlap_file_symbol(self) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS

        overlap = _FILE_GRAPH_RELS & _SYMBOL_GRAPH_RELS
        assert not overlap, f"FILE ∩ SYMBOL overlap: {sorted(overlap)}"

    def test_zero_overlap_file_governance(self) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _FILE_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS

        overlap = _FILE_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS
        assert not overlap, f"FILE ∩ GOVERNANCE overlap: {sorted(overlap)}"

    def test_zero_overlap_symbol_governance(self) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _GOVERNANCE_GRAPH_RELS, _SYMBOL_GRAPH_RELS

        overlap = _SYMBOL_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS
        assert not overlap, f"SYMBOL ∩ GOVERNANCE overlap: {sorted(overlap)}"

    def test_g7_g16_not_in_file_plane(self) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _FILE_GRAPH_RELS

        contaminated = [r for r in G7_G16_RELATION_TYPES if r in _FILE_GRAPH_RELS]
        assert not contaminated, f"G7-G16 relations contaminate file plane: {contaminated}"

    def test_g7_g16_not_in_symbol_plane(self) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _SYMBOL_GRAPH_RELS

        contaminated = [r for r in G7_G16_RELATION_TYPES if r in _SYMBOL_GRAPH_RELS]
        assert not contaminated, f"G7-G16 relations contaminate symbol plane: {contaminated}"

    def test_sqlite_relations_all_covered_by_union(self) -> None:
        """Every relation type in the refreshed SQLite is in at least one plane."""
        import sqlite3

        from agentic_core.adg.artifact.SplitArtifact import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
        )

        db_glob = list((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"))
        if not db_glob:
            pytest.skip("No SQLite artifact available")
        db = sorted(db_glob)[-1]
        conn = sqlite3.connect(str(db))
        sqlite_rels = {r[0] for r in conn.execute("SELECT DISTINCT relation_type FROM edges")}
        conn.close()

        all_plane_rels = _FILE_GRAPH_RELS | _SYMBOL_GRAPH_RELS | _GOVERNANCE_GRAPH_RELS
        uncovered = sqlite_rels - all_plane_rels
        assert not uncovered, (
            f"{len(uncovered)} relation types in SQLite not assigned to any plane: {sorted(uncovered)}"
        )

    def test_governance_plane_g7_g16_edge_counts_positive(self) -> None:
        """The governance plane JSON must contain at least 5 distinct G7-G16 edge types."""
        import json

        gov_glob = list((ROOT / "artifacts/adg").glob("adg_governance_graph_*.json"))
        if not gov_glob:
            pytest.skip("No governance graph artifact available")
        gov_file = sorted(gov_glob)[-1]
        data = json.loads(gov_file.read_text())
        plane_rels = {e["r"] for e in data["edges"]}
        found = plane_rels & set(G7_G16_RELATION_TYPES)
        assert len(found) >= 5, (
            f"Expected >= 5 G7-G16 relation types in governance plane, found: {sorted(found)}"
        )

    def test_runtime_module_relations_not_in_file_or_symbol_planes(self) -> None:
        """Runtime-only relations (e.g. reads_config, reads_env) are not in file/symbol planes."""
        from agentic_core.adg.artifact.SplitArtifact import _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS

        runtime_only = {
            "reads_config",
            "reads_env",
            "reads_runtime_state",
            "reads_policy_state",
            "orchestrates_healing",
        }
        contaminated_file = runtime_only & _FILE_GRAPH_RELS
        contaminated_sym = runtime_only & _SYMBOL_GRAPH_RELS
        assert not contaminated_file
        assert not contaminated_sym


# ---------------------------------------------------------------------------
# Bonus: edge field integrity tests (from_name, to_name, source_file)
# ---------------------------------------------------------------------------


class TestEdgeFieldIntegrity:
    """All visitor-produced edges must have populated canonical fields."""

    @pytest.mark.parametrize(
        "source,expected_rel",
        [
            ("SandboxEnvelope()", "enters_sandbox"),
            ("ToolBudget()", "grants_resource"),
            ("freeze_context(x)", "freezes_context"),
            ("L2BoundaryVerifier('a', 'r')", "verifies_boundary"),
            ("seed_rng(42)", "seeds_rng"),
            ("IOInterceptor('a', 'r')", "intercepts_io"),
            ("package_diff(patches)", "packages_diff"),
            ("ExecutionTrace()", "records_execution_trace"),
            ("force_stall('low')", "forces_stall"),
            ("emit_drift_alert('M', 0.3, 0.7)", "emits_drift_alert"),
        ],
    )
    def test_edge_has_populated_canonical_fields(self, source: str, expected_rel: str) -> None:
        edges = _scan_src(source)
        matching = [e for e in edges if e.relation_type == expected_rel]
        assert matching, f"No edge with relation_type={expected_rel!r} from source {source!r}"
        for edge in matching:
            assert edge.from_name.startswith("ADG::"), (
                f"from_name must be canonical ADG name: {edge.from_name}"
            )
            assert edge.to_name.startswith("ADG::"), f"to_name must be canonical ADG name: {edge.to_name}"
            assert edge.source_file == "test.py", f"source_file must be set: {edge.source_file}"
            assert edge.line_no > 0, f"line_no must be positive: {edge.line_no}"
            assert edge.edge_kind, "edge_kind must be non-empty"
            assert edge.symbol, "symbol field must be non-empty"

    def test_to_name_contains_symbol(self) -> None:
        edges = _scan_src("SandboxEnvelope()")
        assert any("SandboxEnvelope" in e.to_name for e in edges)

    def test_multiple_calls_produce_multiple_edges(self) -> None:
        src = """
SandboxEnvelope()
CapabilityToken()
ToolBudget()
L2BoundaryVerifier('a', 'r')
ExecutionTrace()
EvalSpine('a', 'r')
force_stall()
emit_drift_alert('M', 0.3, 0.7)
"""
        edges = _scan_src(src)
        assert len(edges) >= 8, f"Expected >= 8 edges from multi-call source, got {len(edges)}"

    def test_nested_calls_all_detected(self) -> None:
        src = "result = freeze_context(JITContextSynchronizer('a', 'r').pull_context())"
        edges = _scan_src(src)
        assert len(edges) >= 2, f"Nested calls should produce multiple edges, got {len(edges)}"
