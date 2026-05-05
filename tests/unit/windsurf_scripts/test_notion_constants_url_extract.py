"""tests.unit.windsurf_scripts.test_notion_constants_url_extract

Tests for extract_page_id() and format_uuid() in _notion_constants.py.

RCA: Cascade mis-split a 32-char hex URL ID when inserting dashes manually.
Fix: canonical helpers that mirror the Notion SDK helpers.ts regex logic.
"""

from __future__ import annotations

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.windsurf/scripts"))

from _notion_constants import extract_page_id, format_uuid


EXPECTED = "35727693-f55c-8118-95a8-d62d11d50c25"


class TestFormatUuid:
    def test_compact_no_dashes(self) -> None:
        assert format_uuid("35727693f55c811895a8d62d11d50c25") == EXPECTED

    def test_already_dashed_passthrough(self) -> None:
        assert format_uuid("35727693-f55c-8118-95a8-d62d11d50c25") == EXPECTED

    def test_uppercase_input(self) -> None:
        assert format_uuid("35727693F55C811895A8D62D11D50C25") == EXPECTED

    def test_invalid_length_raises(self) -> None:
        with pytest.raises(ValueError):
            format_uuid("abc123")

    def test_invalid_chars_raises(self) -> None:
        with pytest.raises(ValueError):
            format_uuid("35727693f55c811895a8d62d11d50cZZ")

    def test_segments_correct(self) -> None:
        result = format_uuid("35727693f55c811895a8d62d11d50c25")
        parts = result.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12


class TestExtractPageId:
    def test_full_notion_url_with_slug(self) -> None:
        url = "https://www.notion.so/apps-eval-spine-deferred-p2p3-b7c2a1-35727693f55c811895a8d62d11d50c25?v=7e35d17405bc4bd9bb9dcf73933fefa2&source=copy_link"
        assert extract_page_id(url) == EXPECTED

    def test_full_notion_url_no_query(self) -> None:
        url = "https://www.notion.so/apps-eval-spine-deferred-p2p3-b7c2a1-35727693f55c811895a8d62d11d50c25"
        assert extract_page_id(url) == EXPECTED

    def test_raw_32_hex(self) -> None:
        assert extract_page_id("35727693f55c811895a8d62d11d50c25") == EXPECTED

    def test_already_dashed_uuid(self) -> None:
        assert extract_page_id("35727693-f55c-8118-95a8-d62d11d50c25") == EXPECTED

    def test_none_returns_none(self) -> None:
        assert extract_page_id(None) is None  # type: ignore[arg-type]

    def test_empty_string_returns_none(self) -> None:
        assert extract_page_id("") is None

    def test_garbage_string_returns_none(self) -> None:
        assert extract_page_id("not-a-notion-url") is None

    def test_view_id_not_confused_with_page_id(self) -> None:
        url = "https://www.notion.so/apps-eval-spine-deferred-p2p3-b7c2a1-35727693f55c811895a8d62d11d50c25?v=7e35d17405bc4bd9bb9dcf73933fefa2"
        result = extract_page_id(url)
        assert result == EXPECTED
        assert result != "7e35d174-05bc-4bd9-bb9d-cf73933fefa2"

    def test_different_page(self) -> None:
        url = "https://www.notion.so/my-plan-ac53d31b30684039 9ebe856c12caab32"
        result = extract_page_id(url.replace(" ", ""))
        assert result == "ac53d31b-3068-4039-9ebe-856c12caab32"

    def test_whitespace_stripped(self) -> None:
        assert extract_page_id("  35727693f55c811895a8d62d11d50c25  ") == EXPECTED
