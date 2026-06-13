"""Regression artifact: MCP HTTP routing rule snapshot.

Locks in the three expected routing outcomes so any accidental revert of the
HTTP authority fix is caught immediately.

Routing contract (per docs/guides/MCP_Registry.md):
  - Human-readable web extraction -> Tavily
  - Library documentation         -> context7
  - JS-rendered pages             -> playwright
  - Local/internal HTTP           -> direct httpx in code
"""

from __future__ import annotations

from pathlib import Path

_RULES_PATH = Path(__file__).parents[3] / "docs" / "guides" / "MCP_Registry.md"


def _load_rules() -> str:
    return _RULES_PATH.read_text(encoding="utf-8")


class TestHTTPRoutingRule:
    """MCP registry must encode the current HTTP authority split."""

    def test_enhanced_http_declared_removed(self):
        text = _load_rules()
        assert "enhanced_http" in text
        assert "Removed 2026-04-27" in text

    def test_programmatic_routes_to_direct_httpx(self):
        text = _load_rules()
        assert "local/internal HTTP" in text
        assert "direct `httpx` in code" in text

    def test_http_routes_by_source_type(self):
        text = _load_rules()
        assert "Route content extraction" in text
        assert "library docs" in text
        assert "JS-rendered pages" in text
