#!/usr/bin/env python3
"""test_apply_plan_derived_status.py — Unit tests for apply_plan_derived_status.

Focus: wrong-plan guard helpers (_fetch_page_slug, _assert_slug_matches).
The main() function requires a real delta JSON + Notion token so is tested
via integration; the helpers are pure enough to unit-test with mocks.
"""
import json
import urllib.error
import urllib.request
from io import BytesIO
from unittest import mock

import pytest

from tools.notion.apply_plan_derived_status import (
    _assert_slug_matches,
    _fetch_page_slug,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://api.notion.com/v1/pages/page-id",
        code=code,
        msg="Error",
        hdrs={},
        fp=BytesIO(b""),
    )


def _page_payload(slug_text: str | None) -> bytes:
    """Build a minimal Notion page JSON with a Slug title property."""
    if slug_text is None:
        props: dict = {}
    else:
        props = {
            "Slug": {
                "title": [{"plain_text": slug_text, "text": {"content": slug_text}}]
            }
        }
    return json.dumps({"id": "page-id", "properties": props}).encode("utf-8")


class FakeResponse:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


# ---------------------------------------------------------------------------
# _fetch_page_slug
# ---------------------------------------------------------------------------

class TestFetchPageSlug:
    """Tests for _fetch_page_slug helper."""

    @mock.patch("urllib.request.urlopen")
    def test_returns_slug_when_present(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(_page_payload("my-plan-a1b2c3"))
        result = _fetch_page_slug("page-id", "token")
        assert result == "my-plan-a1b2c3"

    @mock.patch("urllib.request.urlopen")
    def test_returns_none_when_no_slug_property(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(_page_payload(None))
        result = _fetch_page_slug("page-id", "token")
        assert result is None

    @mock.patch("urllib.request.urlopen")
    def test_returns_none_on_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = _make_http_error(404)
        result = _fetch_page_slug("page-id", "token")
        assert result is None

    @mock.patch("urllib.request.urlopen")
    def test_returns_none_on_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("timeout")
        result = _fetch_page_slug("page-id", "token")
        assert result is None

    @mock.patch("urllib.request.urlopen")
    def test_returns_none_on_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("timed out")
        result = _fetch_page_slug("page-id", "token")
        assert result is None

    @mock.patch("urllib.request.urlopen")
    def test_trims_whitespace(self, mock_urlopen):
        payload = json.dumps({
            "id": "page-id",
            "properties": {
                "Slug": {
                    "title": [{"plain_text": "  my-plan  "}]
                }
            }
        }).encode()
        mock_urlopen.return_value = FakeResponse(payload)
        result = _fetch_page_slug("page-id", "token")
        assert result == "my-plan"

    @mock.patch("urllib.request.urlopen")
    def test_falls_back_to_name_property(self, mock_urlopen):
        """Pages without a Slug property may have Name instead."""
        payload = json.dumps({
            "id": "page-id",
            "properties": {
                "Name": {
                    "title": [{"plain_text": "fallback-slug"}]
                }
            }
        }).encode()
        mock_urlopen.return_value = FakeResponse(payload)
        result = _fetch_page_slug("page-id", "token")
        assert result == "fallback-slug"


# ---------------------------------------------------------------------------
# _assert_slug_matches
# ---------------------------------------------------------------------------

class TestAssertSlugMatches:
    """Tests for _assert_slug_matches helper."""

    @mock.patch("tools.notion.apply_plan_derived_status._fetch_page_slug")
    def test_match_returns_ok(self, mock_fetch):
        mock_fetch.return_value = "my-plan-abc123"
        ok, msg = _assert_slug_matches("page-id", "my-plan-abc123", "token")
        assert ok is True
        assert msg == "ok"

    @mock.patch("tools.notion.apply_plan_derived_status._fetch_page_slug")
    def test_mismatch_returns_false(self, mock_fetch):
        mock_fetch.return_value = "other-plan-xyz789"
        ok, msg = _assert_slug_matches("page-id", "my-plan-abc123", "token")
        assert ok is False
        assert "slug_mismatch" in msg
        assert "my-plan-abc123" in msg
        assert "other-plan-xyz789" in msg

    @mock.patch("tools.notion.apply_plan_derived_status._fetch_page_slug")
    def test_none_slug_is_permissive(self, mock_fetch):
        """If the page has no Slug property, the guard is permissive."""
        mock_fetch.return_value = None
        ok, msg = _assert_slug_matches("page-id", "my-plan-abc123", "token")
        assert ok is True
        assert msg == "ok_no_slug"

    @mock.patch("tools.notion.apply_plan_derived_status._fetch_page_slug")
    def test_empty_expected_slug_with_no_page_slug_is_permissive(self, mock_fetch):
        """When expected_slug is empty and page has no slug, guard is permissive.

        The caller (main loop) short-circuits on empty expected_slug; but if
        _assert_slug_matches IS called with empty expected_slug, the fetch returning
        None means 'ok_no_slug' (permissive).  Fetch returning '' would strip to
        None-equivalent.  Either way: no mismatch possible vs an empty expected.
        """
        mock_fetch.return_value = None  # page has no slug property
        ok, msg = _assert_slug_matches("page-id", "", "token")
        assert ok is True

    @mock.patch("tools.notion.apply_plan_derived_status._fetch_page_slug")
    def test_network_failure_is_permissive(self, mock_fetch):
        """Network errors from _fetch_page_slug return None → permissive."""
        mock_fetch.return_value = None
        ok, msg = _assert_slug_matches("page-id", "my-plan-abc123", "token")
        assert ok is True
