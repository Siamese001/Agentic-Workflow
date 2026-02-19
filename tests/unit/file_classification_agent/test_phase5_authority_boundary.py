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
        o_dir = tmp_path / "agentic_core" / "L3_orchestration" / "reasoning"
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
