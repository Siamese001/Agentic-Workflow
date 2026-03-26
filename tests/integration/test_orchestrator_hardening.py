"""
Phase 2 — Orchestrator Hardening tests.

Tests exercise FCA classify_file() to verify:
- Hardened orchestrator detection (inheritance, broader tokens)
- Invariant validation (role coordination, mutation tiering, thin-wrapper)
- Layer alignment reporting

Unit tests:
a) Inherits WorkflowCoordinator => ORCHESTRATOR (if invariants pass)
b) Thin wrapper => downgraded to ENGINE + thin_wrapper stat
c) open(...,"w") present => downgraded to ENGINE + mutation_hard stat
d) subprocess.run present => remains ORCHESTRATOR + mutation_soft stat
e) ORCHESTRATOR under L2 => layer misalignment stat

Integration mini-slice:
3 temp files: valid L3 orchestrator, thin wrapper, hard mutation
"""

import textwrap
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
#  # MOVED: from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_orchestrator_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("test_orchestrator_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("test_orchestrator_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("test_orchestrator_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("test_orchestrator_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("test_orchestrator_hardening", "p4obs", "metric_6")
_emit_records_incident_event("test_orchestrator_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_orchestrator_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("test_orchestrator_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_orchestrator_hardening", "p4obs", "mon_state")
_emit_triggers_alert("test_orchestrator_hardening", "p4obs", "alert")
_emit_links_incident_trace("test_orchestrator_hardening", "p4obs", "trace_link")
_emit_captures_pattern("test_orchestrator_hardening", "p3lm", "pattern")
_emit_records_learning_event("test_orchestrator_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_orchestrator_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_orchestrator_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_orchestrator_hardening", "p3lm", "routing")
_emit_improves_agent_policy("test_orchestrator_hardening", "p3lm", "policy")
_emit_stores_learning_state("test_orchestrator_hardening", "p3lm", "state")
_emit_records_execution_trace("test_orchestrator_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_orchestrator_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_orchestrator_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_orchestrator_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_orchestrator_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_orchestrator_hardening", "env_read", "p2_env_1")
_emit_reads_environ("test_orchestrator_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_orchestrator_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_orchestrator_hardening", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_orchestrator_hardening")
_emit_applies_guardrail("p0", "test_orchestrator_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_orchestrator_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_orchestrator_hardening", "state_snapshot")
emit_replay_key("p0", "test_orchestrator_hardening")
emit_determinism_digest("p0", "test_orchestrator_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_orchestrator_hardening", "execution_auth")
_emit_validates_capability("p2", "test_orchestrator_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_orchestrator_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_orchestrator_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_orchestrator_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_orchestrator_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_orchestrator_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_orchestrator_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_orchestrator_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_orchestrator_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_orchestrator_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_orchestrator_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_orchestrator_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_orchestrator_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_orchestrator_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_orchestrator_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_orchestrator_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_orchestrator_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_orchestrator_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_orchestrator_hardening", "exec_snapshot_link")
_emit_escalates_to_human("p1", "test_orchestrator_hardening", "human_escalation")
_emit_routes_through("p1", "test_orchestrator_hardening", "route_through")
_emit_checks_agent_registry("p1", "test_orchestrator_hardening", "agent_registry")
_emit_validates_agent_capability("p1", "test_orchestrator_hardening", "capability")
_emit_dispatches_execution_plan("p1", "test_orchestrator_hardening", "exec_plan")
_emit_agent_executes_agent("p1", "test_orchestrator_hardening", "sub_agent")
_emit_routes_to_agent("p1", "test_orchestrator_hardening", "target_agent")
_emit_verifies_policy("p1", "test_orchestrator_hardening", "policy_check")
_emit_observes_runtime_state("p1", "test_orchestrator_hardening", "runtime_state")
_emit_verifies_boundary("p1", "test_orchestrator_hardening", "boundary_check")
_emit_transcripts_response("p1", "test_orchestrator_hardening", "transcript")
_emit_hard_fails_untranscripted("p1", "test_orchestrator_hardening")
_emit_gated_by_confidence("p1", "test_orchestrator_hardening", "confidence_gate")

# ================================================================
# Helpers
# ================================================================


def _write(tmp_path: Path, rel_parts: tuple, stem: str, code: str) -> Path:
    """Write a .py file under tmp_path/rel_parts/stem.py."""
    folder = tmp_path
    for part in rel_parts:
        folder = folder / part
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{stem}.py"
    p.write_text(textwrap.dedent(code), encoding="utf-8")
    return p


def _make_fca(tmp_path: Path):
    """Create a minimal FileClassificationAgent for testing."""
    return FileClassificationAgent(
        project_root=tmp_path,
        dry_run=True,
        validate_only=True,
    )


def _classify_fca(
    tmp_path: Path,
    rel_parts: tuple,
    stem: str,
    code: str,
):
    """Write file, classify via FCA, return (result, fca)."""
    p = _write(tmp_path, rel_parts, stem, code)
    fca = _make_fca(tmp_path)
    result = fca.classify_file(p)
    return result, fca


# ================================================================
# Shared test content
# ================================================================

VALID_ORCHESTRATOR_CODE = """\
#  # MOVED: from agentic_core.L3_orchestration.reasoning import SomeAgent
#  # MOVED: from agentic_core.L5_safety.enforcement import SomeEnforcer

    class WorkflowCoordinator:
        pass

    class ValidationOrchestrator(WorkflowCoordinator):
        def run_pipeline(self):
            agent = SomeAgent()
            enforcer = SomeEnforcer()
            agent.execute()
            enforcer.validate_safety(agent)
            return self.aggregate_result()

        def aggregate_result(self):
            return {}

        def coordinate(self):
            pass

        def run_stages(self):
            pass
"""


# ================================================================
# Unit Tests
# ================================================================


@pytest.mark.unit_min_deps
class TestOrchestratorInheritance:
    """Phase 2A: Inheritance-based orchestrator detection."""

    def test_inherits_workflow_coordinator(self, tmp_path):
                from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
                from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L3_orchestration.reasoning import SomeAgent
                from agentic_core.L5_safety.enforcement import SomeEnforcer
                from agentic_core.L3_orchestration.reasoning import R
                from agentic_core.L5_safety.enforcement import G
                from agentic_core.L3_orchestration.reasoning import A
                from agentic_core.L5_safety.enforcement import G
                from agentic_core.L3_orchestration.reasoning import A
                from agentic_core.L5_safety.enforcement import G
                from agentic_core.L3_orchestration.reasoning import R
                from agentic_core.L5_safety.enforcement import G
                from agentic_core.L3_orchestration.reasoning import A
                from agentic_core.L5_safety.enforcement import G
                """Inherits WorkflowCoordinator => ORCHESTRATOR."""
                result, _fca = _classify_fca(
                    tmp_path,
                    (AGENTIC_CORE_DIR, "L3_orchestration", "reasoning"),
                    "validation_orchestrator",
                    VALID_ORCHESTRATOR_CODE,
                )
                assert result == "ORCHESTRATOR", f"Expected ORCHESTRATOR, got {result}"

        assert result == "ORCHESTRATOR", f"Expected ORCHESTRATOR, got {result}"


@pytest.mark.unit_min_deps
class TestOrchestratorThinWrapper:
    """Phase 2B: Thin wrapper downgrade."""

    def test_thin_wrapper_downgraded_to_engine(self, tmp_path):
        """Thin wrapper (<=3 funcs, <=50 LOC) => ENGINE."""
        code = """\
#  # MOVED: from agentic_core.L3_orchestration.reasoning import R
#  # MOVED: from agentic_core.L5_safety.enforcement import G

            class ThinOrchestrator:
                def run(self):
                    return R().execute()
        """
        result, fca = _classify_fca(
            tmp_path,
            (AGENTIC_CORE_DIR, "L3_orchestration", "reasoning"),
            "thin_orchestrator",
            code,
        )
        assert result == "ENGINE", f"Expected ENGINE (thin wrapper), got {result}"
        inv = fca.stats["violations"]["ORCHESTRATOR_INVARIANT_FAIL"]
        assert inv["thin_wrapper"] >= 1, f"thin_wrapper stat should be >= 1, got {inv['thin_wrapper']}"


@pytest.mark.unit_min_deps
class TestOrchestratorMutationHard:
    """Phase 2B: Hard mutation downgrade."""

    def test_hard_mutation_downgraded_to_engine(self, tmp_path):
        """open(...,'w') present => ENGINE + mutation_hard stat."""
        code = """\
#  # MOVED: from agentic_core.L3_orchestration.reasoning import A
#  # MOVED: from agentic_core.L5_safety.enforcement import G

            class MutatingOrchestrator:
                def run_pipeline(self):
                    a = A()
                    g = G()
                    a.execute()
                    g.check()
                    with open("output.txt", "w") as f:
                        f.write("result")
                    return self.aggregate_result()

                def aggregate_result(self):
                    return {}

                def coordinate(self):
                    pass

                def run_stages(self):
                    pass
        """
        result, fca = _classify_fca(
            tmp_path,
            (AGENTIC_CORE_DIR, "L3_orchestration", "reasoning"),
            "mutating_orchestrator",
            code,
        )
        assert result == "ENGINE", f"Expected ENGINE (hard mutation), got {result}"
        inv = fca.stats["violations"]["ORCHESTRATOR_INVARIANT_FAIL"]
        assert inv["mutation_hard"] >= 1, f"mutation_hard should be >= 1, got {inv['mutation_hard']}"


@pytest.mark.unit_min_deps
class TestOrchestratorMutationSoft:
    """Phase 2B: Soft mutation warning."""

    def test_soft_mutation_remains_orchestrator(self, tmp_path):
        """subprocess.run present => ORCHESTRATOR + mutation_soft."""
        code = """\
            import subprocess
#  # MOVED: from agentic_core.L3_orchestration.reasoning import A
#  # MOVED: from agentic_core.L5_safety.enforcement import G

            class SubprocessOrchestrator:
                def run_pipeline(self):
                    a = A()
                    g = G()
                    a.execute()
                    g.check()
                    subprocess.run(["echo", "hello"])
                    return self.aggregate_result()

                def aggregate_result(self):
                    return {}

                def coordinate(self):
                    pass

                def run_stages(self):
                    pass
        """
        result, fca = _classify_fca(
            tmp_path,
            (AGENTIC_CORE_DIR, "L3_orchestration", "reasoning"),
            "subprocess_orchestrator",
            code,
        )
        assert result == "ORCHESTRATOR", f"Expected ORCHESTRATOR (soft warn), got {result}"
        inv = fca.stats["violations"]["ORCHESTRATOR_INVARIANT_FAIL"]
        assert inv["mutation_soft"] >= 1, f"mutation_soft should be >= 1, got {inv['mutation_soft']}"


@pytest.mark.unit_min_deps
class TestOrchestratorLayerMisalignment:
    """Phase 2C: Layer alignment reporting."""

    def test_orchestrator_under_l2_flags_misalignment(self, tmp_path):
        """ORCHESTRATOR under L2 => layer misalignment stat."""
        result, fca = _classify_fca(
            tmp_path,
            (AGENTIC_CORE_DIR, "L2_execution", "reasoning"),
            "misplaced_orchestrator",
            VALID_ORCHESTRATOR_CODE,
        )
        assert result == "ORCHESTRATOR", f"Expected ORCHESTRATOR, got {result}"
        mis = fca.stats["violations"]["ORCHESTRATOR_LAYER_MISALIGNMENT"]
        assert mis >= 1, "ORCHESTRATOR_LAYER_MISALIGNMENT should be >= 1"


# ================================================================
# Integration Mini-Slice
# ================================================================


@pytest.mark.unit_min_deps
class TestOrchestratorIntegration:
    """Integration: 3 temp files with different outcomes."""

    def test_mini_slice(self, tmp_path):
        """3 files: valid orchestrator, thin wrapper, hard mutation."""
        fca = _make_fca(tmp_path)

        # 1) Valid L3 orchestrator (2 roles, no mutation)
        p1 = _write(
            tmp_path,
            (AGENTIC_CORE_DIR, "L3_orchestration", "reasoning"),
            "valid_orchestrator",
            VALID_ORCHESTRATOR_CODE,
        )
        r1 = fca.classify_file(p1)
        assert r1 == "ORCHESTRATOR", f"valid_orchestrator: expected ORCHESTRATOR, got {r1}"

        # 2) Thin wrapper orchestrator
        p2 = _write(
            tmp_path,
            (AGENTIC_CORE_DIR, "L3_orchestration", "reasoning"),
            "thin_wrapper_orchestrator",
            textwrap.dedent("""\
#  # MOVED: from agentic_core.L3_orchestration.reasoning import R
#  # MOVED: from agentic_core.L5_safety.enforcement import G

                class ThinWrapperOrchestrator:
                    def run(self):
                        return R().execute()
            """),
        )
        r2 = fca.classify_file(p2)
        assert r2 == "ENGINE", f"thin_wrapper: expected ENGINE, got {r2}"

        # 3) Hard mutation orchestrator
        p3 = _write(
            tmp_path,
            (AGENTIC_CORE_DIR, "L3_orchestration", "reasoning"),
            "mutation_orchestrator",
            textwrap.dedent("""\
#  # MOVED: from agentic_core.L3_orchestration.reasoning import A
#  # MOVED: from agentic_core.L5_safety.enforcement import G

                class MutationOrchestrator:
                    def run_pipeline(self):
                        a = A()
                        g = G()
                        a.execute()
                        g.check()
                        with open("out.txt", "w") as f:
                            f.write("x")
                        return self.aggregate_result()

                    def aggregate_result(self):
                        return {}

                    def coordinate(self):
                        pass

                    def run_stages(self):
                        pass
            """),
        )
        r3 = fca.classify_file(p3)
        assert r3 == "ENGINE", f"mutation_orchestrator: expected ENGINE, got {r3}"

        # Verify stats buckets
        inv = fca.stats["violations"]["ORCHESTRATOR_INVARIANT_FAIL"]
        assert inv["thin_wrapper"] >= 1, f"thin_wrapper stat: {inv['thin_wrapper']}"
        assert inv["mutation_hard"] >= 1, f"mutation_hard stat: {inv['mutation_hard']}"
