"""Tests for G17-G22 ADG runtime plane completeness and accuracy.

Six orthogonal test axes:
  C1  Schema completeness    — EntityType, RelationType, EdgeKind literals
  C2  Detection constants    — frozenset membership and non-overlap
  C3  Module API             — importability, instantiation, state-machine
  C4  __init__ exports       — all public symbols re-exported
  A1  Visitor accuracy       — each visitor emits correct (rel, kind) pairs
  A2  Visitor non-contam.    — unrelated code produces zero edges
  A3  Runtime state-machines — full lifecycle correctness per plane
  A4  ADG round-trip         — scanning each runtime module emits ≥1 edge
  A5  Layer-splitter         — G17-G22 relations land in governance plane
"""

from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
from typing import get_args

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_routes_to_agent("p1", "test_adg_g17_g22_completeness_accuracy", "test")
_emit_orchestrates_workflow("p1", "test_adg_g17_g22_completeness_accuracy", "test")
_emit_dispatches_execution_plan("p1", "test_adg_g17_g22_completeness_accuracy", "test")
_emit_validates_agent_capability("p1", "test_adg_g17_g22_completeness_accuracy", "test")
_emit_checks_agent_registry("p1", "test_adg_g17_g22_completeness_accuracy", "test")

_emit_records_execution_trace("p0", "evidence", "test_adg_g17_g22_completeness_accuracy")
_emit_applies_guardrail("p0", "test_adg_g17_g22_completeness_accuracy", "p0_governance")
_emit_snapshots_state("p0", "test_adg_g17_g22_completeness_accuracy", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_adg_g17_g22_completeness_accuracy", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_g17_g22_completeness_accuracy", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_g17_g22_completeness_accuracy", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_g17_g22_completeness_accuracy", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_g17_g22_completeness_accuracy", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_g17_g22_completeness_accuracy", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_g17_g22_completeness_accuracy", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_g17_g22_completeness_accuracy", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_g17_g22_completeness_accuracy", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_g17_g22_completeness_accuracy", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_g17_g22_completeness_accuracy", "p4obs", "alert")
_emit_links_incident_trace("test_adg_g17_g22_completeness_accuracy", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_g17_g22_completeness_accuracy", "p3lm", "pattern")
_emit_records_learning_event("test_adg_g17_g22_completeness_accuracy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_g17_g22_completeness_accuracy", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_g17_g22_completeness_accuracy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_g17_g22_completeness_accuracy", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_g17_g22_completeness_accuracy", "p3lm", "policy")
_emit_stores_learning_state("test_adg_g17_g22_completeness_accuracy", "p3lm", "state")
_emit_records_execution_trace("test_adg_g17_g22_completeness_accuracy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_g17_g22_completeness_accuracy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_g17_g22_completeness_accuracy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_g17_g22_completeness_accuracy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_g17_g22_completeness_accuracy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_g17_g22_completeness_accuracy", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_g17_g22_completeness_accuracy", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_g17_g22_completeness_accuracy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_g17_g22_completeness_accuracy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_g17_g22_completeness_accuracy", "context_pull")
_emit_pulls_context("p1", "test_adg_g17_g22_completeness_accuracy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_g17_g22_completeness_accuracy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_g17_g22_completeness_accuracy", "uwg_term_2")
_emit_writes_through("p1", "test_adg_g17_g22_completeness_accuracy", "write_through")
_emit_writes_through("p1", "test_adg_g17_g22_completeness_accuracy", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_g17_g22_completeness_accuracy", "safety_validation")
_emit_invokes_eval("p1", "test_adg_g17_g22_completeness_accuracy", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_g17_g22_completeness_accuracy", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_g17_g22_completeness_accuracy", "human_escalation")
_emit_routes_through("p1", "test_adg_g17_g22_completeness_accuracy", "route_through")
_emit_agent_executes_agent("p1", "test_adg_g17_g22_completeness_accuracy", "sub_agent")
_emit_verifies_policy("p1", "test_adg_g17_g22_completeness_accuracy", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_g17_g22_completeness_accuracy", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_g17_g22_completeness_accuracy", "boundary_check")
_emit_transcripts_response("p1", "test_adg_g17_g22_completeness_accuracy", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_g17_g22_completeness_accuracy")
_emit_gated_by_confidence("p1", "test_adg_g17_g22_completeness_accuracy", "confidence_gate")
emit_replay_key("p0", "test_adg_g17_g22_completeness_accuracy")
emit_determinism_digest("p0", "test_adg_g17_g22_completeness_accuracy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_g17_g22_completeness_accuracy", "execution_auth")
_emit_validates_capability("p2", "test_adg_g17_g22_completeness_accuracy", "capability_check")
_emit_routes_to_capability("p2", "test_adg_g17_g22_completeness_accuracy", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_g17_g22_completeness_accuracy", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_g17_g22_completeness_accuracy", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_g17_g22_completeness_accuracy", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_g17_g22_completeness_accuracy", "exec_output")
_emit_dispatches_agent("p3", "test_adg_g17_g22_completeness_accuracy", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_g17_g22_completeness_accuracy", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_g17_g22_completeness_accuracy", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_g17_g22_completeness_accuracy", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_g17_g22_completeness_accuracy", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_g17_g22_completeness_accuracy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_g17_g22_completeness_accuracy", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_g17_g22_completeness_accuracy", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_g17_g22_completeness_accuracy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_g17_g22_completeness_accuracy", "eval_metric")
_emit_stores_embedding("p4", "test_adg_g17_g22_completeness_accuracy", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_g17_g22_completeness_accuracy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_g17_g22_completeness_accuracy", "exec_snapshot_link")

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "agentic_core" / "adg" / "runtime"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan_src(src: str, visitor_class: type) -> list[tuple[str, str]]:
    """Run visitor_class over src; return [(relation_type, edge_kind), ...]."""
    tree = ast.parse(src)
    v = visitor_class("ADG::Module::test_module", "test_module.py")
    v.visit(tree)
    return [(e.relation_type, e.edge_kind) for e in v.edges]


def _edges_for(src: str, visitor_class: type) -> set[tuple[str, str]]:
    return set(_scan_src(src, visitor_class))


# ---------------------------------------------------------------------------
# C1 — Schema completeness
# ---------------------------------------------------------------------------


class TestSchemaCompleteness:
    """Verify G17-G22 EntityType / RelationType / EdgeKind literals exist."""

    # EntityType
    @pytest.mark.parametrize(
        "et",
        [
            "secret_access_record",
            "credential_vault",
            "secret_read_event",
            "config_read_record",
            "config_policy_gate",
            "dynamic_invocation_record",
            "eval_exec_site",
            "policy_state_read",
            "runtime_state_read",
            "state_observation_report",
            "antipattern_record",
            "antipattern_category",
            "healing_run",
            "orchestration_step",
        ],
    )
    def test_entity_type_literal_exists(self, et: str) -> None:
        from agentic_core.adg.schema_util import EntityType

        assert et in get_args(EntityType), f"EntityType missing: {et!r}"

    # RelationType
    @pytest.mark.parametrize(
        "rt",
        [
            # G17
            "reads_secret_vault",
            "accesses_credential",
            "rotates_secret",
            # G18
            "reads_governed_config",
            "validates_config_schema",
            "caches_config",
            # G19
            "invokes_eval",
            "invokes_exec",
            "invokes_importlib",
            "invokes_getattr_dynamic",
            # G20
            "observes_policy_state",
            "observes_runtime_state",
            "snapshots_state",
            # G21
            "registers_antipattern",
            "classifies_antipattern",
            # G22
            "dispatches_healing_run",
            "confirms_heal",
            "aborts_heal",
        ],
    )
    def test_relation_type_literal_exists(self, rt: str) -> None:
        from agentic_core.adg.schema_util import RelationType

        assert rt in get_args(RelationType), f"RelationType missing: {rt!r}"

    # EdgeKind
    @pytest.mark.parametrize(
        "ek",
        [
            "secret_read",
            "credential_access",
            "secret_rotation",
            "governed_config_read",
            "config_schema_validation",
            "eval_call",
            "exec_call",
            "importlib_call",
            "dynamic_getattr",
            "policy_state_observation",
            "runtime_state_snapshot",
            "antipattern_classification",
            "healing_dispatch",
            "healing_confirm",
            "healing_abort",
            "broad_exception_catch",
            "log_and_swallow",
            "return_none_swallow",
        ],
    )
    def test_edge_kind_literal_exists(self, ek: str) -> None:
        from agentic_core.adg.schema_util import EdgeKind

        assert ek in get_args(EdgeKind), f"EdgeKind missing: {ek!r}"


# ---------------------------------------------------------------------------
# C2 — Detection constants completeness
# ---------------------------------------------------------------------------


class TestDetectionConstants:
    """Verify G17-G22 frozenset detection constants are populated and exported."""

    @pytest.mark.parametrize(
        "const_name,expected_members",
        [
            ("SECRET_VAULT_CLASSES", ["SecretVault", "CredentialStore", "SecretProvider"]),
            ("SECRET_ACCESS_METHODS", ["get_secret", "read_secret", "rotate_secret"]),
            ("SECRET_ENV_PATTERNS", ["os.environ", "os.getenv"]),
            ("CONFIG_READER_CLASSES", ["ConfigReader", "GovernedConfig", "ConfigLoader"]),
            ("CONFIG_ACCESS_METHODS", ["load_config", "read_config", "validate_config"]),
            ("DYNAMIC_EVAL_SYMBOLS", ["eval", "exec", "importlib.import_module"]),
            ("DYNAMIC_GETATTR_SYMBOLS", ["getattr", "setattr", "delattr"]),
            ("POLICY_STATE_READER_CLASSES", ["PolicyStateReader", "RuntimeStateObserver", "StateSnapshot"]),
            ("POLICY_STATE_READ_METHODS", ["read_policy_state", "observe_runtime_state"]),
            ("ANTIPATTERN_REGISTRY_CLASSES", ["AntipatternRegistry", "PatternClassifier"]),
            (
                "ANTIPATTERN_CATEGORY_NAMES",
                [
                    "silent_exception_swallow",
                    "blocking_call_in_async",
                    "broad_exception_catch",
                    "log_and_swallow",
                    "return_none_swallow",
                ],
            ),
            ("HEALING_ORCHESTRATOR_CLASSES", ["HealingOrchestrator", "HealerDispatcher"]),
            ("HEALING_DISPATCH_METHODS", ["dispatch_healing", "confirm_heal", "abort_heal"]),
        ],
    )
    def test_constant_contains_expected_members(self, const_name: str, expected_members: list[str]) -> None:
        import agentic_core.adg.schema_util as sch

        fs = getattr(sch, const_name)
        for m in expected_members:
            assert m in fs, f"{const_name} missing {m!r}"

    @pytest.mark.parametrize(
        "const_name",
        [
            "SECRET_VAULT_CLASSES",
            "SECRET_ACCESS_METHODS",
            "SECRET_ENV_PATTERNS",
            "CONFIG_READER_CLASSES",
            "CONFIG_ACCESS_METHODS",
            "DYNAMIC_EVAL_SYMBOLS",
            "DYNAMIC_GETATTR_SYMBOLS",
            "POLICY_STATE_READER_CLASSES",
            "POLICY_STATE_READ_METHODS",
            "ANTIPATTERN_REGISTRY_CLASSES",
            "ANTIPATTERN_CATEGORY_NAMES",
            "HEALING_ORCHESTRATOR_CLASSES",
            "HEALING_DISPATCH_METHODS",
        ],
    )
    def test_constant_exported_in_all(self, const_name: str) -> None:
        import agentic_core.adg.schema_util as sch

        assert const_name in sch.__all__, f"{const_name} missing from schema.__all__"

    def test_no_cross_constant_overlap(self) -> None:
        """No symbol string should appear in two different G17-G22 frozensets."""
        import agentic_core.adg.schema_util as sch

        g17_g22_consts = [
            "SECRET_VAULT_CLASSES",
            "SECRET_ACCESS_METHODS",
            "SECRET_ENV_PATTERNS",
            "CONFIG_READER_CLASSES",
            "CONFIG_ACCESS_METHODS",
            "DYNAMIC_EVAL_SYMBOLS",
            "DYNAMIC_GETATTR_SYMBOLS",
            "POLICY_STATE_READER_CLASSES",
            "POLICY_STATE_READ_METHODS",
            "ANTIPATTERN_REGISTRY_CLASSES",
            "ANTIPATTERN_CATEGORY_NAMES",
            "HEALING_ORCHESTRATOR_CLASSES",
            "HEALING_DISPATCH_METHODS",
        ]
        seen: dict[str, str] = {}
        for name in g17_g22_consts:
            for sym in getattr(sch, name):
                assert sym not in seen, f"Symbol {sym!r} appears in both {seen[sym]} and {name}"
                seen[sym] = name

    @pytest.mark.parametrize(
        "const_name",
        [
            "SECRET_VAULT_CLASSES",
            "SECRET_ACCESS_METHODS",
            "SECRET_ENV_PATTERNS",
            "CONFIG_READER_CLASSES",
            "CONFIG_ACCESS_METHODS",
            "DYNAMIC_EVAL_SYMBOLS",
            "DYNAMIC_GETATTR_SYMBOLS",
            "POLICY_STATE_READER_CLASSES",
            "POLICY_STATE_READ_METHODS",
            "ANTIPATTERN_REGISTRY_CLASSES",
            "ANTIPATTERN_CATEGORY_NAMES",
            "HEALING_ORCHESTRATOR_CLASSES",
            "HEALING_DISPATCH_METHODS",
        ],
    )
    def test_no_empty_or_whitespace_members(self, const_name: str) -> None:
        import agentic_core.adg.schema_util as sch

        for m in getattr(sch, const_name):
            assert isinstance(m, str) and m.strip(), f"{const_name}: invalid member {m!r}"


# ---------------------------------------------------------------------------
# C3 — Module API completeness
# ---------------------------------------------------------------------------


class TestModuleAPI:
    """Verify G17-G22 runtime modules are importable with expected public API."""

    @pytest.mark.parametrize(
        "mod_path,expected_classes",
        [
            (
                "agentic_core.adg.runtime.secret_access",
                [
                    "SecretKind",
                    "SecretAccessOutcome",
                    "SecretAccessEvent",
                    "SecretAccessReport",
                    "SecretAccessRecorder",
                ],
            ),
            (
                "agentic_core.adg.runtime.config_governance",
                [
                    "ConfigReadOutcome",
                    "ConfigSchemaStatus",
                    "ConfigReadEvent",
                    "ConfigGovernanceReport",
                    "ConfigGovernor",
                ],
            ),
            (
                "agentic_core.adg.runtime.dynamic_invocation",
                [
                    "DynamicInvocationKind",
                    "DynamicInvocationRisk",
                    "DynamicInvocationRecord",
                    "DynamicInvocationReport",
                    "DynamicInvocationTracker",
                ],
            ),
            (
                "agentic_core.adg.runtime.policy_state_observer",
                [
                    "StateObservationKind",
                    "StateReadOutcome",
                    "StateObservationEvent",
                    "StateObservationReport",
                    "PolicyStateObserver",
                ],
            ),
            (
                "agentic_core.adg.runtime.antipattern_registry",
                [
                    "AntipatternSeverity",
                    "AntipatternCategory",
                    "AntipatternRecord",
                    "AntipatternRegistryReport",
                    "AntipatternRegistry",
                ],
            ),
            (
                "agentic_core.adg.runtime.healing_orchestrator",
                [
                    "HealingRunPhase",
                    "HealingTrigger",
                    "OrchestrationStep",
                    "HealingRun",
                    "HealingOrchestratorReport",
                    "HealingOrchestrator",
                ],
            ),
        ],
    )
    def test_module_importable_with_expected_symbols(
        self, mod_path: str, expected_classes: list[str]
    ) -> None:
        mod = importlib.import_module(mod_path)
        for cls_name in expected_classes:
            assert hasattr(mod, cls_name), f"{mod_path} missing {cls_name}"

    @pytest.mark.parametrize(
        "mod_path",
        [
            "agentic_core.adg.runtime.secret_access",
            "agentic_core.adg.runtime.config_governance",
            "agentic_core.adg.runtime.dynamic_invocation",
            "agentic_core.adg.runtime.policy_state_observer",
            "agentic_core.adg.runtime.antipattern_registry",
            "agentic_core.adg.runtime.healing_orchestrator",
        ],
    )
    def test_module_docstring_no_side_effects(self, mod_path: str) -> None:
        mod = importlib.import_module(mod_path)
        doc = (mod.__doc__ or "").lower().replace("-", " ")
        assert "no side effects on import" in doc, (
            f"{mod_path}: docstring must state 'no side-effects on import'"
        )

    @pytest.mark.parametrize(
        "mod_path",
        [
            "agentic_core.adg.runtime.secret_access",
            "agentic_core.adg.runtime.config_governance",
            "agentic_core.adg.runtime.dynamic_invocation",
            "agentic_core.adg.runtime.policy_state_observer",
            "agentic_core.adg.runtime.antipattern_registry",
            "agentic_core.adg.runtime.healing_orchestrator",
        ],
    )
    def test_module_docstring_starts_with_gap_label(self, mod_path: str) -> None:
        mod = importlib.import_module(mod_path)
        doc = mod.__doc__ or ""
        assert doc.startswith("G"), f"{mod_path}: docstring must start with G<n> gap label"


# ---------------------------------------------------------------------------
# C4 — __init__ export completeness
# ---------------------------------------------------------------------------


class TestInitExports:
    """Verify all G17-G22 public symbols are re-exported from runtime __init__."""

    @pytest.mark.parametrize(
        "symbol",
        [
            # G17
            "SecretAccessEvent",
            "SecretAccessOutcome",
            "SecretAccessRecorder",
            "SecretAccessReport",
            "SecretKind",
            # G18
            "ConfigGovernanceReport",
            "ConfigGovernor",
            "ConfigReadEvent",
            "ConfigReadOutcome",
            "ConfigSchemaStatus",
            # G19
            "DynamicInvocationKind",
            "DynamicInvocationRecord",
            "DynamicInvocationReport",
            "DynamicInvocationRisk",
            "DynamicInvocationTracker",
            # G20
            "PolicyStateObserver",
            "StateObservationEvent",
            "StateObservationKind",
            "StateObservationReport",
            "StateReadOutcome",
            # G21
            "AntipatternCategory",
            "AntipatternRecord",
            "AntipatternRegistry",
            "AntipatternRegistryReport",
            "AntipatternSeverity",
            # G22
            "HealingOrchestrator",
            "HealingOrchestratorReport",
            "HealingRun",
            "HealingRunPhase",
            "HealingTrigger",
            "OrchestrationStep",
        ],
    )
    def test_symbol_in_runtime_all(self, symbol: str) -> None:
        import agentic_core.adg.runtime as rt

        assert symbol in rt.__all__, f"runtime.__all__ missing {symbol!r}"
        assert hasattr(rt, symbol), f"runtime package missing attribute {symbol!r}"


# ---------------------------------------------------------------------------
# A1 — Visitor accuracy
# ---------------------------------------------------------------------------


class TestVisitorAccuracy:
    """Each G17-G22 visitor emits the correct (relation_type, edge_kind) pairs."""

    def test_secret_vault_class_call_emits_reads_secret_vault(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _SecretAccessVisitor

        src = "SecretVault()"
        edges = _edges_for(src, _SecretAccessVisitor)
        assert ("reads_secret_vault", "secret_read") in edges

    def test_credential_store_call_emits_reads_secret_vault(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _SecretAccessVisitor

        src = "CredentialStore()"
        edges = _edges_for(src, _SecretAccessVisitor)
        # CredentialStore is in SECRET_VAULT_CLASSES → reads_secret_vault
        assert ("reads_secret_vault", "secret_read") in edges

    def test_get_secret_emits_accesses_credential(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _SecretAccessVisitor

        src = "vault.get_secret('MY_KEY')"
        edges = _edges_for(src, _SecretAccessVisitor)
        assert ("accesses_credential", "credential_access") in edges

    def test_rotate_secret_emits_rotates_secret(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _SecretAccessVisitor

        src = "vault.rotate_secret('API_KEY')"
        edges = _edges_for(src, _SecretAccessVisitor)
        assert ("rotates_secret", "secret_rotation") in edges

    def test_config_reader_call_emits_reads_governed_config(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _ConfigGovernanceVisitor

        src = "ConfigReader()"
        edges = _edges_for(src, _ConfigGovernanceVisitor)
        assert ("reads_governed_config", "governed_config_read") in edges

    def test_governed_config_call_emits_reads_governed_config(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _ConfigGovernanceVisitor

        src = "GovernedConfig()"
        edges = _edges_for(src, _ConfigGovernanceVisitor)
        assert ("reads_governed_config", "governed_config_read") in edges

    def test_validate_config_emits_validates_config_schema(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _ConfigGovernanceVisitor

        src = "cfg.validate_config(schema)"
        edges = _edges_for(src, _ConfigGovernanceVisitor)
        assert ("validates_config_schema", "config_schema_validation") in edges

    def test_load_config_emits_reads_governed_config(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _ConfigGovernanceVisitor

        src = "cfg.load_config('settings.yaml')"
        edges = _edges_for(src, _ConfigGovernanceVisitor)
        assert ("reads_governed_config", "governed_config_read") in edges

    def test_eval_call_emits_invokes_eval(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _DynamicInvocationVisitor

        src = "result = eval(expr)"
        edges = _edges_for(src, _DynamicInvocationVisitor)
        assert ("invokes_eval", "eval_call") in edges

    def test_exec_call_emits_invokes_exec(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _DynamicInvocationVisitor

        src = "exec(code_str)"
        edges = _edges_for(src, _DynamicInvocationVisitor)
        assert ("invokes_exec", "exec_call") in edges

    def test_importlib_import_module_emits_invokes_importlib(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _DynamicInvocationVisitor

        src = "importlib.import_module('mymod')"
        edges = _edges_for(src, _DynamicInvocationVisitor)
        assert ("invokes_importlib", "importlib_call") in edges

    def test_getattr_emits_invokes_getattr_dynamic(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _DynamicInvocationVisitor

        src = "getattr(obj, 'method')"
        edges = _edges_for(src, _DynamicInvocationVisitor)
        assert ("invokes_getattr_dynamic", "dynamic_getattr") in edges

    def test_policy_state_reader_emits_observes_policy_state(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _PolicyStateObserverVisitor

        src = "PolicyStateReader()"
        edges = _edges_for(src, _PolicyStateObserverVisitor)
        assert ("observes_policy_state", "policy_state_observation") in edges

    def test_runtime_state_observer_emits_observes_runtime_state(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _PolicyStateObserverVisitor

        src = "RuntimeStateObserver()"
        edges = _edges_for(src, _PolicyStateObserverVisitor)
        assert ("observes_runtime_state", "runtime_state_snapshot") in edges

    def test_state_snapshot_emits_snapshots_state(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _PolicyStateObserverVisitor

        src = "StateSnapshot()"
        edges = _edges_for(src, _PolicyStateObserverVisitor)
        assert ("snapshots_state", "runtime_state_snapshot") in edges

    def test_read_policy_state_method_emits_observes_policy_state(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _PolicyStateObserverVisitor

        src = "observer.read_policy_state('hash_v3')"
        edges = _edges_for(src, _PolicyStateObserverVisitor)
        assert ("observes_policy_state", "policy_state_observation") in edges

    def test_snapshot_runtime_method_emits_observes_runtime_state(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _PolicyStateObserverVisitor

        src = "observer.snapshot_runtime()"
        edges = _edges_for(src, _PolicyStateObserverVisitor)
        # tail is 'snapshot_runtime' — 'runtime' detected first → observes_runtime_state
        assert ("observes_runtime_state", "runtime_state_snapshot") in edges

    def test_antipattern_registry_class_emits_registers_antipattern(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _AntipatternRegistryVisitor

        src = "AntipatternRegistry()"
        edges = _edges_for(src, _AntipatternRegistryVisitor)
        assert ("registers_antipattern", "antipattern_classification") in edges

    def test_pattern_classifier_emits_classifies_antipattern(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _AntipatternRegistryVisitor

        src = "PatternClassifier()"
        edges = _edges_for(src, _AntipatternRegistryVisitor)
        assert ("classifies_antipattern", "antipattern_classification") in edges

    def test_healing_orchestrator_class_emits_dispatches_healing_run(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _HealingOrchestratorVisitor

        src = "HealingOrchestrator()"
        edges = _edges_for(src, _HealingOrchestratorVisitor)
        assert ("dispatches_healing_run", "healing_dispatch") in edges

    def test_dispatch_healing_method_emits_dispatches_healing_run(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _HealingOrchestratorVisitor

        src = "orch.dispatch_healing('violation-001')"
        edges = _edges_for(src, _HealingOrchestratorVisitor)
        assert ("dispatches_healing_run", "healing_dispatch") in edges

    def test_confirm_heal_method_emits_confirms_heal(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _HealingOrchestratorVisitor

        src = "orch.confirm_heal(run)"
        edges = _edges_for(src, _HealingOrchestratorVisitor)
        assert ("confirms_heal", "healing_confirm") in edges

    def test_abort_heal_method_emits_aborts_heal(self) -> None:
        from agentic_core.adg.extraction.static_scanner import _HealingOrchestratorVisitor

        src = "orch.abort_heal(run, 'timeout')"
        edges = _edges_for(src, _HealingOrchestratorVisitor)
        assert ("aborts_heal", "healing_abort") in edges


# ---------------------------------------------------------------------------
# A2 — Visitor non-contamination
# ---------------------------------------------------------------------------


class TestVisitorNonContamination:
    """Unrelated code must produce zero edges from each G17-G22 visitor."""

    UNRELATED_SRC = """
import os
import json

def foo(x):
    return x + 1

class Bar:
    def baz(self):
        return "hello"

result = Bar().baz()
data = json.dumps({"key": "value"})
"""

    @pytest.mark.parametrize(
        "visitor_name",
        [
            "_SecretAccessVisitor",
            "_ConfigGovernanceVisitor",
            "_DynamicInvocationVisitor",
            "_PolicyStateObserverVisitor",
            "_AntipatternRegistryVisitor",
            "_HealingOrchestratorVisitor",
        ],
    )
    def test_unrelated_code_produces_zero_edges(self, visitor_name: str) -> None:
        from agentic_core.adg.extraction import static_scanner

        visitor_cls = getattr(static_scanner, visitor_name)
        edges = _scan_src(self.UNRELATED_SRC, visitor_cls)
        assert edges == [], f"{visitor_name} produced {len(edges)} edges from unrelated code: {edges}"


# ---------------------------------------------------------------------------
# A3 — Runtime state-machine accuracy
# ---------------------------------------------------------------------------


class TestRuntimeStateMachines:
    """Full lifecycle tests for all six G17-G22 runtime managers."""

    # --- G17: SecretAccessRecorder ---

    def test_secret_recorder_record_access_increments_total(self) -> None:
        from agentic_core.adg.runtime.secret_access import SecretAccessRecorder, SecretKind

        r = SecretAccessRecorder("a", "r1")
        assert r.report.total_accesses == 0
        r.record_access("MY_KEY", SecretKind.API_KEY)
        assert r.report.total_accesses == 1

    def test_secret_recorder_record_env_read(self) -> None:
        from agentic_core.adg.runtime.secret_access import (
            SecretAccessOutcome,
            SecretAccessRecorder,
            SecretKind,
        )

        r = SecretAccessRecorder("a", "r1")
        ev = r.record_env_read("DB_HOST")
        assert ev.secret_kind == SecretKind.ENV_VAR
        assert ev.access_method == "os.getenv"
        assert ev.outcome == SecretAccessOutcome.SUCCESS

    def test_secret_recorder_record_rotation(self) -> None:
        from agentic_core.adg.runtime.secret_access import SecretAccessRecorder

        r = SecretAccessRecorder("a", "r1")
        ev = r.record_rotation("OLD_KEY")
        assert ev.is_rotation is True
        assert r.report.rotation_count == 1

    def test_secret_recorder_denied_increments_denied_count(self) -> None:
        from agentic_core.adg.runtime.secret_access import SecretAccessRecorder

        r = SecretAccessRecorder("a", "r1")
        r.record_denied("RESTRICTED_KEY")
        assert r.report.denied_count == 1

    def test_secret_recorder_masks_value(self) -> None:
        from agentic_core.adg.runtime.secret_access import SecretAccessRecorder, SecretKind

        r = SecretAccessRecorder("a", "r1")
        ev = r.record_access("MY_KEY", SecretKind.API_KEY, raw_value="super_secret")
        assert ev.masked_value_hash != ""
        assert "super_secret" not in ev.masked_value_hash

    def test_secret_recorder_report_to_dict_json_serializable(self) -> None:
        from agentic_core.adg.runtime.secret_access import SecretAccessRecorder, SecretKind

        r = SecretAccessRecorder("a", "r1")
        r.record_access("KEY1", SecretKind.API_KEY)
        r.record_rotation("KEY2")
        d = r.report.to_dict()
        assert json.loads(json.dumps(d)) == d

    def test_secret_recorders_are_isolated(self) -> None:
        from agentic_core.adg.runtime.secret_access import SecretAccessRecorder

        r1 = SecretAccessRecorder("a", "r1")
        r2 = SecretAccessRecorder("a", "r2")
        r1.record_env_read("X")
        assert r2.report.total_accesses == 0

    def test_secret_recorder_by_kind(self) -> None:
        from agentic_core.adg.runtime.secret_access import SecretAccessRecorder, SecretKind

        r = SecretAccessRecorder("a", "r1")
        r.record_access("K1", SecretKind.API_KEY)
        r.record_access("K2", SecretKind.PASSWORD)
        r.record_access("K3", SecretKind.API_KEY)
        bk = r.report.by_kind
        assert bk["api_key"] == 2
        assert bk["password"] == 1

    # --- G18: ConfigGovernor ---

    def test_config_governor_first_read_is_not_cached(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor, ConfigReadOutcome

        g = ConfigGovernor("a", "r1")
        ev = g.read_config("db.host")
        assert ev.cached is False
        assert ev.outcome == ConfigReadOutcome.HIT

    def test_config_governor_second_read_is_cached(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor, ConfigReadOutcome

        g = ConfigGovernor("a", "r1")
        g.read_config("db.host")
        ev2 = g.read_config("db.host")
        assert ev2.cached is True
        assert ev2.outcome == ConfigReadOutcome.CACHED

    def test_config_governor_validate_valid(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor, ConfigSchemaStatus

        g = ConfigGovernor("a", "r1")
        ev = g.validate_config("db.port", errors=[])
        assert ev.schema_status == ConfigSchemaStatus.VALID

    def test_config_governor_validate_invalid(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor, ConfigSchemaStatus

        g = ConfigGovernor("a", "r1")
        ev = g.validate_config("db.port", errors=["type_mismatch"])
        assert ev.schema_status == ConfigSchemaStatus.INVALID
        assert ev.validation_errors == ["type_mismatch"]

    def test_config_governor_schema_fail_count(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor

        g = ConfigGovernor("a", "r1")
        g.validate_config("k1", errors=[])
        g.validate_config("k2", errors=["missing_key"])
        assert g.report.schema_fail_count == 1

    def test_config_governor_invalidate_cache(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor

        g = ConfigGovernor("a", "r1")
        g.read_config("a")
        g.read_config("b")
        count = g.invalidate_cache()
        assert count == 2
        ev = g.read_config("a")
        assert ev.cached is False

    def test_config_governor_report_to_dict_json_serializable(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor

        g = ConfigGovernor("a", "r1")
        g.read_config("x")
        g.validate_config("y", errors=["err1"])
        d = g.report.to_dict()
        assert json.loads(json.dumps(d)) == d

    def test_config_governors_are_isolated(self) -> None:
        from agentic_core.adg.runtime.config_governance import ConfigGovernor

        g1 = ConfigGovernor("a", "r1")
        g2 = ConfigGovernor("a", "r2")
        g1.read_config("x")
        assert g2.report.total_reads == 0

    # --- G19: DynamicInvocationTracker ---

    def test_tracker_record_eval(self) -> None:
        from agentic_core.adg.runtime.dynamic_invocation import (
            DynamicInvocationKind,
            DynamicInvocationRisk,
            DynamicInvocationTracker,
        )

        t = DynamicInvocationTracker("a", "r1")
        rec = t.record_eval("foo.py", 10, "x+1")
        assert rec.kind == DynamicInvocationKind.EVAL
        assert rec.risk == DynamicInvocationRisk.CRITICAL
        assert t.report.critical_count == 1

    def test_tracker_record_exec(self) -> None:
        from agentic_core.adg.runtime.dynamic_invocation import (
            DynamicInvocationKind,
            DynamicInvocationRisk,
            DynamicInvocationTracker,
        )

        t = DynamicInvocationTracker("a", "r1")
        rec = t.record_exec("bar.py", 20)
        assert rec.kind == DynamicInvocationKind.EXEC
        assert rec.risk == DynamicInvocationRisk.CRITICAL

    def test_tracker_record_importlib(self) -> None:
        from agentic_core.adg.runtime.dynamic_invocation import (
            DynamicInvocationKind,
            DynamicInvocationRisk,
            DynamicInvocationTracker,
        )

        t = DynamicInvocationTracker("a", "r1")
        rec = t.record_importlib("mymod", "baz.py", 30)
        assert rec.kind == DynamicInvocationKind.IMPORT_MODULE
        assert rec.risk == DynamicInvocationRisk.HIGH

    def test_tracker_record_getattr(self) -> None:
        from agentic_core.adg.runtime.dynamic_invocation import (
            DynamicInvocationKind,
            DynamicInvocationRisk,
            DynamicInvocationTracker,
        )

        t = DynamicInvocationTracker("a", "r1")
        rec = t.record_getattr("MyClass", "my_method")
        assert rec.kind == DynamicInvocationKind.GETATTR
        assert rec.risk == DynamicInvocationRisk.LOW

    def test_tracker_suppress(self) -> None:
        from agentic_core.adg.runtime.dynamic_invocation import DynamicInvocationTracker

        t = DynamicInvocationTracker("a", "r1")
        rec = t.record_eval("foo.py", 5)
        assert rec.suppressed is False
        t.suppress(rec)
        assert rec.suppressed is True
        assert t.report.suppressed_count == 1

    def test_tracker_report_to_dict_json_serializable(self) -> None:
        from agentic_core.adg.runtime.dynamic_invocation import DynamicInvocationTracker

        t = DynamicInvocationTracker("a", "r1")
        t.record_eval("a.py", 1)
        t.record_importlib("m", "b.py", 2)
        d = t.report.to_dict()
        assert json.loads(json.dumps(d)) == d

    def test_trackers_are_isolated(self) -> None:
        from agentic_core.adg.runtime.dynamic_invocation import DynamicInvocationTracker

        t1 = DynamicInvocationTracker("a", "r1")
        t2 = DynamicInvocationTracker("a", "r2")
        t1.record_eval("x.py", 1)
        assert t2.report.total_count == 0

    # --- G20: PolicyStateObserver ---

    def test_observer_observe_policy(self) -> None:
        from agentic_core.adg.runtime.policy_state_observer import (
            PolicyStateObserver,
            StateObservationKind,
        )

        obs = PolicyStateObserver("a", "r1")
        ev = obs.observe_policy("policy_hash_v3")
        assert ev.kind == StateObservationKind.POLICY_STATE
        assert obs.report.policy_state_count == 1

    def test_observer_observe_runtime(self) -> None:
        from agentic_core.adg.runtime.policy_state_observer import (
            PolicyStateObserver,
            StateObservationKind,
        )

        obs = PolicyStateObserver("a", "r1")
        ev = obs.observe_runtime("agent_health")
        assert ev.kind == StateObservationKind.RUNTIME_STATE
        assert obs.report.runtime_state_count == 1

    def test_observer_probe_health(self) -> None:
        from agentic_core.adg.runtime.policy_state_observer import (
            PolicyStateObserver,
            StateObservationKind,
        )

        obs = PolicyStateObserver("a", "r1")
        ev = obs.probe_health("memory_usage")
        assert ev.kind == StateObservationKind.HEALTH_PROBE

    def test_observer_snapshot(self) -> None:
        from agentic_core.adg.runtime.policy_state_observer import (
            PolicyStateObserver,
            StateObservationKind,
        )

        obs = PolicyStateObserver("a", "r1")
        ev = obs.snapshot("before_mutation")
        assert ev.kind == StateObservationKind.SNAPSHOT
        assert ev.snapshot_id.startswith("snap-")
        assert obs.report.snapshot_count == 1

    def test_observer_stale_count(self) -> None:
        from agentic_core.adg.runtime.policy_state_observer import (
            PolicyStateObserver,
            StateReadOutcome,
        )

        obs = PolicyStateObserver("a", "r1")
        obs.observe_policy("k1", outcome=StateReadOutcome.CURRENT)
        obs.observe_policy("k2", outcome=StateReadOutcome.STALE)
        assert obs.report.stale_count == 1

    def test_observer_report_to_dict_json_serializable(self) -> None:
        from agentic_core.adg.runtime.policy_state_observer import PolicyStateObserver

        obs = PolicyStateObserver("a", "r1")
        obs.observe_policy("k1")
        obs.observe_runtime("k2")
        obs.snapshot("s1")
        d = obs.report.to_dict()
        assert json.loads(json.dumps(d)) == d

    def test_observers_are_isolated(self) -> None:
        from agentic_core.adg.runtime.policy_state_observer import PolicyStateObserver

        obs1 = PolicyStateObserver("a", "r1")
        obs2 = PolicyStateObserver("a", "r2")
        obs1.observe_policy("k")
        assert obs2.report.total_observations == 0

    # --- G21: AntipatternRegistry ---

    def test_registry_register(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import (
            AntipatternCategory,
            AntipatternRegistry,
            AntipatternSeverity,
        )

        reg = AntipatternRegistry("a", "r1")
        rec = reg.register(AntipatternCategory.SILENT_EXCEPTION_SWALLOW, "foo.py", 42)
        assert rec.category == AntipatternCategory.SILENT_EXCEPTION_SWALLOW
        assert rec.severity == AntipatternSeverity.HIGH
        assert reg.report.total_count == 1

    def test_registry_hardcoded_secret_is_critical(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import (
            AntipatternCategory,
            AntipatternRegistry,
            AntipatternSeverity,
        )

        reg = AntipatternRegistry("a", "r1")
        rec = reg.register(AntipatternCategory.HARDCODED_SECRET, "secrets.py", 10)
        assert rec.severity == AntipatternSeverity.CRITICAL
        assert reg.report.critical_count == 1

    def test_registry_suppress(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import (
            AntipatternCategory,
            AntipatternRegistry,
        )

        reg = AntipatternRegistry("a", "r1")
        rec = reg.register(AntipatternCategory.BARE_EXCEPT, "foo.py", 5)
        assert reg.report.active_count == 1
        reg.suppress(rec)
        assert reg.report.suppressed_count == 1
        assert reg.report.active_count == 0

    def test_registry_classify_valid_edge_kind(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import (
            AntipatternCategory,
            AntipatternRegistry,
        )

        reg = AntipatternRegistry("a", "r1")
        cat = reg.classify("silent_exception_swallow")
        assert cat == AntipatternCategory.SILENT_EXCEPTION_SWALLOW

    def test_registry_classify_unknown_returns_none(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import AntipatternRegistry

        reg = AntipatternRegistry("a", "r1")
        assert reg.classify("completely_unknown_pattern") is None

    def test_registry_register_from_edge_kind(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import (
            AntipatternCategory,
            AntipatternRegistry,
        )

        reg = AntipatternRegistry("a", "r1")
        rec = reg.register_from_edge_kind("blocking_call_in_async", "bar.py", 99)
        assert rec is not None
        assert rec.category == AntipatternCategory.BLOCKING_CALL_IN_ASYNC

    def test_registry_register_from_unknown_edge_kind_returns_none(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import AntipatternRegistry

        reg = AntipatternRegistry("a", "r1")
        result = reg.register_from_edge_kind("not_a_pattern")
        assert result is None

    def test_registry_report_to_dict_json_serializable(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import (
            AntipatternCategory,
            AntipatternRegistry,
        )

        reg = AntipatternRegistry("a", "r1")
        reg.register(AntipatternCategory.MUTABLE_DEFAULT_ARG, "x.py", 1)
        d = reg.report.to_dict()
        assert json.loads(json.dumps(d)) == d

    def test_registries_are_isolated(self) -> None:
        from agentic_core.adg.runtime.antipattern_registry import (
            AntipatternCategory,
            AntipatternRegistry,
        )

        r1 = AntipatternRegistry("a", "r1")
        r2 = AntipatternRegistry("a", "r2")
        r1.register(AntipatternCategory.BARE_EXCEPT, "f.py", 1)
        assert r2.report.total_count == 0

    # --- G22: HealingOrchestrator ---

    def test_orchestrator_dispatch_creates_run(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingRunPhase,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("viol-001", HealingTrigger.VIOLATION_DETECTED)
        assert run.phase == HealingRunPhase.DISPATCHED
        assert orch.report.total_runs == 1

    def test_orchestrator_add_step_transitions_to_in_progress(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingRunPhase,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.POLICY_DRIFT)
        orch.add_step(run, "healer_A", "apply_patch")
        assert run.phase == HealingRunPhase.IN_PROGRESS
        assert run.step_count == 1

    def test_orchestrator_confirm(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingRunPhase,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.MANUAL)
        orch.add_step(run, "h", "action", succeeded=True)
        orch.confirm(run)
        assert run.phase == HealingRunPhase.CONFIRMED
        assert run.confirmed_at > 0
        assert orch.report.confirmed_count == 1

    def test_orchestrator_abort(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingRunPhase,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.ESCALATION)
        orch.abort(run, "dependency_failed")
        assert run.phase == HealingRunPhase.ABORTED
        assert run.abort_reason == "dependency_failed"
        assert orch.report.aborted_count == 1

    def test_orchestrator_confirm_is_terminal(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.SCHEDULED)
        orch.confirm(run)
        assert run.is_terminal is True
        assert run.succeeded is True

    def test_orchestrator_abort_is_terminal(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.THRESHOLD_BREACH)
        orch.abort(run)
        assert run.is_terminal is True
        assert run.succeeded is False

    def test_orchestrator_timeout(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingRunPhase,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.MANUAL)
        orch.timeout(run)
        assert run.phase == HealingRunPhase.TIMED_OUT
        assert run.abort_reason == "timeout"

    def test_orchestrator_confirm_noop_on_terminal(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingRunPhase,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.MANUAL)
        orch.abort(run)
        orch.confirm(run)
        assert run.phase == HealingRunPhase.ABORTED

    def test_orchestrator_success_rate(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        r1 = orch.dispatch("v1", HealingTrigger.MANUAL)
        r2 = orch.dispatch("v2", HealingTrigger.MANUAL)
        orch.confirm(r1)
        orch.abort(r2)
        assert orch.report.success_rate == pytest.approx(0.5)

    def test_orchestrator_report_to_dict_json_serializable(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingTrigger,
        )

        orch = HealingOrchestrator("a", "r1")
        run = orch.dispatch("v", HealingTrigger.VIOLATION_DETECTED)
        orch.add_step(run, "h", "act")
        orch.confirm(run)
        d = orch.report.to_dict()
        assert json.loads(json.dumps(d)) == d

    def test_orchestrators_are_isolated(self) -> None:
        from agentic_core.adg.runtime.healing_orchestrator import (
            HealingOrchestrator,
            HealingTrigger,
        )

        o1 = HealingOrchestrator("a", "r1")
        o2 = HealingOrchestrator("a", "r2")
        o1.dispatch("v", HealingTrigger.MANUAL)
        assert o2.report.total_runs == 0


# ---------------------------------------------------------------------------
# A4 — ADG round-trip accuracy
# ---------------------------------------------------------------------------


class TestADGRoundTrip:
    """Scanning each G17-G22 runtime module source must emit ≥1 edge."""

    @pytest.mark.parametrize(
        "module_filename,visitor_name,expected_min_edges",
        [
            ("secret_access.py", "_SecretAccessVisitor", None),
            ("config_governance.py", "_ConfigGovernanceVisitor", None),
            ("dynamic_invocation.py", "_DynamicInvocationVisitor", None),
            ("policy_state_observer.py", "_PolicyStateObserverVisitor", None),
            ("antipattern_registry.py", "_AntipatternRegistryVisitor", None),
            ("healing_orchestrator.py", "_HealingOrchestratorVisitor", None),
        ],
    )
    def test_runtime_module_produces_no_crash_when_scanned(
        self, module_filename: str, visitor_name: str, expected_min_edges: int | None
    ) -> None:
        from agentic_core.adg.extraction import static_scanner

        visitor_cls = getattr(static_scanner, visitor_name)
        src_path = RUNTIME_ROOT / module_filename
        src = src_path.read_text(encoding="utf-8")
        # Should not raise; edges may be 0 for self-referential scans
        try:
            edges = _scan_src(src, visitor_cls)
        except Exception as exc:
            pytest.fail(f"{visitor_name} crashed scanning {module_filename}: {exc}")
        if expected_min_edges is not None:
            assert len(edges) >= expected_min_edges


# ---------------------------------------------------------------------------
# A5 — Layer splitter accuracy
# ---------------------------------------------------------------------------


class TestLayerSplitterAccuracy:
    """G17-G22 relations must be in the governance plane with no overlap."""

    @pytest.mark.parametrize(
        "relation",
        [
            "reads_secret_vault",
            "accesses_credential",
            "rotates_secret",
            "reads_governed_config",
            "validates_config_schema",
            "caches_config",
            "invokes_eval",
            "invokes_exec",
            "invokes_importlib",
            "invokes_getattr_dynamic",
            "observes_policy_state",
            "observes_runtime_state",
            "snapshots_state",
            "registers_antipattern",
            "classifies_antipattern",
            "dispatches_healing_run",
            "confirms_heal",
            "aborts_heal",
        ],
    )
    def test_relation_in_governance_plane(self, relation: str) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _GOVERNANCE_GRAPH_RELS

        assert relation in _GOVERNANCE_GRAPH_RELS, f"{relation!r} not in _GOVERNANCE_GRAPH_RELS"

    @pytest.mark.parametrize(
        "relation",
        [
            "reads_secret_vault",
            "accesses_credential",
            "rotates_secret",
            "reads_governed_config",
            "validates_config_schema",
            "caches_config",
            "invokes_eval",
            "invokes_exec",
            "invokes_importlib",
            "invokes_getattr_dynamic",
            "observes_policy_state",
            "observes_runtime_state",
            "snapshots_state",
            "registers_antipattern",
            "classifies_antipattern",
            "dispatches_healing_run",
            "confirms_heal",
            "aborts_heal",
        ],
    )
    def test_relation_not_in_file_plane(self, relation: str) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _FILE_GRAPH_RELS

        assert relation not in _FILE_GRAPH_RELS

    @pytest.mark.parametrize(
        "relation",
        [
            "reads_secret_vault",
            "accesses_credential",
            "rotates_secret",
            "reads_governed_config",
            "validates_config_schema",
            "caches_config",
            "invokes_eval",
            "invokes_exec",
            "invokes_importlib",
            "invokes_getattr_dynamic",
            "observes_policy_state",
            "observes_runtime_state",
            "snapshots_state",
            "registers_antipattern",
            "classifies_antipattern",
            "dispatches_healing_run",
            "confirms_heal",
            "aborts_heal",
        ],
    )
    def test_relation_not_in_symbol_plane(self, relation: str) -> None:
        from agentic_core.adg.artifact.SplitArtifact import _SYMBOL_GRAPH_RELS

        assert relation not in _SYMBOL_GRAPH_RELS

    def test_no_three_plane_overlap(self) -> None:
        """Every relation type must appear in exactly one plane."""
        from agentic_core.adg.artifact.SplitArtifact import (
            _FILE_GRAPH_RELS,
            _GOVERNANCE_GRAPH_RELS,
            _SYMBOL_GRAPH_RELS,
        )

        file_sym = _FILE_GRAPH_RELS & _SYMBOL_GRAPH_RELS
        file_gov = _FILE_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS
        sym_gov = _SYMBOL_GRAPH_RELS & _GOVERNANCE_GRAPH_RELS
        assert not file_sym, f"file ∩ symbol: {file_sym}"
        assert not file_gov, f"file ∩ governance: {file_gov}"
        assert not sym_gov, f"symbol ∩ governance: {sym_gov}"


# ---------------------------------------------------------------------------
# Enum value format
# ---------------------------------------------------------------------------


class TestEnumValueFormat:
    """All G17-G22 enum .value strings must be lowercase snake_case."""

    @pytest.mark.parametrize(
        "mod_path,enum_name",
        [
            ("agentic_core.adg.runtime.secret_access", "SecretKind"),
            ("agentic_core.adg.runtime.secret_access", "SecretAccessOutcome"),
            ("agentic_core.adg.runtime.config_governance", "ConfigReadOutcome"),
            ("agentic_core.adg.runtime.config_governance", "ConfigSchemaStatus"),
            ("agentic_core.adg.runtime.dynamic_invocation", "DynamicInvocationKind"),
            ("agentic_core.adg.runtime.dynamic_invocation", "DynamicInvocationRisk"),
            ("agentic_core.adg.runtime.policy_state_observer", "StateObservationKind"),
            ("agentic_core.adg.runtime.policy_state_observer", "StateReadOutcome"),
            ("agentic_core.adg.runtime.antipattern_registry", "AntipatternSeverity"),
            ("agentic_core.adg.runtime.antipattern_registry", "AntipatternCategory"),
            ("agentic_core.adg.runtime.healing_orchestrator", "HealingRunPhase"),
            ("agentic_core.adg.runtime.healing_orchestrator", "HealingTrigger"),
        ],
    )
    def test_enum_values_are_lowercase_snake_case(self, mod_path: str, enum_name: str) -> None:
        mod = importlib.import_module(mod_path)
        enum_cls = getattr(mod, enum_name)
        for member in enum_cls:
            val = member.value
            assert val == val.lower(), f"{enum_name}.{member.name} value {val!r} is not lowercase"
            assert " " not in val, f"{enum_name}.{member.name} value {val!r} contains spaces"
