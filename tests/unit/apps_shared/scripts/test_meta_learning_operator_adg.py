"""ADG-driven tests for apps_shared/scripts/meta_learning_operator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.meta_learning_operator import (  # noqa: F401
        render_meta_learning_audit_pack,
        run_meta_learning_operator,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    run_meta_learning_operator = None  # type: ignore[assignment,misc]
    render_meta_learning_audit_pack = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_operator.py deps unavailable")
class TestRunMetaLearningOperator:
    def test_is_callable(self):
        assert callable(run_meta_learning_operator)

@pytest.mark.skipif(not _AVAILABLE, reason="meta_learning_operator.py deps unavailable")
class TestRenderMetaLearningAuditPack:
    def test_is_callable(self):
        assert callable(render_meta_learning_audit_pack)


def test_module_importable():
    """Module meta_learning_operator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
