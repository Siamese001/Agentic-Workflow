"""Audit Codex MCP transport readiness without launching or killing servers.

The script is intentionally read-only. It checks local command/script viability,
credential/env placeholder state, Redis TCP reachability, and visible MCP
process families so Codex can report transport hygiene without creating a
second MCP registry.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PRIMARY_ROOT = Path(os.environ.get("AGENTIC_PRIMARY_ROOT", r"C:/Git/Agentic-Workflow-FRESH"))
PLACEHOLDER_START = "$" + "{"


SCRIPT_PATHS = [
    "tools/adg/mcp/server.py",
    "tools/memory/adg_memory_server.py",
    "tools/mcp/vector_db_server.py",
    "tools/mcp/pytest_server.py",
    "tools/mcp/redis_mcp_server.py",
    "tools/mcp/pytest_server.py",
    "tools/otel/otel_mcp_server.py",
    "tools/adg/adg_redis_ingest.py",
]


PROCESS_MARKERS = {
    "adg_sqlite": {
        "markers": ["tools.adg.mcp.server", "tools/adg/mcp/server.py"],
        "expected": "single-python-stdio-server",
    },
    "memory": {
        "markers": ["adg_memory_server.py"],
        "expected": "single-python-stdio-server",
    },
    "vector_db": {
        "markers": ["vector_db_server.py"],
        "expected": "single-python-stdio-server",
    },
    "notion": {
        "markers": ["@notionhq/notion-mcp-server"],
        "expected": "single-npx-launch-tree",
    },
    "context7": {
        "markers": ["@upstash/context7-mcp", "context7-mcp"],
        "expected": "single-npx-launch-tree",
    },
    "playwright": {
        "markers": ["@playwright/mcp"],
        "expected": "single-npx-launch-tree",
    },
    "redis": {
        "markers": ["redis_mcp_server.py"],
        "expected": "dormant",
    },
    "pytest_mcp": {
        "markers": ["pytest_server.py"],
        "expected": "dormant",
    },
    "otel_mcp": {
        "markers": ["otel_mcp_server.py"],
        "expected": "dormant-on-demand",
    },
    "tavily": {
        "markers": ["tavily-mcp"],
        "expected": "dormant",
    },
}


def _safe_cmdline(cmdline: list[str]) -> list[str]:
    redacted = []
    for part in cmdline[:14]:
        if "TOKEN=" in part or "KEY=" in part or "PASSWORD=" in part:
            redacted.append("<redacted-env>")
        else:
            redacted.append(part)
    return redacted


def _has_placeholder(value: str | None) -> bool:
    return bool(value and PLACEHOLDER_START in value)


def _walk_placeholders(value: Any, path: list[str], server_id: str, out: list[dict[str, Any]]) -> None:
    if isinstance(value, str):
        if _has_placeholder(value):
            out.append({"server": server_id, "path": path, "value": value})
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_placeholders(item, path + [str(index)], server_id, out)
    elif isinstance(value, dict):
        for key, item in value.items():
            _walk_placeholders(item, path + [key], server_id, out)


def _compile_script(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"exists": path.exists()}
    if not path.exists():
        return result
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    result["compile_returncode"] = proc.returncode
    result["compile_stderr"] = proc.stderr.strip()[:1000]
    return result


def _tcp_probe(host: str, port: int) -> dict[str, str]:
    try:
        with socket.create_connection((host, port), timeout=2):
            return {"status": "open"}
    except OSError as exc:
        return {"status": "closed", "error": f"{type(exc).__name__}: {exc}"}


def _processes() -> dict[str, Any]:
    try:
        import psutil  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"psutil": f"unavailable: {type(exc).__name__}: {exc}", "servers": {}}

    current_pid = os.getpid()
    current_script = Path(__file__).name.lower()
    found: dict[str, list[dict[str, Any]]] = {server_id: [] for server_id in PROCESS_MARKERS}

    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        info = proc.info
        pid = info.get("pid")
        if pid == current_pid:
            continue
        cmdline = [str(part) for part in (info.get("cmdline") or [])]
        joined = " ".join(cmdline)
        normalized = joined.lower().replace("\\", "/")
        if current_script in normalized:
            continue
        for server_id, config in PROCESS_MARKERS.items():
            markers = [marker.lower().replace("\\", "/") for marker in config["markers"]]
            if any(marker in normalized for marker in markers):
                found[server_id].append(
                    {
                        "pid": pid,
                        "name": info.get("name"),
                        "cmdline": _safe_cmdline(cmdline),
                        "create_time": info.get("create_time"),
                    }
                )

    classified: dict[str, Any] = {}
    for server_id, rows in found.items():
        expected = PROCESS_MARKERS[server_id]["expected"]
        root_launchers = [
            row
            for row in rows
            if _is_root_launcher(server_id, row.get("cmdline") or [])
        ]
        if not rows:
            classification = "none"
        elif expected.startswith("dormant"):
            classification = "unexpected_live_process"
        elif expected == "single-python-stdio-server":
            classification = "single" if len(rows) == 1 else "duplicate"
        elif expected == "single-npx-launch-tree":
            classification = "single_launch_tree" if len(root_launchers) <= 1 else "duplicate_launch_tree"
        else:
            classification = "unknown"
        classified[server_id] = {
            "expected": expected,
            "process_count": len(rows),
            "root_launcher_count": len(root_launchers),
            "classification": classification,
            "processes": rows,
        }
    return {"psutil": "available", "servers": classified}


def _is_root_launcher(server_id: str, cmdline: list[str]) -> bool:
    joined = " ".join(cmdline).lower().replace("\\", "/")
    if server_id in {"adg_sqlite", "memory", "vector_db"}:
        return "python" in joined
    if server_id in {"notion", "context7", "playwright"}:
        return "cmd" in joined and " npx " in f" {joined} "
    return True


def build_report() -> dict[str, Any]:
    registry_path = ROOT / ".mcp.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    servers = registry.get("mcpServers", {})

    unresolved: list[dict[str, Any]] = []
    for server_id, config in servers.items():
        _walk_placeholders(config, [], server_id, unresolved)

    env_keys = [
        "ADG_REDIS_URL",
        "AGENTIC_REPO_ROOT",
        "NOTION_TOKEN",
        "TAVILY_API_KEY",
        "CONTEXT7_API_KEY",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
        "OTEL_MCP_RUNTIME_ADG_DIR",
        "VECTOR_DB_CHROMA_PATH",
        "MEMORY_DB",
        "GITKRAKEN_GK_PATH",
    ]
    env_state = {
        key: {
            "state": "set" if os.environ.get(key) else "unset",
            "length": len(os.environ.get(key, "")),
            "has_unresolved_placeholder": _has_placeholder(os.environ.get(key)),
        }
        for key in env_keys
    }

    env_file = Path(r"C:/Users/amita/env/.env")
    tavily_env_file = {"exists": env_file.exists(), "present": False, "line": None, "length": 0}
    if env_file.exists():
        for line_number, line in enumerate(env_file.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.strip().startswith("TAVILY_API_KEY="):
                value = line.split("=", 1)[1].strip()
                tavily_env_file = {
                    "exists": True,
                    "present": bool(value),
                    "line": line_number,
                    "length": len(value),
                }

    return {
        "repo_root": str(ROOT),
        "primary_root": str(PRIMARY_ROOT),
        "registry_path": str(registry_path),
        "command_paths": {name: shutil.which(name) for name in ["python", "cmd", "npx", "node", "git", "redis-cli"]},
        "script_compile": {rel: _compile_script(ROOT / rel) for rel in sorted(set(SCRIPT_PATHS))},
        "tcp": {"localhost:6379": _tcp_probe("localhost", 6379)},
        "env": env_state,
        "env_file_tavily_api_key": tavily_env_file,
        "registry_unresolved_placeholders": unresolved,
        "normalized_paths": {
            "eval_artifacts_adg_exists": (ROOT / "artifacts" / "adg").exists(),
            "primary_artifacts_adg_exists": (PRIMARY_ROOT / "artifacts" / "adg").exists(),
        },
        "processes": _processes(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
