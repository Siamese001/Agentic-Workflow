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
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRIMARY_ROOT = Path(os.environ.get("AGENTIC_PRIMARY_ROOT", r"C:/Git/Agentic-Workflow-FRESH"))
PLACEHOLDER_START = "$" + "{"
CODEX_GOVERNANCE_SCRIPTS = ROOT / ".codex" / "governance" / "scripts"
if str(CODEX_GOVERNANCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(CODEX_GOVERNANCE_SCRIPTS))

import mcp_callability_epoch

SCRIPT_PATHS = [
    "tools/adg/mcp/server.py",
    "tools/memory/adg_memory_server.py",
    "tools/mcp/vector_db_server.py",
    "tools/mcp/pytest_server.py",
    "tools/mcp/redis_mcp_server.py",
    "tools/mcp/pytest_server.py",
    "tools/otel/otel_mcp_server.py",
    "tools/adg/adg_redis_ingest.py",
    "tools/mcp/launch_adg_sqlite_http_mcp.py",
    "tools/mcp/launch_memory_http_mcp.py",
]


PROCESS_MARKERS = {
    "GitKraken": {
        "markers": ["gk.exe mcp"],
        "expected": "single-process-stdio-server",
    },
    "adg_sqlite": {
        "markers": [
            "tools.adg.mcp.server",
            "tools/adg/mcp/server.py",
            "tools.mcp.launch_adg_sqlite_mcp",
            "tools.mcp.launch_adg_sqlite_http_mcp",
        ],
        "expected": "single-python-mcp-service",
    },
    "memory": {
        "markers": ["adg_memory_server.py", "tools.mcp.launch_memory_http_mcp"],
        "expected": "single-python-mcp-service",
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

CALLABLE_STATUS_ENV_PREFIX = "CODEX_MCP_CALLABLE_"
TRUST_ROUTE_CONTRACT_ENV = "CODEX_MCP_TRUST_ROUTE_CONTRACT"
ROUTE_CONTRACT_GLOB = "codex_mcp_live_route_contract.json"
ALWAYS_ON_CORE_SERVERS = frozenset({"GitKraken", "adg_sqlite", "memory"})
PROVEN_CALLABLE_STATUSES = frozenset({"healthy"})
ADG_HTTP_PROOF_TOOLS = frozenset({"adg_health", "adg_runtime_info", "adg_process_identity"})
REPO_MANAGED_HTTP_SERVERS = frozenset({"adg_sqlite", "memory"})
HTTP_SERVICE_DOWN = "http_service_down"
HTTP_PROTOCOL_UNHEALTHY = "http_protocol_unhealthy"
CODEX_HTTP_ROUTE_UNPROVEN = "codex_http_route_unproven"
CODEX_HTTP_ROUTE_CALLABLE = "codex_http_route_callable"
LEGACY_STDIO_CLOSED = "legacy_stdio_closed"


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
                expected = str(config.get("expected") or "")
                process_name = str(info.get("name") or "").lower()
                if expected.startswith("single-python-") and process_name not in {
                    "python",
                    "python.exe",
                    "pythonw",
                    "pythonw.exe",
                }:
                    continue
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
        root_launchers = [row for row in rows if _is_root_launcher(server_id, row.get("cmdline") or [])]
        if not rows:
            classification = "none"
        elif expected.startswith("dormant"):
            classification = "unexpected_live_process"
        elif expected == "single-process-stdio-server":
            classification = "single" if len(rows) == 1 else "duplicate"
        elif expected in {"single-python-stdio-server", "single-python-mcp-service"}:
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


def _latest_route_contract_path() -> Path | None:
    reports_dir = ROOT / "docs" / "reports" / "codex"
    if not reports_dir.exists():
        return None
    candidates = sorted(
        reports_dir.glob(ROUTE_CONTRACT_GLOB),
        key=lambda p: (p.stat().st_mtime, p.name),
        reverse=True,
    )
    return candidates[0] if candidates else None


def _load_route_contract(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _env_callable_status(server_id: str) -> str:
    value = os.environ.get(f"{CALLABLE_STATUS_ENV_PREFIX}{server_id.upper()}", "").strip().lower()
    if value in {"healthy", "closed_transport", "plugin_callable", "substitute_callable", "absent"}:
        return value
    return "absent"


def _file_callable_status(server_id: str, *, root: Path | None = None) -> dict[str, Any]:
    try:
        status = mcp_callability_epoch.proof_status(server_id, repo_root=root or ROOT)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        return {
            "server_id": server_id,
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
        }
    return status


def _route_kind_from_config(config: dict[str, Any] | None) -> str:
    if not isinstance(config, dict):
        return "unknown"
    if config.get("url") or config.get("serverUrl"):
        return "http"
    if config.get("command"):
        return "stdio"
    return "unknown"


def _route_endpoint_from_config(config: dict[str, Any] | None) -> str:
    if not isinstance(config, dict):
        return ""
    return str(config.get("url") or config.get("serverUrl") or "").strip()


def _read_json_dict(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _pid_alive(pid: Any) -> bool | None:
    if not isinstance(pid, int) or pid <= 0:
        return None
    try:
        import psutil  # type: ignore[import-not-found]
    except Exception:  # pragma: no cover - environment dependent
        return None
    try:
        return bool(psutil.pid_exists(pid))
    except Exception:  # pragma: no cover - psutil backend dependent
        return None


def _http_service_state(server_id: str, configured_url: str, *, root: Path = ROOT) -> dict[str, Any]:
    state_path = root / "artifacts" / "mcp_heartbeat" / f"{server_id}_http_launcher.json"
    state = _read_json_dict(state_path)
    if not state:
        return {
            "available": False,
            "status": "absent",
            "state_path": str(state_path),
            "configured_url": configured_url,
            "url_matches_config": False,
        }
    pid = state.get("pid")
    pid_alive = _pid_alive(pid)
    state_url = str(state.get("url") or "").strip()
    return {
        **state,
        "available": True,
        "state_path": str(state_path),
        "configured_url": configured_url,
        "url_matches_config": bool(configured_url and state_url == configured_url),
        "pid_alive": pid_alive,
    }


def _http_service_down(service_state: dict[str, Any]) -> bool:
    if not service_state.get("available"):
        return True
    if str(service_state.get("status") or "").strip().lower() != "running":
        return True
    if service_state.get("pid_alive") is False:
        return True
    if service_state.get("url_matches_config") is False:
        return True
    return False


def _http_protocol_unhealthy(service_state: dict[str, Any]) -> bool:
    explicit = str(service_state.get("protocol_status") or "").strip().lower()
    if explicit in {"fail", "failed", "error", "unhealthy"}:
        return True
    protocol_probe = service_state.get("protocol_probe")
    if isinstance(protocol_probe, dict):
        status = str(protocol_probe.get("status") or "").strip().lower()
        if status and status != "ok":
            return True
    preflight = service_state.get("preflight")
    if isinstance(preflight, dict):
        status = str(preflight.get("status") or "").strip().lower()
        if status and status != "ok":
            return True
    return False


def _http_proof_matches_route(server_id: str, configured_url: str, proof: dict[str, Any]) -> bool:
    if str(proof.get("status") or "").strip().lower() != "healthy":
        return False
    if str(proof.get("route_kind") or "").strip().lower() != "http":
        return False
    if not configured_url or str(proof.get("endpoint") or "").strip() != configured_url:
        return False
    if server_id == "adg_sqlite":
        tool = str(proof.get("tool") or "").strip()
        if tool not in ADG_HTTP_PROOF_TOOLS:
            return False
    return True


def http_route_acceptance(server_id: str, configured_url: str, proof: dict[str, Any]) -> dict[str, Any]:
    """Explain whether a current-session proof is acceptable for a HTTP route."""
    accepted = _http_proof_matches_route(server_id, configured_url, proof)
    reasons: list[str] = []
    if str(proof.get("status") or "").strip().lower() != "healthy":
        reasons.append("proof_not_healthy")
    if str(proof.get("route_kind") or "").strip().lower() != "http":
        reasons.append("proof_route_kind_not_http")
    if str(proof.get("endpoint") or "").strip() != configured_url:
        reasons.append("proof_endpoint_mismatch")
    if server_id == "adg_sqlite" and str(proof.get("tool") or "").strip() not in ADG_HTTP_PROOF_TOOLS:
        reasons.append("adg_proof_tool_not_allowed")
    return {
        "accepted": accepted,
        "required_route_kind": "http",
        "required_endpoint": configured_url,
        "required_tools": sorted(ADG_HTTP_PROOF_TOOLS) if server_id == "adg_sqlite" else [],
        "reasons": [] if accepted else reasons,
    }


def _callable_status(server_id: str, *, root: Path | None = None) -> tuple[str, dict[str, Any]]:
    value = _env_callable_status(server_id)
    file_status = _file_callable_status(server_id, root=root)
    if value == "absent" and file_status.get("status") == "healthy":
        return "healthy", file_status
    return value, file_status


def _route_callable_status(route: dict[str, Any], *, trust_contract_proof: bool = False) -> str:
    if not trust_contract_proof:
        return "absent"
    status = str(route.get("callable_status") or "").strip().lower()
    if status not in PROVEN_CALLABLE_STATUSES:
        return "absent"
    proof = route.get("proof")
    if not isinstance(proof, dict):
        return "absent"
    tool = str(proof.get("tool") or "").strip()
    evidence = str(proof.get("evidence") or "").strip()
    return status if tool and evidence else "absent"


def _normalize_selected_route(route: dict[str, Any]) -> str:
    selected = str(route.get("selected_codex_route") or route.get("codex_route") or "").strip()
    if selected == "raw_mcp_callable":
        return "raw_mcp_callable"
    if selected == "raw_mcp":
        return (
            "host_mcp_required"
            if str(route.get("server_id", "")) in ALWAYS_ON_CORE_SERVERS
            else "degraded_fallback"
        )
    if selected == "none":
        server_id = str(route.get("server_id", ""))
        status = str(route.get("status", ""))
        if server_id in ALWAYS_ON_CORE_SERVERS:
            return "host_mcp_required"
        if status == "blocked_degraded":
            return "degraded_fallback"
        if status == "callable_substitute":
            return "substitute_callable"
    if selected == "node_repl_or_browser_plugin":
        return "substitute_callable"
    return selected


def _normalize_fallback_key(route: dict[str, Any]) -> str:
    fallback = str(route.get("fallback_message_key") or "").strip()
    if fallback:
        return fallback

    status = str(route.get("status", ""))
    server_id = str(route.get("server_id", ""))
    if status == "transport_green_payload_blocked":
        return "closed_transport"
    if status == "blocked_degraded":
        return "raw_mcp_unavailable"
    if status == "blocked":
        return "no_substitute" if server_id in ALWAYS_ON_CORE_SERVERS else "raw_mcp_unavailable"
    if status in {"callable", "plugin_substitute"}:
        return "plugin_substitute"
    if status == "callable_substitute":
        return "plugin_substitute"
    return ""


def classify_route(
    route: dict[str, Any],
    process_state: dict[str, Any],
    callable_status: str = "absent",
    *,
    route_kind: str = "stdio",
    http_service_state: dict[str, Any] | None = None,
    http_proof_accepted: bool = False,
) -> str:
    """Classify a Codex MCP route without treating process presence as parity."""
    selected = _normalize_selected_route(route)
    fallback_key = _normalize_fallback_key(route)
    server_id = str(route.get("server_id") or "").strip()
    process_count = int(process_state.get("process_count") or 0)
    normalized_kind = str(route_kind or "stdio").strip().lower()

    if normalized_kind == "http":
        state = http_service_state or {}
        if callable_status == "healthy" and http_proof_accepted:
            return CODEX_HTTP_ROUTE_CALLABLE
        if server_id in REPO_MANAGED_HTTP_SERVERS:
            if _http_service_down(state):
                return HTTP_SERVICE_DOWN
            if _http_protocol_unhealthy(state):
                return HTTP_PROTOCOL_UNHEALTHY
        return CODEX_HTTP_ROUTE_UNPROVEN

    if callable_status == "healthy":
        return "CALLABLE"
    if callable_status == "closed_transport" or fallback_key == "closed_transport":
        return LEGACY_STDIO_CLOSED
    if selected == "raw_mcp_callable":
        return "PROCESS_ONLY" if process_count > 0 else "HOST_MCP_REQUIRED"
    if callable_status == "plugin_callable" or selected == "plugin_substitute":
        return "PLUGIN_SUBSTITUTE"
    if callable_status == "substitute_callable" or selected == "substitute_callable":
        return "SUBSTITUTE_CALLABLE"
    if process_count > 0:
        return "PROCESS_ONLY"
    if selected == "host_mcp_required":
        return "HOST_MCP_REQUIRED"
    if selected == "degraded_fallback":
        return "DEGRADED_FALLBACK"
    return "NOT_EXPOSED"


def build_route_evidence(
    contract: dict[str, Any] | None,
    process_servers: dict[str, Any],
    *,
    trust_contract_callable_proof: bool = False,
    registry_servers: dict[str, Any] | None = None,
    http_service_states: dict[str, dict[str, Any]] | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    if not contract:
        return {"available": False, "reason": "no route contract found", "servers": {}}

    classified: dict[str, Any] = {}
    counts: dict[str, int] = {}
    registry = registry_servers if isinstance(registry_servers, dict) else {}
    resolved_root = root or ROOT
    for route in contract.get("routes", []):
        server_id = str(route.get("server_id", ""))
        process_state = process_servers.get(server_id, {})
        callable_status, file_callability_proof = _callable_status(server_id, root=resolved_root)
        route_config = registry.get(server_id)
        route_config = route_config if isinstance(route_config, dict) else {}
        route_kind = _route_kind_from_config(route_config)
        configured_url = _route_endpoint_from_config(route_config)
        http_state = {}
        http_acceptance: dict[str, Any] = {}
        if route_kind == "http":
            if http_service_states is not None and server_id in http_service_states:
                http_state = dict(http_service_states[server_id])
            else:
                http_state = _http_service_state(server_id, configured_url, root=resolved_root)
            http_acceptance = http_route_acceptance(
                server_id,
                configured_url,
                file_callability_proof,
            )
            if http_acceptance.get("accepted"):
                callable_status = "healthy"
            elif callable_status == "healthy":
                callable_status = "absent"
        if callable_status == "absent":
            callable_status = _route_callable_status(
                route,
                trust_contract_proof=trust_contract_callable_proof,
            )
        classification = classify_route(
            route,
            process_state,
            callable_status,
            route_kind=route_kind,
            http_service_state=http_state,
            http_proof_accepted=bool(http_acceptance.get("accepted")),
        )
        counts[classification] = counts.get(classification, 0) + 1
        classified[server_id] = {
            "classification": classification,
            "callable_status": callable_status,
            "selected_codex_route": route.get("selected_codex_route"),
            "fallback_message_key": route.get("fallback_message_key"),
            "route_kind": route_kind,
            "configured_url": configured_url,
            "process_classification": process_state.get("classification", "none"),
            "process_count": process_state.get("process_count", 0),
            "route_owner": route.get("route_owner"),
            "w2_decision": route.get("w2_decision"),
            "callability_proof": file_callability_proof,
        }
        if route_kind == "http":
            classified[server_id]["http_service_state"] = http_state
            classified[server_id]["http_callability_acceptance"] = http_acceptance

    return {
        "available": True,
        "contract_plan_id": contract.get("plan_id"),
        "contract_wave": contract.get("wave"),
        "counts": dict(sorted(counts.items())),
        "servers": classified,
    }


def build_report(route_contract_path: Path | None = None) -> dict[str, Any]:
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
        for line_number, line in enumerate(
            env_file.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            if line.strip().startswith("TAVILY_API_KEY="):
                value = line.split("=", 1)[1].strip()
                tavily_env_file = {
                    "exists": True,
                    "present": bool(value),
                    "line": line_number,
                    "length": len(value),
                }

    processes = _processes()
    env_contract = os.environ.get("CODEX_MCP_ROUTE_CONTRACT")
    contract_path = (
        route_contract_path or (Path(env_contract) if env_contract else None) or _latest_route_contract_path()
    )
    route_contract = _load_route_contract(contract_path)
    trust_contract_callable_proof = os.environ.get(TRUST_ROUTE_CONTRACT_ENV, "").strip() == "1"

    return {
        "repo_root": str(ROOT),
        "primary_root": str(PRIMARY_ROOT),
        "registry_path": str(registry_path),
        "route_contract_path": str(contract_path) if contract_path else None,
        "command_paths": {
            name: shutil.which(name) for name in ["python", "cmd", "npx", "node", "git", "gk", "redis-cli"]
        },
        "script_compile": {rel: _compile_script(ROOT / rel) for rel in sorted(set(SCRIPT_PATHS))},
        "tcp": {"localhost:6379": _tcp_probe("localhost", 6379)},
        "env": env_state,
        "env_file_tavily_api_key": tavily_env_file,
        "registry_unresolved_placeholders": unresolved,
        "normalized_paths": {
            "eval_artifacts_adg_exists": (ROOT / "artifacts" / "adg").exists(),
            "primary_artifacts_adg_exists": (PRIMARY_ROOT / "artifacts" / "adg").exists(),
        },
        "processes": processes,
        "route_evidence": build_route_evidence(
            route_contract,
            processes.get("servers", {}),
            trust_contract_callable_proof=trust_contract_callable_proof,
            registry_servers=servers,
            root=ROOT,
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument(
        "--route-contract",
        type=Path,
        help="Optional Codex route contract JSON; defaults to docs/reports/codex/codex_mcp_live_route_contract.json",
    )
    args = parser.parse_args()
    report = build_report(args.route_contract)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
