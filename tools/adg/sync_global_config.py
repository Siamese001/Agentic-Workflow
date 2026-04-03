"""
MCP Config SSOT Sync — workspace → global.

SSOT: .windsurf/mcp_config.json (version-controlled, inside repo)
Target: C:\\Users\\amita\\.codeium\\windsurf\\mcp_config.json (read by Windsurf IDE)

Modes:
  --check   Drift detection only (exit 0=synced, 1=drifted). No writes.
  --sync    Overwrite global from workspace SSOT (default).
  --diff    Show per-server field differences.

Usage:
  python tools/adg/sync_global_config.py           # sync (default)
  python tools/adg/sync_global_config.py --check    # CI/pre-commit gate
  python tools/adg/sync_global_config.py --diff     # show divergence
"""

import json
import shutil
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SSOT_PATH = REPO_ROOT / ".windsurf" / "mcp_config.json"
GLOBAL_PATH = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
BACKUP_DIR = GLOBAL_PATH.parent / "mcp_config_backups"

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS_PYTHON = {"command", "args", "cwd", "env"}
PYTHON_SERVERS_NEEDING_CWD = {
    "adg_redis", "memory", "terminal", "pytest", "enhanced_http", "vector_db",
}


def _validate_ssot(config: dict) -> list[str]:
    """Validate the SSOT config for common issues. Returns list of warnings."""
    warnings = []
    servers = config.get("mcpServers", {})
    if not servers:
        warnings.append("CRITICAL: mcpServers is empty")
        return warnings

    for name, srv in servers.items():
        cmd = srv.get("command", "")
        if cmd == "python" and name in PYTHON_SERVERS_NEEDING_CWD:
            if "cwd" not in srv:
                warnings.append(f"{name}: missing 'cwd' (Python server)")
            if "env" not in srv:
                warnings.append(f"{name}: missing 'env' (Python server)")
    return warnings


def _compute_diffs(ws_servers: dict, gl_servers: dict) -> list[str]:
    """Compute per-server field differences, ignoring _comment."""
    diffs = []
    ws_names = set(ws_servers.keys())
    gl_names = set(gl_servers.keys())

    for name in sorted(ws_names - gl_names):
        diffs.append(f"  + {name}: ONLY in workspace (will be added)")
    for name in sorted(gl_names - ws_names):
        diffs.append(f"  - {name}: ONLY in global (will be removed)")

    for name in sorted(ws_names & gl_names):
        ws_s = ws_servers[name]
        gl_s = gl_servers[name]
        for k in sorted(set(list(ws_s.keys()) + list(gl_s.keys()))):
            if k == "_comment":
                continue
            ws_v = ws_s.get(k)
            gl_v = gl_s.get(k)
            if ws_v != gl_v:
                diffs.append(f"  ~ {name}.{k}: WS={ws_v!r} GL={gl_v!r}")
    return diffs


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


def check() -> int:
    """Drift detection. Returns 0 if synced, 1 if drifted."""
    if not SSOT_PATH.exists():
        print(f"[FAIL] SSOT not found: {SSOT_PATH}")
        return 2
    if not GLOBAL_PATH.exists():
        print(f"[DRIFT] Global config missing: {GLOBAL_PATH}")
        return 1

    with open(SSOT_PATH, encoding="utf-8") as f:
        ws = json.load(f)
    with open(GLOBAL_PATH, encoding="utf-8") as f:
        gl = json.load(f)

    ws_servers = ws.get("mcpServers", {})
    gl_servers = gl.get("mcpServers", {})
    diffs = _compute_diffs(ws_servers, gl_servers)

    if not diffs:
        print(f"[OK] Configs synced — {len(ws_servers)} servers, 0 diffs")
        return 0

    print(f"[DRIFT] {len(diffs)} differences found:")
    for d in diffs:
        print(d)
    print(f"\nRun: python tools/adg/sync_global_config.py --sync")
    return 1


def diff() -> int:
    """Show detailed diff."""
    if not SSOT_PATH.exists() or not GLOBAL_PATH.exists():
        print("[FAIL] One or both config files missing")
        return 2

    with open(SSOT_PATH, encoding="utf-8") as f:
        ws = json.load(f)
    with open(GLOBAL_PATH, encoding="utf-8") as f:
        gl = json.load(f)

    diffs = _compute_diffs(
        ws.get("mcpServers", {}), gl.get("mcpServers", {})
    )
    if not diffs:
        print("[OK] No differences")
        return 0

    print(f"Differences ({len(diffs)}):")
    for d in diffs:
        print(d)
    return 1


def sync() -> int:
    """Overwrite global from workspace SSOT. Creates backup first."""
    if not SSOT_PATH.exists():
        print(f"[FAIL] SSOT not found: {SSOT_PATH}")
        return 2

    with open(SSOT_PATH, encoding="utf-8") as f:
        ws = json.load(f)

    # Validate SSOT before propagating
    warnings = _validate_ssot(ws)
    if warnings:
        print("[WARN] SSOT validation warnings:")
        for w in warnings:
            print(f"  {w}")

    # Backup existing global config
    if GLOBAL_PATH.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / f"mcp_config_{ts}.json"
        shutil.copy2(GLOBAL_PATH, backup)
        print(f"[backup] {backup}")

    # Write SSOT → global
    GLOBAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GLOBAL_PATH, "w", encoding="utf-8") as f:
        json.dump(ws, f, indent=2)
        f.write("\n")

    # Verify round-trip
    with open(GLOBAL_PATH, encoding="utf-8") as f:
        gl = json.load(f)

    ws_servers = ws.get("mcpServers", {})
    gl_servers = gl.get("mcpServers", {})
    diffs = _compute_diffs(ws_servers, gl_servers)

    if diffs:
        print(f"[FAIL] {len(diffs)} mismatches after sync!")
        for d in diffs:
            print(d)
        return 1

    print(f"[OK] Global config synced — {len(gl_servers)} servers, 0 diffs")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--check" in args:
        sys.exit(check())
    elif "--diff" in args:
        sys.exit(diff())
    else:
        sys.exit(sync())
