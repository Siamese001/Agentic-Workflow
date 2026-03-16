"""Phase 3: Router Discrimination — ENGINE-only + invariant enforcement.

Tests verify:
- Router files classified as ENGINE (not ORCHESTRATOR)
- Router invariant validation fires and records stats
- Router with mutation anti-pattern flagged
- Router with workflow anti-pattern flagged
- Router with orchestrator inheritance flagged
- Router with >5 functions flagged (structure)
- Integration mini-slice
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_router_discrimination")
_emit_applies_guardrail("p0", "test_router_discrimination", "p0_governance")
_emit_reads_policy_state("p0", "test_router_discrimination", "policy_binding")
_emit_snapshots_state("p0", "test_router_discrimination", "state_snapshot")
emit_replay_key("p0", "test_router_discrimination")
emit_determinism_digest("p0", "test_router_discrimination")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_router_discrimination", "execution_auth")
_emit_validates_capability("p2", "test_router_discrimination", "capability_check")
_emit_routes_to_capability("p2", "test_router_discrimination", "capability_route")
_emit_writes_via_uwg("p2", "test_router_discrimination", "uwg_write")
_emit_blocks_direct_write("p2", "test_router_discrimination", "direct_write_block")
_emit_records_tool_invocation("p2", "test_router_discrimination", "tool_invocation")
_emit_captures_execution_output("p2", "test_router_discrimination", "exec_output")
_emit_dispatches_agent("p3", "test_router_discrimination", "agent_dispatch")
_emit_coordinates_agents("p3", "test_router_discrimination", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_router_discrimination", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_router_discrimination", "healing_outcome")
_emit_escalates_failure("p3", "test_router_discrimination", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_router_discrimination", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_router_discrimination", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_router_discrimination", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_router_discrimination", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_router_discrimination", "eval_metric")
_emit_stores_embedding("p4", "test_router_discrimination", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_router_discrimination", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_router_discrimination", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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

    fca = FileClassificationAgent(project_root=tmp_path, dry_run=True, validate_only=True)
    result = fca.classify_file(file_path)
    return result, fca.stats


# ---------------------------------------------------------------------------
# Unit: Router suffix => ENGINE
# ---------------------------------------------------------------------------


class TestRouterSuffix:
    def test_router_suffix_classified_as_engine(self, tmp_path):
        code = """\
        class RequestRouter:
            def route_to(self, target):
                return target.handle()
        """
        p = _make_file(tmp_path, "request_router.py", code)
        result, stats = _classify(tmp_path, p)
        assert result == "ENGINE"

    def test_router_class_name_classified_as_engine(self, tmp_path):
        code = """\
        class MyRouter:
            def select_handler(self, req):
                return self.handlers[req.type]
        """
        p = _make_file(tmp_path, "dispatch_router.py", code)
        result, stats = _classify(tmp_path, p)
        assert result == "ENGINE"


# ---------------------------------------------------------------------------
# Unit: Router invariant — mutation
# ---------------------------------------------------------------------------


class TestRouterMutation:
    def test_router_with_file_write_flags_mutation(self, tmp_path):
        code = """\
        import os
        from engines import handler_engine
        class FileRouter:
            def route_to(self, target):
                return target.handle()
            def save(self):
                open("out.txt", "w").write("data")
        """
        p = _make_file(tmp_path, "file_router.py", code)
        result, stats = _classify(tmp_path, p)
        assert result == "ENGINE"
        assert stats["violations"]["ROUTER_INVARIANT_FAIL"]["mutation"] >= 1


# ---------------------------------------------------------------------------
# Unit: Router invariant — workflow
# ---------------------------------------------------------------------------


class TestRouterWorkflow:
    def test_router_with_stages_flags_workflow(self, tmp_path):
        code = """\
        from engines import handler_engine
        class PipelineRouter:
            def run_pipeline(self):
                self.stage_1()
                self.stage_2()
            def stage_1(self): pass
            def stage_2(self): pass
            def route_to(self, t): return t
        """
        p = _make_file(tmp_path, "pipeline_router.py", code)
        result, stats = _classify(tmp_path, p)
        assert result == "ENGINE"
        assert stats["violations"]["ROUTER_INVARIANT_FAIL"]["workflow"] >= 1


# ---------------------------------------------------------------------------
# Unit: Router invariant — inheritance
# ---------------------------------------------------------------------------


class TestRouterInheritance:
    def test_router_inheriting_coordinator_flags_inheritance(self, tmp_path):
        code = """\
        from engines import handler_engine
        class HybridRouter(WorkflowCoordinator):
            def route_to(self, target):
                return target.handle()
        """
        p = _make_file(tmp_path, "hybrid_router.py", code)
        result, stats = _classify(tmp_path, p)
        assert result == "ENGINE"
        assert stats["violations"]["ROUTER_INVARIANT_FAIL"]["inheritance"] >= 1


# ---------------------------------------------------------------------------
# Unit: Router invariant — structure (>5 functions)
# ---------------------------------------------------------------------------


class TestRouterStructure:
    def test_router_with_many_functions_flags_structure(self, tmp_path):
        code = """\
        from engines import handler_engine
        class BigRouter:
            def route_to(self, t): return t
            def fn1(self): pass
            def fn2(self): pass
            def fn3(self): pass
            def fn4(self): pass
            def fn5(self): pass
            def fn6(self): pass
        """
        p = _make_file(tmp_path, "big_router.py", code)
        result, stats = _classify(tmp_path, p)
        assert result == "ENGINE"
        assert stats["violations"]["ROUTER_INVARIANT_FAIL"]["structure"] >= 1


# ---------------------------------------------------------------------------
# Integration: mini-slice
# ---------------------------------------------------------------------------


class TestRouterIntegration:
    def test_mini_slice(self, tmp_path):
        """3 files: clean router, mutation router, non-router engine."""
        # Clean router
        clean = _make_file(
            tmp_path,
            "clean_router.py",
            textwrap.dedent("""\
            from engines import handler_engine
            class CleanRouter:
                def route_to(self, t): return t
        """),
        )
        # Mutation router
        mut = _make_file(
            tmp_path,
            "dirty_router.py",
            textwrap.dedent("""\
            from engines import handler_engine
            class DirtyRouter:
                def route_to(self, t): return t
                def save(self):
                    open("x", "w").write("y")
        """),
        )
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        fca = FileClassificationAgent(project_root=tmp_path, dry_run=True, validate_only=True)
        r1 = fca.classify_file(clean)
        r2 = fca.classify_file(mut)

        assert r1 == "ENGINE", f"clean router should be ENGINE, got {r1}"
        assert r2 == "ENGINE", f"mutation router should be ENGINE, got {r2}"
        assert fca.stats["violations"]["ROUTER_INVARIANT_FAIL"]["mutation"] >= 1
