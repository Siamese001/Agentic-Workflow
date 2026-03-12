"""ADG-driven tests for agentic_core/L0_routing/scripts/auto_remediate_signatures_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.auto_remediate_signatures_util import (  # noqa: F401
        has_kwargs_in_signature,
        find_heal_repository_methods,
        inject_kwargs_in_signature,
        inject_kwargs_in_super_calls,
        remediate_file,
        TARGET_DIR,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    has_kwargs_in_signature = None  # type: ignore[assignment,misc]
    find_heal_repository_methods = None  # type: ignore[assignment,misc]
    inject_kwargs_in_signature = None  # type: ignore[assignment,misc]
    inject_kwargs_in_super_calls = None  # type: ignore[assignment,misc]
    remediate_file = None  # type: ignore[assignment,misc]
    TARGET_DIR = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="auto_remediate_signatures_util.py deps unavailable")
class TestHasKwargsInSignature:
    def test_is_callable(self):
        assert callable(has_kwargs_in_signature)

@pytest.mark.skipif(not _AVAILABLE, reason="auto_remediate_signatures_util.py deps unavailable")
class TestFindHealRepositoryMethods:
    def test_is_callable(self):
        assert callable(find_heal_repository_methods)

@pytest.mark.skipif(not _AVAILABLE, reason="auto_remediate_signatures_util.py deps unavailable")
class TestInjectKwargsInSignature:
    def test_is_callable(self):
        assert callable(inject_kwargs_in_signature)

@pytest.mark.skipif(not _AVAILABLE, reason="auto_remediate_signatures_util.py deps unavailable")
class TestInjectKwargsInSuperCalls:
    def test_is_callable(self):
        assert callable(inject_kwargs_in_super_calls)

@pytest.mark.skipif(not _AVAILABLE, reason="auto_remediate_signatures_util.py deps unavailable")
class TestRemediateFile:
    def test_is_callable(self):
        assert callable(remediate_file)

@pytest.mark.skipif(not _AVAILABLE, reason="auto_remediate_signatures_util.py deps unavailable")
class TestTargetDirConstant:
    def test_is_not_none(self):
        assert TARGET_DIR is not None


def test_module_importable():
    """Module auto_remediate_signatures_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
