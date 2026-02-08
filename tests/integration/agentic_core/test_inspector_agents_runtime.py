"""
Integration tests: verify inspector agents at runtime with full dependencies.

These tests require pydantic to be installed (transitive dep via agentic_core).
Run with: pytest -m integration_full_deps

Tests verify:
    1. InspectionCapability mixin works end-to-end with InspectionResult
    2. Decorator canonical imports work at runtime with full dep chain
    3. Real agent modules are importable (xfail where MRO defects exist)

To install required deps: pip install pydantic

BEHAVIOR:
- When run with INTEGRATION_FULL_DEPS_REQUIRED=1 and pydantic is missing: FAIL
- When run without explicit env var: skip if deps missing
"""

from __future__ import annotations

import os
from typing import Any

import pytest

# Check if pydantic is available
try:
    import pydantic  # noqa: F401

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


# If integration explicitly required and pydantic is missing, FAIL immediately
if os.environ.get("INTEGRATION_FULL_DEPS_REQUIRED", "0") == "1" and not PYDANTIC_AVAILABLE:
    pytest.fail(
        "integration_full_deps tests require pydantic. Install with: pip install pydantic",
        pytrace=False,
    )

pytestmark = [
    pytest.mark.integration_full_deps,
    pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="pydantic not installed"),
]


# ---------------------------------------------------------------------------
# Test: InspectionCapability end-to-end
# ---------------------------------------------------------------------------


class TestInspectionCapabilityEndToEnd:
    """Verify InspectionCapability mixin produces InspectionResult at runtime."""

    def test_inspection_result_importable(self) -> None:
        from agentic_core.mixins.inspection_capability import InspectionResult

        result = InspectionResult()
        assert result.healthy is True
        assert result.issues == []
        assert result.metrics == {}

    def test_inspection_capability_importable(self) -> None:
        from agentic_core.mixins.inspection_capability import InspectionCapability

        assert hasattr(InspectionCapability, "run_inspection")
        assert hasattr(InspectionCapability, "perform_checks")

    def test_run_inspection_produces_result(self) -> None:
        """Build a minimal agent using InspectionCapability and verify it works."""
        from agentic_core.mixins.inspection_capability import (
            InspectionCapability,
            InspectionResult,
        )

        class _TestInspector(InspectionCapability):
            INSPECTION_LOG_PREFIX = "Test inspection"

            def perform_checks(
                self,
                target: Any,
                context: dict[str, Any] | None = None,
            ) -> tuple[list[str], dict[str, Any]]:
                return [], {"scanned": 1}

        inspector = _TestInspector()
        result = inspector.run_inspection("dummy_target")

        assert isinstance(result, InspectionResult)
        assert result.healthy is True
        assert result.metrics == {"scanned": 1}

    def test_run_inspection_with_issues(self) -> None:
        from agentic_core.mixins.inspection_capability import (
            InspectionCapability,
            InspectionResult,
        )

        class _FailingInspector(InspectionCapability):
            INSPECTION_LOG_PREFIX = "Failing inspection"

            def perform_checks(
                self,
                target: Any,
                context: dict[str, Any] | None = None,
            ) -> tuple[list[str], dict[str, Any]]:
                return ["violation-1"], {"checked": 5}

        inspector = _FailingInspector()
        result = inspector.run_inspection("target")

        assert isinstance(result, InspectionResult)
        assert result.healthy is False
        assert len(result.issues) == 1


# ---------------------------------------------------------------------------
# Test: Decorator canonical imports work at runtime
# ---------------------------------------------------------------------------


class TestDecoratorRuntimeImports:
    """Verify canonical decorator imports work with full dep chain loaded."""

    def test_standard_heal_importable_with_full_deps(self) -> None:
        from agentic_core.base_agents.decorators import standard_heal

        assert callable(standard_heal)

    def test_timeout_importable_with_full_deps(self) -> None:
        from agentic_core.base_agents.timeout_decorator import timeout

        decorator = timeout(30)
        assert callable(decorator)

    def test_shim_identity_with_full_deps(self) -> None:
        from agentic_core.base_agents.decorators import standard_heal as canonical
        from agentic_core.L5_safety.utils.decorators_util import (
            standard_heal as shim,
        )

        assert shim is canonical

    def test_timeout_shim_identity_with_full_deps(self) -> None:
        from agentic_core.base_agents.timeout_decorator import timeout as canonical
        from agentic_core.L0_maintenance.utils.timeout_decorator_util import (
            timeout as shim,
        )

        assert shim is canonical


# ---------------------------------------------------------------------------
# Test: Real inspector agent modules (xfail for known MRO defects)
# ---------------------------------------------------------------------------


class TestInspectorAgentImports:
    """Test real inspector agent imports. Known MRO issues are marked xfail."""

    @pytest.mark.xfail(
        reason="Pre-existing MRO defect: SubatomicTestingMixin + SovereignBaseAgent",
        strict=True,
    )
    def test_dag_runtime_inspector_importable(self) -> None:
        from agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent import (
            DagRuntimeInspectorAgent,
        )

        assert DagRuntimeInspectorAgent is not None

    @pytest.mark.xfail(
        reason="Pre-existing MRO defect: SubatomicTestingMixin + SovereignBaseAgent",
        strict=True,
    )
    def test_token_budget_inspector_importable(self) -> None:
        from agentic_core.L5_safety.reasoning.TokenBudgetInspectorAgent import (
            TokenBudgetInspectorAgent,
        )

        assert TokenBudgetInspectorAgent is not None

    @pytest.mark.xfail(
        reason="Pre-existing MRO defect: SubatomicTestingMixin + SovereignBaseAgent",
        strict=True,
    )
    def test_signature_verifier_importable(self) -> None:
        from agentic_core.L5_safety.reasoning.SignatureVerifierAgent import (
            SignatureVerifierAgent,
        )

        assert SignatureVerifierAgent is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
