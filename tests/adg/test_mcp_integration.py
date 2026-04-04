"""MCP integration tests — Server responds correctly to tool calls."""
import subprocess
import json
import time
import pytest


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
        """Server responds to MCP initialize request."""
        proc = subprocess.Popen(
            ["python", "-m", "tools.adg.mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        try:
            # Send initialize request
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {}
                }
            }
            
            proc.stdin.write(json.dumps(init_msg) + "\n")
            proc.stdin.flush()
            
            # Read response with timeout
            import select
            ready, _, _ = select.select([proc.stdout], [], [], 5.0)
            assert ready, "Server did not respond within timeout"
            
            response_line = proc.stdout.readline()
            response = json.loads(response_line)
            
            assert response["id"] == 1
            assert "result" in response
            
        finally:
            proc.terminate()
            proc.wait(timeout=5)
    
    def test_adg_health_tool_available(self):
        """adg_health tool is available and responds."""
        proc = subprocess.Popen(
            ["python", "-m", "tools.adg.mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        try:
            # First initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}}
            }
            proc.stdin.write(json.dumps(init_msg) + "\n")
            proc.stdin.flush()
            
            # Read init response
            import select
            ready, _, _ = select.select([proc.stdout], [], [], 5.0)
            if ready:
                proc.stdout.readline()  # Consume init response
            
            # Call adg_health
            health_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "adg_health",
                    "arguments": {}
                }
            }
            proc.stdin.write(json.dumps(health_msg) + "\n")
            proc.stdin.flush()
            
            # Read response
            ready, _, _ = select.select([proc.stdout], [], [], 5.0)
            assert ready, "adg_health did not respond"
            
            response_line = proc.stdout.readline()
            response = json.loads(response_line)
            
            assert response["id"] == 2
            assert "result" in response
            
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
            stderr_data = proc.stderr.read1(1024) if hasattr(proc.stderr, 'read1') else ""
            # stderr may have initialization logs
            
            # Stdout should be empty (no random output)
            import select
            ready, _, _ = select.select([proc.stdout], [], [], 0.1)
            if ready:
                stdout_line = proc.stdout.readline()
                # If there's stdout, it should be valid MCP protocol
                if stdout_line:
                    try:
                        json.loads(stdout_line)
                    except json.JSONDecodeError:
                        pytest.fail("Server wrote non-JSON to stdout")
            
        finally:
            proc.terminate()
            proc.wait(timeout=5)
