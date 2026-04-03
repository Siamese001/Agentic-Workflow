#!/usr/bin/env python3
"""
MCP Config Drift Validation — CI Gate

Validates that workspace MCP config matches global config.
Fails CI if drift detected, forcing explicit sync decisions.

Usage:
    python ops_scripts/ci/validate_mcp_config.py     # validation check
    python ops_scripts/ci/validate_mcp_config.py --fix   # auto-sync (dangerous)

Exit codes:
    0 = configs in sync
    1 = drift detected (CI failure)
    2 = system error
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SSOT_PATH = REPO_ROOT / ".windsurf" / "mcp_config.json"
GLOBAL_PATH = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"

REQUIRED_FIELDS_PYTHON = {"command", "args", "cwd"}
PYTHON_SERVERS_NEEDING_CWD = {
    "adg_redis", "memory", "terminal", "pytest", "enhanced_http", "vector_db",
}


def _compute_diffs(ws_servers: dict, gl_servers: dict) -> list[str]:
    """Compute per-server field differences, ignoring _comment."""
    diffs = []
    ws_names = set(ws_servers.keys())
    gl_names = set(gl_servers.keys())

    for name in sorted(ws_names - gl_names):
        diffs.append(f"+ {name}: only in workspace")
    for name in sorted(gl_names - ws_names):
        diffs.append(f"- {name}: only in global")

    for name in sorted(ws_names & gl_names):
        ws_s = ws_servers[name]
        gl_s = gl_servers[name]
        for k in sorted(set(list(ws_s.keys()) + list(gl_s.keys()))):
            if k == "_comment":
                continue
            ws_v = ws_s.get(k)
            gl_v = gl_s.get(k)
            if ws_v != gl_v:
                diffs.append(f"~ {name}.{k}: workspace={ws_v!r} global={gl_v!r}")
    return diffs


def _validate_cwd_requirements(config: dict) -> list[str]:
    """Validate that Python servers have required fields."""
    errors = []
    servers = config.get("mcpServers", {})

    for name, srv in servers.items():
        cmd = srv.get("command", "")
        if cmd == "python" and name in PYTHON_SERVERS_NEEDING_CWD:
            if "cwd" not in srv:
                errors.append(f"{name}: missing 'cwd' field (Python server)")
            if "env" not in srv:
                errors.append(f"{name}: missing 'env' field (Python server)")

    return errors


def validate() -> int:
    """Main validation. Returns exit code."""
    if not SSOT_PATH.exists():
        print(f"[ERROR] Workspace config not found: {SSOT_PATH}")
        return 2

    if not GLOBAL_PATH.exists():
        print(f"[ERROR] Global config not found: {GLOBAL_PATH}")
        print("[HINT] Run: python tools/adg/sync_global_config.py")
        return 1

    with open(SSOT_PATH, encoding="utf-8") as f:
        ws = json.load(f)
    with open(GLOBAL_PATH, encoding="utf-8") as f:
        gl = json.load(f)

    ws_servers = ws.get("mcpServers", {})
    gl_servers = gl.get("mcpServers", {})

    # Check for drift
    diffs = _compute_diffs(ws_servers, gl_servers)

    # Validate workspace config has required fields
    ws_errors = _validate_cwd_requirements(ws)
    gl_errors = _validate_cwd_requirements(gl)

    if diffs or ws_errors or gl_errors:
        print("[FAIL] MCP config drift detected")
        print()

        if diffs:
            print(f"Differences ({len(diffs)}):")
            for d in diffs:
                print(f"  {d}")
            print()

        if ws_errors:
            print(f"Workspace validation errors ({len(ws_errors)}):")
            for e in ws_errors:
                print(f"  {e}")
            print()

        if gl_errors:
            print(f"Global validation errors ({len(gl_errors)}):")
            for e in gl_errors:
                print(f"  {e}")
            print()

        print("[ACTION] Run: python tools/adg/sync_global_config.py")
        return 1

    print(f"[OK] MCP configs in sync — {len(ws_servers)} servers validated")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--fix" in args:
        print("[WARN] Auto-fix not implemented — run sync_global_config.py manually")
        return 1
    return validate()


if __name__ == "__main__":
    sys.exit(main())
