"""Post-write hook: sync .windsurf/mcp_config.json -> ~/.codeium/windsurf/mcp_config.json.

Triggered by hooks.json post_write_code when .windsurf/mcp_config.json is written.
Stdlib only — no external dependencies.

Exit 0 always (sync failure is advisory, never blocks the write).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SSOT = REPO_ROOT / ".windsurf" / "mcp_config.json"
GLOBAL = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"


def _validate_ssot(path: Path) -> list[str]:
    """Basic sanity checks before copying — catches malformed edits early."""
    issues: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"JSON parse error: {exc}"]

    if "mcpServers" not in data:
        issues.append("Missing top-level 'mcpServers' key")
    else:
        servers = data["mcpServers"]
        for name, cfg in servers.items():
            if not isinstance(cfg, dict):
                continue
            if not cfg.get("command") and not cfg.get("url"):
                issues.append(f"Server '{name}' has neither 'command' nor 'url'")
            env = cfg.get("env", {})
            for key, val in env.items():
                if not isinstance(val, str) or val.startswith("${"):
                    continue
                key_upper = key.upper()
                is_secret_key = any(kw in key_upper for kw in ("KEY", "TOKEN", "SECRET", "PASSWORD", "API"))
                is_localhost = "localhost" in val or "127.0.0.1" in val
                if is_secret_key and not is_localhost and len(val) > 8:
                    issues.append(f"Server '{name}' env '{key}' looks like a hardcoded secret")
    return issues


def main() -> int:
    if not SSOT.exists():
        print(f"[mcp_sync] SSOT not found: {SSOT} — skipping", flush=True)
        return 0

    issues = _validate_ssot(SSOT)
    if issues:
        print("[mcp_sync] VALIDATION FAILED — not copying to global:", flush=True)
        for issue in issues:
            print(f"  - {issue}", flush=True)
        print(f"[mcp_sync] Fix {SSOT} and save again.", flush=True)
        return 0  # advisory only — never block the write

    try:
        GLOBAL.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(SSOT), str(GLOBAL))
        servers = json.loads(SSOT.read_text(encoding="utf-8")).get("mcpServers", {})
        print(
            f"[mcp_sync] Synced {len(servers)} servers to global config. Restart Windsurf to apply.",
            flush=True,
        )
    except OSError as exc:
        print(f"[mcp_sync] WARNING: copy failed: {exc}", flush=True)
        print(
            f"[mcp_sync] Manually copy: {SSOT} -> {GLOBAL}",
            flush=True,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
