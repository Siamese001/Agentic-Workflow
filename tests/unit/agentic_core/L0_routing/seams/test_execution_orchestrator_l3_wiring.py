"""Runtime-hardened top-level export tests for execution orchestrator L3 wiring."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def agentic_core_package():
    return pytest.importorskip("agentic_core")


class TestExecutionOrchestratorL3Wiring:
    def test_module_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "execution_orchestrator_l3_wiring", None) is not None

    def test_class_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "ExecutionOrchestratorL3Wiring", None) is not None

    def test_validator_is_callable(self, agentic_core_package):
        validator = getattr(agentic_core_package, "validate_execution_orchestrator_l3_wiring", None)
        assert callable(validator)
