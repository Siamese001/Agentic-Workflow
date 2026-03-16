"""Phase 4: Stability & Regression Guardrails.

Tests verify:
- Classification determinism (same file => same result across N runs)
- Stats dict key stability (expected keys present after classification)
- Classification order independence (A,B vs B,A yields same results)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L3_ORCHESTRATION_DIR,
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
)

_emit_records_execution_trace("p0", "evidence", "test_stability_guardrails")
_emit_applies_guardrail("p0", "test_stability_guardrails", "p0_governance")
_emit_reads_policy_state("p0", "test_stability_guardrails", "policy_binding")
_emit_snapshots_state("p0", "test_stability_guardrails", "state_snapshot")
emit_replay_key("p0", "test_stability_guardrails")
emit_determinism_digest("p0", "test_stability_guardrails")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_stability_guardrails", "execution_auth")
_emit_validates_capability("p2", "test_stability_guardrails", "capability_check")
_emit_routes_to_capability("p2", "test_stability_guardrails", "capability_route")
_emit_writes_via_uwg("p2", "test_stability_guardrails", "uwg_write")
_emit_blocks_direct_write("p2", "test_stability_guardrails", "direct_write_block")
_emit_records_tool_invocation("p2", "test_stability_guardrails", "tool_invocation")
_emit_captures_execution_output("p2", "test_stability_guardrails", "exec_output")
_emit_dispatches_agent("p3", "test_stability_guardrails", "agent_dispatch")
_emit_coordinates_agents("p3", "test_stability_guardrails", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_stability_guardrails", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_stability_guardrails", "healing_outcome")
_emit_escalates_failure("p3", "test_stability_guardrails", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_stability_guardrails", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_stability_guardrails", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_stability_guardrails", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_stability_guardrails", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_stability_guardrails", "eval_metric")
_emit_stores_embedding("p4", "test_stability_guardrails", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_stability_guardrails", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_stability_guardrails", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_file(tmp_path: Path, name: str, code: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(code), encoding="utf-8")
    return p


def _new_fca(tmp_path: Path):
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    return FileClassificationAgent(
        project_root=tmp_path,
        dry_run=True,
        validate_only=True,
    )


# ---------------------------------------------------------------------------
# Test 1: Determinism — same file classified 10 times => identical result
# ---------------------------------------------------------------------------


class TestClassificationDeterminism:
    def test_repeated_classification_is_stable(self, tmp_path):
        code = """\
        from engines import handler_engine
        class RequestRouter:
            def route_to(self, target):
                return target.handle()
        """
        p = _make_file(tmp_path, "request_router.py", code)
        fca = _new_fca(tmp_path)

        results = [fca.classify_file(p) for _ in range(10)]
        assert len(set(results)) == 1, f"Non-deterministic: got {set(results)}"
        assert results[0] == "ENGINE"

    def test_orchestrator_determinism(self, tmp_path):
        o_dir = tmp_path / L3_ORCHESTRATION_DIR / "reasoning"
        o_dir.mkdir(parents=True, exist_ok=True)
        code = """\
        from agentic_core.L3_orchestration.reasoning import AgentA
        from agentic_core.L5_safety.enforcement import GuardB
        class WorkflowOrchestrator:
            def run_pipeline(self):
                self.stage_1()
                self.stage_2()
            def stage_1(self): pass
            def stage_2(self): pass
            def dispatch_to_agents(self): pass
        """
        p = o_dir / "workflow_orchestrator.py"
        p.write_text(textwrap.dedent(code), encoding="utf-8")
        fca = _new_fca(tmp_path)

        results = [fca.classify_file(p) for _ in range(10)]
        assert len(set(results)) == 1
        assert results[0] == "ORCHESTRATOR"


# ---------------------------------------------------------------------------
# Test 2: Stats dict key stability
# ---------------------------------------------------------------------------


class TestStatsDictKeyStability:
    def test_violations_keys_present(self, tmp_path):
        code = """\
        class Dummy:
            pass
        """
        p = _make_file(tmp_path, "dummy_class.py", code)
        fca = _new_fca(tmp_path)
        fca.classify_file(p)

        v = fca.stats["violations"]
        # Phase 1 keys
        assert "ENFORCER" in v
        assert "SEAM" in v
        assert "EXCEPTION" in v
        # Phase 2 keys
        assert "ORCHESTRATOR_INVARIANT_FAIL" in v
        oif = v["ORCHESTRATOR_INVARIANT_FAIL"]
        assert "mutation_hard" in oif
        assert "mutation_soft" in oif
        assert "thin_wrapper" in oif
        assert "insufficient_roles" in oif
        assert "ORCHESTRATOR_LAYER_MISALIGNMENT" in v
        # Phase 3 keys
        assert "ROUTER_INVARIANT_FAIL" in v
        rif = v["ROUTER_INVARIANT_FAIL"]
        assert "mutation" in rif
        assert "workflow" in rif
        assert "inheritance" in rif
        assert "structure" in rif

    def test_stats_territory_moves_exists(self, tmp_path):
        code = """\
        class Dummy:
            pass
        """
        p = _make_file(tmp_path, "dummy2.py", code)
        fca = _new_fca(tmp_path)
        fca.classify_file(p)
        assert "territory_moves" in fca.stats


# ---------------------------------------------------------------------------
# Test 3: Order independence
# ---------------------------------------------------------------------------


class TestClassificationOrderIndependence:
    def test_order_does_not_affect_results(self, tmp_path):
        router_code = """\
        from engines import handler_engine
        class MyRouter:
            def route_to(self, t): return t
        """
        enforcer_code = """\
        class AccessEnforcer:
            GATE_POLICY = True
            def enforce(self, ctx):
                if not ctx.ok:
                    raise PermissionError("no")
        """
        orchestrator_code = """\
        from agentic_core.L3_orchestration.reasoning import AgentA
        from agentic_core.L5_safety.enforcement import GuardB
        class WorkflowOrchestrator:
            def run_pipeline(self):
                self.stage_1()
                self.stage_2()
            def stage_1(self): pass
            def stage_2(self): pass
            def dispatch_to_agents(self): pass
        """

        r = _make_file(tmp_path, "my_router.py", router_code)
        e = _make_file(tmp_path, "access_enforcer.py", enforcer_code)
        o_dir = tmp_path / L3_ORCHESTRATION_DIR / "reasoning"
        o_dir.mkdir(parents=True, exist_ok=True)
        o = o_dir / "workflow_orchestrator.py"
        o.write_text(textwrap.dedent(orchestrator_code), encoding="utf-8")

        # Order A: router, enforcer, orchestrator
        fca_a = _new_fca(tmp_path)
        ra = (fca_a.classify_file(r), fca_a.classify_file(e), fca_a.classify_file(o))

        # Order B: orchestrator, enforcer, router
        fca_b = _new_fca(tmp_path)
        rb = (fca_b.classify_file(o), fca_b.classify_file(e), fca_b.classify_file(r))

        # Results should be identical regardless of order
        assert ra[0] == rb[2], f"Router: {ra[0]} vs {rb[2]}"
        assert ra[1] == rb[1], f"Enforcer: {ra[1]} vs {rb[1]}"
        assert ra[2] == rb[0], f"Orchestrator: {ra[2]} vs {rb[0]}"
