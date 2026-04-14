"""Runtime-hardened public-surface tests for FilesystemSSOTReconcilerAgent."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

MODULE_CANDIDATES = ["filesystem_ssot_reconciler_agent", "FilesystemSSOTReconcilerAgent"]
CLASS_CANDIDATES = ["FilesystemSSOTReconcilerAgent", "FilesystemSsotReconcilerAgent"]
VALIDATOR_CANDIDATES = ["validate_filesystem_ssot_reconciler_agent", "validate_FilesystemSSOTReconcilerAgent"]


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
