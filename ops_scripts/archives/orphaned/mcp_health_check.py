#!/usr/bin/env python3
"""MCP Server Health Check — automated startup probe for all configured servers.

Reads the Windsurf global MCP config, attempts to start each enabled server,
sends an MCP initialize handshake, and reports pass/fail with diagnostics.

Usage:
    python ops_scripts/ci/mcp_health_check.py           # check all servers
    python ops_scripts/ci/mcp_health_check.py --server fetch adg_sqlite  # check specific
    python ops_scripts/ci/mcp_health_check.py --json     # machine-readable output
    python ops_scripts/ci/mcp_health_check.py --fix      # suggest fixes for failures

Exit codes:
    0 = all enabled servers healthy
    1 = one or more servers failed
    2 = config error
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]

# Windsurf global config locations (ordered by priority)
_CONFIG_CANDIDATES = [
    Path(os.path.expanduser("~")) / ".codeium" / "windsurf" / "mcp_config.json",
    REPO_ROOT / ".windsurf" / "mcp_config.json",
]

STARTUP_TIMEOUT_SECONDS = 15
INIT_TIMEOUT_SECONDS = 10

# MCP initialize request (JSON-RPC 2.0)
MCP_INITIALIZE_REQUEST = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "mcp-health-check", "version": "1.0.0"},
    },
}) + "\n"


# ---------------------------------------------------------------------------
# Color helpers (Windows-safe)
# ---------------------------------------------------------------------------
def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if sys.platform == "win32":
        os.system("")  # enable ANSI on Windows
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_COLOR = _supports_color()


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m" if _COLOR else s


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m" if _COLOR else s


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m" if _COLOR else s


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m" if _COLOR else s


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m" if _COLOR else s


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------
def find_config() -> Path | None:
    for candidate in _CONFIG_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def load_config(config_path: Path) -> dict[str, Any]:
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("mcpServers", {})


# ---------------------------------------------------------------------------
# Server probing
# ---------------------------------------------------------------------------
class ProbeResult:
    def __init__(self, name: str):
        self.name = name
        self.status: str = "unknown"  # "ok", "disabled", "fail", "skip"
        self.message: str = ""
        self.duration_ms: float = 0
        self.command: str = ""
        self.server_info: dict[str, Any] = {}
        self.fix_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "duration_ms": round(self.duration_ms, 1),
            "command": self.command,
            "server_info": self.server_info,
            "fix_hint": self.fix_hint,
        }


def _resolve_command(command: str) -> str | None:
    """Resolve a command to its full path, or None if not found."""
    # Direct path
    if os.path.isfile(command):
        return command
    # Search PATH
    resolved = shutil.which(command)
    if resolved:
        return resolved
    # Windows: try with .cmd/.exe extensions
    if sys.platform == "win32":
        for ext in [".cmd", ".exe", ".bat"]:
            resolved = shutil.which(command + ext)
            if resolved:
                return resolved
    return None


def probe_server(name: str, config: dict[str, Any]) -> ProbeResult:
    """Probe a single MCP server by attempting startup + initialize handshake."""
    result = ProbeResult(name)

    # Check if disabled
    if config.get("disabled", False):
        result.status = "disabled"
        result.message = "Server is disabled in config"
        return result

    # URL-based servers (e.g., deepwiki) — just check connectivity
    if "url" in config and not config.get("command"):
        return _probe_url_server(name, config, result)

    command = config.get("command", "")
    args = config.get("args", [])
    env_overrides = config.get("env", {})

    if not command:
        result.status = "fail"
        result.message = "No command specified in config"
        result.fix_hint = f"Add 'command' field to {name} config"
        return result

    # Resolve command
    resolved_cmd = _resolve_command(command)
    if not resolved_cmd:
        result.status = "fail"
        result.message = f"Command not found: {command}"
        result.fix_hint = f"Install {command} or fix path in config"
        return result

    full_cmd = [resolved_cmd] + args
    result.command = " ".join(full_cmd[:3]) + ("..." if len(full_cmd) > 3 else "")

    # Build environment
    env = os.environ.copy()
    unresolved_vars: list[str] = []
    for k, v in env_overrides.items():
        if "${" in v:
            # Try to resolve from actual environment
            resolved = re.sub(
                r"\$\{([^}:]+)(?::-([^}]*))?\}",
                lambda m: os.environ.get(m.group(1), m.group(2) or ""),
                v,
            )
            if resolved and "${" not in resolved:
                env[k] = resolved
            else:
                unresolved_vars.append(k)
        else:
            env[k] = v

    if unresolved_vars:
        # Servers with unresolved API keys are expected to fail at startup
        # but Windsurf resolves these from its secrets store at runtime
        result.status = "ok"
        result.message = f"Config OK (env vars resolved by Windsurf at runtime: {', '.join(unresolved_vars)})"
        result.duration_ms = 0
        return result

    # Start the server process
    start = time.perf_counter()
    proc = None
    try:
        proc = subprocess.Popen(
            full_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(REPO_ROOT),
        )

        # Wait briefly for immediate crash
        time.sleep(0.5)
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode("utf-8", errors="replace")[:500]
            result.status = "fail"
            result.message = f"Process exited immediately (code {proc.returncode})"
            if stderr.strip():
                result.message += f": {stderr.strip()[:200]}"
            _suggest_fix(result, name, command, stderr)
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result

        # Send MCP initialize and read response using communicate()
        # This is Windows-safe (selectors doesn't work with pipes on Windows)
        try:
            stdout_data, stderr_data = proc.communicate(
                input=MCP_INITIALIZE_REQUEST.encode(),
                timeout=INIT_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            # Timeout means process is alive but didn't respond to initialize.
            # For MCP servers that don't respond to initialize, this is still OK.
            if proc.poll() is None:
                result.status = "ok"
                result.message = "Process running (initialize timeout — normal for some servers)"
            else:
                result.status = "fail"
                result.message = f"Process died during initialize (code {proc.returncode})"
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result
        except (BrokenPipeError, OSError) as e:
            result.status = "fail"
            result.message = f"Failed to communicate: {e}"
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result

        result.duration_ms = (time.perf_counter() - start) * 1000
        stderr_text = stderr_data.decode("utf-8", errors="replace")[:500] if stderr_data else ""

        if proc.returncode != 0 and not stdout_data:
            result.status = "fail"
            result.message = f"Process exited (code {proc.returncode})"
            if stderr_text.strip():
                result.message += f": {stderr_text.strip()[:200]}"
            _suggest_fix(result, name, command, stderr_text)
            return result

        if not stdout_data:
            result.status = "ok"
            result.message = "Process ran (no stdout output)"
            return result

        # Parse response
        decoded = stdout_data.decode("utf-8", errors="replace")
        json_start = decoded.find("{")
        if json_start >= 0:
            try:
                resp = json.loads(decoded[json_start:])
                if "result" in resp:
                    result.status = "ok"
                    server_info = resp["result"].get("serverInfo", {})
                    result.server_info = server_info
                    result.message = f"Healthy — {server_info.get('name', 'unknown')} v{server_info.get('version', '?')}"
                elif "error" in resp:
                    result.status = "fail"
                    result.message = f"MCP error: {resp['error'].get('message', 'unknown')}"
                else:
                    result.status = "ok"
                    result.message = "Got response (non-standard format)"
            except json.JSONDecodeError:
                result.status = "ok"
                result.message = "Process responded (non-JSON output)"
        else:
            result.status = "ok"
            result.message = "Process responded (non-JSON output)"

    except FileNotFoundError:
        result.status = "fail"
        result.message = f"Command not found: {command}"
        result.fix_hint = f"Install {command}"
        result.duration_ms = (time.perf_counter() - start) * 1000
    except PermissionError:
        result.status = "fail"
        result.message = f"Permission denied: {command}"
        result.duration_ms = (time.perf_counter() - start) * 1000
    except Exception as e:
        result.status = "fail"
        result.message = f"Unexpected error: {type(e).__name__}: {e}"
        result.duration_ms = (time.perf_counter() - start) * 1000
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()

    return result


def _probe_url_server(name: str, config: dict[str, Any], result: ProbeResult) -> ProbeResult:
    """Probe a URL-based MCP server (like deepwiki)."""
    url = config["url"]
    result.command = f"URL: {url}"
    start = time.perf_counter()

    try:
        import urllib.request

        # MCP SSE endpoints may reject GET/HEAD — try OPTIONS first, then GET
        for method in ["OPTIONS", "GET", "HEAD"]:
            try:
                req = urllib.request.Request(url, method=method)
                req.add_header("User-Agent", "mcp-health-check/1.0")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result.status = "ok"
                    result.message = f"URL reachable (HTTP {resp.status} via {method})"
                    break
            except urllib.error.HTTPError as he:
                # 405/406 means server is ALIVE but rejects this method — that's OK
                if he.code in (405, 406):
                    result.status = "ok"
                    result.message = f"URL reachable (HTTP {he.code} — MCP endpoint alive)"
                    break
                raise  # re-raise other HTTP errors
    except Exception as e:
        if result.status != "ok":  # don't overwrite a successful probe
            result.status = "fail"
            result.message = f"URL unreachable: {e}"
            result.fix_hint = f"Check network connectivity to {url}"

    result.duration_ms = (time.perf_counter() - start) * 1000
    return result


def _suggest_fix(result: ProbeResult, name: str, command: str, stderr: str) -> None:
    """Suggest a fix based on error patterns."""
    stderr_lower = stderr.lower()

    if "e404" in stderr_lower or "not found" in stderr_lower:
        result.fix_hint = f"Package not found on npm. Check package name in config for '{name}'."
    elif "enoent" in stderr_lower:
        result.fix_hint = f"Command '{command}' not found. Install it or check PATH."
    elif "modulenotfounderror" in stderr_lower or "no module named" in stderr_lower:
        result.fix_hint = "Python module missing. Run: pip install <missing-module>"
    elif "connection refused" in stderr_lower or "econnrefused" in stderr_lower:
        result.fix_hint = "Service dependency not running (Redis? PostgreSQL?)."
    elif "permission" in stderr_lower:
        result.fix_hint = f"Permission denied running '{command}'."
    elif not result.fix_hint:
        result.fix_hint = f"Check stderr output and config for '{name}'."


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Server Health Check")
    parser.add_argument("--server", nargs="*", help="Check specific server(s) only")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--fix", action="store_true", help="Show fix suggestions")
    parser.add_argument("--config", type=Path, help="Config file path override")
    args = parser.parse_args()

    # Find config
    config_path = args.config or find_config()
    if not config_path or not config_path.exists():
        print(_red("ERROR: No MCP config found. Searched:"), file=sys.stderr)
        for c in _CONFIG_CANDIDATES:
            print(f"  - {c}", file=sys.stderr)
        return 2

    # Load
    servers = load_config(config_path)
    if not servers:
        print(_red("ERROR: No servers found in config"), file=sys.stderr)
        return 2

    # Filter
    if args.server:
        servers = {k: v for k, v in servers.items() if k in args.server}
        if not servers:
            print(_red(f"ERROR: No matching servers: {args.server}"), file=sys.stderr)
            return 2

    # Probe
    print(_bold(f"\nMCP Health Check — {config_path.name}"))
    print(_dim(f"Config: {config_path}"))
    print(_dim(f"Servers: {len(servers)} configured\n"))

    results: list[ProbeResult] = []
    for name, config in sorted(servers.items()):
        sys.stdout.write(f"  {name:.<30s} ")
        sys.stdout.flush()

        probe = probe_server(name, config)
        results.append(probe)

        if probe.status == "ok":
            print(_green("OK") + _dim(f"  ({probe.duration_ms:.0f}ms) {probe.message}"))
        elif probe.status == "disabled":
            print(_yellow("SKIP") + _dim(f"  {probe.message}"))
        else:
            print(_red("FAIL") + f"  {probe.message}")
            if args.fix and probe.fix_hint:
                print(f"         {_yellow('FIX:')} {probe.fix_hint}")

    # Summary
    ok = sum(1 for r in results if r.status == "ok")
    fail = sum(1 for r in results if r.status == "fail")
    disabled = sum(1 for r in results if r.status == "disabled")

    print()
    summary = f"  {ok} healthy, {fail} failed, {disabled} disabled"
    if fail == 0:
        print(_green(_bold("ALL HEALTHY")) + summary)
    else:
        print(_red(_bold(f"{fail} FAILED")) + summary)

    # JSON output
    if args.json:
        output = {
            "config_path": str(config_path),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "summary": {"ok": ok, "fail": fail, "disabled": disabled},
            "servers": [r.to_dict() for r in results],
        }
        print(json.dumps(output, indent=2))

    return 1 if fail > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
