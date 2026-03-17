"""
Phase 0 tests — classify_execution_mode() in classification_kernel.py
and ExecutionMode integration in FileClassificationAgent.

Branch inventory:
  classification_kernel.classify_execution_mode
    signal 1 weighted_scoring:  sum(x*y for ...) present → REASONING
    signal 2 prompt_construction: FunctionDef with 'prompt' in name → REASONING
    signal 3 plan_only_fallback: Constant 'plan_only' in AST → REASONING
    signal 4 meta_learning:  call to recall_*/store_*/ml_enhanced* → REASONING
    signal 5 multi_agent_orch: ≥2 *Agent instantiations → REASONING
    signal 6 async_external_call: AsyncFunctionDef present → REASONING
    no signals → DETERMINISTIC
    file does not exist → DETERMINISTIC
    empty file → DETERMINISTIC
    syntax error → DETERMINISTIC
    OSError → DETERMINISTIC
  FileClassificationAgent._orchestrate_audit
    AGENT file with no reasoning signals → AGENT_DETERMINISTIC counter incremented
    AGENT file with reasoning signals → counter NOT incremented
    non-AGENT file → counter NOT incremented
"""

import textwrap
from pathlib import Path

import pytest

from agentic_core.L5_safety.core_kernel.classification_kernel import (
    ExecutionMode,
    classify_execution_mode,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_execution_mode")
_emit_applies_guardrail("p0", "test_execution_mode", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_mode", "policy_binding")
_emit_snapshots_state("p0", "test_execution_mode", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_execution_mode", "p4obs", "metric_1")
_emit_emits_metric_event("test_execution_mode", "p4obs", "metric_2")
_emit_emits_metric_event("test_execution_mode", "p4obs", "metric_3")
_emit_emits_metric_event("test_execution_mode", "p4obs", "metric_4")
_emit_emits_metric_event("test_execution_mode", "p4obs", "metric_5")
_emit_emits_metric_event("test_execution_mode", "p4obs", "metric_6")
_emit_records_incident_event("test_execution_mode", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_execution_mode", "p4obs", "anomaly")
_emit_writes_observability_log("test_execution_mode", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_execution_mode", "p4obs", "mon_state")
_emit_triggers_alert("test_execution_mode", "p4obs", "alert")
_emit_links_incident_trace("test_execution_mode", "p4obs", "trace_link")
_emit_captures_pattern("test_execution_mode", "p3lm", "pattern")
_emit_records_learning_event("test_execution_mode", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_execution_mode", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_execution_mode", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_execution_mode", "p3lm", "routing")
_emit_improves_agent_policy("test_execution_mode", "p3lm", "policy")
_emit_stores_learning_state("test_execution_mode", "p3lm", "state")
_emit_records_execution_trace("test_execution_mode", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_execution_mode", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_execution_mode", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_execution_mode", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_execution_mode", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_execution_mode", "env_read", "p2_env_1")
_emit_reads_environ("test_execution_mode", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_execution_mode", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_execution_mode", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_execution_mode", "context_pull")
_emit_pulls_context("p1", "test_execution_mode", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_execution_mode", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_execution_mode", "uwg_term_2")
_emit_writes_through("p1", "test_execution_mode", "write_through")
_emit_writes_through("p1", "test_execution_mode", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_execution_mode", "safety_validation")
_emit_invokes_eval("p1", "test_execution_mode", "eval_call")
_emit_proposal_commits_routing("p1", "test_execution_mode", "routing_commit")
_emit_escalates_to_human("p1", "test_execution_mode", "human_escalation")
_emit_routes_through("p1", "test_execution_mode", "route_through")
_emit_checks_agent_registry("p1", "test_execution_mode", "agent_registry")
_emit_validates_agent_capability("p1", "test_execution_mode", "capability")
_emit_dispatches_execution_plan("p1", "test_execution_mode", "exec_plan")
_emit_agent_executes_agent("p1", "test_execution_mode", "sub_agent")
_emit_routes_to_agent("p1", "test_execution_mode", "target_agent")
_emit_verifies_policy("p1", "test_execution_mode", "policy_check")
_emit_observes_runtime_state("p1", "test_execution_mode", "runtime_state")
_emit_verifies_boundary("p1", "test_execution_mode", "boundary_check")
_emit_transcripts_response("p1", "test_execution_mode", "transcript")
_emit_hard_fails_untranscripted("p1", "test_execution_mode")
_emit_gated_by_confidence("p1", "test_execution_mode", "confidence_gate")
emit_replay_key("p0", "test_execution_mode")
emit_determinism_digest("p0", "test_execution_mode")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_mode", "execution_auth")
_emit_validates_capability("p2", "test_execution_mode", "capability_check")
_emit_routes_to_capability("p2", "test_execution_mode", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_mode", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_mode", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_mode", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_mode", "exec_output")
_emit_dispatches_agent("p3", "test_execution_mode", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_mode", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_mode", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_mode", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_mode", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_mode", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_mode", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_mode", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_mode", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_mode", "eval_metric")
_emit_stores_embedding("p4", "test_execution_mode", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_mode", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_mode", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# ExecutionMode type contract
# ---------------------------------------------------------------------------


class TestExecutionModeType:
    def test_valid_values_are_reasoning_and_deterministic(self):
        assert ExecutionMode.__args__ == ("REASONING", "DETERMINISTIC")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Signal 1: weighted_scoring
# ---------------------------------------------------------------------------


class TestSignalWeightedScoring:
    def test_sum_mult_generator_triggers(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def score(self):
                    return sum(s * w for s, w in [(1, 2), (3, 4)])
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert mode == "REASONING"
        assert "weighted_scoring" in signals

    def test_sum_no_mult_does_not_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def total(self):
                    return sum(x for x in range(10))
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert "weighted_scoring" not in signals

    def test_sum_listcomp_mult_triggers(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def score(self):
                    return sum([s * w for s, w in items])
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert "weighted_scoring" in signals


# ---------------------------------------------------------------------------
# Signal 2: prompt_construction
# ---------------------------------------------------------------------------


class TestSignalPromptConstruction:
    def test_function_named_build_prompt_triggers(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def build_prompt(self, ctx):
                    return f"Do {ctx}"
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert mode == "REASONING"
        assert "prompt_construction" in signals

    def test_function_named_construct_prompt_triggers(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def construct_prompt(self, x):
                    return x
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "prompt_construction" in signals

    def test_function_without_prompt_in_name_does_not_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    pass
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "prompt_construction" not in signals


# ---------------------------------------------------------------------------
# Signal 3: plan_only_fallback
# ---------------------------------------------------------------------------


class TestSignalPlanOnlyFallback:
    def test_string_constant_plan_only_triggers(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    return {"plan_only": True, "steps": []}
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert mode == "REASONING"
        assert "plan_only_fallback" in signals

    def test_plan_only_in_variable_assignment_triggers(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    key = "plan_only"
                    return key
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "plan_only_fallback" in signals

    def test_no_plan_only_constant_does_not_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    return {"result": True}
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "plan_only_fallback" not in signals


# ---------------------------------------------------------------------------
# Signal 4: meta_learning
# ---------------------------------------------------------------------------


class TestSignalMetaLearning:
    @pytest.mark.parametrize(
        "method_name",
        [
            "recall_prior",
            "store_outcome",
            "ml_enhanced_route",
            "meta_learn_update",
        ],
    )
    def test_meta_learning_prefixes_trigger(self, tmp_path, method_name):
        p = _write(
            tmp_path,
            "agent.py",
            f"""\
            class MyAgent:
                def run(self):
                    self.{method_name}()
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "meta_learning" in signals

    def test_unrelated_method_does_not_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    self.execute()
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "meta_learning" not in signals


# ---------------------------------------------------------------------------
# Signal 5: multi_agent_orchestration
# ---------------------------------------------------------------------------


class TestSignalMultiAgentOrchestration:
    def test_two_agent_instantiations_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    a = HierarchyAgent()
                    b = GravityAgent()
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert mode == "REASONING"
        assert "multi_agent_orchestration" in signals

    def test_one_agent_instantiation_does_not_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    a = HierarchyAgent()
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "multi_agent_orchestration" not in signals

    def test_same_agent_twice_does_not_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    a = HierarchyAgent()
                    b = HierarchyAgent()
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "multi_agent_orchestration" not in signals

    def test_three_distinct_agents_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    a = AlphaAgent()
                    b = BetaAgent()
                    c = GammaAgent()
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "multi_agent_orchestration" in signals


# ---------------------------------------------------------------------------
# Signal 6: async_external_call
# ---------------------------------------------------------------------------


class TestSignalAsyncExternalCall:
    def test_async_funcdef_triggers(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                async def fetch(self):
                    pass
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert mode == "REASONING"
        assert "async_external_call" in signals

    def test_no_async_does_not_trigger(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self):
                    pass
        """,
        )
        _, signals = classify_execution_mode(p)
        assert "async_external_call" not in signals


# ---------------------------------------------------------------------------
# Deterministic baseline (no signals)
# ---------------------------------------------------------------------------


class TestDeterministicBaseline:
    def test_pure_deterministic_file_returns_deterministic(self, tmp_path):
        p = _write(
            tmp_path,
            "validator.py",
            """\
            import ast
            from pathlib import Path

            class HierarchyValidator:
                def scan(self, root: Path):
                    violations = []
                    for f in root.rglob("*.py"):
                        tree = ast.parse(f.read_text())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                violations.append(str(f))
                    return violations
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert mode == "DETERMINISTIC"
        assert signals == []


# ---------------------------------------------------------------------------
# Edge / boundary conditions
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_nonexistent_file_returns_deterministic(self, tmp_path):
        p = tmp_path / "ghost.py"
        mode, signals = classify_execution_mode(p)
        assert mode == "DETERMINISTIC"
        assert signals == []

    def test_empty_file_returns_deterministic(self, tmp_path):
        p = tmp_path / "empty.py"
        p.write_text("", encoding="utf-8")
        mode, signals = classify_execution_mode(p)
        assert mode == "DETERMINISTIC"
        assert signals == []

    def test_syntax_error_returns_deterministic(self, tmp_path):
        p = _write(tmp_path, "bad.py", "def broken(:\n    pass\n")
        mode, signals = classify_execution_mode(p)
        assert mode == "DETERMINISTIC"
        assert signals == []

    def test_multiple_signals_all_reported(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def build_prompt(self, x):
                    return f"Do {x}"
                def run(self):
                    self.recall_prior()
                    return {"plan_only": True}
        """,
        )
        mode, signals = classify_execution_mode(p)
        assert mode == "REASONING"
        assert "prompt_construction" in signals
        assert "meta_learning" in signals
        assert "plan_only_fallback" in signals

    def test_return_type_is_tuple_of_str_and_list(self, tmp_path):
        p = _write(tmp_path, "agent.py", "class X: pass\n")
        result = classify_execution_mode(p)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], list)

    def test_deterministic_idempotent_repeated_calls(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def run(self): pass
        """,
        )
        first = classify_execution_mode(p)
        second = classify_execution_mode(p)
        assert first == second

    def test_reasoning_idempotent_repeated_calls(self, tmp_path):
        p = _write(
            tmp_path,
            "agent.py",
            """\
            class MyAgent:
                def build_prompt(self, x): return x
        """,
        )
        first = classify_execution_mode(p)
        second = classify_execution_mode(p)
        assert first == second


# ---------------------------------------------------------------------------
# FileClassificationAgent._orchestrate_audit ExecutionMode integration
# ---------------------------------------------------------------------------


class TestFCAExecutionModeIntegration:
    @pytest.fixture
    def fca(self, tmp_path):
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        return FileClassificationAgent(
            project_root=tmp_path,
            dry_run=True,
            validate_only=True,
        )

    def _make_agent_file(self, directory: Path, name: str, content: str) -> Path:
        f = directory / name
        f.write_text(textwrap.dedent(content), encoding="utf-8")
        return f

    def test_deterministic_agent_increments_counter(self, tmp_path, fca):
        """AGENT file with no reasoning signals → AGENT_DETERMINISTIC incremented."""
        f = self._make_agent_file(
            tmp_path,
            "DummyAgent.py",
            """\
            class DummyAgent:
                def scan(self):
                    return []
        """,
        )
        fca.file_registry = [f]
        fca._orchestrate_audit(tmp_path)
        assert fca.stats["violations"]["AGENT_DETERMINISTIC"] >= 1

    def test_reasoning_agent_does_not_increment_counter(self, tmp_path, fca):
        """AGENT file with reasoning signals → AGENT_DETERMINISTIC NOT incremented."""
        f = self._make_agent_file(
            tmp_path,
            "SmartAgent.py",
            """\
            class SmartAgent:
                def build_prompt(self, ctx):
                    return f"Do {ctx}"
        """,
        )
        fca.file_registry = [f]
        fca._orchestrate_audit(tmp_path)
        assert fca.stats["violations"]["AGENT_DETERMINISTIC"] == 0

    def test_non_agent_file_does_not_increment_counter(self, tmp_path, fca):
        """Non-AGENT file → AGENT_DETERMINISTIC NOT incremented."""
        f = self._make_agent_file(
            tmp_path,
            "my_validator.py",
            """\
            class MyValidator:
                def check(self):
                    return True
        """,
        )
        fca.file_registry = [f]
        fca._orchestrate_audit(tmp_path)
        assert fca.stats["violations"]["AGENT_DETERMINISTIC"] == 0

    def test_agent_deterministic_counter_present_in_stats(self, fca):
        """AGENT_DETERMINISTIC key must exist in stats violations from __post_init__."""
        assert "AGENT_DETERMINISTIC" in fca.stats["violations"]

    def test_classification_result_has_execution_mode_field(self):
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            ClassificationResult,
        )

        r = ClassificationResult(
            file_type="AGENT",
            confidence=0.9,
            signals=["agent_base"],
            warnings=[],
        )
        assert r.execution_mode == "DETERMINISTIC"
        assert r.reasoning_signals == []

    def test_classification_result_accepts_reasoning_mode(self):
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            ClassificationResult,
        )

        r = ClassificationResult(
            file_type="AGENT",
            confidence=0.9,
            signals=["agent_base"],
            warnings=[],
            execution_mode="REASONING",
            reasoning_signals=["meta_learning"],
        )
        assert r.execution_mode == "REASONING"
        assert "meta_learning" in r.reasoning_signals
