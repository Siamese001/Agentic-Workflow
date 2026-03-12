"""ADG-driven tests for prompt_governance/security/utils/normalization_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.prompt_governance.security.utils.normalization_util import (
    MAX_DECODED_CHARS,
    MAX_INPUT_CHARS,
    MAX_URL_DECODE_PASSES,
    _ZERO_WIDTH_CHARS,
)


class TestConstants:
    def test_max_input_chars(self):
        assert MAX_INPUT_CHARS == 100_000

    def test_max_decoded_chars(self):
        assert MAX_DECODED_CHARS == 8_000

    def test_max_url_decode_passes(self):
        assert MAX_URL_DECODE_PASSES == 2

    def test_zero_width_chars_is_frozenset(self):
        assert isinstance(_ZERO_WIDTH_CHARS, frozenset)

    def test_zero_width_chars_nonempty(self):
        assert len(_ZERO_WIDTH_CHARS) > 0


class TestNormalizeAndDecode:
    def test_importable(self):
        from agentic_core.prompt_governance.security.utils.normalization_util import normalize_and_decode
        assert callable(normalize_and_decode)

    def test_plain_text_passthrough(self):
        from agentic_core.prompt_governance.security.utils.normalization_util import normalize_and_decode
        result = normalize_and_decode("hello world")
        text = result[0] if isinstance(result, tuple) else result
        assert isinstance(text, str)
        assert "hello" in text

    def test_returns_tuple_or_string(self):
        from agentic_core.prompt_governance.security.utils.normalization_util import normalize_and_decode
        result = normalize_and_decode("test input")
        assert isinstance(result, (str, tuple))
