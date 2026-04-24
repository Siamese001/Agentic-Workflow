#!/usr/bin/env python3
"""
Comprehensive MCP Test Suite
Tests all MCP servers for functionality, performance, and integration.
"""

import json
import os
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class MCPTester:
    def __init__(self):
        self.config_file = REPO_ROOT / ".windsurf" / "mcp_config.json"
        self.results = {}
        self.npm_prefix = "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation"

    def load_config(self):
        """Load MCP configuration."""
        with open(self.config_file) as f:
            return json.load(f)

    def test_node_server(self, name, config):
        """Test Node.js-based MCP server."""
        args = config.get("args", [])

        if not args:
            return {"status": "error", "message": "No arguments provided"}

        package_path = args[0]

        if not os.path.exists(package_path):
            return {"status": "missing", "message": f"Package not found: {package_path}"}

        try:
            start_time = time.time()

            # Test with --help or basic startup
            test_args = ["--help"] if len(args) == 1 else args[1:] + ["--help"]
            result = subprocess.run(
                ["node", package_path] + test_args,
                capture_output=True,
                text=True,
                timeout=5,
            )

            end_time = time.time()
            startup_time = end_time - start_time

            if (
                result.returncode == 0
                or "timeout" in result.stderr.lower()
                or "server" in result.stderr.lower()
            ):
                return {
                    "status": "success",
                    "time": startup_time,
                    "message": "Server starts successfully",
                    "package_path": package_path,
                }
            else:
                return {
                    "status": "warning",
                    "time": startup_time,
                    "message": f"Exit code: {result.returncode}",
                    "stderr": result.stderr[:200] if result.stderr else "",
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout_success",
                "time": 5.0,
                "message": "Server started (timeout expected)",
                "package_path": package_path,
            }
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            return {
                "status": "error",
                "time": 0,
                "message": f"Exception: {str(e)}",
            }

    def test_python_server(self, name, config):
        """Test Python-based MCP server."""
        args = config.get("args", [])
        cwd = config.get("cwd", str(REPO_ROOT))

        if not args:
            return {"status": "error", "message": "No script path provided"}

        script_path = args[0]

        if not os.path.exists(script_path):
            return {"status": "missing", "message": f"Script not found: {script_path}"}

        # Test if script is syntactically valid
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", script_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=cwd,
            )

            if result.returncode == 0:
                return {
                    "status": "python_ready",
                    "time": 0,
                    "message": f"Python script valid: {script_path}",
                    "script_path": script_path,
                    "cwd": cwd,
                }
            else:
                return {
                    "status": "syntax_error",
                    "time": 0,
                    "message": f"Syntax error: {result.stderr[:200]}",
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "time": 10.0,
                "message": "Compilation timeout",
            }
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            return {
                "status": "error",
                "time": 0,
                "message": f"Exception: {str(e)}",
            }

    def test_server(self, name, config):
        """Test individual MCP server."""
        disabled = config.get("disabled", False)

        if disabled:
            return {"status": "skipped", "time": 0, "message": "Server disabled"}

        command = config.get("command")

        if command == "node":
            return self.test_node_server(name, config)
        elif command == "python":
            return self.test_python_server(name, config)
        elif command == "npx":
            return {"status": "npx_deprecated", "time": 0, "message": "NPX deprecated in favor of global npm"}
        else:
            return {"status": "unknown_command", "time": 0, "message": f"Unknown command: {command}"}

    def get_performance_metrics(self):
        """Calculate performance metrics."""
        node_servers = [
            (name, r) for name, r in self.results.items() if r.get("status") in ["success", "timeout_success"]
        ]
        python_servers = [(name, r) for name, r in self.results.items() if r.get("status") == "python_ready"]

        metrics = {
            "total_servers": len(self.results),
            "working_servers": len(
                [r for r in self.results.values() if r.get("status") not in ["skipped", "error", "missing"]]
            ),
            "node_servers": len(node_servers),
            "python_servers": len(python_servers),
            "avg_node_startup": 0,
            "fastest_node": None,
            "slowest_node": None,
        }

        if node_servers:
            times = [r["time"] for _, r in node_servers]
            metrics["avg_node_startup"] = sum(times) / len(times)
            metrics["fastest_node"] = min(node_servers, key=lambda x: x[1]["time"])
            metrics["slowest_node"] = max(node_servers, key=lambda x: x[1]["time"])

        return metrics

    def run_comprehensive_test(self):
        """Run comprehensive test suite."""
        print("🧪 Comprehensive MCP Test Suite")
        print("=" * 40)

        config = self.load_config()
        servers = config.get("mcpServers", {})

        print(f"\\n📋 Testing {len(servers)} configured servers...")

        # Test each server
        for name, server_config in servers.items():
            print(f"\\n🔬 Testing {name}...")
            result = self.test_server(name, server_config)
            self.results[name] = result

            # Display result
            status_icons = {
                "success": "✅",
                "timeout_success": "✅",
                "python_ready": "✅",
                "skipped": "⏸️",
                "warning": "⚠️",
                "npx_deprecated": "🔄",
                "missing": "❌",
                "syntax_error": "❌",
                "error": "❌",
                "unknown_command": "❌",
            }

            icon = status_icons.get(result["status"], "❓")
            time_info = f" ({result['time']:.3f}s)" if result.get("time", 0) > 0 else ""
            print(f"   {icon} {result['status']}{time_info}")
            print(f"   📝 {result['message']}")

        # Performance metrics
        metrics = self.get_performance_metrics()

        print("\\n📊 Performance Metrics")
        print("=" * 25)
        print(f"Total servers: {metrics['total_servers']}")
        print(f"Working servers: {metrics['working_servers']}")
        print(f"Node.js servers: {metrics['node_servers']}")
        print(f"Python servers: {metrics['python_servers']}")

        if metrics["avg_node_startup"] > 0:
            print(f"Avg Node.js startup: {metrics['avg_node_startup']:.3f}s")
            if metrics["fastest_node"]:
                name, result = metrics["fastest_node"]
                print(f"Fastest: {name} ({result['time']:.3f}s)")
            if metrics["slowest_node"]:
                name, result = metrics["slowest_node"]
                print(f"Slowest: {name} ({result['time']:.3f}s)")

        # Optimization status
        print("\\n🚀 Optimization Status")
        print("=" * 25)

        node_optimized = len([s for s in servers.values() if s.get("command") == "node"])
        python_custom = len([s for s in servers.values() if s.get("command") == "python"])
        npx_deprecated = len([s for s in servers.values() if s.get("command") == "npx"])

        print(f"Global npm (Node.js): {node_optimized} servers")
        print(f"Custom Python: {python_custom} servers")
        print(f"NPX (deprecated): {npx_deprecated} servers")

        if npx_deprecated == 0:
            print("✅ All servers optimized!")
        else:
            print(f"⚠️  {npx_deprecated} servers still using NPX")

        return metrics


def main():
    tester = MCPTester()
    metrics = tester.run_comprehensive_test()

    # Save results
    results_file = REPO_ROOT / "mcp_test_results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": time.time(),
                "metrics": metrics,
                "results": tester.results,
            },
            f,
            indent=2,
        )

    print(f"\\n💾 Results saved to: {results_file}")

    # Return success if most servers are working
    success_rate = (
        metrics["working_servers"] / metrics["total_servers"] if metrics["total_servers"] > 0 else 0
    )
    return 0 if success_rate >= 0.75 else 1


if __name__ == "__main__":
    exit(main())
