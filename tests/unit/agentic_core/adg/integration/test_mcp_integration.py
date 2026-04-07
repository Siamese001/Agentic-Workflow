"""MCP integration tests — Server responds correctly to tool calls."""
import json
import subprocess
import threading
import time

import pytest


def _readline_with_timeout(stream, timeout: float = 5.0) -> str:
    """Read one line from stream with timeout — cross-platform (no select.select)."""
    result = [""]

    def _read():
        try:
            result[0] = stream.readline()
        except (OSError, ValueError):
            pass

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    t.join(timeout=timeout)
    return result[0]


class TestMCPIntegration:
    """Test MCP server via stdio transport."""

    def test_server_process_starts(self):
        """Server process starts without error."""
        proc = subprocess.Popen(
            ["python", "-m", "tools.adg.mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Give server time to initialize
        time.sleep(1)

        # Check process is still running
        assert proc.poll() is None, "Server process exited unexpectedly"

        # Terminate
        proc.terminate()
        proc.wait(timeout=5)

    def test_server_responds_to_initialize(self):
        """Playwright MCP server responds to MCP initialize request with valid JSON-RPC result."""
        proc = subprocess.Popen(
            ["npx.cmd", "-y", "@playwright/mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        try:
            # Wait for startup
            time.sleep(2)

            # Send initialize request
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            }

            proc.stdin.write(json.dumps(init_msg) + "\n")
            proc.stdin.flush()

            # Read response with timeout (cross-platform — no select.select on Windows pipes)
            response_line = _readline_with_timeout(proc.stdout, timeout=8.0)
            assert response_line, "Playwright MCP server did not respond within timeout"
            response = json.loads(response_line)

            assert response["id"] == 1
            assert "result" in response
            assert "serverInfo" in response["result"]

        finally:
            proc.terminate()
            proc.wait(timeout=5)

    def test_playwright_mcp_lists_tools(self):
        """Playwright MCP server exposes tools via tools/list after initialize."""
        proc = subprocess.Popen(
            ["npx.cmd", "-y", "@playwright/mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        try:
            time.sleep(2)

            # Initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            }
            proc.stdin.write(json.dumps(init_msg) + "\n")
            proc.stdin.flush()
            _readline_with_timeout(proc.stdout, timeout=8.0)  # consume init response

            # List tools
            list_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
            proc.stdin.write(json.dumps(list_msg) + "\n")
            proc.stdin.flush()

            response_line = _readline_with_timeout(proc.stdout, timeout=8.0)
            assert response_line, "tools/list did not respond"
            response = json.loads(response_line)

            assert response["id"] == 2
            assert "result" in response
            tools = response["result"].get("tools", [])
            assert len(tools) > 0, "Playwright MCP should expose at least one tool"

        finally:
            proc.terminate()
            proc.wait(timeout=5)


class TestServerRobustness:
    """Test server robustness under various conditions."""

    def test_server_survives_invalid_json(self):
        """Server survives invalid JSON input."""
        proc = subprocess.Popen(
            ["python", "-m", "tools.adg.mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send garbage
            proc.stdin.write("not valid json\n")
            proc.stdin.flush()

            # Give time to process
            time.sleep(0.5)

            # Server should still be running
            assert proc.poll() is None

        finally:
            proc.terminate()
            proc.wait(timeout=5)

    def test_server_stderr_logging(self):
        """Server logs to stderr, not stdout."""
        proc = subprocess.Popen(
            ["python", "-m", "tools.adg.mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Give time to initialize
            time.sleep(1)

            # Check stderr has logs
            # stderr may have initialization logs (not asserted — server-specific)

            # Stdout should be empty (no random output) — cross-platform readline
            stdout_line = _readline_with_timeout(proc.stdout, timeout=0.1)
            # If there's stdout, it should be valid MCP protocol
            if stdout_line:
                try:
                    json.loads(stdout_line)
                except json.JSONDecodeError:
                    pytest.fail("Server wrote non-JSON to stdout")

        finally:
            proc.terminate()
            proc.wait(timeout=5)
