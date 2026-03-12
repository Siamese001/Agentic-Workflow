"""ADG-driven tests for utils/meta_learning_engine_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.utils.meta_learning_engine_util import MetaLearningEngine


class TestMetaLearningEngine:
    def test_importable(self):
        assert callable(MetaLearningEngine)

    def test_kg_bridge_default_none(self):
        assert MetaLearningEngine._kg_bridge is None

    def test_has_ensure_kg_connection(self):
        assert hasattr(MetaLearningEngine, "ensure_kg_connection")

    def test_is_class(self):
        assert isinstance(MetaLearningEngine, type)
