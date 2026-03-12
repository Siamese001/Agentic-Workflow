"""ADG-driven tests for agentic_core/utils/meta_learning_types_util.py — fan_in=2.

Contract tests: re-export shim identity for LearningContext, LearningResult, MetaLearningProtocol.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestMetaLearningTypesShim:
    def test_importable(self):
        import agentic_core.utils.meta_learning_types_util as mod
        assert mod is not None

    def test_learning_context_exported(self):
        from agentic_core.utils.meta_learning_types_util import LearningContext
        assert callable(LearningContext)

    def test_learning_result_exported(self):
        from agentic_core.utils.meta_learning_types_util import LearningResult
        assert callable(LearningResult)

    def test_meta_learning_protocol_exported(self):
        from agentic_core.utils.meta_learning_types_util import MetaLearningProtocol
        assert callable(MetaLearningProtocol)

    def test_all_list_complete(self):
        from agentic_core.utils.meta_learning_types_util import __all__
        for name in ("LearningContext", "LearningResult", "MetaLearningProtocol"):
            assert name in __all__

    def test_identity_matches_canonical(self):
        from agentic_core.utils.meta_learning_types_util import LearningContext as shim
        from agentic_core.L5_safety.types.meta_learning_types import LearningContext as canon
        assert shim is canon
