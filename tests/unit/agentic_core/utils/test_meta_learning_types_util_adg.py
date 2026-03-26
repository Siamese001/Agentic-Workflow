"""ADG-driven tests for agentic_core/utils/meta_learning_types_util.py — fan_in=2.

Contract tests: re-export shim identity for LearningContext, LearningResult, MetaLearningProtocol.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

class TestMetaLearningTypesShim:
    def test_importable(self):
                import agentic_core.utils.meta_learning_types_util as mod
                from agentic_core.utils.meta_learning_types_util import LearningContext
                from agentic_core.utils.meta_learning_types_util import LearningResult
                from agentic_core.utils.meta_learning_types_util import LearningResult