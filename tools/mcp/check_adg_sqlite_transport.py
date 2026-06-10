"""Out-of-band ADG SQLite MCP transport checker."""

from __future__ import annotations

from tools.adg.mcp.supervisor import main_check


if __name__ == "__main__":
    raise SystemExit(main_check())
