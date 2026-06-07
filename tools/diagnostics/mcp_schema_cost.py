"""mcp_schema_cost.py - one-shot audit of MCP server schema bytes.

Spawns each enabled stdio MCP server from `.cursor/mcp.json`, sends
JSON-RPC `initialize` + `tools/list`, captures the response, measures the
serialized-bytes cost of the tool schemas, and writes a ranked report to:

  - `artifacts/governance/mcp_schema_cost.json` (machine-readable)
  - `docs/reports/token-burn/mcp_schema_cost.md` (human-readable summary)

Servers without a `command` (e.g. HTTP `url`-only entries like deepwiki) and
servers requiring uninitialized auth env vars are marked `skipped` with a reason.

Why this matters: every connected MCP loads its full tool schemas into
context at session start, regardless of use. A 13-server fleet with
verbose schemas can sink thousands of tokens before the user types a thing.
This audit identifies retirement candidates (rarely-used MCPs with bloated
schemas) for the W3 always-on trim phase.

Usage:
  python tools/diagnostics/mcp_schema_cost.py
  python tools/diagnostics/mcp_schema_cost.py --timeout 10
  python tools/diagnostics/mcp_schema_cost.py --servers adg_sqlite,redis
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_CONFIG = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"
OUT_JSON = REPO_ROOT / "artifacts" / "governance" / "mcp_schema_cost.json"
OUT_MD = REPO_ROOT / "docs" / "reports" / "token-burn" / "mcp_schema_cost.md"

# Substitute ${env:VAR} references in command/args/env values.
_ENV_SUB = re.compile(r"\$\{env:([A-Z_][A-Z0-9_]*)\}")


def _expand(value: str) -> str:
    def repl(m: re.Match[str]) -> str:
        var = m.group(1)
        return os.environ.get(var, "")
    return _ENV_SUB.sub(repl, value or "")


def _expand_list(values: list[str]) -> list[str]:
    return [_expand(v) for v in values]


def _expand_env(env_dict: dict[str, str]) -> dict[str, str]:
    return {k: _expand(v) for k, v in env_dict.items()}


def _build_init_request() -> str:
    """JSON-RPC initialize message. MCP servers require this before tools/list."""
    msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp_schema_cost", "version": "1.0"},
        },
    }
    return json.dumps(msg) + "\n"


def _build_initialized_notification() -> str:
    msg = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
    return json.dumps(msg) + "\n"


def _build_tools_list_request() -> str:
    msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    return json.dumps(msg) + "\n"


def _probe_server(
    name: str, spec: dict[str, Any], timeout: float
) -> dict[str, Any]:
    """Spawn a stdio MCP server and capture its tools/list response.

    Returns a result row with status in {"measured", "skipped", "error"}.
    """
    result: dict[str, Any] = {
        "server": name,
        "status": "skipped",
        "reason": None,
        "tools_count": 0,
        "schema_bytes": 0,
        "approx_schema_tokens": 0,
        "tool_names": [],
    }

    if spec.get("disabled"):
        result["reason"] = "disabled in mcp_config.json"
        return result

    if "url" in spec and "command" not in spec:
        result["reason"] = "remote (HTTP url) - schema not measured by this probe"
        return result

    command = spec.get("command")
    if not command:
        result["reason"] = "no command in spec"
        return result

    # Expand ${env:VAR}.
    cmd_expanded = _expand(command)
    args_expanded = _expand_list(spec.get("args", []))

    if not cmd_expanded:
        result["reason"] = f"command resolved to empty (env var missing): {command}"
        return result

    # Windows PATHEXT resolution: bare commands like `npx` / `node` are actually
    # `.cmd` / `.exe` shims that subprocess.Popen with shell=False cannot find.
    # shutil.which() honors PATHEXT and returns the full resolved path.
    if not Path(cmd_expanded).is_absolute():
        resolved = shutil.which(cmd_expanded)
        if resolved:
            cmd_expanded = resolved
        else:
            result["status"] = "error"
            result["reason"] = f"command not found on PATH: {cmd_expanded!r}"
            return result

    # Build environment.
    env = os.environ.copy()
    spec_env = _expand_env(spec.get("env", {}))
    for k, v in spec_env.items():
        if v:
            env[k] = v
        # If the value resolved empty AND the key looks like an auth token,
        # skip with an actionable reason (matches pre_mcp_gate semantics).
        elif "TOKEN" in k.upper() or "API_KEY" in k.upper():
            result["reason"] = f"required auth env var '{k}' is empty"
            return result

    argv = [cmd_expanded, *args_expanded]
    proc = None
    try:
        proc = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Send initialize -> wait for response -> send initialized notif -> tools/list.
        assert proc.stdin is not None and proc.stdout is not None
        proc.stdin.write(_build_init_request())
        proc.stdin.write(_build_initialized_notification())
        proc.stdin.write(_build_tools_list_request())
        proc.stdin.flush()
        proc.stdin.close()

        # Read available output up to timeout.
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate(timeout=2)
            result["status"] = "error"
            result["reason"] = f"timeout after {timeout}s"
            return result

        # Find the tools/list response (id=2) line.
        tools_response: dict[str, Any] | None = None
        for line in (stdout or "").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except (ValueError, TypeError):
                continue
            if isinstance(msg, dict) and msg.get("id") == 2 and "result" in msg:
                tools_response = msg
                break

        if tools_response is None:
            result["status"] = "error"
            result["reason"] = (
                f"no tools/list response in stdout "
                f"(stderr tail: {(stderr or '')[-200:].strip()!r})"
            )
            return result

        tools = tools_response.get("result", {}).get("tools", [])
        if not isinstance(tools, list):
            result["status"] = "error"
            result["reason"] = "tools/list result.tools is not a list"
            return result

        # Measure: serialize the tools array as JSON; that's the schema cost.
        schema_json = json.dumps(tools, separators=(",", ":"))
        result["status"] = "measured"
        result["reason"] = None
        result["tools_count"] = len(tools)
        result["schema_bytes"] = len(schema_json.encode("utf-8"))
        result["approx_schema_tokens"] = result["schema_bytes"] // 4
        result["tool_names"] = sorted(
            t.get("name", "") for t in tools if isinstance(t, dict)
        )
        return result

    except (OSError, ValueError, RuntimeError) as exc:
        result["status"] = "error"
        result["reason"] = f"{type(exc).__name__}: {exc}"
        return result
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.kill()
            except OSError:
                pass


def _render_markdown(report: dict[str, Any]) -> str:
    measured = [r for r in report["servers"] if r["status"] == "measured"]
    skipped = [r for r in report["servers"] if r["status"] == "skipped"]
    errored = [r for r in report["servers"] if r["status"] == "error"]
    measured.sort(key=lambda r: r["schema_bytes"], reverse=True)

    total_bytes = sum(r["schema_bytes"] for r in measured)
    total_tokens = total_bytes // 4
    total_tools = sum(r["tools_count"] for r in measured)

    lines: list[str] = []
    lines.append("# MCP Schema Cost Audit")
    lines.append("")
    lines.append(f"**Generated:** {report['timestamp']}")
    lines.append(f"**Servers measured:** {len(measured)} of {len(report['servers'])}")
    lines.append(f"**Total schema bytes (measured):** {total_bytes:,}")
    lines.append(f"**Approx total schema tokens:** {total_tokens:,} (bytes/4)")
    lines.append(f"**Total tools registered:** {total_tools}")
    lines.append("")
    lines.append("> Every always-on session pays this token cost regardless of use.")
    lines.append("> Retirement candidates: high-cost low-frequency MCPs.")
    lines.append("")
    lines.append("## Ranked by Schema Bytes")
    lines.append("")
    lines.append("| Rank | Server | Tools | Schema Bytes | Approx Tokens |")
    lines.append("|-----:|--------|------:|-------------:|--------------:|")
    for i, r in enumerate(measured, 1):
        lines.append(
            f"| {i} | `{r['server']}` | {r['tools_count']} | "
            f"{r['schema_bytes']:,} | {r['approx_schema_tokens']:,} |"
        )
    lines.append("")
    if skipped:
        lines.append("## Skipped")
        lines.append("")
        lines.append("| Server | Reason |")
        lines.append("|--------|--------|")
        for r in skipped:
            lines.append(f"| `{r['server']}` | {r['reason']} |")
        lines.append("")
    if errored:
        lines.append("## Errored")
        lines.append("")
        lines.append("| Server | Reason |")
        lines.append("|--------|--------|")
        for r in errored:
            lines.append(f"| `{r['server']}` | {r['reason']} |")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Source: `tools/diagnostics/mcp_schema_cost.py`")
    lines.append("- Machine-readable: `artifacts/governance/mcp_schema_cost.json`")
    lines.append("- Plan reference: `docs/archive/windsurf/legacy-tree/plans/windsurf-token-burn-augmentation-b7a3f1.md` W2/P6")
    lines.append("- Approximation: tokens = bytes/4 (Claude tokenizer ratio 3-5x)")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit MCP server schema cost")
    ap.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Per-server probe timeout in seconds (default 10.0)",
    )
    ap.add_argument(
        "--servers",
        default=None,
        help="Comma-separated subset of server names to probe (default: all enabled)",
    )
    args = ap.parse_args(argv)

    if not MCP_CONFIG.exists():
        sys.stderr.write(f"mcp_config not found at {MCP_CONFIG}\n")
        return 1

    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict):
        sys.stderr.write("mcp_config.mcpServers is not a dict\n")
        return 1

    subset: set[str] | None = None
    if args.servers:
        subset = {s.strip() for s in args.servers.split(",") if s.strip()}

    rows: list[dict[str, Any]] = []
    for name, spec in servers.items():
        if subset is not None and name not in subset:
            continue
        if not isinstance(spec, dict):
            continue
        sys.stderr.write(f"[mcp_schema_cost] probing {name} ...\n")
        rows.append(_probe_server(name, spec, args.timeout))

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "servers": rows,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(_render_markdown(report), encoding="utf-8")

    measured = [r for r in rows if r["status"] == "measured"]
    sys.stdout.write(
        f"Probed {len(rows)} servers; measured {len(measured)}; "
        f"total schema bytes = {sum(r['schema_bytes'] for r in measured):,}\n"
    )
    sys.stdout.write(f"Wrote {OUT_JSON}\n")
    sys.stdout.write(f"Wrote {OUT_MD}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
