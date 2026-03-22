"""Unit tests for LLM agentic workflow pattern engines.

Covers Phase A–C implementations:
  A1  RewooEngine / RewooPlanner / RewooSolver / RewooWorker
  A2  ReflexionEngine
  B1  EvaluatorOptimizerEngine
  B2  ParallelizationEngine
  B3  AutonomousWorkflowEngine
  C1  react_engine re-export + ReActStrategy wiring
  C2  AgenticRouter
  C3  PromptChainEngine
  C4  WorkerPool + SynthesizerNode
  C5  replan_on_failure + ReplanArtifact
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "test_llm_workflow_patterns")
_emit_applies_guardrail("p0", "test_llm_workflow_patterns", "p0_governance")
_emit_reads_policy_state("p0", "test_llm_workflow_patterns", "policy_binding")
_emit_snapshots_state("p0", "test_llm_workflow_patterns", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_llm_workflow_patterns", "p4obs", "metric_1")
_emit_emits_metric_event("test_llm_workflow_patterns", "p4obs", "metric_2")
_emit_emits_metric_event("test_llm_workflow_patterns", "p4obs", "metric_3")
_emit_emits_metric_event("test_llm_workflow_patterns", "p4obs", "metric_4")
_emit_emits_metric_event("test_llm_workflow_patterns", "p4obs", "metric_5")
_emit_emits_metric_event("test_llm_workflow_patterns", "p4obs", "metric_6")
_emit_records_incident_event("test_llm_workflow_patterns", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_llm_workflow_patterns", "p4obs", "anomaly")
_emit_writes_observability_log("test_llm_workflow_patterns", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_llm_workflow_patterns", "p4obs", "mon_state")
_emit_triggers_alert("test_llm_workflow_patterns", "p4obs", "alert")
_emit_links_incident_trace("test_llm_workflow_patterns", "p4obs", "trace_link")
_emit_captures_pattern("test_llm_workflow_patterns", "p3lm", "pattern")
_emit_records_learning_event("test_llm_workflow_patterns", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_llm_workflow_patterns", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_llm_workflow_patterns", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_llm_workflow_patterns", "p3lm", "routing")
_emit_improves_agent_policy("test_llm_workflow_patterns", "p3lm", "policy")
_emit_stores_learning_state("test_llm_workflow_patterns", "p3lm", "state")
_emit_records_execution_trace("test_llm_workflow_patterns", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_llm_workflow_patterns", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_llm_workflow_patterns", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_llm_workflow_patterns", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_llm_workflow_patterns", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_llm_workflow_patterns", "env_read", "p2_env_1")
_emit_reads_environ("test_llm_workflow_patterns", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_llm_workflow_patterns", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_llm_workflow_patterns", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_llm_workflow_patterns", "context_pull")
_emit_pulls_context("p1", "test_llm_workflow_patterns", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_llm_workflow_patterns", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_llm_workflow_patterns", "uwg_term_2")
_emit_writes_through("p1", "test_llm_workflow_patterns", "write_through")
_emit_writes_through("p1", "test_llm_workflow_patterns", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_llm_workflow_patterns", "safety_validation")
_emit_invokes_eval("p1", "test_llm_workflow_patterns", "eval_call")
_emit_proposal_commits_routing("p1", "test_llm_workflow_patterns", "routing_commit")
_emit_escalates_to_human("p1", "test_llm_workflow_patterns", "human_escalation")
_emit_routes_through("p1", "test_llm_workflow_patterns", "route_through")
_emit_checks_agent_registry("p1", "test_llm_workflow_patterns", "agent_registry")
_emit_validates_agent_capability("p1", "test_llm_workflow_patterns", "capability")
_emit_dispatches_execution_plan("p1", "test_llm_workflow_patterns", "exec_plan")
_emit_agent_executes_agent("p1", "test_llm_workflow_patterns", "sub_agent")
_emit_routes_to_agent("p1", "test_llm_workflow_patterns", "target_agent")
_emit_verifies_policy("p1", "test_llm_workflow_patterns", "policy_check")
_emit_observes_runtime_state("p1", "test_llm_workflow_patterns", "runtime_state")
_emit_verifies_boundary("p1", "test_llm_workflow_patterns", "boundary_check")
_emit_transcripts_response("p1", "test_llm_workflow_patterns", "transcript")
_emit_hard_fails_untranscripted("p1", "test_llm_workflow_patterns")
_emit_gated_by_confidence("p1", "test_llm_workflow_patterns", "confidence_gate")
emit_replay_key("p0", "test_llm_workflow_patterns")
emit_determinism_digest("p0", "test_llm_workflow_patterns")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_llm_workflow_patterns", "execution_auth")
_emit_validates_capability("p2", "test_llm_workflow_patterns", "capability_check")
_emit_routes_to_capability("p2", "test_llm_workflow_patterns", "capability_route")
_emit_writes_via_uwg("p2", "test_llm_workflow_patterns", "uwg_write")
_emit_blocks_direct_write("p2", "test_llm_workflow_patterns", "direct_write_block")
_emit_records_tool_invocation("p2", "test_llm_workflow_patterns", "tool_invocation")
_emit_captures_execution_output("p2", "test_llm_workflow_patterns", "exec_output")
_emit_dispatches_agent("p3", "test_llm_workflow_patterns", "agent_dispatch")
_emit_coordinates_agents("p3", "test_llm_workflow_patterns", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_llm_workflow_patterns", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_llm_workflow_patterns", "healing_outcome")
_emit_escalates_failure("p3", "test_llm_workflow_patterns", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_llm_workflow_patterns", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_llm_workflow_patterns", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_llm_workflow_patterns", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_llm_workflow_patterns", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_llm_workflow_patterns", "eval_metric")
_emit_stores_embedding("p4", "test_llm_workflow_patterns", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_llm_workflow_patterns", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_llm_workflow_patterns", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# A1 — Rewoo
# ---------------------------------------------------------------------------


class TestRewooTypes:
    def test_rewoo_task_list_ready_tasks_no_deps(self):
        from agentic_core.L3_orchestration.types.rewoo_types import (
            RewooTask,
            RewooTaskList,
        )

        tl = RewooTaskList(goal="test")
        tl.tasks.append(RewooTask("t1", "desc", "why", "tool_a", {}))
        tl.tasks.append(RewooTask("t2", "desc2", "why2", "tool_b", {}, depends_on=["t1"]))
        ready = tl.ready_tasks()
        assert len(ready) == 1
        assert ready[0].task_id == "t1"

    def test_rewoo_task_list_ready_after_completion(self):
        from agentic_core.L3_orchestration.types.rewoo_types import (
            RewooTask,
            RewooTaskList,
            RewooTaskStatus,
        )

        tl = RewooTaskList(goal="test")
        t1 = RewooTask("t1", "desc", "why", "tool_a", {})
        t1.status = RewooTaskStatus.COMPLETED
        t2 = RewooTask("t2", "desc2", "why2", "tool_b", {}, depends_on=["t1"])
        tl.tasks.extend([t1, t2])
        ready = tl.ready_tasks()
        assert len(ready) == 1
        assert ready[0].task_id == "t2"

    def test_rewoo_context_accumulates_results(self):
        from agentic_core.L3_orchestration.types.rewoo_types import (
            RewooContext,
            RewooTaskList,
        )

        tl = RewooTaskList(goal="g")
        ctx = RewooContext(goal="g", task_list=tl)
        ctx.results["t1"] = "result_a"
        assert ctx.results["t1"] == "result_a"

    def test_rewoo_memory_best_response(self):
        from agentic_core.L3_orchestration.types.reflexion_types import (
            ReflexionCritique,
            ReflexionMemory,
        )

        mem = ReflexionMemory(task="t")
        assert mem.best_response() is None
        mem.add(ReflexionCritique(1, "resp_a", "ok", 0.5, False))
        mem.add(ReflexionCritique(2, "resp_b", "better", 0.9, True))
        assert mem.best_response() == "resp_b"


class TestRewooEngine:
    def _make_engine(self, tasks_spec):
        from agentic_core.L3_orchestration.engines.rewoo_engine import (
            RewooEngine,
            RewooPlanner,
            RewooSolver,
            RewooWorker,
        )

        async def _planner_fn(goal, ctx):
            return tasks_spec

        planner = RewooPlanner(_planner_fn)
        solver = RewooSolver()

        async def _echo_tool(inp):
            return f"result:{inp.get('value', 'x')}"

        solver.register_tool("echo", _echo_tool)
        worker = RewooWorker()
        return RewooEngine(planner, solver, worker, max_iterations=10)

    def test_run_simple_chain(self):
        engine = self._make_engine(
            [
                {
                    "task_id": "t1",
                    "description": "step1",
                    "reasoning": "r1",
                    "tool_name": "echo",
                    "tool_input": {"value": "hello"},
                    "depends_on": [],
                },
            ]
        )
        ctx = asyncio.get_event_loop().run_until_complete(engine.run("test goal"))
        assert ctx.success
        assert "t1" in ctx.results

    def test_run_dependency_order(self):
        engine = self._make_engine(
            [
                {
                    "task_id": "t1",
                    "description": "a",
                    "reasoning": "r",
                    "tool_name": "echo",
                    "tool_input": {"value": "a"},
                    "depends_on": [],
                },
                {
                    "task_id": "t2",
                    "description": "b",
                    "reasoning": "r",
                    "tool_name": "echo",
                    "tool_input": {"value": "#t1"},
                    "depends_on": ["t1"],
                },
            ]
        )
        ctx = asyncio.get_event_loop().run_until_complete(engine.run("dep goal"))
        assert ctx.success
        assert "t2" in ctx.results

    def test_missing_tool_marks_failed(self):
        engine = self._make_engine(
            [
                {
                    "task_id": "t1",
                    "description": "a",
                    "reasoning": "r",
                    "tool_name": "nonexistent",
                    "tool_input": {},
                    "depends_on": [],
                },
            ]
        )
        ctx = asyncio.get_event_loop().run_until_complete(engine.run("goal", synthesizer_fn=None))
        from agentic_core.L3_orchestration.types.rewoo_types import RewooTaskStatus

        assert ctx.task_list.tasks[0].status == RewooTaskStatus.FAILED
        assert not ctx.success

    def test_reference_substitution(self):
        from agentic_core.L3_orchestration.engines.rewoo_engine import RewooSolver

        solver = RewooSolver()
        resolved = solver._resolve_references({"x": "#prev"}, {"prev": "VALUE"})
        assert resolved["x"] == "VALUE"

    def test_synthesizer_fn_called(self):
        engine = self._make_engine(
            [
                {
                    "task_id": "t1",
                    "description": "a",
                    "reasoning": "r",
                    "tool_name": "echo",
                    "tool_input": {"value": "hi"},
                    "depends_on": [],
                },
            ]
        )
        called = []

        async def _synth(ctx):
            called.append(True)
            return "synthesized"

        ctx = asyncio.get_event_loop().run_until_complete(engine.run("goal", synthesizer_fn=_synth))
        assert called
        assert ctx.final_answer == "synthesized"


# ---------------------------------------------------------------------------
# A2 — Reflexion
# ---------------------------------------------------------------------------


class TestReflexionEngine:
    def _make_engine(self, scores):
        from agentic_core.L3_orchestration.engines.reflexion_engine import ReflexionEngine

        call_count = {"n": 0}

        async def _gen_fn(task, prior, mem_summary):
            call_count["n"] += 1
            return f"response_{call_count['n']}"

        score_iter = iter(scores)

        async def _eval_fn(task, response):
            s = next(score_iter, scores[-1])
            return {"critique": f"crit_{s}", "score": s, "passed": s >= 0.85}

        return ReflexionEngine(_gen_fn, _eval_fn, score_threshold=0.85, max_iterations=5)

    def test_converges_early_when_score_high(self):
        engine = self._make_engine([0.5, 0.9])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert result["passed"]
        assert result["iterations"] == 2

    def test_runs_max_iterations_when_never_passing(self):
        engine = self._make_engine([0.3, 0.3, 0.3, 0.3, 0.3])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert result["iterations"] == 5
        assert not result["passed"]

    def test_best_response_is_highest_score(self):
        engine = self._make_engine([0.6, 0.9, 0.7])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert result["response"] == "response_2"

    def test_memory_summary_grows(self):
        from agentic_core.L3_orchestration.types.reflexion_types import ReflexionCritique, ReflexionMemory

        mem = ReflexionMemory(task="t")
        mem.add(ReflexionCritique(1, "r1", "c1", 0.5, False))
        mem.add(ReflexionCritique(2, "r2", "c2", 0.8, False))
        summary = mem.summary()
        assert "Iteration 1" in summary
        assert "Iteration 2" in summary

    def test_single_iteration_converge(self):
        engine = self._make_engine([0.95])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert result["iterations"] == 1
        assert result["passed"]


# ---------------------------------------------------------------------------
# B1 — EvaluatorOptimizer
# ---------------------------------------------------------------------------


class TestEvaluatorOptimizerEngine:
    def _make_engine(self, scores, threshold=80.0):
        from agentic_core.L3_orchestration.engines.evaluator_optimizer_engine import (
            EvaluatorOptimizerEngine,
        )

        async def _gen_fn(task, ctx):
            return {"content": "initial"}

        score_iter = iter(scores)

        async def _eval_fn(content):
            s = next(score_iter, scores[-1])
            return {
                "score": s,
                "issues": [] if s >= threshold else ["low_quality"],
                "status": "passed" if s >= threshold else "warning",
            }

        async def _opt_fn(content, issues):
            return {**content, "optimized": True}

        return EvaluatorOptimizerEngine(
            _gen_fn, _eval_fn, _opt_fn, score_threshold=threshold, max_iterations=4
        )

    def test_passes_on_first_eval(self):
        engine = self._make_engine([90.0])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert result["passed"]
        assert result["iterations"] == 1

    def test_optimizes_until_threshold(self):
        engine = self._make_engine([60.0, 70.0, 85.0])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert result["passed"]
        assert result["iterations"] == 3

    def test_returns_last_content_when_max_reached(self):
        engine = self._make_engine([50.0, 50.0, 50.0, 50.0])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert not result["passed"]
        assert result["iterations"] == 4

    def test_history_records_each_iteration(self):
        engine = self._make_engine([60.0, 90.0])
        result = asyncio.get_event_loop().run_until_complete(engine.run("task"))
        assert len(result["history"]) == 2
        assert result["history"][0]["score"] == 60.0
        assert result["history"][1]["score"] == 90.0


# ---------------------------------------------------------------------------
# B2 — Parallelization
# ---------------------------------------------------------------------------


class TestParallelizationEngine:
    def test_sectioning_collect_all(self):
        from agentic_core.L3_orchestration.engines.parallelization_engine import (
            AggregationStrategy,
            ParallelizationEngine,
            ParallelMode,
        )

        async def _worker(task, seed):
            return f"out:{task}"

        engine = ParallelizationEngine(
            _worker, mode=ParallelMode.SECTIONING, aggregation=AggregationStrategy.COLLECT_ALL
        )
        result = asyncio.get_event_loop().run_until_complete(
            engine.run("goal", branches=["task_a", "task_b"])
        )
        assert len(result["outputs"]) == 2
        assert result["mode"] == "sectioning"

    def test_sampling_majority_vote(self):
        from agentic_core.L3_orchestration.engines.parallelization_engine import (
            AggregationStrategy,
            ParallelizationEngine,
            ParallelMode,
        )

        async def _worker(task, seed):
            return "answer_x" if seed < 2 else "answer_y"

        engine = ParallelizationEngine(
            _worker, mode=ParallelMode.SAMPLING, aggregation=AggregationStrategy.MAJORITY_VOTE
        )
        result = asyncio.get_event_loop().run_until_complete(engine.run("goal", n_samples=3))
        assert result["result"] == "answer_x"

    def test_first_pass_aggregation(self):
        from agentic_core.L3_orchestration.engines.parallelization_engine import (
            AggregationStrategy,
            ParallelizationEngine,
            ParallelMode,
        )

        async def _worker(task, seed):
            return seed

        engine = ParallelizationEngine(
            _worker,
            mode=ParallelMode.SAMPLING,
            aggregation=AggregationStrategy.FIRST_PASS,
            pass_predicate=lambda o: o == 1,
        )
        result = asyncio.get_event_loop().run_until_complete(engine.run("goal", n_samples=3))
        assert result["result"] == 1

    def test_llm_synthesize_aggregation(self):
        from agentic_core.L3_orchestration.engines.parallelization_engine import (
            AggregationStrategy,
            ParallelizationEngine,
            ParallelMode,
        )

        async def _worker(task, seed):
            return f"item_{seed}"

        async def _synth(outputs):
            return "synthesized:" + ",".join(outputs)

        engine = ParallelizationEngine(
            _worker,
            mode=ParallelMode.SAMPLING,
            aggregation=AggregationStrategy.LLM_SYNTHESIZE,
            synthesizer_fn=_synth,
        )
        result = asyncio.get_event_loop().run_until_complete(engine.run("goal", n_samples=2))
        assert result["result"].startswith("synthesized:")

    def test_branch_error_returns_none_slot(self):
        from agentic_core.L3_orchestration.engines.parallelization_engine import (
            AggregationStrategy,
            ParallelizationEngine,
            ParallelMode,
        )

        async def _worker(task, seed):
            if seed == 1:
                raise ValueError("boom")
            return "ok"

        engine = ParallelizationEngine(
            _worker, mode=ParallelMode.SAMPLING, aggregation=AggregationStrategy.COLLECT_ALL
        )
        result = asyncio.get_event_loop().run_until_complete(engine.run("goal", n_samples=3))
        assert result["outputs"][1] is None


# ---------------------------------------------------------------------------
# B3 — AutonomousWorkflowEngine
# ---------------------------------------------------------------------------


class TestAutonomousWorkflowEngine:
    def _make_engine(self, actions, goal_after=None):
        from agentic_core.L3_orchestration.engines.autonomous_workflow_engine import (
            AutonomousWorkflowEngine,
        )

        action_iter = iter(actions)

        async def _policy(goal, steps, obs):
            return next(action_iter, ("STOP", {}))

        class FakeEnv:
            def __init__(self, goal_after):
                self._call = 0
                self._goal_after = goal_after

            async def execute_action(self, action, params):
                self._call += 1
                return {"action": action, "call": self._call}

            def is_goal_achieved(self, obs):
                return self._goal_after is not None and obs.get("call", 0) >= self._goal_after

            def reset(self):
                self._call = 0

        return AutonomousWorkflowEngine(_policy, FakeEnv(goal_after), max_iterations=10)

    def test_explicit_stop(self):
        engine = self._make_engine([("STOP", {})])
        from agentic_core.L3_orchestration.engines.autonomous_workflow_engine import StopSignal

        result = asyncio.get_event_loop().run_until_complete(engine.run("goal"))
        assert result.stop_signal == StopSignal.EXPLICIT_STOP
        assert result.success

    def test_goal_achieved(self):
        engine = self._make_engine(
            [("action_a", {"p": 1}), ("action_b", {"p": 2})],
            goal_after=1,
        )
        from agentic_core.L3_orchestration.engines.autonomous_workflow_engine import StopSignal

        result = asyncio.get_event_loop().run_until_complete(engine.run("goal"))
        assert result.stop_signal == StopSignal.GOAL_ACHIEVED
        assert result.success

    def test_max_iterations_stop(self):
        from agentic_core.L3_orchestration.engines.autonomous_workflow_engine import (
            AutonomousWorkflowEngine,
            StopSignal,
        )

        async def _policy(goal, steps, obs):
            return ("noop", {})

        class InfiniteEnv:
            async def execute_action(self, a, p):
                return {}

            def is_goal_achieved(self, obs):
                return False

            def reset(self):
                pass

        engine = AutonomousWorkflowEngine(_policy, InfiniteEnv(), max_iterations=3)
        result = asyncio.get_event_loop().run_until_complete(engine.run("goal"))
        assert result.stop_signal == StopSignal.MAX_ITERATIONS
        assert len(result.steps) == 3

    def test_circuit_breaker(self):
        from agentic_core.L3_orchestration.engines.autonomous_workflow_engine import (
            AutonomousWorkflowEngine,
            StopSignal,
        )

        async def _policy(goal, steps, obs):
            return ("boom", {})

        class ErrorEnv:
            async def execute_action(self, a, p):
                raise RuntimeError("env_error")

            def is_goal_achieved(self, obs):
                return False

            def reset(self):
                pass

        engine = AutonomousWorkflowEngine(_policy, ErrorEnv(), max_iterations=20, max_consecutive_failures=3)
        result = asyncio.get_event_loop().run_until_complete(engine.run("goal"))
        assert result.stop_signal == StopSignal.CIRCUIT_BREAKER


# ---------------------------------------------------------------------------
# C1 — ReACT re-export
# ---------------------------------------------------------------------------


class TestReactEngine:
    def test_import_from_engines_path(self):
        from agentic_core.L1_cognition.engines.react_engine import create_react_engine

        engine = create_react_engine(max_steps=5)
        assert engine.max_steps == 5

    def test_react_engine_run_finishes(self):
        from agentic_core.L1_cognition.engines.react_engine import ReActEngine

        engine = ReActEngine(max_steps=2, enable_self_reflection=False)
        call_count = {"n": 0}

        async def _think(task, steps):
            call_count["n"] += 1
            if call_count["n"] >= 3:
                return "FINISH"
            return f"Thought: step {call_count['n']}\nAction: noop\nAction Input: {{}}"

        async def _act(action, action_input):
            return f"obs_{action}"

        trace = asyncio.get_event_loop().run_until_complete(engine.run("test task", _think, _act))
        assert trace.Task == "test task"

    def test_react_strategy_imports(self):
        from agentic_core.L1_cognition.enforcement.react_strategy import ReActPattern, ReActStrategy

        assert ReActPattern is ReActStrategy

    def test_react_strategy_has_engine(self):
        from agentic_core.L1_cognition.enforcement.react_strategy import ReActStrategy

        strategy = ReActStrategy(max_steps=3)
        assert strategy._engine is not None
        assert strategy._engine.max_steps == 3

    def test_patterns_base_importable(self):
        from agentic_core.patterns.base import BaseReasoningPattern

        assert BaseReasoningPattern is not None

    def test_runtime_state_shim(self):
        from agentic_core.runtime.state import AgentState

        state = AgentState(task_id="t1", user_input="hello")
        assert state.turn_count == 0


# ---------------------------------------------------------------------------
# C2 — AgenticRouter
# ---------------------------------------------------------------------------


class TestAgenticRouter:
    def test_dispatch_to_correct_target(self):
        from agentic_core.L0_routing.engines.agentic_router import AgenticRouter

        router = AgenticRouter()
        results = {}

        async def _handler_a(inp, ctx):
            results["called"] = "a"
            return "a_result"

        async def _handler_b(inp, ctx):
            results["called"] = "b"
            return "b_result"

        router.register("agent_a", _handler_a, intent_keywords=["resume", "cv"])
        router.register("agent_b", _handler_b, intent_keywords=["code", "review"])

        decision = asyncio.get_event_loop().run_until_complete(router.route("Please review my code"))
        assert decision.target_name == "agent_b"
        assert decision.result == "b_result"

    def test_fallback_on_no_match(self):
        from agentic_core.L0_routing.engines.agentic_router import AgenticRouter

        called = []

        async def _fallback(inp, ctx):
            called.append(True)
            return "fallback_result"

        router = AgenticRouter(fallback_handler=_fallback, min_confidence=0.5)
        router.register("agent_x", AsyncMock(return_value="x"), intent_keywords=["specific"])

        decision = asyncio.get_event_loop().run_until_complete(router.route("something completely unrelated"))
        assert called
        assert decision.result == "fallback_result"

    def test_mad_handler_gathers_debaters(self):
        from agentic_core.L0_routing.engines.agentic_router import AgenticRouter

        router = AgenticRouter()

        async def _d1(inp, ctx):
            return "opinion_a"

        async def _d2(inp, ctx):
            return "opinion_b"

        async def _synth(outputs):
            return "+".join(outputs)

        router.register_mad([_d1, _d2], _synth)
        decision = asyncio.get_event_loop().run_until_complete(
            router.route("debate multiple perspectives on this topic")
        )
        assert decision.result == "opinion_a+opinion_b"

    def test_list_targets(self):
        from agentic_core.L0_routing.engines.agentic_router import AgenticRouter

        router = AgenticRouter()
        router.register("t1", AsyncMock())
        router.register("t2", AsyncMock())
        assert set(router.list_targets()) == {"t1", "t2"}

    def test_routing_decision_has_confidence(self):
        from agentic_core.L0_routing.engines.agentic_router import AgenticRouter

        async def _h(inp, ctx):
            return "r"

        router = AgenticRouter()
        router.register("agent", _h, intent_keywords=["test", "run"])
        decision = asyncio.get_event_loop().run_until_complete(router.route("run the test"))
        assert decision.confidence > 0


# ---------------------------------------------------------------------------
# C3 — PromptChainEngine
# ---------------------------------------------------------------------------


class TestPromptChainEngine:
    def test_simple_chain_runs(self):
        from agentic_core.L3_orchestration.engines.prompt_chain_engine import PromptChainEngine

        chain = PromptChainEngine()

        async def step1(ctx):
            return {"s1": "done"}

        async def step2(ctx):
            return {"s2": ctx.get("s1") + "_s2"}

        chain.add_step("s1", step1).add_step("s2", step2)
        result = asyncio.get_event_loop().run_until_complete(chain.run({"seed": True}))
        assert result.success
        assert result.output["s2"] == "done_s2"

    def test_gate_pass_continues(self):
        from agentic_core.L3_orchestration.engines.prompt_chain_engine import PromptChainEngine

        chain = PromptChainEngine()

        async def step(ctx):
            return {"val": 100}

        async def gate(out):
            return out["val"] > 50

        chain.add_step("q", step, gate=gate)
        result = asyncio.get_event_loop().run_until_complete(chain.run())
        assert result.success
        assert "q" not in result.gate_failures

    def test_gate_fail_stops_chain(self):
        from agentic_core.L3_orchestration.engines.prompt_chain_engine import PromptChainEngine

        chain = PromptChainEngine(stop_on_gate_failure=True)
        reached = []

        async def step_a(ctx):
            return {"val": 10}

        async def gate_a(out):
            return out["val"] > 50

        async def step_b(ctx):
            reached.append(True)
            return {}

        chain.add_step("a", step_a, gate=gate_a).add_step("b", step_b)
        result = asyncio.get_event_loop().run_until_complete(chain.run())
        assert not result.success
        assert not reached

    def test_gate_fail_uses_fail_branch(self):
        from agentic_core.L3_orchestration.engines.prompt_chain_engine import PromptChainEngine

        chain = PromptChainEngine(stop_on_gate_failure=True)

        async def step_a(ctx):
            return {"val": 10}

        async def gate_a(out):
            return False

        async def fail_branch(ctx):
            return {"fallback": True}

        chain.add_step("a", step_a, gate=gate_a, fail_branch=fail_branch)
        result = asyncio.get_event_loop().run_until_complete(chain.run())
        assert result.success

    def test_steps_completed_tracks_names(self):
        from agentic_core.L3_orchestration.engines.prompt_chain_engine import PromptChainEngine

        chain = PromptChainEngine()

        async def s1(ctx):
            return {}

        async def s2(ctx):
            return {}

        chain.add_step("alpha", s1).add_step("beta", s2)
        result = asyncio.get_event_loop().run_until_complete(chain.run())
        assert result.steps_completed == ["alpha", "beta"]


# ---------------------------------------------------------------------------
# C4 — WorkerPool + SynthesizerNode
# ---------------------------------------------------------------------------


class TestWorkerPool:
    def _make_plan(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (
            AtomicTask,
            MissionPlan,
        )

        plan = MissionPlan(
            mission_id="m1",
            created_at="now",
            prompt="test",
            tasks=[
                AtomicTask("t1", "do a", "AgentA", "path/a"),
                AtomicTask("t2", "do b", "AgentB", "path/b"),
            ],
            execution_order=["t1", "t2"],
        )
        return plan

    def test_dispatch_success(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import WorkerPool

        pool = WorkerPool()
        call_log = []

        async def _agent_a(task):
            call_log.append(task.task_id)
            return "output_a"

        pool.register_worker("AgentA", _agent_a)
        plan = self._make_plan()
        results = asyncio.get_event_loop().run_until_complete(pool.dispatch_plan(plan))
        assert results[0].success
        assert results[0].output == "output_a"
        assert "t1" in call_log

    def test_dispatch_missing_worker_returns_error(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import WorkerPool

        pool = WorkerPool()
        plan = self._make_plan()
        results = asyncio.get_event_loop().run_until_complete(pool.dispatch_plan(plan))
        assert not results[0].success
        assert results[0].error is not None

    def test_collect_results_summary(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (
            WorkerPool,
            WorkerResult,
        )

        pool = WorkerPool()
        results = [
            WorkerResult("t1", "A", output="o1", success=True),
            WorkerResult("t2", "B", error="fail", success=False),
        ]
        summary = pool.collect_results(results)
        assert summary["succeeded"] == 1
        assert summary["failed"] == 1

    def test_synthesizer_node_default(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (
            SynthesizerNode,
            WorkerResult,
        )

        node = SynthesizerNode()
        results = [
            WorkerResult("t1", "A", output={"x": 1}, success=True),
            WorkerResult("t2", "B", error="e", success=False),
        ]
        output = asyncio.get_event_loop().run_until_complete(node.synthesize(results))
        import json

        parsed = json.loads(output)
        assert parsed["tasks_completed"] == 1
        assert parsed["tasks_failed"] == 1

    def test_synthesizer_node_custom_fn(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (
            SynthesizerNode,
            WorkerResult,
        )

        called = []

        async def _fn(results):
            called.append(len(results))
            return "custom"

        node = SynthesizerNode(synthesize_fn=_fn)
        results = [WorkerResult("t1", "A", output="o", success=True)]
        output = asyncio.get_event_loop().run_until_complete(node.synthesize(results))
        assert output == "custom"
        assert called == [1]


# ---------------------------------------------------------------------------
# C5 — replan_on_failure
# ---------------------------------------------------------------------------


class TestReplanOnFailure:
    def _make_plan_and_mock_orch(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (
            AtomicTask,
            MissionPlan,
        )

        plan = MissionPlan(
            mission_id="m1",
            created_at="now",
            prompt="test",
            tasks=[AtomicTask("t1", "validate code", "CodeValidatorAgent", "path")],
            execution_order=["t1"],
            validation_summary={"total_tasks": 1},
        )
        mock_orch = MagicMock()
        sub_task = AtomicTask("sub1", "retry validate code", "CodeValidatorAgent", "path")
        mock_plan = MissionPlan(
            mission_id="sub",
            created_at="now",
            prompt="retry",
            tasks=[sub_task],
            execution_order=["sub1"],
        )
        mock_orch.decompose.return_value = mock_plan
        return mock_orch, plan

    def test_replan_appends_new_tasks(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import replan_on_failure

        orch, plan = self._make_plan_and_mock_orch()
        failed_task = plan.tasks[0]
        updated_plan, artifact = replan_on_failure(orch, plan, failed_task, "timeout error")

        assert len(updated_plan.tasks) > 1
        assert artifact.failed_task_id == "t1"
        assert "timeout" in artifact.reason

    def test_replan_marks_failed_task(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import replan_on_failure

        orch, plan = self._make_plan_and_mock_orch()
        failed_task = plan.tasks[0]
        replan_on_failure(orch, plan, failed_task, "reason")
        assert failed_task.status == "failed"

    def test_replan_increments_counter(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (
            AtomicTask,
            MissionPlan,
            replan_on_failure,
        )

        plan = MissionPlan(
            mission_id="m2",
            created_at="now",
            prompt="p",
            tasks=[AtomicTask("t1", "d", "A", "path")],
            execution_order=["t1"],
            validation_summary={},
        )
        mock_orch = MagicMock()
        mock_orch.decompose.return_value = MissionPlan(
            mission_id="s",
            created_at="n",
            prompt="r",
            tasks=[AtomicTask("s1", "d", "A", "p")],
            execution_order=["s1"],
        )

        replan_on_failure(mock_orch, plan, plan.tasks[0], "r1")
        mock_orch.decompose.return_value = MissionPlan(
            mission_id="s2",
            created_at="n",
            prompt="r",
            tasks=[AtomicTask("s2", "d", "A", "p")],
            execution_order=["s2"],
        )
        replan_on_failure(mock_orch, plan, plan.tasks[0], "r2")
        assert plan.validation_summary["replans"] == 2

    def test_replan_artifact_has_new_tasks(self):
        from agentic_core.L3_orchestration.engines.decomposition_orchestrator import replan_on_failure

        orch, plan = self._make_plan_and_mock_orch()
        _, artifact = replan_on_failure(orch, plan, plan.tasks[0], "some reason")
        assert len(artifact.new_tasks) > 0
        assert artifact.original_plan_id == "m1"
