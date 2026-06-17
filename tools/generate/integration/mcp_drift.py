"""MCP config drift check integration for ADG generation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


def _load_mcp_servers(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    servers = data.get("mcpServers", {}) if isinstance(data, dict) else {}
    if not isinstance(servers, dict):
        raise ValueError(f"mcpServers must be a mapping in {path}")
    return set(servers.keys())


ROOT = _discover_repo_root(Path(__file__).resolve().parent)
MCP_CONFIG_FINGERPRINT = ROOT / "artifacts" / "governance" / "mcp_config_fingerprint.json"


def _fingerprint_repo_mcp(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    servers = data.get("mcpServers", {}) if isinstance(data, dict) else {}
    if not isinstance(servers, dict):
        raise ValueError(f"mcpServers must be a mapping in {path}")
    payload = json.dumps(servers, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return {
        "mcpServers_sha256": digest,
        "server_count": len(servers),
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _check_mcp_config_drift() -> None:
    """Fingerprint the repo SSOT and invalidate derived config caches on change.

    The ADG gate is repo-local: it treats root `.mcp.json` as the only SSOT,
    fingerprints its `mcpServers` block, and refreshes the cached fingerprint
    artifact when the config changes. No legacy legacy editor/legacy editor mirror is
    consulted here.
    """
    print("[ADG] Checking MCP config drift...")
    repo_ssot = ROOT / ".mcp.json"

    if not repo_ssot.exists():
        print(f"[WARNING] Repo SSOT not found: {repo_ssot} — skipping drift check")
        return

    try:
        current = _fingerprint_repo_mcp(repo_ssot)
    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ) as exc:  # guardian: allow-broad-exception -- non-critical: drift check failure must not block ADG generation
        print(f"[WARNING] Could not check MCP config drift: {exc}")
        print("[WARNING]   Proceeding with ADG generation...")
        return

    if not MCP_CONFIG_FINGERPRINT.exists():
        _write_json(MCP_CONFIG_FINGERPRINT, current)
        print(f"[ADG] MCP config fingerprint initialized ({current['server_count']} servers)")
        return

    try:
        previous = _load_json(MCP_CONFIG_FINGERPRINT)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[WARNING] Could not read MCP config fingerprint: {exc}")
        print("[WARNING]   Proceeding with ADG generation...")
        return

    if previous.get("mcpServers_sha256") == current.get("mcpServers_sha256"):
        print(f"[ADG] MCP config unchanged ({current['server_count']} servers)")
        return

    print("[WARNING] MCP config changed since the last fingerprint.")
    print("[WARNING]   Repo SSOT remains .mcp.json; derived caches will be refreshed.")
    print("[WARNING]   Proceeding with ADG generation...")
    _write_json(MCP_CONFIG_FINGERPRINT, current)
