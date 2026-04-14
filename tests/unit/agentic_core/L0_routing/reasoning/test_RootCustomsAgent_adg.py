"""Runtime-hardened public-surface tests for RootCustomsAgent adg."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

MODULE_CANDIDATES = ["root_customs_agent_adg", "RootCustomsAgent_adg"]
CLASS_CANDIDATES = ["RootCustomsAgent_adg", "RootCustomsAgentAdg"]
VALIDATOR_CANDIDATES = ["validate_root_customs_agent_adg", "validate_RootCustomsAgent_adg"]


@pytest.fixture(scope="module")
def agentic_core_package():
    return pytest.importorskip("agentic_core")


def _resolve_first(package, candidates):
    for name in candidates:
        value = getattr(package, name, None)
        if value is not None:
            return name, value
    return None, None


class TestPublicSurface:
    def test_module_export_exists(self, agentic_core_package):
        name, value = _resolve_first(agentic_core_package, MODULE_CANDIDATES)
        assert value is not None, f"Expected one of {MODULE_CANDIDATES} on agentic_core, found none"

    def test_class_export_exists(self, agentic_core_package):
        name, value = _resolve_first(agentic_core_package, CLASS_CANDIDATES)
        assert value is not None, f"Expected one of {CLASS_CANDIDATES} on agentic_core, found none"

    def test_validator_export_is_callable(self, agentic_core_package):
        name, value = _resolve_first(agentic_core_package, VALIDATOR_CANDIDATES)
        assert callable(value), f"Expected callable validator from {VALIDATOR_CANDIDATES}, found none"
