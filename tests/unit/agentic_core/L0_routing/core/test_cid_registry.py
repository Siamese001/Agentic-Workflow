"""Runtime-hardened CID registry surface tests."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def cid_registry_module():
    return pytest.importorskip("agentic_core.L2_execution.cid_registry")


class TestCidRegistry:
    def test_module_imports(self, cid_registry_module):
        assert cid_registry_module is not None

    def test_cid_registry_class_is_exposed(self, cid_registry_module):
        assert getattr(cid_registry_module, "CIDRegistry", None) is not None

    def test_register_cid_is_callable(self, cid_registry_module):
        assert callable(getattr(cid_registry_module, "register_cid", None))
