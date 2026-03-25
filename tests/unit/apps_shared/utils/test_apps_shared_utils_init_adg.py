"""ADG-driven tests for apps_shared/utils/__init__.py — fan_in=11.

Contract tests: all __all__ re-exports must be importable and functional.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAppsSharedUtilsPublicAPI:
    def test_all_exports_present(self):
        import apps_shared.utils as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_text_processor_importable(self):
        from apps_shared.utils import TextProcessor
        assert callable(TextProcessor)

    def test_text_match_importable(self):
        from apps_shared.utils import TextMatch
        assert TextMatch is not None

"""Test apps_shared import functionality."""
import apps_shared.utils
# Basic functionality assertion
assert True  # Replace with meaningful assertion
    def test_score_result_importable(self):
        from apps_shared.utils import ScoreResult
        assert ScoreResult is not None

    def test_json_parser_importable(self):
        from apps_shared.utils import JsonParser
        assert callable(JsonParser)

    def test_parse_result_importable(self):
        from apps_shared.utils import ParseResult
        assert ParseResult is not None


class TestAppsSharedUtilsShimIdentity:
    """Re-exports must be identical to canonical source modules."""

    def test_text_processor_same_object(self):
        from apps_shared.utils import TextProcessor as shim
        from apps_shared.utils.text_processing_validator_util import TextProcessor as canon
        assert shim is canon

    def test_math_processor_same_object(self):
        from apps_shared.utils import MathProcessor as shim
        from apps_shared.utils.math_operations_util import MathProcessor as canon
        assert shim is canon

    def test_json_parser_same_object(self):
        from apps_shared.utils import JsonParser as shim
        from apps_shared.utils.json_parser_validator_util import JsonParser as canon
        assert shim is canon
