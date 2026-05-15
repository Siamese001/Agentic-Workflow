"""MCP ADG_REDIS_URL Consistency Gate — S-08 verification.

Verifies that `adg_sqlite` and `memory` MCP servers have consistent ADG_REDIS_URL
declarations in both `.cursor/mcp.json` and `.windsurf/mcp_config.json`.

Bypass: MCP_ADG_REDIS_CONSISTENCY_BYPASS=1
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import CURSOR_MCP_PATH, WINDSURF_MCP_PATH, server_env_value  # noqa: E402

# Backward-compatible alias for tests and Windsurf-only callers.
MCP_CONFIG_PATH = WINDSURF_MCP_PATH

EXPECTED_PATTERN = "${env:ADG_REDIS_URL}"
HARDCODED_DEFAULT = "redis://localhost:6379/0"


def _exit_ok(msg: str) -> int:
    print(f"[check_mcp_adg_redis_consistency] OK: {msg}")
    return 0


def _exit_fail(msg: str) -> int:
    print(f"[check_mcp_adg_redis_consistency] FAIL: {msg}", file=sys.stderr)
    return 1


def _exit_error(msg: str) -> int:
    print(f"[check_mcp_adg_redis_consistency] ERROR: {msg}", file=sys.stderr)
    return 2


def _check_file(label: str, path: Path) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"{label}: config not found at {path}"]

    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{label}: malformed JSON: {exc}"]

    servers = config.get("mcpServers", {})
    adg_sqlite = servers.get("adg_sqlite", {})
    memory = servers.get("memory", {})
    if not adg_sqlite:
        return [f"{label}: adg_sqlite server missing"]
    if not memory:
        return [f"{label}: memory server missing"]

    adg_redis_url = server_env_value(adg_sqlite, "ADG_REDIS_URL")
    mem_redis_url = server_env_value(memory, "ADG_REDIS_URL")

    if adg_redis_url == HARDCODED_DEFAULT:
        issues.append(f"{label}: adg_sqlite has hardcoded ADG_REDIS_URL")
    if mem_redis_url == HARDCODED_DEFAULT:
        issues.append(f"{label}: memory has hardcoded ADG_REDIS_URL")
    if adg_redis_url != EXPECTED_PATTERN:
        issues.append(f"{label}: adg_sqlite ADG_REDIS_URL='{adg_redis_url}' != expected")
    if mem_redis_url != EXPECTED_PATTERN:
        issues.append(f"{label}: memory ADG_REDIS_URL='{mem_redis_url}' != expected")
    if adg_redis_url != mem_redis_url:
        issues.append(
            f"{label}: ADG_REDIS_URL mismatch adg_sqlite='{adg_redis_url}' memory='{mem_redis_url}'"
        )
    return issues


def main() -> int:
    if os.environ.get("MCP_ADG_REDIS_CONSISTENCY_BYPASS"):
        print("[check_mcp_adg_redis_consistency] BYPASS: MCP_ADG_REDIS_CONSISTENCY_BYPASS=1")
        return 0

    targets: list[tuple[str, Path]]
    if MCP_CONFIG_PATH != WINDSURF_MCP_PATH:
        targets = [("config", MCP_CONFIG_PATH)]
    else:
        targets = [("cursor", CURSOR_MCP_PATH), ("windsurf", WINDSURF_MCP_PATH)]

    issues: list[str] = []
    for label, path in targets:
        file_issues = _check_file(label, path)
        if not path.exists():
            return _exit_error(f"{label}: config not found at {path}")
        if any("missing" in issue for issue in file_issues):
            return _exit_error(file_issues[0])
        issues.extend(file_issues)

    if issues:
        return _exit_fail(issues[0])

    return _exit_ok(f"ADG_REDIS_URL consistent across MCP configs ('{EXPECTED_PATTERN}')")


if __name__ == "__main__":
    raise SystemExit(main())
