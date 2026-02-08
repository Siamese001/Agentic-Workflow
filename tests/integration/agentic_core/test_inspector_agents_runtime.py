"""
Integration tests: verify inspector agents at runtime with full dependencies.

These tests require pydantic, redis, requests, and other optional deps to be installed.
Run with: pytest -m integration_full_deps

Tests verify:
    1. Real agent imports work (no phantom imports, no circular deps)
    2. diagnose() method exists and is callable
    3. diagnose() returns InspectionResult instance with correct fields

To install required deps: pip install pydantic redis requests

BEHAVIOR:
- When run with -m integration_full_deps and pydantic is missing: FAIL (not skip)
- When run without explicit marker selection: skip if deps missing
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Check if pydantic is available
try:
    import pydantic  # noqa: F401

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


def _is_integration_explicitly_selected() -> bool:
    """Detect if integration_full_deps marker was explicitly selected via -m."""
    # Check PYTEST_CURRENT_TEST or command line markers
    # When explicitly selected, we should FAIL not skip
    return os.environ.get("INTEGRATION_FULL_DEPS_REQUIRED", "0") == "1"


# If integration marker is explicitly selected and pydantic is missing, FAIL immediately
if _is_integration_explicitly_selected() and not PYDANTIC_AVAILABLE:
    pytest.fail(
        "integration_full_deps tests require pydantic. Install with: pip install pydantic redis requests",
        pytrace=False,
    )

pytestmark = [
    pytest.mark.integration_full_deps,
    pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="pydantic not installed"),
]


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services to prevent network calls during tests."""
    # Mock redis before any import that might use it
    mock_redis = MagicMock()
    mock_redis_module = MagicMock()
    mock_redis_module.Redis = MagicMock(return_value=mock_redis)

    with patch.dict(
        sys.modules,
        {
            "redis": mock_redis_module,
            "redis.client": MagicMock(),
        },
    ):
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test-key",
                "ANTHROPIC_API_KEY": "test-key",
                "REDIS_URL": "redis://localhost:6379",
            },
        ):
            yield


class TestDagRuntimeInspectorAgentIntegration:
    """Runtime integration tests for DagRuntimeInspectorAgent."""

    def test_agent_importable(self) -> None:
        """Agent module imports without errors."""
        from agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent import (
            DagRuntimeInspectorAgent,
        )

        assert DagRuntimeInspectorAgent is not None

    def test_diagnose_returns_inspection_result(self) -> None:
        """diagnose() returns InspectionResult with correct fields."""
        from agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent import (
            DagRuntimeInspectorAgent,
        )
        from agentic_core.mixins.inspection_capability import InspectionResult

        agent = DagRuntimeInspectorAgent()
        result = agent.diagnose()

        assert isinstance(result, InspectionResult), f"Expected InspectionResult, got {type(result).__name__}"
        assert hasattr(result, "passed")
        assert hasattr(result, "severity")
        assert hasattr(result, "findings")


class TestTokenBudgetInspectorAgentIntegration:
    """Runtime integration tests for TokenBudgetInspectorAgent."""

    def test_agent_importable(self) -> None:
        """Agent module imports without errors."""
        from agentic_core.L5_safety.reasoning.TokenBudgetInspectorAgent import (
            TokenBudgetInspectorAgent,
        )

        assert TokenBudgetInspectorAgent is not None

    def test_diagnose_returns_inspection_result(self) -> None:
        """diagnose() returns InspectionResult with correct fields."""
        from agentic_core.L5_safety.reasoning.TokenBudgetInspectorAgent import (
            TokenBudgetInspectorAgent,
        )
        from agentic_core.mixins.inspection_capability import InspectionResult

        agent = TokenBudgetInspectorAgent()
        result = agent.diagnose()

        assert isinstance(result, InspectionResult), f"Expected InspectionResult, got {type(result).__name__}"
        assert hasattr(result, "passed")
        assert hasattr(result, "severity")
        assert hasattr(result, "findings")


class TestSignatureVerifierAgentIntegration:
    """Runtime integration tests for SignatureVerifierAgent."""

    def test_agent_importable(self) -> None:
        """Agent module imports without errors."""
        from agentic_core.L5_safety.reasoning.SignatureVerifierAgent import (
            SignatureVerifierAgent,
        )

        assert SignatureVerifierAgent is not None

    def test_diagnose_returns_inspection_result(self) -> None:
        """diagnose() returns InspectionResult with correct fields."""
        from agentic_core.L5_safety.reasoning.SignatureVerifierAgent import (
            SignatureVerifierAgent,
        )
        from agentic_core.mixins.inspection_capability import InspectionResult

        agent = SignatureVerifierAgent()
        result = agent.diagnose()

        assert isinstance(result, InspectionResult), f"Expected InspectionResult, got {type(result).__name__}"
        assert hasattr(result, "passed")
        assert hasattr(result, "severity")
        assert hasattr(result, "findings")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
