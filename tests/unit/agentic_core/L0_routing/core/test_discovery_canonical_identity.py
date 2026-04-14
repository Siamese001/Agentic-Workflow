"""Runtime-hardened top-level export tests for discovery canonical identity."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def agentic_core_package():
    return pytest.importorskip("agentic_core")


class TestDiscoveryCanonicalIdentity:
    def test_module_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "discovery_canonical_identity", None) is not None

    def test_class_is_exposed(self, agentic_core_package):
        assert getattr(agentic_core_package, "DiscoveryCanonicalIdentity", None) is not None

    def test_validator_is_callable(self, agentic_core_package):
        validator = getattr(agentic_core_package, "validate_discovery_canonical_identity", None)
        assert callable(validator)
