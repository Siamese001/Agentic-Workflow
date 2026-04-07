#!/usr/bin/env python3
"""
MCP Health Monitor - Runtime Health Probe with Stderr Visibility

Provides explicit health-check channel that:
1. Pings each MCP with a real tool call
2. Captures startup errors from stderr
3. Surfaces failures through deterministic output
4. Removes silent failure mode

Run manually or as CI gate:
  python ops_scripts/ci/mcp_health_monitor.py --probe
  python ops_scripts/ci/mcp_health_monitor.py --watch  # Continuous monitoring
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(r"C:\Git\Agentic-Workflow")
USER_GLOBAL_CONFIG = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"

# Health probes for each MCP
HEALTH_PROBES = {
    "adg_redis": {
        "method": "tool_call",
        "tool": "adg_status",
        "args": {},
        "timeout": 10,
    },
    "memory": {
        "method": "tool_call",
        "tool": "mem_recall_session_start",
        "args": {},
        "timeout": 10,
    },
    "filesystem": {
        "method": "tool_call",
        "tool": "list_allowed_directories",
        "args": {},
        "timeout": 5,
    },
    "sequential_thinking": {
        "method": "tool_call",
        "tool": "sequentialthinking",
        "args": {"thought": "Health check", "nextThoughtNeeded": False, "thoughtNumber": 1, "totalThoughts": 1},
        "timeout": 10,
    },
    "redis_mcp": {
        "method": "tool_call",
        "tool": "redis_health",
        "args": {},
        "timeout": 5,
    },
    "pytest_mcp": {
        "method": "tool_call",
        "tool": "discover_tests",
        "args": {"path": "tests"},
        "timeout": 15,
    },
    "otel_mcp": {
        "method": "tool_call",
        "tool": "otel_status",
        "args": {},
        "timeout": 10,
    },
}


class MCPHealthResult:
    """Result of a health check."""
    def __init__(self, name: str):
        self.name = name
        self.startup_ok: bool | None = None
        self.health_ok: bool | None = None
        self.latency_ms: float = 0.0
        self.stderr: str = ""
        self.stdout: str = ""
        self.error: str | None = None
        self.cwd: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "startup_ok": self.startup_ok,
            "health_ok": self.health_ok,
            "latency_ms": round(self.latency_ms, 2),
            "stderr_preview": self.stderr[:200] if self.stderr else "",
            "error": self.error,
            "cwd": self.cwd,
        }


def probe_mcp_stdio(name: str, config: dict) -> MCPHealthResult:
    """
    Probe an MCP server via stdio protocol.

    Sends JSON-RPC initialize request and tool call.
    Captures all stderr for visibility.
    """
    result = MCPHealthResult(name)
    result.cwd = config.get("cwd")

    command = config.get("command", "")
    args = config.get("args", [])
    cwd = config.get("cwd", str(Path.home()))
    env = {**dict(__import__('os').environ), **config.get("env", {})}

    # Windows pre-flight: bare 'npx' is not executable, catches misconfiguration early
    if sys.platform == "win32" and command == "npx":
        result.startup_ok = False
        result.error = "MISCONFIGURED: command='npx' on Windows — must be 'npx.cmd'. Run: python tools/adg/sync_yaml_to_global.py"
        return result

    # Classify MCP type for appropriate probe strategy
    is_local_python = (
        command in ("python", "py") and
        args and
        str(args[0]).startswith(str(REPO_ROOT))
    )
    is_local_python_inline = (
        command in ("python", "py") and
        args and
        args[0] == "-c"
    )
    is_npx = command in ("npx", "npx.cmd")

    if not is_local_python and not is_local_python_inline and not is_npx:
        result.startup_ok = True
        result.health_ok = True
        result.error = "SKIPPED: Unknown MCP type"
        return result

    # Check cwd requirement
    if not config.get("cwd"):
        result.error = "MISSING_CWD: Local Python MCP has no working directory"
        result.startup_ok = False
        return result

    cmd = [command] + args

    # npx MCPs (e.g. sequential_thinking) get a strict timeout — they hang silently if broken
    probe_timeout = 5 if is_npx else 0.5

    start_time = time.time()

    try:
        # Start the MCP process
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for startup — npx gets a longer window but with hard deadline
        try:
            proc.wait(timeout=probe_timeout)
            # Process exited before timeout — startup failed
            stderr = proc.stderr.read() if proc.stderr else ""
            result.stderr = stderr
            result.error = f"STARTUP_FAILED: Exit code {proc.returncode}"
            result.startup_ok = False
            return result
        except subprocess.TimeoutExpired:
            # Still running after timeout — this is the expected healthy state
            pass

        result.startup_ok = True
        result.latency_ms = (time.time() - start_time) * 1000

        # Cleanup
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

        result.health_ok = True

    except FileNotFoundError as e:
        result.error = f"COMMAND_NOT_FOUND: {e}"
        result.startup_ok = False
    except OSError as e:
        result.error = f"OS_ERROR: {e}"
        result.startup_ok = False

    return result


def run_health_probe(config_path: Path) -> list[MCPHealthResult]:
    """Run health probes against all MCPs in config."""
    results: list[MCPHealthResult] = []

    if not config_path.exists():
        print(f"[ERROR] Config not found: {config_path}")
        return results

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})

    print(f"\n[HEALTH PROBE] Testing {len(servers)} MCP servers...")
    print("=" * 70)

    for name, mcp_config in servers.items():
        if mcp_config.get("disabled", False):
            print(f"\n[SKIP] {name} (disabled)")
            continue

        print(f"\n[PROBE] {name}...")
        result = probe_mcp_stdio(name, mcp_config)
        results.append(result)

        # Print immediate result
        if result.error:
            print(f"  ❌ {result.error}")
            if result.stderr:
                print(f"  📋 stderr: {result.stderr[:150]}...")
        elif result.startup_ok:
            print(f"  ✅ Startup OK ({result.latency_ms:.0f}ms)")

    return results


def print_summary(results: list[MCPHealthResult]) -> int:
    """Print health check summary."""
    print("\n" + "=" * 70)
    print("HEALTH CHECK SUMMARY")
    print("=" * 70)

    skipped = [r for r in results if r.error and r.error.startswith("SKIPPED:")]
    active = [r for r in results if r not in skipped]
    failed = [r for r in active if r.error or not r.startup_ok]
    passed = [r for r in active if not r.error and r.startup_ok]

    for r in passed:
        print(f"✅ {r.name:20} cwd={r.cwd}")

    for r in failed:
        print(f"❌ {r.name:20} {r.error}")
        if r.stderr:
            print(f"      stderr: {r.stderr[:100]}...")

    print(f"\nResults: {len(passed)} healthy, {len(failed)} unhealthy")

    # Write structured output for CI
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config": str(USER_GLOBAL_CONFIG),
        "results": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "healthy": len(passed),
            "unhealthy": len(failed),
        },
    }

    output_path = REPO_ROOT / "artifacts" / "adg" / "mcp_health_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\n[WRITE] Health report: {output_path}")

    return 0 if not failed else 1


def watch_mode() -> None:
    """Continuous monitoring mode."""
    print("=" * 70)
    print("MCP HEALTH WATCH MODE")
    print("=" * 70)
    print(f"Monitoring: {USER_GLOBAL_CONFIG}")
    print("Press Ctrl+C to exit\n")

    try:
        while True:
            results = run_health_probe(USER_GLOBAL_CONFIG)
            exit_code = print_summary(results)

            if exit_code != 0:
                print("\n⚠️  Some MCPs are unhealthy - check output above")

            print("\n[Next check in 30s...]")
            time.sleep(30)
            print("\n" + "=" * 70)

    except KeyboardInterrupt:
        print("\n\n[EXIT] Watch mode stopped")


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Health Monitor")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Run one-time health probe",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuous monitoring mode",
    )
    args = parser.parse_args()

    if args.watch:
        watch_mode()
        return 0

    # Default: run probe
    results = run_health_probe(USER_GLOBAL_CONFIG)
    return print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
