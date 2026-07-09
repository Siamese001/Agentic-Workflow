#!/usr/bin/env python3
"""Codex MCP transport readiness gate for UserPromptSubmit.

This gate checks every enabled repo-declared MCP server before a normal user
prompt is accepted. A server's configured command/url probe is green only when
it can complete a real MCP JSON-RPC ``initialize`` plus ``tools/list`` exchange.
That proves protocol viability, not active-session Codex tool callability.

Scope: root ``.mcp.json`` is the repo MCP SSOT. The generated Codex Desktop
projection marks these servers ``required = true``. This hook records the same
per-turn evidence, blocks strict proof/eval/publication prompts and nonnegotiable
config/spawn failures, and warns for ordinary exploratory prompts instead of
letting transport churn stop low-risk design work.

Explicit MCP/ADG repair/RCA prompts are allowed through so a red transport can
be fixed from inside Codex. Active-session ADG callability is enforced by the
dedicated ADG SSOT gate and Codex readiness checks.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Callable
import urllib.error
import urllib.request


GOV_DIR = Path(__file__).resolve().parent
if str(GOV_DIR) not in sys.path:
    sys.path.insert(0, str(GOV_DIR))

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
GOVERNANCE_SCRIPTS = REPO_ROOT / "scripts" / "governance"
if str(GOVERNANCE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_SCRIPTS))

MCP_CONFIG = REPO_ROOT / ".mcp.json"
LOG_PATH = REPO_ROOT / "artifacts" / "mcp" / "required_mcp_gate.jsonl"
DEFAULT_TIMEOUT_SEC = 30.0
DEFAULT_MAX_WORKERS = 8
ADG_PROTOCOL_PROBE_STATE = "artifacts/mcp_heartbeat/adg_sqlite_protocol_probe_launcher.json"

BYPASS_ENV = "REQUIRED_MCP_GATE_BYPASS"
DISABLE_REPAIR_BYPASS_ENV = "REQUIRED_MCP_GATE_DISABLE_REPAIR_BYPASS"
SERVER_LIST_ENV = "REQUIRED_MCP_GATE_SERVERS"
CALLABILITY_SERVER_LIST_ENV = "REQUIRED_MCP_GATE_CALLABILITY_SERVERS"
TIMEOUT_ENV = "REQUIRED_MCP_GATE_TIMEOUT_SEC"
MAX_WORKERS_ENV = "REQUIRED_MCP_GATE_MAX_WORKERS"
ENFORCE_ENV = "REQUIRED_MCP_GATE_ENFORCE"

DEFAULT_CALLABILITY_REQUIRED_SERVERS = ("memory", "GitKraken", "adg_sqlite", "vector_db")
CALLABLE_ROUTE_CLASSIFICATIONS = {
    "CALLABLE",
    "PLUGIN_SUBSTITUTE",
    "SUBSTITUTE_CALLABLE",
    "codex_http_route_callable",
}

_MCP_REPAIR_PHRASES = (
    "/mcp-failure-rca",
    "mcp_repair:",
    "mcp repair:",
    "repair mcp transport",
    "repair mcp callability",
    "fix mcp transport",
    "fix mcp callability",
    "debug mcp transport",
    "debug mcp callability",
    "mcp transport rca",
    "mcp callability rca",
    "mcp failure rca",
    "adg transport rca",
    "adg callability rca",
    "repair adg transport",
    "fix adg transport",
    "debug adg transport",
    "restore adg transport",
    "restore mcp transport",
    "reconnect mcp transport",
)

_STRICT_PROMPT_PHRASES = (
    "codex_readiness",
    "codex_main_closeout",
    "create pr",
    "draft pr",
    "end to end",
    "e2e",
    "eval",
    "evaluation",
    "full adg",
    "full run",
    "merge to local main",
    "merge to main",
    "origin/main",
    "pr branch",
    "proof",
    "publish",
    "publication",
    "pull request",
    "push origin",
    "release",
    "strict",
)


@dataclass(frozen=True)
class ProbeSpec:
    server_id: str
    transport: str
    command: str = ""
    args: tuple[str, ...] = ()
    cwd: str = ""
    env: dict[str, str] | None = None
    url: str = ""
    missing_env: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProbeResult:
    server_id: str
    status: str
    reason: str = ""
    transport: str = ""
    tools_count: int = 0
    tool_names: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "ok"


ProbeFunc = Callable[[ProbeSpec, float], ProbeResult]
CallabilityCheckFunc = Callable[[tuple[str, ...]], list[ProbeResult]]


def _parse_positive_float(raw: str, default: float) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _parse_positive_int(raw: str, default: int) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _read_payload(raw: str) -> dict[str, Any]:
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return payload if isinstance(payload, dict) else {"value": payload}


def _read_prompt(raw: str) -> str:
    payload = _read_payload(raw)
    candidates: list[Any] = [
        payload.get("prompt"),
        payload.get("user_prompt"),
        payload.get("message"),
        payload.get("text"),
        payload.get("raw"),
    ]
    for nested_key in ("tool_info", "toolInfo"):
        nested = payload.get(nested_key)
        if isinstance(nested, dict):
            candidates.extend(
                [
                    nested.get("prompt"),
                    nested.get("user_prompt"),
                    nested.get("message"),
                    nested.get("text"),
                ]
            )
    return "\n".join(str(value) for value in candidates if isinstance(value, str) and value.strip())


def _is_mcp_repair_prompt(prompt: str) -> bool:
    text = " ".join(prompt.lower().split())
    return any(phrase in text for phrase in _MCP_REPAIR_PHRASES)


def _repair_bypass_enabled() -> bool:
    return os.environ.get(DISABLE_REPAIR_BYPASS_ENV) != "1"


def _enforcement_mode() -> str:
    raw = os.environ.get(ENFORCE_ENV, "auto").strip().lower()
    return raw if raw in {"auto", "block", "warn"} else "auto"


def _is_strict_prompt(prompt: str) -> bool:
    text = " ".join(prompt.lower().split())
    return any(phrase in text for phrase in _STRICT_PROMPT_PHRASES)


def _should_block_failures(prompt: str) -> bool:
    mode = _enforcement_mode()
    if mode == "block":
        return True
    if mode == "warn":
        return False
    return _is_strict_prompt(prompt)


def _has_nonnegotiable_failure(failures: list[ProbeResult]) -> bool:
    """Config/spawn-safety failures are not advisory transport readiness churn."""
    for failure in failures:
        if failure.transport == "config":
            return True
        if failure.reason.startswith("missing required environment:"):
            return True
        if failure.reason == "missing command/url":
            return True
    return False


def _server_filter_from_env() -> set[str] | None:
    raw = os.environ.get(SERVER_LIST_ENV, "").strip()
    if not raw:
        return None
    return {part.strip() for part in raw.split(",") if part.strip()}


def _callability_servers_from_env() -> tuple[str, ...]:
    raw = os.environ.get(CALLABILITY_SERVER_LIST_ENV)
    if raw is None:
        return DEFAULT_CALLABILITY_REQUIRED_SERVERS
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def _load_enabled_specs(config_path: Path = MCP_CONFIG) -> list[ProbeSpec]:
    import sync_mcp_config as sync

    data = sync.load_repo_config(config_path)
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        raise ValueError(f"{config_path} has no mcpServers object")

    include = _server_filter_from_env()
    specs: list[ProbeSpec] = []
    for server_id, cfg_value in servers.items():
        if include is not None and server_id not in include:
            continue
        if not isinstance(cfg_value, dict) or cfg_value.get("disabled"):
            continue

        cfg = cfg_value
        if cfg.get("command"):
            command, args = sync._codex_command_projection(  # noqa: SLF001 - same governance package
                str(cfg["command"]),
                list(cfg.get("args", []) or []),
                REPO_ROOT,
            )
            static_env: dict[str, str] = {}
            passthrough_vars: list[str] = []
            if isinstance(cfg.get("env"), dict):
                static_env, passthrough_vars = sync._env_projection(cfg["env"], REPO_ROOT)  # noqa: SLF001

            env = os.environ.copy()
            env.update(static_env)
            missing_env = tuple(
                key
                for key in passthrough_vars
                if not os.environ.get(key) and ("TOKEN" in key.upper() or "API_KEY" in key.upper())
            )
            for key in passthrough_vars:
                value = os.environ.get(key)
                if value:
                    env[key] = value

            probe_args = [str(arg) for arg in args]
            if str(server_id) == "adg_sqlite":
                env["ADG_SKIP_ZOMBIE_KILL"] = "1"
                env["MCP_HEARTBEAT_DISABLE"] = "1"
                if "tools.mcp.launch_adg_sqlite_mcp" in probe_args:
                    if "--skip-guard" not in probe_args:
                        probe_args.append("--skip-guard")
                    if "--state-path" not in probe_args:
                        probe_args.extend(["--state-path", ADG_PROTOCOL_PROBE_STATE])

            specs.append(
                ProbeSpec(
                    server_id=str(server_id),
                    transport="stdio",
                    command=command,
                    args=tuple(probe_args),
                    cwd=str(REPO_ROOT),
                    env=env,
                    missing_env=missing_env,
                )
            )
            continue

        url = cfg.get("url") or cfg.get("serverUrl")
        if url:
            specs.append(
                ProbeSpec(
                    server_id=str(server_id),
                    transport="http",
                    url=sync._expand_mcp_placeholders(str(url), REPO_ROOT),  # noqa: SLF001
                )
            )
            continue

        specs.append(
            ProbeSpec(
                server_id=str(server_id),
                transport="unknown",
                missing_env=("missing command/url",),
            )
        )
    return specs


def _initialize_request() -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "codex_required_mcp_gate", "version": "1.0"},
        },
    }


def _initialized_notification() -> dict[str, Any]:
    return {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}


def _tools_list_request() -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}


def _stdio_payload() -> str:
    return "\n".join(
        json.dumps(message)
        for message in (_initialize_request(), _initialized_notification(), _tools_list_request())
    ) + "\n"


def _json_messages_from_text(text: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("data:"):
            line = line[5:].strip()
        elif line.startswith("event:") or line.startswith(":"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            messages.append(value)
    if messages:
        return messages
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return []
    return [value] if isinstance(value, dict) else []


def _tools_from_messages(messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]] | None, str]:
    saw_initialize = False
    for message in messages:
        if message.get("id") == 1 and isinstance(message.get("result"), dict):
            saw_initialize = True
        if message.get("id") != 2:
            continue
        if "error" in message:
            return None, f"tools/list error: {message.get('error')}"
        result = message.get("result")
        tools = result.get("tools") if isinstance(result, dict) else None
        if isinstance(tools, list):
            return [tool for tool in tools if isinstance(tool, dict)], ""
        return None, "tools/list result.tools is not a list"
    if not saw_initialize:
        return None, "no initialize response"
    return None, "no tools/list response"


def _result_from_tools(spec: ProbeSpec, tools: list[dict[str, Any]]) -> ProbeResult:
    names = tuple(
        sorted(str(tool.get("name")) for tool in tools if isinstance(tool.get("name"), str))
    )
    return ProbeResult(
        server_id=spec.server_id,
        status="ok",
        transport=spec.transport,
        tools_count=len(tools),
        tool_names=names[:50],
    )


def probe_stdio_server(spec: ProbeSpec, timeout: float) -> ProbeResult:
    if spec.missing_env:
        return ProbeResult(
            server_id=spec.server_id,
            status="fail",
            reason=f"missing required environment: {', '.join(spec.missing_env)}",
            transport=spec.transport,
        )

    command = spec.command
    if not command:
        return ProbeResult(spec.server_id, "fail", "missing command", spec.transport)
    if not Path(command).is_absolute():
        resolved = shutil.which(command)
        if resolved:
            command = resolved
        else:
            return ProbeResult(spec.server_id, "fail", f"command not found: {command}", spec.transport)

    argv = [command, *spec.args]
    proc: subprocess.Popen[str] | None = None
    try:
        proc = subprocess.Popen(
            argv,
            cwd=spec.cwd or str(REPO_ROOT),
            env=spec.env or os.environ.copy(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        stdout, stderr = proc.communicate(input=_stdio_payload(), timeout=timeout)
    except subprocess.TimeoutExpired:
        if proc is not None:
            proc.kill()
            stdout, stderr = proc.communicate(timeout=5)
        else:
            stdout, stderr = "", ""
        return ProbeResult(
            spec.server_id,
            "fail",
            f"timeout after {timeout:g}s; stderr_tail={(stderr or '')[-300:].strip()!r}",
            spec.transport,
        )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        return ProbeResult(spec.server_id, "fail", f"{type(exc).__name__}: {exc}", spec.transport)
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.kill()
            except OSError:
                pass

    tools, reason = _tools_from_messages(_json_messages_from_text(stdout or ""))
    if tools is None:
        stderr_tail = (stderr or "")[-300:].strip()
        detail = reason if not stderr_tail else f"{reason}; stderr_tail={stderr_tail!r}"
        return ProbeResult(spec.server_id, "fail", detail, spec.transport)
    return _result_from_tools(spec, tools)


def _http_post_jsonrpc(
    url: str,
    message: dict[str, Any],
    timeout: float,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], list[dict[str, Any]]]:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "User-Agent": "codex-required-mcp-gate/1.0",
    }
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(
        url,
        data=json.dumps(message).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - user-configured MCP URL
        body = response.read().decode("utf-8", "replace")
        return response.status, {k.lower(): v for k, v in response.headers.items()}, _json_messages_from_text(body)


def probe_http_server(spec: ProbeSpec, timeout: float) -> ProbeResult:
    if not spec.url:
        return ProbeResult(spec.server_id, "fail", "missing url", spec.transport)
    try:
        init_status, init_headers, init_messages = _http_post_jsonrpc(
            spec.url,
            _initialize_request(),
            timeout,
        )
        if init_status >= 400:
            return ProbeResult(spec.server_id, "fail", f"initialize HTTP {init_status}", spec.transport)
        if not any(message.get("id") == 1 and isinstance(message.get("result"), dict) for message in init_messages):
            return ProbeResult(spec.server_id, "fail", "no initialize response", spec.transport)

        session_id = init_headers.get("mcp-session-id")
        session_headers = {"Mcp-Session-Id": session_id} if session_id else {}
        _http_post_jsonrpc(spec.url, _initialized_notification(), timeout, session_headers)
        _tools_status, _tools_headers, tools_messages = _http_post_jsonrpc(
            spec.url,
            _tools_list_request(),
            timeout,
            session_headers,
        )
    except urllib.error.HTTPError as exc:
        body = exc.read(300).decode("utf-8", "replace")
        return ProbeResult(
            spec.server_id,
            "fail",
            f"HTTP {exc.code}: {body.strip()!r}",
            spec.transport,
        )
    except (urllib.error.URLError, OSError, TimeoutError, ValueError, RuntimeError) as exc:
        return ProbeResult(spec.server_id, "fail", f"{type(exc).__name__}: {exc}", spec.transport)

    tools, reason = _tools_from_messages(tools_messages)
    if tools is None:
        return ProbeResult(spec.server_id, "fail", reason, spec.transport)
    return _result_from_tools(spec, tools)


def probe_server(spec: ProbeSpec, timeout: float) -> ProbeResult:
    if spec.transport == "stdio":
        return probe_stdio_server(spec, timeout)
    if spec.transport == "http":
        return probe_http_server(spec, timeout)
    return ProbeResult(spec.server_id, "fail", "unsupported MCP transport", spec.transport)


def _append_receipt(payload: dict[str, Any], results: list[ProbeResult], decision: str) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "schema_version": "required-mcp-gate/v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "decision": decision,
            "session_id": str(payload.get("session_id") or payload.get("sessionId") or ""),
            "results": [asdict(result) for result in results],
        }
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except Exception:  # guardian: receipt write must never change gate decision
        return


def _run_probes(specs: list[ProbeSpec], timeout: float, probe_func: ProbeFunc) -> list[ProbeResult]:
    if not specs:
        return []
    max_workers = min(
        len(specs),
        _parse_positive_int(os.environ.get(MAX_WORKERS_ENV, ""), DEFAULT_MAX_WORKERS),
    )
    results: list[ProbeResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(probe_func, spec, timeout): spec for spec in specs}
        for future in as_completed(futures):
            spec = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # guardian: one probe crash is one red server, not a hook crash
                results.append(
                    ProbeResult(
                        spec.server_id,
                        "fail",
                        f"probe crashed: {type(exc).__name__}: {exc}",
                        spec.transport,
                    )
                )
    return sorted(results, key=lambda result: result.server_id.lower())


def _route_failure_reason(state: dict[str, Any] | None) -> str:
    if not isinstance(state, dict):
        return "route evidence absent"
    parts = [
        f"classification={state.get('classification') or 'absent'}",
        f"callable_status={state.get('callable_status') or 'absent'}",
        f"selected_route={state.get('selected_codex_route') or 'absent'}",
        f"route_kind={state.get('route_kind') or 'absent'}",
        f"configured_url={state.get('configured_url') or 'absent'}",
        f"process_classification={state.get('process_classification') or 'absent'}",
        f"process_count={state.get('process_count') or 0}",
    ]
    fallback = state.get("fallback_message_key")
    if fallback:
        parts.append(f"fallback={fallback}")
    return "; ".join(parts)


def _check_required_route_callability(required_servers: tuple[str, ...]) -> list[ProbeResult]:
    if not required_servers:
        return []
    try:
        import audit_codex_mcp_transports as audit
    except Exception as exc:
        return [
            ProbeResult(
                "mcp_route_contract",
                "fail",
                f"route audit import failed: {type(exc).__name__}: {exc}",
                "codex-route",
            )
        ]
    try:
        report = audit.build_report()
    except Exception as exc:
        return [
            ProbeResult(
                "mcp_route_contract",
                "fail",
                f"route audit failed: {type(exc).__name__}: {exc}",
                "codex-route",
            )
        ]

    evidence = report.get("route_evidence", {})
    if not isinstance(evidence, dict) or not evidence.get("available"):
        return [
            ProbeResult(
                "mcp_route_contract",
                "fail",
                f"route evidence unavailable: {evidence.get('reason') if isinstance(evidence, dict) else 'missing'}",
                "codex-route",
            )
        ]
    servers = evidence.get("servers", {})
    failures: list[ProbeResult] = []
    for server_id in required_servers:
        state = servers.get(server_id) if isinstance(servers, dict) else None
        classification = str(state.get("classification", "")) if isinstance(state, dict) else ""
        if classification in CALLABLE_ROUTE_CLASSIFICATIONS or classification.upper() in CALLABLE_ROUTE_CLASSIFICATIONS:
            continue
        failures.append(
            ProbeResult(
                server_id,
                "fail",
                _route_failure_reason(state),
                "codex-route",
            )
        )
    return failures


def _print_failures(failures: list[ProbeResult]) -> None:
    print("[required_mcp_gate] BLOCKED: required Codex MCP transports are not green.", file=sys.stderr)
    for failure in failures:
        print(
            f"[required_mcp_gate] RED {failure.server_id} "
            f"({failure.transport or 'unknown'}): {failure.reason}",
            file=sys.stderr,
        )
    print(
        "[required_mcp_gate] Repair MCP transport/callability first, then retry the original prompt.",
        file=sys.stderr,
    )


def _print_warnings(failures: list[ProbeResult], prompt: str) -> None:
    mode = _enforcement_mode()
    strict_note = (
        "Strict proof/eval/publication prompts still block; set "
        f"{ENFORCE_ENV}=block to force old behavior or {ENFORCE_ENV}=warn to always warn."
    )
    print(
        "[required_mcp_gate] WARNING: required Codex MCP transports are not green; "
        f"allowing non-strict prompt in {mode!r} mode. {strict_note}",
        file=sys.stderr,
    )
    if prompt:
        print(f"[required_mcp_gate] prompt_class=strict:{_is_strict_prompt(prompt)}", file=sys.stderr)
    for failure in failures:
        print(
            f"[required_mcp_gate] WARN {failure.server_id} "
            f"({failure.transport or 'unknown'}): {failure.reason}",
            file=sys.stderr,
        )


def run_gate(
    raw: str,
    *,
    config_path: Path = MCP_CONFIG,
    probe_func: ProbeFunc = probe_server,
    callability_check_func: CallabilityCheckFunc = _check_required_route_callability,
    timeout: float | None = None,
) -> int:
    payload = _read_payload(raw)
    prompt = _read_prompt(raw)
    if os.environ.get(BYPASS_ENV) == "1":
        print(f"[required_mcp_gate] {BYPASS_ENV}=1; bypassing required MCP gate.", file=sys.stderr)
        _append_receipt(payload, [], "bypass")
        return 0
    if not raw.strip():
        return 0
    if _repair_bypass_enabled() and _is_mcp_repair_prompt(prompt):
        print(
            "[required_mcp_gate] MCP repair/RCA prompt detected; allowing recovery path.",
            file=sys.stderr,
        )
        _append_receipt(payload, [], "repair_prompt")
        return 0

    timeout_value = timeout if timeout is not None else _parse_positive_float(
        os.environ.get(TIMEOUT_ENV, ""),
        DEFAULT_TIMEOUT_SEC,
    )
    try:
        specs = _load_enabled_specs(config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = ProbeResult("mcp_config", "fail", f"{type(exc).__name__}: {exc}", "config")
        _print_failures([result])
        _append_receipt(payload, [result], "block")
        return 2

    if not specs:
        result = ProbeResult("mcp_config", "fail", "no enabled MCP servers found", "config")
        _print_failures([result])
        _append_receipt(payload, [result], "block")
        return 2

    results = _run_probes(specs, timeout_value, probe_func)
    failures = [result for result in results if not result.ok]
    if failures:
        if _has_nonnegotiable_failure(failures) or _should_block_failures(prompt):
            _print_failures(failures)
            _append_receipt(payload, results, "block")
            return 2
        _print_warnings(failures, prompt)
        _append_receipt(payload, results, "warn")
        return 0

    callability_failures = callability_check_func(_callability_servers_from_env())
    if callability_failures:
        if _should_block_failures(prompt):
            _print_failures(callability_failures)
            _append_receipt(payload, [*results, *callability_failures], "block")
            return 2
        _print_warnings(callability_failures, prompt)
        _append_receipt(payload, [*results, *callability_failures], "warn")
        return 0

    summary = ", ".join(f"{result.server_id}:{result.tools_count}" for result in results)
    print(
        "[required_mcp_gate] PASS: configured MCP protocol probes green "
        f"({summary}); active-session ADG callability is enforced separately.",
        file=sys.stderr,
    )
    _append_receipt(payload, results, "allow")
    return 0


def main() -> int:
    try:
        if sys.stdin.isatty():
            return 0
    except (OSError, ValueError):
        pass
    return run_gate(sys.stdin.read())


if __name__ == "__main__":
    raise SystemExit(main())
