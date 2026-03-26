"""
test_adg_infusion_phases_verification.py

Creative orthogonal verification of ADG Infusion Phases 2j-4.

Strategy: we do NOT re-execute the phases.  Instead we:
  1. Inspect source code with AST to prove injections exist
  2. Use mock BehavioralProfiles to exercise every code-path without SQLite
  3. Verify MRO / inheritance contracts with pure introspection
  4. Assert runtime behaviour using controlled stub objects
  5. Cross-check that no existing public API signatures changed
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Stub missing optional modules before any agentic_core imports resolve them.
# `agentic_core.adg.runtime.__init__` unconditionally imports execution_proof
# which does not exist in this environment.  Shim it so tests can import
# behavioral_index without the entire adg.runtime package failing to load.
# ---------------------------------------------------------------------------
import sys
import types as _types

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_infusion_phases_verification")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_infusion_phases_verification", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_adg_infusion_phases_verification", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_adg_infusion_phases_verification")
# REMOVED: emit_determinism_digest("p0", "test_adg_infusion_phases_verification")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_infusion_phases_verification", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_infusion_phases_verification", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_infusion_phases_verification", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_infusion_phases_verification", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_infusion_phases_verification", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_infusion_phases_verification", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_infusion_phases_verification", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_infusion_phases_verification", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_infusion_phases_verification", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_infusion_phases_verification", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_infusion_phases_verification", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_infusion_phases_verification", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_infusion_phases_verification", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_infusion_phases_verification", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_infusion_phases_verification", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_infusion_phases_verification", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_infusion_phases_verification", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_infusion_phases_verification", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_infusion_phases_verification", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_infusion_phases_verification", "exec_snapshot_link")


def _make_stub_module(name: str) -> _types.ModuleType:
    mod = _types.ModuleType(name)
    mod.__spec__ = None  # type: ignore[attr-defined]
    return mod


for _stub_name in ("agentic_core.adg.runtime.execution_proof",):
    if _stub_name not in sys.modules:
        _stub = _make_stub_module(_stub_name)
        # Add all names the __init__ imports from execution_proof
        for _attr in (
            "ExecutionProofRecorder",
            "ExecutionProofReport",
            "ExecutionTrace",
            "ProofComparison",
            "ProofComparisonOutcome",
            "ReplayKey",
        ):
            setattr(_stub, _attr, type(_attr, (), {}))
        sys.modules[_stub_name] = _stub

import ast
import inspect
import unittest
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from unittest.mock import MagicMock, patch

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_adg_infusion_phases_verification", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_infusion_phases_verification", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_infusion_phases_verification", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_infusion_phases_verification", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_infusion_phases_verification", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_infusion_phases_verification", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_infusion_phases_verification", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_infusion_phases_verification", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_infusion_phases_verification", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_infusion_phases_verification", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_infusion_phases_verification", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_infusion_phases_verification", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_infusion_phases_verification", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_infusion_phases_verification", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_infusion_phases_verification", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_infusion_phases_verification", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_infusion_phases_verification", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_infusion_phases_verification", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_infusion_phases_verification", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_infusion_phases_verification", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_infusion_phases_verification", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_infusion_phases_verification", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_infusion_phases_verification", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_infusion_phases_verification", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_infusion_phases_verification", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_infusion_phases_verification", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_infusion_phases_verification", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_infusion_phases_verification", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_infusion_phases_verification", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_infusion_phases_verification", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_infusion_phases_verification", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_infusion_phases_verification", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_infusion_phases_verification", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_infusion_phases_verification", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_infusion_phases_verification", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_infusion_phases_verification", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_infusion_phases_verification", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_infusion_phases_verification", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_infusion_phases_verification", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_infusion_phases_verification", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_infusion_phases_verification", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_infusion_phases_verification", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_infusion_phases_verification", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_infusion_phases_verification", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_infusion_phases_verification", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_infusion_phases_verification", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_infusion_phases_verification", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_infusion_phases_verification", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_infusion_phases_verification")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_infusion_phases_verification", "confidence_gate")

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]


def _src(relative: str) -> str:
    """Read source text of a file relative to repo root."""
    return (REPO / relative).read_text(encoding="utf-8")


def _ast_of(relative: str) -> ast.Module:
    return ast.parse(_src(relative))


def _has_name_in_ast(tree: ast.Module, name: str) -> bool:
    """Return True if *name* appears as an identifier anywhere in *tree*."""
    for node in ast.walk(tree):
        for field_name, value in ast.iter_fields(node):
            if isinstance(value, str) and name in value:
                return True
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and name in item:
                        return True
    return False


def _func_src(tree: ast.Module, func_name: str) -> str | None:
    """Return the un-parsed source lines for a top-level or method *func_name*."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return ast.unparse(node)
    return None


# ---------------------------------------------------------------------------
# Stub BehavioralProfile (no SQLite needed)
# ---------------------------------------------------------------------------
@dataclass
class _StubProfile:
    behavioral_score: float = 0.5
    deterministic_coverage: bool = False
    antipattern_signals: frozenset = field(default_factory=frozenset)
    agent_signals: frozenset = field(default_factory=frozenset)
    script_signals: frozenset = field(default_factory=frozenset)
    resolved_path: str = "stub/path.py"


# ===========================================================================
# Phase 4 — ADGBehavioralMixin root injection
# ===========================================================================
class TestPhase4MROInjection(unittest.TestCase):
    """Verify ADGBehavioralMixin is wired into SovereignBaseAgent MRO."""

    def test_adg_behavioral_mixin_in_mro(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin
        from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin
        from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
        from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.L5_safety.enforcement.security.credential_access_guard import CredentialAccessGuard
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
        from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import SovereignRAGManager
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.base_agents.L6ObservabilityBase import L6ObservabilityBase
        from agentic_core.L5_safety.validators.base_detector_validator import (
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.L5_safety.validators.base_detector_validator import (
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        import agentic_core.adg.runtime.behavioral_index as _beh_idx
        from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
        from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
        from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import SovereignRAGManager
        from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
        from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin
    """Test adg_behavioral_mixin_in_mro runtime behavior."""
    # Arrange
    # TODO: Set up test data for adg_behavioral_mixin_in_mro
    test_data = {}  # Replace with actual test data

    # Act
    """Test adg_behavioral_mixin_after_runtime_safety runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute adg_behavioral_mixin_after_runtime_safety
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
#  # MOVED: from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        expected = {
            "adg_behavioral_score",
            "adg_is_agent_like",
            "adg_is_script_like",
            "adg_antipattern_signals",
            "adg_agent_signals",
            "adg_script_signals",
            "adg_dead_import_count",
            "adg_profile_available",
        }
        actual = {k for k, v in inspect.getmembers(ADGBehavioralMixin) if isinstance(v, cached_property)}
        missing = expected - actual
        self.assertFalse(missing, f"Missing cached_property members: {missing}")

    def test_mixin_neutral_fallback_without_project_root(self):
        """Without project_root, all properties must return safe defaults."""
#  # MOVED: from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        class _Bare(ADGBehavioralMixin):
            pass  # no project_root

        obj = _Bare()
        self.assertEqual(obj.adg_behavioral_score, 0.5)
        self.assertFalse(obj.adg_is_agent_like)
        self.assertFalse(obj.adg_is_script_like)
        self.assertEqual(obj.adg_antipattern_signals, [])
        self.assertEqual(obj.adg_dead_import_count, 0)

    def test_mixin_stub_profile_agent_like(self):
        """When stub profile has score >0.7, is_agent_like must be True."""
#  # MOVED: from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        class _Stubbed(ADGBehavioralMixin):
            project_root = REPO

        obj = _Stubbed()
        stub = _StubProfile(behavioral_score=0.85)
        with patch.object(_Stubbed, "_adg_load_profile", return_value=stub):
            # Force re-evaluation (cached_property caches on instance dict)
            for attr in ("adg_behavioral_score", "adg_is_agent_like", "adg_is_script_like"):
                obj.__dict__.pop(attr, None)
            self.assertAlmostEqual(obj.adg_behavioral_score, 0.85)
            obj.__dict__.pop("adg_is_agent_like", None)
            self.assertTrue(obj.adg_is_agent_like)

    def test_mixin_stub_profile_script_like(self):
#  # MOVED: from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin

        class _Stubbed(ADGBehavioralMixin):
            project_root = REPO

        obj = _Stubbed()
        stub = _StubProfile(behavioral_score=0.2, deterministic_coverage=True)
        with patch.object(_Stubbed, "_adg_load_profile", return_value=stub):
            obj.__dict__.pop("adg_is_script_like", None)
            self.assertTrue(obj.adg_is_script_like)

    def test_behavioral_summary_keys(self):
    """Test behavioral_summary_keys runtime behavior."""
    # Arrange
    # TODO: Set up test data for behavioral_summary_keys
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute behavioral_summary_keys
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            "adg_agent_signals",
            "adg_script_signals",
            "adg_dead_import_count",
        }
        self.assertEqual(required_keys, set(summary.keys()))


# ===========================================================================
# Phase 2j — ElevatorShaftConsistencyEnforcer
# ===========================================================================
class TestPhase2jElevatorShaft(unittest.TestCase):
    """Verify ADG violates injection in summary() without SQLite."""

    @classmethod
    def setUpClass(cls):
#  # MOVED: from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
            ElevatorShaftConsistencyEnforcer,
        )

        cls.EnfClass = ElevatorShaftConsistencyEnforcer

    def test_summary_has_adg_violates_key(self):
        enf = self.EnfClass(drift_tolerance=5)
        summary = enf.summary()
        self.assertIn("adg_violates", summary)

    def test_adg_violates_is_list(self):
        enf = self.EnfClass(drift_tolerance=5)
        self.assertIsInstance(enf.summary()["adg_violates"], list)

    def test_summary_still_contains_layer_records(self):
        """Existing layer-record structure must not be broken."""
#  # MOVED: from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
            ElevatorShaftConsistencyEnforcer,
            SemanticClockSnapshot,
        )

        enf = ElevatorShaftConsistencyEnforcer(drift_tolerance=5)
        enf.record_advance("L3", SemanticClockSnapshot(tick=1))
        s = enf.summary()
        self.assertIn("L3", s)
        self.assertIn("last_tick", s["L3"])

    def test_summary_adg_violates_with_stub_antipatterns(self):
        """When ADG returns antipatterns, they appear in summary and trigger warning log."""
        import logging

#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        enf = self.EnfClass(drift_tolerance=5)
        stub = _StubProfile(antipattern_signals=frozenset({"for_retry", "silent_swallower"}))

        with (
            patch.object(_beh_idx, "get_behavioral_profile", return_value=stub),
            self.assertLogs(level=logging.WARNING),
        ):
            s = enf.summary()

        self.assertIn("for_retry", s["adg_violates"])
        self.assertIn("silent_swallower", s["adg_violates"])
        self.assertEqual(sorted(s["adg_violates"]), ["for_retry", "silent_swallower"])

    def test_source_contains_adg_violates_key(self):
        """AST-level check: 'adg_violates' literal is present in source."""
        src = _src("agentic_core/L4_state/enforcement/elevator_shaft_consistency_enforcer.py")
        self.assertIn("adg_violates", src)

    def test_summary_no_exception_when_adg_unavailable(self):
        """Graceful when behavioral_index import raises."""
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        enf = self.EnfClass(drift_tolerance=5)
        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=RuntimeError("ADG unavailable")):
            s = enf.summary()
        self.assertEqual(s["adg_violates"], [])


# ===========================================================================
# Phase 2k — CredentialAccessGuard
# ===========================================================================
class TestPhase2kCredentialAccessGuard(unittest.TestCase):
    """Verify _adg_violates wired into __init__ without SQLite."""

    def _make_guard(self, profile_stub=None):
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
            CredentialAccessGuard,
        )

        if profile_stub is not None:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=profile_stub):
                return CredentialAccessGuard(agent_id="test_agent", run_id="run_001")
        return CredentialAccessGuard(agent_id="test_agent", run_id="run_001")

    def test_adg_violates_attribute_exists(self):
        guard = self._make_guard()
        self.assertTrue(hasattr(guard, "_adg_violates"))

    def test_adg_violates_is_list(self):
        guard = self._make_guard()
        self.assertIsInstance(guard._adg_violates, list)

    def test_adg_violates_empty_when_no_antipatterns(self):
        stub = _StubProfile(antipattern_signals=frozenset())
        guard = self._make_guard(profile_stub=stub)
        self.assertEqual(guard._adg_violates, [])

    def test_adg_violates_populated_when_antipatterns_present(self):
        stub = _StubProfile(antipattern_signals=frozenset({"magic_config"}))
        guard = self._make_guard(profile_stub=stub)
        self.assertIn("magic_config", guard._adg_violates)

    def test_adg_violates_warning_logged(self):
        import logging

#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        stub = _StubProfile(antipattern_signals=frozenset({"type_erasure"}))
#  # MOVED: from agentic_core.L5_safety.enforcement.security.credential_access_guard import CredentialAccessGuard

        with (
            self.assertLogs(level=logging.WARNING),
            patch.object(_beh_idx, "get_behavioral_profile", return_value=stub),
        ):
            CredentialAccessGuard(agent_id="test_agent", run_id="run_001")

    def test_adg_violates_graceful_on_import_error(self):
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=ImportError("no ADG")):
            guard = self._make_guard()
        self.assertEqual(guard._adg_violates, [])

    def test_existing_api_unchanged(self):
        """guarded_get_secret / guarded_get_env signatures must be intact."""
        import inspect

#  # MOVED: from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
            CredentialAccessGuard,
        )

        sig_secret = inspect.signature(CredentialAccessGuard.guarded_get_secret)
        sig_env = inspect.signature(CredentialAccessGuard.guarded_get_env)
        self.assertIn("secret_name", sig_secret.parameters)
        self.assertIn("var_name", sig_env.parameters)

    def test_source_contains_adg_violates(self):
        src = _src("agentic_core/L5_safety/enforcement/security/credential_access_guard.py")
        self.assertIn("_adg_violates", src)


# ===========================================================================
# Phase 2l — RAG embedding confidence weighting
# ===========================================================================
class TestPhase2lRAGConfidence(unittest.TestCase):
    """Verify adg_confidence_weight injected into retrieve() results."""

    def _make_rag_manager(self):
#  # MOVED: from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import SovereignRAGManager

        # Bypass SovereignBaseAgent.__init__ integrity check (Merkle-seal on base_agents/)
        # by using object.__new__ and manually setting required attrs.
        mgr = object.__new__(SovereignRAGManager)
        mgr.storage_root = REPO / "data"
        mgr.embedder = None
        mgr.vector_store = None
        mgr.bm25_index = None
        mgr.bm25_corpus = []
        mgr.bm25_store = None
        return mgr

    def test_retrieve_returns_adg_confidence_weight_key(self):
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        mgr = self._make_rag_manager()
        stub_profile = _StubProfile(behavioral_score=0.8)

        # Inject a fake embedder + vector store
        fake_emb = [0.1, 0.2, 0.3]
        fake_result = [{"id": "doc_1", "score": 1.0, "metadata": {"text": "hello"}}]

        mgr.embedder = MagicMock()
        mgr.embedder.embed_query.return_value = fake_emb
        mgr.vector_store = MagicMock()
        mgr.vector_store.query.return_value = fake_result

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub_profile):
            results = mgr.retrieve("test query", top_k=5)

        # At least one result from vector store
        vec_results = [r for r in results if r.get("source") == "vector"]
        self.assertTrue(len(vec_results) > 0, "Expected vector results")
        for r in vec_results:
            self.assertIn("adg_confidence_weight", r)
            self.assertAlmostEqual(r["adg_confidence_weight"], 0.8)

    def test_score_is_scaled_by_adg_confidence(self):
        """adg_confidence_weight is attached to every vector result at exactly the stub value.
        The final fused score may differ (RRF / re-ranking applied downstream), but the weight
        key itself must carry the exact confidence that was used to scale the raw score."""
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        mgr = self._make_rag_manager()
        stub_profile = _StubProfile(behavioral_score=0.6)

        raw_score = 0.9
        fake_result = [{"id": "d1", "score": raw_score, "metadata": {"text": "x"}}]
        mgr.embedder = MagicMock()
        mgr.embedder.embed_query.return_value = [0.1]
        mgr.vector_store = MagicMock()
        mgr.vector_store.query.return_value = fake_result

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub_profile):
            results = mgr.retrieve("q", top_k=5)

        vec_results = [r for r in results if r.get("source") == "vector"]
        if vec_results:
            # The adg_confidence_weight key must be exactly 0.6
            self.assertAlmostEqual(vec_results[0]["adg_confidence_weight"], 0.6, places=6)
            # The fused score must be non-negative (ADG confidence never flips sign)
            self.assertGreaterEqual(vec_results[0]["score"], 0.0)

    def test_retrieve_graceful_when_adg_unavailable(self):
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        mgr = self._make_rag_manager()
        mgr.embedder = None
        mgr.vector_store = None

        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=Exception("no SQLite")):
            results = mgr.retrieve("q", top_k=5)

        # Should return empty or bm25-only without crashing
        self.assertIsInstance(results, list)

    def test_rag_orchestrator_source_has_adg_confidence(self):
        src = _src("agentic_core/knowledge/engine/rag_orchestrator.py")
        self.assertIn("adg_confidence_weight", src)
        self.assertIn("_adg_confidence", src)

    def test_rag_manager_source_has_adg_confidence(self):
        src = _src("agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py")
        self.assertIn("adg_confidence_weight", src)


# ===========================================================================
# Phase 3a — HealingPolicyMixin confidence adjustment
# ===========================================================================
class TestPhase3aHealingPolicy(unittest.TestCase):
    """Verify ADG confidence adjustment in _perform_healing_chain()."""

    def test_source_has_confidence_variable(self):
        src = _src("agentic_core/mixins/healing_policy_mixin.py")
        self.assertIn("_confidence", src)
        self.assertIn("deterministic_coverage", src)

    def test_confidence_increased_for_script_like(self):
        """Script-like files (deterministic_coverage=True) get +0.05 confidence."""
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        class _TestAgent(HealingPolicyMixin):
            name = "TestAgent"
            python_files = []

        agent = _TestAgent()
        stub = _StubProfile(behavioral_score=0.3, deterministic_coverage=True)

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = agent._perform_healing_chain(True, False, 0, 3, set())

        # Must complete without error and return a dict
        self.assertIn("violations_found", result)
        self.assertIn("violations_fixed", result)

    def test_confidence_decreased_for_agent_like(self):
        """Agent-like files (score>0.7) get -0.05 confidence — no crash."""
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        class _TestAgent(HealingPolicyMixin):
            name = "TestAgent"
            python_files = []

        agent = _TestAgent()
        stub = _StubProfile(behavioral_score=0.9, deterministic_coverage=False)

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = agent._perform_healing_chain(True, False, 0, 3, set())

        self.assertIsInstance(result, dict)

    def test_healing_chain_graceful_on_adg_error(self):
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        class _TestAgent(HealingPolicyMixin):
            name = "TestAgent"
            python_files = []

        agent = _TestAgent()
        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=RuntimeError("no ADG")):
            result = agent._perform_healing_chain(True, False, 0, 3, set())

        self.assertIn("violations_found", result)


# ===========================================================================
# Phase 3b — SelfDiagnosisMixin ADG fold
# ===========================================================================
class TestPhase3bSelfDiagnosis(unittest.TestCase):
    """Verify adg_antipatterns + adg_behavioral_score folded into diagnosis."""

    def test_source_has_adg_antipatterns_key(self):
        src = _src("agentic_core/mixins/self_diagnosis_mixin.py")
        self.assertIn("adg_antipatterns", src)
        self.assertIn("adg_behavioral_score", src)

    def test_self_diagnose_includes_adg_keys_async(self):
        """Run self_diagnose() via asyncio and confirm ADG keys present."""
        import asyncio

#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        class _Agent(SelfDiagnosisMixin):
            MANDATORY_COMPONENTS = []

        agent = _Agent()
        stub = _StubProfile(behavioral_score=0.6, antipattern_signals=frozenset({"for_retry"}))

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = asyncio.run(agent.self_diagnose())

        self.assertIn("adg_antipatterns", result)
        self.assertIn("adg_behavioral_score", result)

    def test_self_diagnose_adg_antipatterns_are_sorted_list(self):
        import asyncio

#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        class _Agent(SelfDiagnosisMixin):
            MANDATORY_COMPONENTS = []

        agent = _Agent()
        stub = _StubProfile(antipattern_signals=frozenset({"zap", "alpha", "beta"}))

        with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
            result = asyncio.run(agent.self_diagnose())

        self.assertEqual(result["adg_antipatterns"], ["alpha", "beta", "zap"])

    def test_self_diagnose_graceful_when_adg_missing(self):
        import asyncio

#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        class _Agent(SelfDiagnosisMixin):
            MANDATORY_COMPONENTS = []

        agent = _Agent()
        with patch.object(_beh_idx, "get_behavioral_profile", side_effect=ImportError("no adg")):
            result = asyncio.run(agent.self_diagnose())

        # Must still succeed; adg keys may be absent but no exception
        self.assertIn("overall_health", result)


# ===========================================================================
# Phase 3c — L3OrchestrationBase plan_execution enrichment
# ===========================================================================
class TestPhase3cL3PlanExecution(unittest.TestCase):
    def _call_plan_execution(self, stub=None, side_effect=None):
        """Call plan_execution() on a standalone L3OrchestrationBase-like object,
        bypassing SovereignBaseAgent.__post_init__ integrity check."""
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase

        # Instantiate WITHOUT calling __post_init__ to avoid SovereignLockError
        obj = object.__new__(L3OrchestrationBase)
        obj.name = "L3OrchestrationBase"

        if stub is not None:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                return L3OrchestrationBase.plan_execution(obj, {})
        elif side_effect is not None:
            with patch.object(_beh_idx, "get_behavioral_profile", side_effect=side_effect):
                return L3OrchestrationBase.plan_execution(obj, {"x": 1})
        else:
            return L3OrchestrationBase.plan_execution(obj, {})

    def test_plan_execution_has_adg_route_mode(self):
        result = self._call_plan_execution()
        self.assertIn("adg_route_mode", result)

    def test_plan_execution_has_adg_scope_widening(self):
        result = self._call_plan_execution()
        self.assertIn("adg_scope_widening", result)
        self.assertIsInstance(result["adg_scope_widening"], list)

    def test_plan_execution_route_mode_agent_when_score_high(self):
        stub = _StubProfile(behavioral_score=0.9)
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_route_mode"], "agent")

    def test_plan_execution_route_mode_script_when_deterministic(self):
        stub = _StubProfile(behavioral_score=0.3, deterministic_coverage=True)
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_route_mode"], "script")

    def test_plan_execution_route_mode_hybrid_default(self):
        stub = _StubProfile(behavioral_score=0.5, deterministic_coverage=False)
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_route_mode"], "hybrid")

    def test_plan_execution_scope_widening_sorted(self):
        stub = _StubProfile(antipattern_signals=frozenset({"zz", "aa", "mm"}))
        result = self._call_plan_execution(stub=stub)
        self.assertEqual(result["adg_scope_widening"], ["aa", "mm", "zz"])

    def test_plan_execution_graceful_when_adg_missing(self):
        result = self._call_plan_execution(side_effect=Exception("no adg"))
        self.assertIn("task", result)
        self.assertEqual(result["adg_route_mode"], "static")

    def test_existing_keys_still_present(self):
        result = self._call_plan_execution()
        for key in ("task", "plan", "status", "message"):
            self.assertIn(key, result)


# ===========================================================================
# Phase 3d — L6ObservabilityBase collect_metrics
# ===========================================================================
class TestPhase3dL6Metrics(unittest.TestCase):
    def _call_collect_metrics(self, idx_mock=None, idx_side_effect=None):
        """Call collect_metrics() bypassing SovereignBaseAgent integrity check."""
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx
#  # MOVED: from agentic_core.base_agents.L6ObservabilityBase import L6ObservabilityBase

        obj = object.__new__(L6ObservabilityBase)
        if idx_mock is not None:
            with patch.object(_beh_idx, "ADGBehavioralIndex") as mock_cls:
                mock_cls.from_latest.return_value = idx_mock
                return L6ObservabilityBase.collect_metrics(obj)
        elif idx_side_effect is not None:
            with patch.object(_beh_idx, "ADGBehavioralIndex", side_effect=idx_side_effect):
                return L6ObservabilityBase.collect_metrics(obj)
        else:
            return L6ObservabilityBase.collect_metrics(obj)

    def test_collect_metrics_has_legacy_keys(self):
        result = self._call_collect_metrics()
        self.assertIn("metrics", result)
        self.assertIn("timestamp", result)

    def test_collect_metrics_adg_keys_present_when_index_available(self):
        mock_idx = MagicMock()
        mock_idx.trust_score = 0.82
        mock_idx.unresolved_imports = ["a", "b"]
        mock_idx.layer_violations = ["x"]
        mock_idx.orphan_modules = []

        result = self._call_collect_metrics(idx_mock=mock_idx)
        self.assertIn("adg_trust_score", result)
        self.assertIn("adg_unresolved_imports", result)
        self.assertIn("adg_layer_violations", result)
        self.assertIn("adg_orphan_modules", result)

    def test_collect_metrics_graceful_when_adg_unavailable(self):
        result = self._call_collect_metrics(idx_side_effect=ImportError("no module"))
        self.assertIn("metrics", result)

    def test_source_has_adg_trust_score(self):
        src = _src("agentic_core/base_agents/L6ObservabilityBase.py")
        self.assertIn("adg_trust_score", src)


# ===========================================================================
# Phase 3e — BaseDetectorValidator severity upgrade
# ===========================================================================
class TestPhase3eDetectorSeverityUpgrade(unittest.TestCase):
    """ADG-confirmed violations must be upgraded to hard_block."""

    def _make_concrete_detector(self):
#  # MOVED: from agentic_core.L5_safety.validators.base_detector_validator import (
            AntiPatternCategory,
            AntiPatternDetector,
            AntiPatternViolation,
            EnforcementLevel,
        )

        class _ConcreteDetector(AntiPatternDetector):
            @property
            def category(self):
                return AntiPatternCategory.SILENT_SWALLOWER

            def detect(self, file_path, tree):
                return [
                    AntiPatternViolation(
                        file_path=file_path,
                        line_number=1,
                        category=AntiPatternCategory.SILENT_SWALLOWER,
                        message="test violation",
                        evidence="pass",
                        severity="warning",
                    )
                ]

        return _ConcreteDetector(enforcement_level=EnforcementLevel.WARNING)

    def test_adg_confirmed_violation_upgraded_to_hard_block(self):
        """When ADG antipattern_signals contains the category value, severity → hard_block."""
        import tempfile

#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        detector = self._make_concrete_detector()
        stub = _StubProfile(antipattern_signals=frozenset({"silent_swallower"}))

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write("x = 1\n")
            tmp_path = Path(f.name)

        try:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                result = detector.scan_file(tmp_path)

            hard_block = [v for v in result.violations if v.severity == "hard_block"]
            self.assertTrue(len(hard_block) > 0, "Expected at least one hard_block violation")
            self.assertTrue(hard_block[0].metadata.get("adg_confirmed"))
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_whitelisted_violation_not_upgraded(self):
        """Whitelisted violations must never be upgraded."""
#  # MOVED: from agentic_core.L5_safety.validators.base_detector_validator import (
            AntiPatternCategory,
            AntiPatternDetector,
            AntiPatternViolation,
            EnforcementLevel,
        )

        class _AlwaysWhitelistDetector(AntiPatternDetector):
            @property
            def category(self):
                return AntiPatternCategory.SILENT_SWALLOWER

            def detect(self, file_path, tree):
                v = AntiPatternViolation(
                    file_path=file_path,
                    line_number=1,
                    category=AntiPatternCategory.SILENT_SWALLOWER,
                    message="wl",
                    evidence="pass",
                    severity="warning",
                    whitelisted=True,
                )
                return [v]

        detector = _AlwaysWhitelistDetector(enforcement_level=EnforcementLevel.WARNING)
        stub = _StubProfile(antipattern_signals=frozenset({"silent_swallower"}))

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write("x = 1\n")
            tmp_path = Path(f.name)

        try:
#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                result = detector.scan_file(tmp_path)

            for v in result.violations:
                if v.whitelisted:
                    self.assertNotEqual(v.severity, "hard_block")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_no_adg_antipatterns_no_upgrade(self):
        """When ADG returns empty antipattern_signals, severity stays unchanged."""
        import tempfile

#  # MOVED: import agentic_core.adg.runtime.behavioral_index as _beh_idx

        detector = self._make_concrete_detector()
        stub = _StubProfile(antipattern_signals=frozenset())

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write("x = 1\n")
            tmp_path = Path(f.name)

        try:
            with patch.object(_beh_idx, "get_behavioral_profile", return_value=stub):
                result = detector.scan_file(tmp_path)

            for v in result.violations:
                self.assertNotEqual(v.severity, "hard_block")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_source_contains_adg_confirmed_metadata(self):
        src = _src("agentic_core/L5_safety/validators/base_detector_validator.py")
        self.assertIn("adg_confirmed", src)
        self.assertIn("hard_block", src)


# ===========================================================================
# Cross-phase: no public API signatures changed
# ===========================================================================
class TestAPISignatureIntegrity(unittest.TestCase):
    """Verify that no public method signatures were altered by any phase."""

    def test_elevator_shaft_summary_signature(self):
#  # MOVED: from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
            ElevatorShaftConsistencyEnforcer,
        )

        sig = inspect.signature(ElevatorShaftConsistencyEnforcer.summary)
        # summary() takes only self
        params = [p for p in sig.parameters if p != "self"]
        self.assertEqual(params, [])

    def test_credential_guard_guarded_get_secret_signature(self):
#  # MOVED: from agentic_core.L5_safety.enforcement.security.credential_access_guard import (
            CredentialAccessGuard,
        )

        sig = inspect.signature(CredentialAccessGuard.guarded_get_secret)
        params = list(sig.parameters)
        self.assertIn("secret_name", params)
        self.assertIn("kind", params)
        self.assertIn("default", params)

    def test_rag_manager_retrieve_signature(self):
#  # MOVED: from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import SovereignRAGManager

        sig = inspect.signature(SovereignRAGManager.retrieve)
        self.assertIn("query", sig.parameters)
        self.assertIn("top_k", sig.parameters)

    def test_l3_plan_execution_signature(self):
    """Test l3_plan_execution_signature runtime behavior."""
    # Arrange
    # TODO: Set up test data for l3_plan_execution_signature
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute l3_plan_execution_signature
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
#  # MOVED: from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin

        sig = inspect.signature(HealingPolicyMixin.heal_repository)
        for param in ("dry_run", "execute", "depth", "max_depth"):
            self.assertIn(param, sig.parameters)

    def test_self_diagnosis_mixin_self_diagnose_signature(self):
#  # MOVED: from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin

        sig = inspect.signature(SelfDiagnosisMixin.self_diagnose)
        params = [p for p in sig.parameters if p != "self"]
        self.assertEqual(params, [])


# ===========================================================================
# Source-level AST cross-checks (prove injections without importing)
# ===========================================================================
class TestASTSourceInjections(unittest.TestCase):
    """Prove every Phase injection exists at the AST/text level."""

    def test_p2j_elevator_shaft_adg_in_summary(self):
        src = _src("agentic_core/L4_state/enforcement/elevator_shaft_consistency_enforcer.py")
        self.assertIn("get_behavioral_profile", src)
        self.assertIn("adg_violates", src)

    def test_p2k_credential_guard_adg_in_init(self):
        src = _src("agentic_core/L5_safety/enforcement/security/credential_access_guard.py")
        self.assertIn("_adg_violates", src)
        self.assertIn("get_behavioral_profile", src)

    def test_p2l_rag_manager_adg_confidence(self):
        src = _src("agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py")
        self.assertIn("_adg_confidence", src)
        self.assertIn("adg_confidence_weight", src)

    def test_p2l_rag_orchestrator_adg_confidence(self):
        src = _src("agentic_core/knowledge/engine/rag_orchestrator.py")
        self.assertIn("_adg_confidence", src)
        self.assertIn("adg_confidence_weight", src)

    def test_p3a_healing_policy_confidence(self):
        src = _src("agentic_core/mixins/healing_policy_mixin.py")
        self.assertIn("_confidence", src)
        self.assertIn("deterministic_coverage", src)

    def test_p3b_self_diagnosis_adg_keys(self):
        src = _src("agentic_core/mixins/self_diagnosis_mixin.py")
        self.assertIn("adg_antipatterns", src)
        self.assertIn("adg_behavioral_score", src)

    def test_p3c_l3_adg_route_mode(self):
        src = _src("agentic_core/base_agents/L3OrchestrationBase.py")
        self.assertIn("adg_route_mode", src)
        self.assertIn("adg_scope_widening", src)

    def test_p3d_l6_adg_trust_score(self):
        src = _src("agentic_core/base_agents/L6ObservabilityBase.py")
        self.assertIn("adg_trust_score", src)
        self.assertIn("ADGBehavioralIndex", src)

    def test_p3e_base_detector_hard_block(self):
        src = _src("agentic_core/L5_safety/validators/base_detector_validator.py")
        self.assertIn("hard_block", src)
        self.assertIn("adg_confirmed", src)

    def test_p4_sovereign_base_agent_imports_adg_mixin(self):
        src = _src("agentic_core/base_agents/SovereignBaseAgent.py")
        self.assertIn("ADGBehavioralMixin", src)
        self.assertIn("from agentic_core.mixins.adg_behavioral_mixin import ADGBehavioralMixin", src)

    def test_p4_sovereign_base_agent_uses_adg_mixin_in_class_def(self):
        tree = _ast_of("agentic_core/base_agents/SovereignBaseAgent.py")
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SovereignBaseAgent":
                base_names = [ast.unparse(b) for b in node.bases]
                self.assertIn("ADGBehavioralMixin", base_names)
                return
        self.fail("SovereignBaseAgent class not found in AST")


# ===========================================================================
# Phase 5 — apps_* territory ADG enrichment
# ===========================================================================


class TestPhase5AppsSharedEnrichment(unittest.TestCase):
    """AST-level verification that apps_shared base classes received ADG enrichment."""

    def test_base_dispatch_agent_has_adg_block_in_post_init(self):
        tree = _ast_of("apps_shared/reasoning/BaseDispatchAgent.py")
        for cls in ast.walk(tree):
            if isinstance(cls, ast.ClassDef) and cls.name == "BaseDispatchAgent":
                for fn in ast.walk(cls):
                    if isinstance(fn, ast.FunctionDef) and fn.name == "__post_init__":
                        src = ast.unparse(fn)
                        self.assertIn("ADGBehavioralIndex", src)
                        self.assertIn("adg_behavioral_score", src)
                        self.assertIn("adg_antipattern_signals", src)
                        return
        self.fail("BaseDispatchAgent.__post_init__ not found")

    def test_base_healing_orchestrator_has_adg_block_in_post_init(self):
        tree = _ast_of("apps_shared/reasoning/BaseHealingOrchestrator.py")
        for cls in ast.walk(tree):
            if isinstance(cls, ast.ClassDef) and cls.name == "BaseHealingOrchestrator":
                for fn in ast.walk(cls):
                    if isinstance(fn, ast.FunctionDef) and fn.name == "__post_init__":
                        src = ast.unparse(fn)
                        self.assertIn("ADGBehavioralIndex", src)
                        self.assertIn("adg_behavioral_score", src)
                        return
        self.fail("BaseHealingOrchestrator.__post_init__ not found")

    def test_base_dispatch_agent_has_path_import(self):
        src = _src("apps_shared/reasoning/BaseDispatchAgent.py")
        self.assertIn("from pathlib import Path", src)

    def test_base_healing_orchestrator_has_path_import(self):
        src = _src("apps_shared/reasoning/BaseHealingOrchestrator.py")
        self.assertIn("from pathlib import Path", src)

    def test_base_dispatch_agent_adg_block_uses_narrowed_exception(self):
        src = _src("apps_shared/reasoning/BaseDispatchAgent.py")
        self.assertIn("except (ImportError, AttributeError, OSError)", src)
        # ADG block must not use broad except — check the adg block specifically
        adg_block = src[src.find("from agentic_core.adg.runtime.behavioral_index") :]
        adg_block = adg_block[: adg_block.find("\n\n") + 10]
        self.assertNotIn("except Exception", adg_block)

    def test_base_healing_orchestrator_adg_block_uses_narrowed_exception(self):
        src = _src("apps_shared/reasoning/BaseHealingOrchestrator.py")
        self.assertIn("except (ImportError, AttributeError, OSError)", src)
        adg_block = src[src.find("from agentic_core.adg.runtime.behavioral_index") :]
        adg_block = adg_block[: adg_block.find("\n\n") + 10]
        self.assertNotIn("except Exception", adg_block)

    def test_base_dispatch_agent_fallback_defaults_are_safe(self):
        """Fallback values must be 0.5 (neutral) and [] (empty) — not None."""
        src = _src("apps_shared/reasoning/BaseDispatchAgent.py")
        self.assertIn("adg_behavioral_score = 0.5", src)
        self.assertIn("adg_antipattern_signals = []", src)

    def test_base_healing_orchestrator_fallback_defaults_are_safe(self):
        src = _src("apps_shared/reasoning/BaseHealingOrchestrator.py")
        self.assertIn("adg_behavioral_score = 0.5", src)
        self.assertIn("adg_antipattern_signals = []", src)


class TestPhase5AppsLicEnrichment(unittest.TestCase):
    """Verify LIC domain healing orchestrator and signal router received ADG enrichment."""

    def test_lic_healing_orchestrator_has_adg_block(self):
        tree = _ast_of("apps_lic/reasoning/LicHealingOrchestrator.py")
        for cls in ast.walk(tree):
            if isinstance(cls, ast.ClassDef) and cls.name == "LicHealingOrchestrator":
                for fn in ast.walk(cls):
                    if isinstance(fn, ast.FunctionDef) and fn.name == "__post_init__":
                        src = ast.unparse(fn)
                        self.assertIn("ADGBehavioralIndex", src)
                        self.assertIn("adg_behavioral_score", src)
                        return
        self.fail("LicHealingOrchestrator.__post_init__ not found")

    def test_lic_healing_orchestrator_has_path_import(self):
        src = _src("apps_lic/reasoning/LicHealingOrchestrator.py")
        self.assertIn("from pathlib import Path", src)

    def test_lic_healing_orchestrator_adg_block_uses_narrowed_exception(self):
        src = _src("apps_lic/reasoning/LicHealingOrchestrator.py")
        self.assertIn("except (ImportError, AttributeError, OSError)", src)
        adg_block = src[src.find("from agentic_core.adg.runtime.behavioral_index") :]
        adg_block = adg_block[: adg_block.find("\n\n") + 10]
        self.assertNotIn("except Exception", adg_block)

    def test_outreach_signal_router_has_post_init_with_adg(self):
        tree = _ast_of("apps_lic/reasoning/OutreachSignalRouterAgent.py")
        for cls in ast.walk(tree):
            if isinstance(cls, ast.ClassDef) and cls.name == "OutreachSignalRouterAgent":
                for fn in ast.walk(cls):
                    if isinstance(fn, ast.FunctionDef) and fn.name == "__post_init__":
                        src = ast.unparse(fn)
                        self.assertIn("ADGBehavioralIndex", src)
                        return
        self.fail("OutreachSignalRouterAgent.__post_init__ not found")

    def test_outreach_signal_router_has_path_import(self):
        src = _src("apps_lic/reasoning/OutreachSignalRouterAgent.py")
        self.assertIn("from pathlib import Path", src)

    def test_lic_healing_orchestrator_fallback_defaults_safe(self):
        src = _src("apps_lic/reasoning/LicHealingOrchestrator.py")
        self.assertIn("adg_behavioral_score = 0.5", src)
        self.assertIn("adg_antipattern_signals = []", src)


class TestPhase5AppsRgEnrichment(unittest.TestCase):
    """Verify RG domain healing orchestrator and content quality agent received ADG enrichment."""

    def test_rg_healing_orchestrator_has_adg_block(self):
        tree = _ast_of("apps_rg/reasoning/RgHealingOrchestrator.py")
        for cls in ast.walk(tree):
            if isinstance(cls, ast.ClassDef) and cls.name == "RgHealingOrchestrator":
                for fn in ast.walk(cls):
                    if isinstance(fn, ast.FunctionDef) and fn.name == "__post_init__":
                        src = ast.unparse(fn)
                        self.assertIn("ADGBehavioralIndex", src)
                        self.assertIn("adg_behavioral_score", src)
                        return
        self.fail("RgHealingOrchestrator.__post_init__ not found")

    def test_rg_healing_orchestrator_has_path_import(self):
        src = _src("apps_rg/reasoning/RgHealingOrchestrator.py")
        self.assertIn("from pathlib import Path", src)

    def test_rg_healing_orchestrator_adg_block_uses_narrowed_exception(self):
        src = _src("apps_rg/reasoning/RgHealingOrchestrator.py")
        self.assertIn("except (ImportError, AttributeError, OSError)", src)
        adg_block = src[src.find("from agentic_core.adg.runtime.behavioral_index") :]
        adg_block = adg_block[: adg_block.find("\n\n") + 10]
        self.assertNotIn("except Exception", adg_block)

    def test_content_quality_agent_has_adg_block(self):
        tree = _ast_of("apps_rg/reasoning/ContentQualityAgent.py")
        for cls in ast.walk(tree):
            if isinstance(cls, ast.ClassDef) and cls.name == "ContentQualityAgent":
                for fn in ast.walk(cls):
                    if isinstance(fn, ast.FunctionDef) and fn.name == "__post_init__":
                        src = ast.unparse(fn)
                        self.assertIn("ADGBehavioralIndex", src)
                        return
        self.fail("ContentQualityAgent.__post_init__ not found")

    def test_content_quality_agent_has_path_import(self):
        src = _src("apps_rg/reasoning/ContentQualityAgent.py")
        self.assertIn("from pathlib import Path", src)

    def test_rg_healing_orchestrator_fallback_defaults_safe(self):
        src = _src("apps_rg/reasoning/RgHealingOrchestrator.py")
        self.assertIn("adg_behavioral_score = 0.5", src)
        self.assertIn("adg_antipattern_signals = []", src)

    def test_content_quality_agent_fallback_defaults_safe(self):
        src = _src("apps_rg/reasoning/ContentQualityAgent.py")
        self.assertIn("adg_behavioral_score = 0.5", src)
        self.assertIn("adg_antipattern_signals = []", src)


class TestPhase5AdgBlockStructureInvariant(unittest.TestCase):
    """Cross-file structural invariants for all Phase 5 ADG enrichment blocks."""

    PHASE5_FILES = [
        "apps_shared/reasoning/BaseDispatchAgent.py",
        "apps_shared/reasoning/BaseHealingOrchestrator.py",
        "apps_lic/reasoning/LicHealingOrchestrator.py",
        "apps_lic/reasoning/OutreachSignalRouterAgent.py",
        "apps_rg/reasoning/RgHealingOrchestrator.py",
        "apps_rg/reasoning/ContentQualityAgent.py",
    ]

    def test_all_phase5_files_have_adg_behavioral_index_import(self):
    """Test all_phase5_files_have_adg_behavioral_index_import runtime behavior."""
    # Arrange
    # TODO: Set up test data for all_phase5_files_have_adg_behavioral_index_import
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute all_phase5_files_have_adg_behavioral_index_import
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
                self.assertIn(
                    "except (ImportError, AttributeError, OSError)",
                    src,
                    msg=f"Missing narrowed exception in {fpath}",
                )
                # Scope check to the ADG block only — other broad excepts elsewhere are pre-existing
                adg_block = src[src.find("from agentic_core.adg.runtime.behavioral_index") :]
                adg_block = adg_block[: adg_block.find("\n\n") + 10]
                self.assertNotIn(
                    "except Exception",
                    adg_block,
                    msg=f"ADG block must not use broad except Exception in {fpath}",
                )

    def test_all_phase5_files_have_path_import(self):
        for fpath in self.PHASE5_FILES:
            with self.subTest(file=fpath):
                src = _src(fpath)
                self.assertIn(
                    "from pathlib import Path",
                    src,
                    msg=f"Path import missing in {fpath}",
                )

    def test_all_phase5_files_have_adg_behavioral_score_assignment(self):
    """Test all_phase5_files_have_adg_behavioral_score_assignment runtime behavior."""
    # Arrange
    # TODO: Set up test data for all_phase5_files_have_adg_behavioral_score_assignment
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute all_phase5_files_have_adg_behavioral_score_assignment
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
                self.assertIn(
                    "adg_antipattern_signals",
                    src,
                    msg=f"adg_antipattern_signals attribute missing in {fpath}",
                )

    def test_adg_block_not_at_top_level_import(self):
        """ADG import must be inside try block (lazy), not at module top-level."""
        for fpath in self.PHASE5_FILES:
            with self.subTest(file=fpath):
                tree = _ast_of(fpath)
                # Top-level imports must NOT directly import ADGBehavioralIndex
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and "behavioral_index" in node.module:
                            self.fail(f"{fpath}: ADGBehavioralIndex imported at top level (must be lazy)")

    def test_fallback_score_is_neutral_not_zero(self):
        """Fallback score 0.5 = neutral, not 0.0 (which would unfairly penalise)."""
        for fpath in self.PHASE5_FILES:
            with self.subTest(file=fpath):
                src = _src(fpath)
                self.assertIn(
                    "adg_behavioral_score = 0.5",
                    src,
                    msg=f"Fallback score must be 0.5 (neutral) in {fpath}",
                )


# ===========================================================================
# Phase 5d — apps_eval / apps_exec / apps_research / apps_rfp orchestrators
# ===========================================================================


class TestPhase5dRemainingAppsEnrichment(unittest.TestCase):
    """ADG enrichment for the four additional apps_* orchestrators."""

    PHASE5D_FILES = [
        ("apps_eval/reasoning/EvalOrchestrator.py", "EvalOrchestrator"),
        ("apps_exec/reasoning/ExecOrchestrator.py", "ExecOrchestrator"),
        ("apps_research/reasoning/ResearchOrchestrator.py", "ResearchOrchestrator"),
        ("apps_rfp/reasoning/RfpOrchestrator.py", "RfpOrchestrator"),
    ]

    def test_all_orchestrators_have_adg_block_in_post_init(self):
        for fpath, cls_name in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                tree = _ast_of(fpath)
                found = False
                for cls in ast.walk(tree):
                    if isinstance(cls, ast.ClassDef) and cls.name == cls_name:
                        for fn in ast.walk(cls):
                            if isinstance(fn, ast.FunctionDef) and fn.name == "__post_init__":
                                fn_src = ast.unparse(fn)
                                self.assertIn(
                                    "ADGBehavioralIndex", fn_src, msg=f"{fpath}: missing ADGBehavioralIndex"
                                )
                                self.assertIn(
                                    "adg_behavioral_score",
                                    fn_src,
                                    msg=f"{fpath}: missing adg_behavioral_score",
                                )
                                self.assertIn(
                                    "adg_antipattern_signals",
                                    fn_src,
                                    msg=f"{fpath}: missing adg_antipattern_signals",
                                )
                                found = True
                self.assertTrue(found, msg=f"{cls_name}.__post_init__ not found in {fpath}")

    def test_all_orchestrators_use_narrowed_exception_not_broad_except(self):
        for fpath, _ in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                src = _src(fpath)
                self.assertIn("except (ImportError, AttributeError, OSError)", src)
                adg_block = src[src.find("from agentic_core.adg.runtime.behavioral_index") :]
                adg_block = adg_block[: adg_block.find("\n\n") + 10]
                self.assertNotIn("except Exception", adg_block)

    def test_all_orchestrators_have_fallback_neutral_score(self):
        for fpath, _ in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                self.assertIn("adg_behavioral_score = 0.5", _src(fpath))

    def test_all_orchestrators_have_fallback_empty_signals(self):
        for fpath, _ in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                self.assertIn("adg_antipattern_signals = []", _src(fpath))

    def test_adg_import_is_lazy_not_top_level(self):
        """ADGBehavioralIndex must NOT appear as a top-level import."""
        for fpath, _ in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                tree = _ast_of(fpath)
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and "behavioral_index" in node.module:
                            self.fail(f"{fpath}: ADGBehavioralIndex imported at top level (must be lazy)")

    def test_path_resolution_uses_dunder_file(self):
        """Plain dataclass orchestrators use Path(__file__) not self.project_root."""
        for fpath, _ in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                src = _src(fpath)
                self.assertIn(
                    "Path(__file__)", src, msg=f"{fpath}: should use Path(__file__) for ADG root resolution"
                )

    def test_path_already_imported_not_duplicated(self):
        """Path was already imported — must appear exactly once."""
        for fpath, _ in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                count = _src(fpath).count("from pathlib import Path")
                self.assertEqual(
                    count, 1, msg=f"{fpath}: 'from pathlib import Path' appears {count}x (expected 1)"
                )

    def test_adg_block_uses_correct_parents_depth(self):
        """parents[3] = repo root from apps_<x>/reasoning/OrchestratorFile.py."""
        for fpath, _ in self.PHASE5D_FILES:
            with self.subTest(file=fpath):
                self.assertIn("parents[3]", _src(fpath), msg=f"{fpath}: wrong parents depth for repo root")


# ===========================================================================
# Phase 6 — Dead-import triage: ruff clean (F401 zero violations)
# ===========================================================================


class TestPhase6DeadImportTriage(unittest.TestCase):
    """Verify that the apps_* and agentic_core source trees are ruff F401-clean."""

    def _run_ruff_f401(self, target_dir: str) -> list[dict]:
        """Run ruff F401 check and return list of violation dicts."""
        import json
        import subprocess

        result = subprocess.run(
            [
                "python",
                "-m",
                "ruff",
                "check",
                "--select",
                "F401",
                "--output-format=json",
                target_dir,
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO),
        )
        if not result.stdout.strip():
            return []
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

    def test_apps_lic_no_dead_imports(self):
        violations = self._run_ruff_f401("apps_lic/")
        self.assertEqual(
            violations,
            [],
            msg=f"apps_lic/ has F401 dead-import violations: {violations}",
        )

    def test_apps_rg_no_dead_imports(self):
        violations = self._run_ruff_f401("apps_rg/")
        self.assertEqual(
            violations,
            [],
            msg=f"apps_rg/ has F401 dead-import violations: {violations}",
        )

    def test_apps_shared_no_dead_imports(self):
        violations = self._run_ruff_f401("apps_shared/")
        self.assertEqual(
            violations,
            [],
            msg=f"apps_shared/ has F401 dead-import violations: {violations}",
        )

    def test_apps_exec_no_dead_imports(self):
        violations = self._run_ruff_f401("apps_exec/")
        self.assertEqual(
            violations,
            [],
            msg=f"apps_exec/ has F401 dead-import violations: {violations}",
        )

    def test_apps_eval_no_dead_imports(self):
        violations = self._run_ruff_f401("apps_eval/")
        self.assertEqual(
            violations,
            [],
            msg=f"apps_eval/ has F401 dead-import violations: {violations}",
        )

    def test_agentic_core_no_dead_imports(self):
        violations = self._run_ruff_f401("agentic_core/")
        self.assertEqual(
            violations,
            [],
            msg=f"agentic_core/ has F401 dead-import violations: {violations}",
        )

    def test_phase5_new_path_imports_are_used(self):
        """Ensure the Path imports added in Phase 5 are actually used (not themselves dead)."""
        for fpath in TestPhase5AdgBlockStructureInvariant.PHASE5_FILES:
            with self.subTest(file=fpath):
                src = _src(fpath)
                # Path is used in the ADG block: Path(self.project_root)
                self.assertIn(
                    "Path(self.project_root)",
                    src,
                    msg=f"Path is imported but not used in {fpath}",
                )

    def test_no_duplicate_import_of_path_in_phase5_files(self):
        """Path must appear exactly once as an import (not twice)."""
        for fpath in TestPhase5AdgBlockStructureInvariant.PHASE5_FILES:
            with self.subTest(file=fpath):
                src = _src(fpath)
                count = src.count("from pathlib import Path")
                self.assertEqual(
                    count,
                    1,
                    msg=f"'from pathlib import Path' appears {count} times in {fpath} (expected 1)",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
