#!/usr/bin/env python3
"""
MCP Hung Process Detector - CI Gate for MCP Process Liveness

Detects and reports hung MCP processes during testing.
Critical for MCP Redis and ADG stability.

Usage:
  python ops_scripts/ci/mcp_hung_process_detector.py --check
  python ops_scripts/ci/mcp_hung_process_detector.py --simulate-hung
"""
import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import psutil

REPO_ROOT = Path(r"C:\Git\Agentic-Workflow")

# MCP process patterns to monitor
MCP_PROCESS_PATTERNS = [
    "adg_mcp_server",
    "redis_mcp",
    "memory_mcp",
    "filesystem_mcp",
    "mcp_server",
]

# Timeout thresholds (seconds)
HUNG_THRESHOLD = 30  # Process considered hung after 30s of no activity
CPU_THRESHOLD = 0.1  # CPU usage below 0.1% for 30s = hung


class HungProcessResult:
    """Result of hung process detection."""
    def __init__(self, pid: int, name: str, reason: str):
        self.pid = pid
        self.name = name
        self.reason = reason
        self.cpu_percent = 0.0
        self.memory_mb = 0.0
        self.runtime_seconds = 0.0


def find_mcp_processes() -> List[Dict[str, Any]]:
    """Find all MCP-related processes."""
    mcp_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
        try:
            proc_info = proc.info
            cmdline = ' '.join(proc_info['cmdline'] or [])

            # Check if process matches MCP patterns
            if any(pattern in cmdline.lower() for pattern in MCP_PROCESS_PATTERNS):
                mcp_processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'cmdline': cmdline,
                    'cpu_percent': proc_info['cpu_percent'],
                    'memory_mb': proc_info['memory_info'].rss / 1024 / 1024 if proc_info['memory_info'] else 0,
                    'create_time': proc_info['create_time'],
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return mcp_processes


def check_hung_processes() -> List[HungProcessResult]:
    """Check for hung MCP processes."""
    hung_processes = []
    current_time = time.time()

    mcp_procs = find_mcp_processes()

    for proc in mcp_procs:
        runtime = current_time - proc['create_time']

        # Check if process is hung (low CPU for extended time)
        if runtime > HUNG_THRESHOLD and proc['cpu_percent'] < CPU_THRESHOLD:
            result = HungProcessResult(
                pid=proc['pid'],
                name=proc['name'],
                reason=f"Low CPU ({proc['cpu_percent']:.1f}%) for {runtime:.1f}s",
            )
            result.cpu_percent = proc['cpu_percent']
            result.memory_mb = proc['memory_mb']
            result.runtime_seconds = runtime
            hung_processes.append(result)

        # Check for zombie process (no CPU, no memory change)
        if proc['cpu_percent'] == 0.0 and proc['memory_mb'] < 1.0:
            result = HungProcessResult(
                pid=proc['pid'],
                name=proc['name'],
                reason="Zombie process (0% CPU, <1MB memory)",
            )
            result.cpu_percent = proc['cpu_percent']
            result.memory_mb = proc['memory_mb']
            result.runtime_seconds = runtime
            hung_processes.append(result)

    return hung_processes


def kill_hung_process(pid: int) -> bool:
    """Attempt to kill a hung process."""
    try:
        proc = psutil.Process(pid)

        # Try graceful termination first
        proc.terminate()

        # Wait up to 5 seconds for graceful shutdown
        try:
            proc.wait(timeout=5)
            return True
        except psutil.TimeoutExpired:
            # Force kill if graceful shutdown fails
            proc.kill()
            proc.wait(timeout=2)
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def simulate_hung_process() -> None:
    """Simulate a hung MCP process for testing."""
    print("[SIMULATION] Creating hung MCP process...")

    # Create a process that hangs
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(3600)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print(f"[SIMULATION] Hung process created: PID={proc.pid}")
    print("[SIMULATION] Run detector: python ops_scripts/ci/mcp_hung_process_detector.py --check")
    print(f"[SIMULATION] To kill: kill {proc.pid}")

    # Keep it alive for demonstration
    time.sleep(2)
    print("[SIMULATION] Process is now hung (sleeping for 1 hour)")
    print("[SIMULATION] Press Ctrl+C to stop simulation")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Hung Process Detector")
    parser.add_argument("--check", action="store_true", help="Check for hung MCP processes")
    parser.add_argument("--simulate-hung", action="store_true", help="Simulate a hung process for testing")
    parser.add_argument("--kill", type=int, help="Kill process by PID")

    args = parser.parse_args()

    if args.simulate_hung:
        simulate_hung_process()
        return 0

    if args.kill:
        if kill_hung_process(args.kill):
            print(f"✓ Killed process {args.kill}")
            return 0
        else:
            print(f"✗ Failed to kill process {args.kill}")
            return 1

    if args.check:
        print("\n[MCP HUNG PROCESS DETECTOR]")
        print("=" * 50)

        mcp_procs = find_mcp_processes()
        print(f"\nFound {len(mcp_procs)} MCP-related process(es):")

        for proc in mcp_procs:
            runtime = time.time() - proc['create_time']
            print(f"  PID {proc['pid']}: {proc['name']}")
            print(f"    CPU: {proc['cpu_percent']:.1f}% | Memory: {proc['memory_mb']:.1f}MB | Runtime: {runtime:.1f}s")
            print(f"    Cmd: {proc['cmdline'][:80]}...")

        hung = check_hung_processes()

        if hung:
            print(f"\n⚠️  DETECTED {len(hung)} HUNG PROCESS(ES):")
            for h in hung:
                print(f"  PID {h.pid} ({h.name}): {h.reason}")
                print(f"    CPU: {h.cpu_percent:.1f}% | Memory: {h.memory_mb:.1f}MB | Runtime: {h.runtime_seconds:.1f}s")
                print(f"    To kill: python ops_scripts/ci/mcp_hung_process_detector.py --kill {h.pid}")
            print("\n❌ HUNG PROCESSES DETECTED - CI FAILURE")
            return 1
        else:
            print("\n✅ No hung MCP processes detected")
            return 0

    print("Error: No action specified. Use --check, --simulate-hung, or --kill <pid>")
    return 1


if __name__ == "__main__":
    sys.exit(main())
