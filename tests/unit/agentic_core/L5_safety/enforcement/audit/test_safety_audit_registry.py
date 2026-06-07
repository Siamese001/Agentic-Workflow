"""Surface coverage for `agentic_core.L5_safety.enforcement.audit.safety_audit_registry`.

Wave 10 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3). L5
audit registry — durable record of safety decisions and human reviews.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.audit.safety_audit_registry"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_resolvable(mod):
    assert hasattr(mod, "__all__")
    missing = [n for n in mod.__all__ if not hasattr(mod, n)]
    assert not missing, f"__all__ leaks unresolved: {missing}"


@pytest.mark.parametrize(
    "name",
    [
        "SafetyAuditRecord",
        "HumanReviewAuditRecord",
        "SafetyAuditRegistry",
        "SafetyAuditMissingError",
        "HumanReviewAuditError",
        "AuditQueryError",
    ],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


def test_error_classes_inherit_exception(mod):
    for name in ("SafetyAuditMissingError", "HumanReviewAuditError", "AuditQueryError"):
        assert issubclass(getattr(mod, name), Exception)


def test_registry_singleton_seam(mod):
    assert callable(mod.get_safety_audit_registry)
    assert callable(mod.reset_safety_audit_registry)
    mod.reset_safety_audit_registry()
    reg = mod.get_safety_audit_registry()
    assert reg is not None
    assert isinstance(reg, mod.SafetyAuditRegistry)
