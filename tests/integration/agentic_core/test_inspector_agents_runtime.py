"""
Integration tests: verify inspector agents at runtime with full dependencies.

These tests require pydantic to be installed (transitive dep via agentic_core).
Run with: pytest tests/integration/ -q

Tests verify:
    1. Real inspector agents import and instantiate (MRO resolved)
    2. InspectionCapability.run_inspection() returns InspectionResult
    3. Decorator canonical imports work at runtime with full dep chain
    4. Shim identity holds at runtime

To install required deps: pip install pydantic
"""

from __future__ import annotations

import os

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
# Test: Real inspector agents import, instantiate, and run_inspection
# ---------------------------------------------------------------------------


class TestDagRuntimeInspectorAgent:
    """Validate DagRuntimeInspectorAgent imports and runs diagnostics."""

    def test_importable(self) -> None:
        from agentic_core.L3_orchestration.engines.DagRuntimeInspectorAgent import (
            DagRuntimeInspectorAgent,
        )

        assert DagRuntimeInspectorAgent is not None

    def test_diagnose_returns_inspection_result(self) -> None:
        from agentic_core.L3_orchestration.engines.DagRuntimeInspectorAgent import (
            DagRuntimeInspectorAgent,
        )
        from agentic_core.mixins.inspection_capability_mixin import InspectionResult

        agent = DagRuntimeInspectorAgent()
        result = agent.run_inspection("test_target")

        assert isinstance(result, InspectionResult)
        assert isinstance(result.healthy, bool)
        assert isinstance(result.issues, list)
        assert isinstance(result.metrics, dict)


class TestTokenBudgetInspectorAgent:
    """Validate TokenBudgetInspectorAgent imports and runs diagnostics."""

    def test_importable(self) -> None:
        from agentic_core.L5_safety.reasoning.TokenBudgetInspectorAgent import (
            TokenBudgetInspectorAgent,
        )

        assert TokenBudgetInspectorAgent is not None

    def test_run_inspection_returns_inspection_result(self) -> None:
        from agentic_core.L5_safety.reasoning.TokenBudgetInspectorAgent import (
            TokenBudgetInspectorAgent,
        )
        from agentic_core.mixins.inspection_capability_mixin import InspectionResult

        agent = TokenBudgetInspectorAgent()
        result = agent.run_inspection("test_target")

        assert isinstance(result, InspectionResult)
        assert isinstance(result.healthy, bool)
        assert isinstance(result.issues, list)
        assert isinstance(result.metrics, dict)


class TestSignatureVerifierAgent:
    """Validate SignatureVerifierAgent imports and runs diagnostics."""

    def test_importable(self) -> None:
        from agentic_core.L5_safety.reasoning.SignatureVerifierAgent import (
            SignatureVerifierAgent,
        )

        assert SignatureVerifierAgent is not None

    def test_run_inspection_returns_inspection_result(self) -> None:
        from agentic_core.L5_safety.reasoning.SignatureVerifierAgent import (
            SignatureVerifierAgent,
        )
        from agentic_core.mixins.inspection_capability_mixin import InspectionResult

        agent = SignatureVerifierAgent()
        result = agent.run_inspection("test_target")

        assert isinstance(result, InspectionResult)
        assert isinstance(result.healthy, bool)
        assert isinstance(result.issues, list)
        assert isinstance(result.metrics, dict)


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
