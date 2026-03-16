"""Phase 5: Authority-Boundary Validation Sweep.

Tests verify cross-type classification boundaries:
- ENFORCER never classified as ORCHESTRATOR
- SEAM never classified as ORCHESTRATOR
- ORCHESTRATOR never classified as ENFORCER or SEAM
- ROUTER always ENGINE, never ORCHESTRATOR
- Negative: plain class not accidentally hardened
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

_emit_records_execution_trace("p0", "evidence", "test_authority_boundary")
_emit_applies_guardrail("p0", "test_authority_boundary", "p0_governance")
_emit_reads_policy_state("p0", "test_authority_boundary", "policy_binding")
_emit_snapshots_state("p0", "test_authority_boundary", "state_snapshot")
emit_replay_key("p0", "test_authority_boundary")
emit_determinism_digest("p0", "test_authority_boundary")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_authority_boundary", "execution_auth")
_emit_validates_capability("p2", "test_authority_boundary", "capability_check")
_emit_routes_to_capability("p2", "test_authority_boundary", "capability_route")
_emit_writes_via_uwg("p2", "test_authority_boundary", "uwg_write")
_emit_blocks_direct_write("p2", "test_authority_boundary", "direct_write_block")
_emit_records_tool_invocation("p2", "test_authority_boundary", "tool_invocation")
_emit_captures_execution_output("p2", "test_authority_boundary", "exec_output")
_emit_dispatches_agent("p3", "test_authority_boundary", "agent_dispatch")
_emit_coordinates_agents("p3", "test_authority_boundary", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_authority_boundary", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_authority_boundary", "healing_outcome")
_emit_escalates_failure("p3", "test_authority_boundary", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_authority_boundary", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_authority_boundary", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_authority_boundary", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_authority_boundary", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_authority_boundary", "eval_metric")
_emit_stores_embedding("p4", "test_authority_boundary", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_authority_boundary", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_authority_boundary", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_file(tmp_path: Path, name: str, code: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(code), encoding="utf-8")
    return p


def _classify(tmp_path: Path, file_path: Path):
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    fca = FileClassificationAgent(
        project_root=tmp_path,
        dry_run=True,
        validate_only=True,
    )
    return fca.classify_file(file_path)


# ---------------------------------------------------------------------------
# Boundary: ENFORCER must not be ORCHESTRATOR
# ---------------------------------------------------------------------------


class TestEnforcerBoundary:
    def test_enforcer_suffix_not_orchestrator(self, tmp_path):
        code = """\
        class PolicyEnforcer:
            GATE_POLICY = True
            def enforce(self, ctx):
                if not ctx.allowed:
                    raise PermissionError("blocked")
        """
        p = _make_file(tmp_path, "policy_enforcer.py", code)
        result = _classify(tmp_path, p)
        assert result != "ORCHESTRATOR", f"ENFORCER file misclassified as {result}"

    def test_guard_suffix_not_orchestrator(self, tmp_path):
        code = """\
        class AccessGuard:
            GATE_POLICY = True
            def check(self, req):
                return req.token is not None
        """
        p = _make_file(tmp_path, "access_guard.py", code)
        result = _classify(tmp_path, p)
        assert result != "ORCHESTRATOR"


# ---------------------------------------------------------------------------
# Boundary: SEAM must not be ORCHESTRATOR
# ---------------------------------------------------------------------------


class TestSeamBoundary:
    def test_seam_suffix_not_orchestrator(self, tmp_path):
        code = """\
        class DataSeam:
            def bridge(self, src, dst):
                return dst.accept(src.export())
        """
        p = _make_file(tmp_path, "data_seam.py", code)
        result = _classify(tmp_path, p)
        assert result != "ORCHESTRATOR"


# ---------------------------------------------------------------------------
# Boundary: ORCHESTRATOR must not be ENFORCER or SEAM
# ---------------------------------------------------------------------------


class TestOrchestratorBoundary:
    def test_orchestrator_not_enforcer(self, tmp_path):
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
        result = _classify(tmp_path, p)
        assert result not in ("ENFORCER", "SEAM"), f"ORCHESTRATOR misclassified as {result}"
        assert result == "ORCHESTRATOR"


# ---------------------------------------------------------------------------
# Boundary: ROUTER must be ENGINE, never ORCHESTRATOR
# ---------------------------------------------------------------------------


class TestRouterBoundary:
    def test_router_is_engine_not_orchestrator(self, tmp_path):
        code = """\
        from engines import handler_engine
        class RequestRouter:
            def route_to(self, target):
                return target.handle()
        """
        p = _make_file(tmp_path, "request_router.py", code)
        result = _classify(tmp_path, p)
        assert result == "ENGINE"
        assert result != "ORCHESTRATOR"

    def test_router_class_name_is_engine(self, tmp_path):
        code = """\
        class ApiRouter:
            def dispatch_to(self, endpoint):
                return endpoint.process()
        """
        p = _make_file(tmp_path, "api_dispatch_router.py", code)
        result = _classify(tmp_path, p)
        assert result == "ENGINE"


# ---------------------------------------------------------------------------
# Negative: plain class must not get hardened type
# ---------------------------------------------------------------------------


class TestNegativeBoundary:
    def test_plain_class_not_enforcer(self, tmp_path):
        code = """\
        class DataProcessor:
            def process(self, data):
                return [x * 2 for x in data]
        """
        p = _make_file(tmp_path, "data_processor.py", code)
        result = _classify(tmp_path, p)
        assert result not in ("ENFORCER", "SEAM", "ORCHESTRATOR")

    def test_plain_utility_not_router(self, tmp_path):
        code = """\
        def helper_func(x):
            return x + 1

        def another_func(y):
            return y * 2
        """
        p = _make_file(tmp_path, "math_helpers.py", code)
        result = _classify(tmp_path, p)
        assert result not in ("ENFORCER", "SEAM", "ORCHESTRATOR")
        assert result != "ENGINE"
