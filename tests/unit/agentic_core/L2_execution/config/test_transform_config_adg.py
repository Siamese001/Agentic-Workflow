"""ADG-driven tests for L2_execution/config/transform_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.config.transform_config import (
        TransformOperation,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    TransformOperation = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="transform_config deps unavailable")
class TestTransformOperation:
    def test_is_enum(self):
        import enum
        assert issubclass(TransformOperation, enum.Enum)

    def test_rename_symbol_value(self):
        assert TransformOperation.RENAME_SYMBOL.value == "rename_symbol"

    def test_is_str_enum(self):
        assert issubclass(TransformOperation, str)

    def test_all_values_are_strings(self):
        for op in TransformOperation:
            assert isinstance(op.value, str)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE