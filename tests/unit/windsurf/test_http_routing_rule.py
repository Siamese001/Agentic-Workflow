"""Regression artifact: global_rules.md HTTP routing rule snapshot.

Locks in the three expected routing outcomes so any accidental revert of the
enhanced_http authority fix is caught immediately.

Routing contract (per global_rules.md and docs/guides/MCP_Registry.md):
  - Simple documentation GET  -> read_url_content  (user-approval gate)
  - Autonomous/programmatic   -> enhanced_http      (http_get, http_post, ...)
  - Authenticated POST        -> enhanced_http      (http_post)
  - Batch fetch               -> enhanced_http      (batch_requests)
"""

from __future__ import annotations

from pathlib import Path

_RULES_PATH = Path(__file__).parents[3] / ".cursor" / "rules" / "global_rules.md"


def _load_rules() -> str:
    return _RULES_PATH.read_text(encoding="utf-8")


class TestHTTPRoutingRule:
    """global_rules.md must encode the correct HTTP authority split."""

    def test_enhanced_http_declared_sole_authority(self):
        text = _load_rules()
        assert "enhanced_http" in text
        assert "sole authority" in text

    def test_programmatic_routes_to_enhanced_http_tools(self):
        text = _load_rules()
        # Assert logical tool names appear — prefix-agnostic so MCP reorder
        # cannot cause a false regression.
        assert "http_get" in text
        assert "http_post" in text
        assert "batch_requests" in text

    def test_read_url_content_restricted_to_user_approval(self):
        text = _load_rules()
        assert "read_url_content" in text
        assert "user" in text.lower() and "approval" in text.lower()
