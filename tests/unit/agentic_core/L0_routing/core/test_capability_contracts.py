"""Runtime-hardened capability contract surface tests."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def agentic_core_package():
    return pytest.importorskip("agentic_core")


@pytest.fixture(scope="module")
def capability_contracts_module():
    return pytest.importorskip("agentic_core.capability_contracts")


class TestCapabilityContracts:
    def test_module_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "capability_contracts", None) is not None

    def test_capability_contract_class_is_exposed(self, capability_contracts_module):
        assert getattr(capability_contracts_module, "CapabilityContract", None) is not None

    def test_validate_capability_is_callable(self, capability_contracts_module):
        assert callable(getattr(capability_contracts_module, "validate_capability", None))
