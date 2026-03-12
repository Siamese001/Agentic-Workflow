"""ADG-driven tests for agentic_core/L1_cognition/__init__.py — fan_in=5.

Contract tests: all __all__ re-exports must be importable, have correct types,
and be identical to their canonical source in the types submodule.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestL1CognitionPublicAPI:
    def test_all_exports_present(self):
        import agentic_core.L1_cognition as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_action_request_importable(self):
        from agentic_core.L1_cognition import ActionRequest
        assert callable(ActionRequest)

    def test_action_result_importable(self):
        from agentic_core.L1_cognition import ActionResult
        assert callable(ActionResult)

    def test_planning_request_importable(self):
        from agentic_core.L1_cognition import PlanningRequest
        assert callable(PlanningRequest)

    def test_planning_result_importable(self):
        from agentic_core.L1_cognition import PlanningResult
        assert callable(PlanningResult)

    def test_package_docstring_present(self):
        import agentic_core.L1_cognition as m
        assert m.__doc__ is not None and "cognition" in m.__doc__.lower()


class TestL1CognitionShimIdentity:
    """Re-exports must be identical to canonical source types."""

    def test_action_request_same_object(self):
        from agentic_core.L1_cognition import ActionRequest as shim
        from agentic_core.L1_cognition.types.action_request_types import ActionRequest as canon
        assert shim is canon

    def test_action_result_same_object(self):
        from agentic_core.L1_cognition import ActionResult as shim
        from agentic_core.L1_cognition.types.action_request_types import ActionResult as canon
        assert shim is canon

    def test_planning_request_same_object(self):
        from agentic_core.L1_cognition import PlanningRequest as shim
        from agentic_core.L1_cognition.types.action_request_types import PlanningRequest as canon
        assert shim is canon

    def test_planning_result_same_object(self):
        from agentic_core.L1_cognition import PlanningResult as shim
        from agentic_core.L1_cognition.types.action_request_types import PlanningResult as canon
        assert shim is canon


class TestL1CognitionSovereigntyContract:
    """The L1 layer must contain NO execution or routing logic."""

    def test_no_write_gateway_import(self):
        """L1 must not import write_gateway (L2 execution module)."""
        import agentic_core.L1_cognition as m
        source = getattr(m, "__file__", "") or ""
        # Verify by checking the package's __init__ doesn't import write_gateway
        from pathlib import Path
        init_src = Path(source).read_text() if source else ""
        assert "write_gateway" not in init_src

    def test_reasoning_subpackage_exists(self):
        from pathlib import Path
        import agentic_core.L1_cognition as m
        pkg_dir = Path(m.__file__).parent
        assert (pkg_dir / "reasoning").is_dir()
