"""Sync repo-controlled mcp_config.json to the Windsurf global config.

Run this after any change to .windsurf/mcp_config.json:
    python .windsurf/scripts/sync_mcp_config.py

The repo file is the SSOT. The global file at
~/.codeium/windsurf/mcp_config.json is what Windsurf actually reads at startup.
"""

import json
import pathlib
import shutil
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO_CONFIG = REPO_ROOT / ".windsurf" / "mcp_config.json"
GLOBAL_CONFIG = pathlib.Path.home() / ".codeium" / "windsurf" / "mcp_config.json"


def sync() -> None:
    if not REPO_CONFIG.exists():
        print(f"ERROR: repo config not found: {REPO_CONFIG}", file=sys.stderr)
        sys.exit(1)

    repo_data = json.loads(REPO_CONFIG.read_text(encoding="utf-8"))

    if GLOBAL_CONFIG.exists():
        global_data = json.loads(GLOBAL_CONFIG.read_text(encoding="utf-8"))
        # Merge: repo servers win; any extra servers in global are preserved
        global_servers = global_data.get("mcpServers", {})
        repo_servers = repo_data.get("mcpServers", {})
        merged = {**global_servers, **repo_servers}
        global_data["mcpServers"] = merged
        GLOBAL_CONFIG.write_text(json.dumps(global_data, indent=2), encoding="utf-8")
        print(f"Synced {len(repo_servers)} server(s) from repo config to global.")
    else:
        GLOBAL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_CONFIG, GLOBAL_CONFIG)
        print(f"Copied repo config to new global config at {GLOBAL_CONFIG}")


if __name__ == "__main__":
    sync()
