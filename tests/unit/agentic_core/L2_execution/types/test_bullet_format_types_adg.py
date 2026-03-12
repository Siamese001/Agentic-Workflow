"""ADG-driven tests for L2_execution/types/bullet_format_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.bullet_format_types import BulletFormat, ProvenanceType


class TestBulletFormat:
    def test_is_enum(self):
        import enum
        assert issubclass(BulletFormat, enum.Enum)


class TestProvenanceType:
    def test_is_enum(self):
        import enum
        assert issubclass(ProvenanceType, enum.Enum)
