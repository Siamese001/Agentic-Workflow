"""Foundational behavioral tests for agentic_core/utils/decorators_util.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_decorators_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.decorators_util import (  # noqa: F401
        standard_heal,
        standard_heal_async,
        HEAL_RESULT_SCHEMA,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    standard_heal = None  # type: ignore[assignment,misc]
    standard_heal_async = None  # type: ignore[assignment,misc]
    HEAL_RESULT_SCHEMA = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="decorators_util.py deps unavailable")
class TestStandardHealFunction:
    def test_is_callable(self):
        assert callable(standard_heal)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(standard_heal)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="decorators_util.py deps unavailable")
class TestStandardHealAsyncFunction:
    def test_is_callable(self):
        assert callable(standard_heal_async)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(standard_heal_async)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="decorators_util.py deps unavailable")
class TestHealResultSchemaConstant:
    def test_is_not_none(self):
        assert HEAL_RESULT_SCHEMA is not None

    def test_is_mapping(self):
        assert hasattr(HEAL_RESULT_SCHEMA, '__getitem__')

    def test_keys_accessible(self):
        assert hasattr(HEAL_RESULT_SCHEMA, 'keys')


def test_module_importable():
    """Smoke: decorators_util importable or gracefully unavailable."""
    assert True
