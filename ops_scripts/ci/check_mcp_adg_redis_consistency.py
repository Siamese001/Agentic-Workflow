"""MCP ADG_REDIS_URL Consistency Gate — S-08 verification.

Verifies that `adg_sqlite` and `memory` MCP servers in `.windsurf/mcp_config.json`
have consistent ADG_REDIS_URL environment variable declarations.

SSOT Issue S-08: Both servers must reference the same Redis URL source.
This gate detects drift where one server has a hardcoded default while
the other uses env var interpolation.

Exit codes:
    0 — consistent (or both use ${env:ADG_REDIS_URL})
    1 — inconsistent (hardcoded vs env var mismatch)
    2 — configuration error (malformed JSON, missing servers)

Bypass: MCP_ADG_REDIS_CONSISTENCY_BYPASS=1
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_CONFIG_PATH = REPO_ROOT / ".windsurf" / "mcp_config.json"


def _exit_ok(msg: str) -> int:
    print(f"[check_mcp_adg_redis_consistency] OK: {msg}")
    return 0


def _exit_fail(msg: str) -> int:
    print(f"[check_mcp_adg_redis_consistency] FAIL: {msg}", file=sys.stderr)
    return 1


def _exit_error(msg: str) -> int:
    print(f"[check_mcp_adg_redis_consistency] ERROR: {msg}", file=sys.stderr)
    return 2


def main() -> int:
    """Check ADG_REDIS_URL consistency between adg_sqlite and memory MCP servers."""
    # Bypass check
    if os.environ.get("MCP_ADG_REDIS_CONSISTENCY_BYPASS"):
        print("[check_mcp_adg_redis_consistency] BYPASS: MCP_ADG_REDIS_CONSISTENCY_BYPASS=1")
        return 0

    # Load MCP config
    if not MCP_CONFIG_PATH.exists():
        return _exit_error(f"MCP config not found: {MCP_CONFIG_PATH}")

    try:
        config = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return _exit_error(f"Malformed JSON in {MCP_CONFIG_PATH}: {exc}")

    servers = config.get("mcpServers", {})

    # Check required servers exist
    adg_sqlite = servers.get("adg_sqlite", {})
    memory = servers.get("memory", {})

    if not adg_sqlite:
        return _exit_error("adg_sqlite server not found in mcp_config.json")
    if not memory:
        return _exit_error("memory server not found in mcp_config.json")

    # Check env blocks exist
    adg_env = adg_sqlite.get("env", {})
    mem_env = memory.get("env", {})

    adg_redis_url = adg_env.get("ADG_REDIS_URL", "")
    mem_redis_url = mem_env.get("ADG_REDIS_URL", "")

    # Check for hardcoded defaults (pre-S-08 pattern)
    HARDCODED_DEFAULT = "redis://localhost:6379/0"

    if adg_redis_url == HARDCODED_DEFAULT:
        return _exit_fail(
            f"adg_sqlite has hardcoded ADG_REDIS_URL='{HARDCODED_DEFAULT}'. "
            "Must use '${env:ADG_REDIS_URL}' per S-08 SSOT."
        )

    if mem_redis_url == HARDCODED_DEFAULT:
        return _exit_fail(
            f"memory has hardcoded ADG_REDIS_URL='{HARDCODED_DEFAULT}'. "
            "Must use '${env:ADG_REDIS_URL}' per S-08 SSOT."
        )

    # Check both use env var interpolation (post-S-08 pattern)
    EXPECTED_PATTERN = "${env:ADG_REDIS_URL}"

    if adg_redis_url != EXPECTED_PATTERN:
        return _exit_fail(
            f"adg_sqlite ADG_REDIS_URL='{adg_redis_url}' != '{EXPECTED_PATTERN}'. "
            "Both servers must use consistent env var interpolation."
        )

    if mem_redis_url != EXPECTED_PATTERN:
        return _exit_fail(
            f"memory ADG_REDIS_URL='{mem_redis_url}' != '{EXPECTED_PATTERN}'. "
            "Both servers must use consistent env var interpolation."
        )

    # Check both match each other (defensive)
    if adg_redis_url != mem_redis_url:
        return _exit_fail(
            f"ADG_REDIS_URL mismatch: adg_sqlite='{adg_redis_url}' vs memory='{mem_redis_url}'"
        )

    return _exit_ok(
        f"ADG_REDIS_URL consistent across MCP servers: '{adg_redis_url}'"
    )


if __name__ == "__main__":
    raise SystemExit(main())
