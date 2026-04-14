"""Runtime-hardened top-level export tests for determinism contracts types ADG."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def agentic_core_package():
    return pytest.importorskip("agentic_core")


class TestExports:
    def test_module_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "determinism_contracts_types_adg", None) is not None

    def test_class_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "DeterminismContractsTypesAdg", None) is not None

    def test_validator_is_callable(self, agentic_core_package):
        validator = getattr(agentic_core_package, "validate_determinism_contracts_types_adg", None)
        assert callable(validator)
