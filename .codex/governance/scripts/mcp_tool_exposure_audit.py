#!/usr/bin/env python3
"""Audit declared major MCPs against native and Codex-exposure evidence.

This script closes the gap between "declared in .mcp.json" and "actually
usable from Codex." Local scripts cannot call Codex's deferred `tool_search`
API directly, so host exposure evidence is accepted as an optional JSON
snapshot. Without that snapshot, the audit still verifies config declaration,
Python MCP process liveness, and native server tool listing where available
(notably GitKraken's `gk mcp --list-tools`).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_CONFIG = REPO_ROOT / ".mcp.json"
HEARTBEAT_PATH = Path(__file__).resolve().parent / "mcp_python_heartbeat.py"
DEFAULT_SUBPROCESS_TIMEOUT = 15

MAJOR_MCP_TOOLS: dict[str, tuple[str, ...]] = {
    # Always-on core MCPs. Keep this list small so the session surface stays usable.
    "GitKraken": (
        "git_status",
        "git_add_or_commit",
        "git_log_or_diff",
        "pull_request_create",
    ),
    "adg_sqlite": (
        "adg_health",
        "adg_nodes_by_file",
        "adg_edge_fanin",
        "adg_edge_fanout",
    ),
    "memory": ("mem_recall_session_start", "create_entities", "add_observations", "search_nodes"),
}

PYTHON_PROCESS_REQUIRED = frozenset({"adg_sqlite", "memory", "vector_db"})
NATIVE_LIST_TOOLS_REQUIRED = frozenset({"GitKraken"})
_ENV_PLACEHOLDER_RE = re.compile(r"\$\{(?:env:)?([A-Za-z_][A-Za-z0-9_]*)\}")
_TOOL_LINE_RE = re.compile(r"^\s*Tool:\s+([A-Za-z0-9_.-]+)\s*$", re.MULTILINE)


@dataclass
class ExposureResult:
    server_id: str
    status: str
    declared: bool
    host_exposed: bool | None
    native_ok: bool | None
    expected_tools: list[str]
    observed_tools: list[str] = field(default_factory=list)
    missing_tools: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    rca: dict[str, str] = field(default_factory=dict)


def _read_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        raise ValueError(f"{path} missing top-level mcpServers object")
    return data


def _expand_env_vars(value: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        return os.environ.get(match.group(1), "")

    return _ENV_PLACEHOLDER_RE.sub(_replace, value)


def _missing_env_vars(value: str) -> list[str]:
    return sorted(
        {
            match.group(1)
            for match in _ENV_PLACEHOLDER_RE.finditer(value)
            if not os.environ.get(match.group(1))
        }
    )


def _load_heartbeat() -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location("_mcp_python_heartbeat_for_exposure", HEARTBEAT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load heartbeat probe at {HEARTBEAT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _collect_tool_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned:
            names.add(cleaned)
            names.add(cleaned.rsplit(".", 1)[-1])
            names.add(cleaned.rsplit("__", 1)[-1])
    elif isinstance(value, dict):
        for key in ("name", "tool", "tool_name", "function", "id"):
            if isinstance(value.get(key), str):
                names.update(_collect_tool_names(value[key]))
        namespace = value.get("namespace")
        name = value.get("name") or value.get("tool") or value.get("tool_name")
        if isinstance(namespace, str) and isinstance(name, str):
            names.add(f"{namespace}.{name}")
            names.add(f"{namespace}__{name}")
        for nested in value.values():
            names.update(_collect_tool_names(nested))
    elif isinstance(value, list):
        for item in value:
            names.update(_collect_tool_names(item))
    return names


def load_tool_search_snapshot(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _collect_tool_names(payload)


def _config_command_tools(
    server_id: str,
    config: dict[str, Any],
    timeout: int = DEFAULT_SUBPROCESS_TIMEOUT,
) -> tuple[bool, set[str], str]:
    servers = config.get("mcpServers", {})
    cfg = servers.get(server_id, {})
    if not isinstance(cfg, dict):
        return False, set(), "server config missing or malformed"
    command = cfg.get("command")
    args = cfg.get("args", [])
    if not isinstance(command, str) or not isinstance(args, list):
        return False, set(), "server command or args missing"
    unresolved = sorted(
        {name for value in [command, *(str(arg) for arg in args)] for name in _missing_env_vars(value)}
    )
    if unresolved:
        return False, set(), f"missing env var(s): {', '.join(unresolved)}"
    expanded_command = _expand_env_vars(command)
    expanded_args = [_expand_env_vars(str(arg)) for arg in args]
    if not expanded_command.strip():
        return False, set(), "server command expanded to empty"
    argv = [expanded_command, *expanded_args, "--list-tools"]
    try:
        result = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, set(), f"native list-tools failed to start: {exc}"
    output = f"{result.stdout}\n{result.stderr}"
    tools = set(_TOOL_LINE_RE.findall(output))
    if result.returncode != 0:
        return False, tools, f"native list-tools exited {result.returncode}"
    if not tools:
        return False, tools, "native list-tools returned no tool names"
    return True, tools, "native list-tools ok"


def _heartbeat_native_status(
    server_id: str,
    heartbeat_report: dict[str, Any] | None,
) -> tuple[bool, str]:
    report = heartbeat_report
    if report is None:
        try:
            report = _load_heartbeat().check()
        except (OSError, RuntimeError, ValueError) as exc:
            return False, f"heartbeat probe failed: {exc}"
    if "reason" in report:
        return False, f"heartbeat probe failed: {report['reason']}"
    alive = set(report.get("alive", []))
    dead = set(report.get("dead", []))
    if server_id in alive:
        return True, "python MCP process alive"
    if server_id in dead:
        return False, "python MCP process dead"
    return False, "python MCP process not reported by heartbeat"


def _host_exposure(
    expected_tools: tuple[str, ...],
    observed_host_tools: set[str] | None,
) -> tuple[bool | None, list[str], list[str]]:
    if observed_host_tools is None:
        return None, [], list(expected_tools)
    observed = sorted(tool for tool in expected_tools if tool in observed_host_tools)
    missing = sorted(tool for tool in expected_tools if tool not in observed_host_tools)
    return bool(observed), observed, missing


def _rca_for_result(
    *,
    server_id: str,
    declared: bool,
    host_ok: bool | None,
    native_ok: bool | None,
) -> dict[str, str]:
    if declared and host_ok is True and native_ok is not False:
        return {}
    if not declared:
        return {
            "symptom": f"{server_id} is absent from the configured MCP registry.",
            "root_cause": "The repo-owned .mcp.json does not declare the required MCP server.",
            "fix_or_next": f"fix:add {server_id} to .mcp.json before expecting Codex host exposure.",
            "recurrence_guard": "Keep .mcp.json and .codex/config.toml aligned for always-on MCP servers.",
        }
    if server_id == "memory" and native_ok is False:
        return {
            "symptom": "Memory MCP is not available to Codex readiness.",
            "root_cause": "The Memory Python MCP process is not alive, and no callable Codex Memory route was proven.",
            "fix_or_next": "next:restart or reattach the Codex MCP host so memory starts, then prove a live mcp__memory call before setting CODEX_MCP_CALLABLE_MEMORY=healthy.",
            "recurrence_guard": "Do not treat local script compilation or file-memory fallback as Memory MCP callability.",
        }
    if server_id == "GitKraken" and host_ok is not True:
        return {
            "symptom": "GitKraken MCP is not available to Codex readiness.",
            "root_cause": "The GitKraken CLI can list MCP tools, but the active Codex host did not expose a callable GitKraken tool surface.",
            "fix_or_next": "next:reload or reconfigure the Codex host so GitKraken tools are mounted, then prove a live GitKraken tool call before setting CODEX_MCP_CALLABLE_GITKRAKEN=healthy.",
            "recurrence_guard": "Keep native gk availability separate from host-exposed GitKraken MCP callability.",
        }
    if host_ok is not True:
        return {
            "symptom": f"{server_id} host exposure is unproven.",
            "root_cause": "No Codex tool-search exposure snapshot proved a callable host route.",
            "fix_or_next": f"next:prove a live Codex tool call for {server_id} or keep reporting the degraded route.",
            "recurrence_guard": "Require callable-route proof before marking host MCP parity healthy.",
        }
    return {}


def audit(
    config_path: Path = REPO_CONFIG,
    observed_host_tools: set[str] | None = None,
    heartbeat_report: dict[str, Any] | None = None,
    native_tool_lister: Callable[[str, dict[str, Any]], tuple[bool, set[str], str]] | None = None,
    require_host_exposure: bool = False,
    skip_native_probes: bool = False,
) -> list[ExposureResult]:
    config = _read_config(config_path)
    servers = config.get("mcpServers", {})
    native_lister = native_tool_lister or _config_command_tools
    results: list[ExposureResult] = []

    for server_id, expected in MAJOR_MCP_TOOLS.items():
        reasons: list[str] = []
        declared = server_id in servers
        host_ok, host_observed, host_missing = _host_exposure(expected, observed_host_tools)
        native_ok: bool | None = None
        native_tools: set[str] = set()

        if not declared:
            reasons.append("not declared in .mcp.json")
        if require_host_exposure and host_ok is None:
            reasons.append("no Codex tool_search exposure snapshot supplied")
        elif host_ok is False:
            reasons.append("not exposed in Codex tool_search snapshot")

        if declared and not skip_native_probes:
            if server_id in NATIVE_LIST_TOOLS_REQUIRED:
                native_ok, native_tools, native_reason = native_lister(server_id, config)
                reasons.append(native_reason)
                native_missing = sorted(tool for tool in expected if tool not in native_tools)
                if native_ok and native_missing:
                    native_ok = False
                    reasons.append(f"native list-tools missing: {', '.join(native_missing)}")
            elif server_id in PYTHON_PROCESS_REQUIRED:
                native_ok, native_reason = _heartbeat_native_status(server_id, heartbeat_report)
                reasons.append(native_reason)

        status = "GREEN"
        if not declared or host_ok is False or native_ok is False or (require_host_exposure and host_ok is None):
            status = "RED"
        elif host_ok is None:
            status = "YELLOW"
            reasons.append("Codex tool_search exposure not verified")
        elif native_ok is None:
            status = "YELLOW"
            reasons.append("native server liveness not probed")

        observed_tools = sorted(set(host_observed) | native_tools)
        missing_tools = host_missing if observed_host_tools is not None else []
        results.append(
            ExposureResult(
                server_id=server_id,
                status=status,
                declared=declared,
                host_exposed=host_ok,
                native_ok=native_ok,
                expected_tools=list(expected),
                observed_tools=observed_tools,
                missing_tools=missing_tools,
                reasons=reasons,
                rca=_rca_for_result(
                    server_id=server_id,
                    declared=declared,
                    host_ok=host_ok,
                    native_ok=native_ok,
                ),
            )
        )
    return results


def render_table(results: list[ExposureResult]) -> str:
    lines = [
        "MCP Tool Exposure Audit",
        "",
        f"{'Server':<14} {'Status':<7} {'Declared':<8} {'Host':<8} {'Native':<8} Detail",
        "-" * 100,
    ]
    for result in results:
        host = "unknown" if result.host_exposed is None else str(result.host_exposed).lower()
        native = "n/a" if result.native_ok is None else str(result.native_ok).lower()
        detail = "; ".join(result.reasons) if result.reasons else "ok"
        lines.append(
            f"{result.server_id:<14} {result.status:<7} {str(result.declared).lower():<8} "
            f"{host:<8} {native:<8} {detail}"
        )
    red = sum(1 for item in results if item.status == "RED")
    yellow = sum(1 for item in results if item.status == "YELLOW")
    green = sum(1 for item in results if item.status == "GREEN")
    lines.append("-" * 100)
    lines.append(f"Summary: {green} green, {yellow} yellow, {red} red")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPO_CONFIG)
    parser.add_argument("--tool-search-json", type=Path, default=None)
    parser.add_argument("--require-host-exposure", action="store_true")
    parser.add_argument("--skip-native-probes", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--advisory", action="store_true", help="Always exit 0 after reporting")
    args = parser.parse_args(argv)

    try:
        observed_host_tools = load_tool_search_snapshot(args.tool_search_json)
        results = audit(
            config_path=args.config,
            observed_host_tools=observed_host_tools,
            require_host_exposure=args.require_host_exposure,
            skip_native_probes=args.skip_native_probes,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[mcp_tool_exposure_audit] FAIL: {exc}", file=sys.stderr)
        return 0 if args.advisory else 2

    if args.json:
        print(json.dumps([asdict(item) for item in results], indent=2, sort_keys=True))
    else:
        print(render_table(results))

    failed = any(item.status == "RED" for item in results)
    if failed and not args.advisory:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
