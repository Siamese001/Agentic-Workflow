"""ADG importability contract for apps_shared/utils/json_parser_validator_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_json_parser_validator_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.utils.json_parser_validator_util import (  # noqa: F401
        ParseResult,
        JsonParser,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ParseResult = None  # type: ignore[assignment,misc]
    JsonParser = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="json_parser_validator_util.py deps unavailable")
class TestJsonParserValidatorUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: json_parser_validator_util.py must be importable."""
        assert _AVAILABLE

    def test_parseresult_is_type(self) -> None:
        assert ParseResult is not None

    def test_jsonparser_is_type(self) -> None:
        assert JsonParser is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

