"""
Tests for MCP Hardening Implementation

Tests the MCPHardenedMixin features:
- safe_mcp_call with validation and sandboxing
- validate_mcp_response for code injection, resource limits
- audit_mcp_call logging
- Tool whitelist enforcement
- Response sanitization
"""

import pytest
import asyncio
import time
from typing import Dict, Any

import sys
sys.path.insert(0, 'c:/Git/Agentic-Workflow')

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import (
    MCPHardenedMixin,
    MCPAuditEntry,
    MCPValidationResult,
)


# ============== Test Fixtures ==============

class TestHardenedAgent(MCPHardenedMixin):
    """Test agent with MCP hardening."""
    

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
        
        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self):
        super().__init__()


@pytest.fixture
def hardened_agent():
    """Create test hardened agent."""
    return TestHardenedAgent()


# ============== Tool Whitelist Tests ==============

class TestToolWhitelist:
    """Tests for tool whitelist validation."""
    
    def test_valid_tool_in_whitelist(self, hardened_agent):
        """Test that whitelisted tools pass validation."""
        assert hardened_agent._validate_tool_name("read_file") == True
        assert hardened_agent._validate_tool_name("write_file") == True
        assert hardened_agent._validate_tool_name("grep_search") == True
        assert hardened_agent._validate_tool_name("git_status") == True
        assert hardened_agent._validate_tool_name("redis_get") == True
    
    def test_invalid_tool_not_in_whitelist(self, hardened_agent):
        """Test that non-whitelisted tools fail validation."""
        assert hardened_agent._validate_tool_name("malicious_tool") == False
        assert hardened_agent._validate_tool_name("unknown_operation") == False
        assert hardened_agent._validate_tool_name("system_exec") == False
    
    def test_tool_name_case_insensitive(self, hardened_agent):
        """Test that tool name validation is case insensitive."""
        assert hardened_agent._validate_tool_name("READ_FILE") == True
        assert hardened_agent._validate_tool_name("Read_File") == True
        assert hardened_agent._validate_tool_name("GREP_SEARCH") == True
    
    def test_tool_name_with_prefix_suffix(self, hardened_agent):
        """Test that namespaced tools are allowed."""
        assert hardened_agent._validate_tool_name("read_file_async") == True
        assert hardened_agent._validate_tool_name("async_read_file") == True


class TestArgumentValidation:
    """Tests for argument validation."""
    
    def test_valid_args(self, hardened_agent):
        """Test that valid arguments pass."""
        args = {"file_path": "/test/path", "content": "hello"}
        errors = hardened_agent._validate_args("write_file", args)
        assert len(errors) == 0
    
    def test_none_args_allowed(self, hardened_agent):
        """Test that None args are allowed."""
        errors = hardened_agent._validate_args("read_file", None)
        assert len(errors) == 0
    
    def test_dangerous_pattern_eval(self, hardened_agent):
        """Test detection of eval() pattern."""
        args = {"code": "eval('malicious')"}
        errors = hardened_agent._validate_args("run_command", args)
        assert len(errors) > 0
        assert any("Dangerous pattern" in e for e in errors)
    
    def test_dangerous_pattern_exec(self, hardened_agent):
        """Test detection of exec() pattern."""
        args = {"code": "exec('malicious')"}
        errors = hardened_agent._validate_args("run_command", args)
        assert len(errors) > 0
    
    def test_dangerous_pattern_import(self, hardened_agent):
        """Test detection of __import__ pattern."""
        args = {"code": "__import__('os')"}
        errors = hardened_agent._validate_args("run_command", args)
        assert len(errors) > 0
    
    def test_dangerous_pattern_subprocess(self, hardened_agent):
        """Test detection of subprocess pattern."""
        args = {"cmd": "subprocess.run('rm -rf /')"}
        errors = hardened_agent._validate_args("run_command", args)
        assert len(errors) > 0
    
    def test_dangerous_pattern_sql_injection(self, hardened_agent):
        """Test detection of SQL injection patterns."""
        args = {"query": "DROP TABLE users"}
        errors = hardened_agent._validate_args("redis_get", args)
        assert len(errors) > 0
    
    def test_dangerous_pattern_script_tag(self, hardened_agent):
        """Test detection of script tag."""
        args = {"html": "<script>alert('xss')</script>"}
        errors = hardened_agent._validate_args("write_file", args)
        assert len(errors) > 0


# ============== Response Validation Tests ==============

class TestResponseValidation:
    """Tests for MCP response validation."""
    
    def test_valid_response(self, hardened_agent):
        """Test that valid responses pass."""
        response = {"status": "success", "data": "hello"}
        result = hardened_agent.validate_mcp_response(response)
        assert result.valid == True
        assert len(result.reasons) == 0
    
    def test_code_injection_in_response(self, hardened_agent):
        """Test detection of code injection in response."""
        response = "eval('malicious_code')"
        result = hardened_agent.validate_mcp_response(response)
        assert result.valid == False
        assert any("injection" in r.lower() for r in result.reasons)
    
    def test_response_size_limit(self, hardened_agent):
        """Test response size limit enforcement."""
        # Create oversized response
        hardened_agent.MAX_RESPONSE_SIZE = 100  # Small for testing
        response = "x" * 200
        result = hardened_agent.validate_mcp_response(response)
        assert result.valid == False
        assert any("size limit" in r.lower() for r in result.reasons)
        hardened_agent.MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # Reset
    
    def test_response_depth_limit(self, hardened_agent):
        """Test response depth limit enforcement."""
        hardened_agent.MAX_RESPONSE_DEPTH = 5  # Small for testing
        # Create deeply nested response
        response = {"a": {"b": {"c": {"d": {"e": {"f": {"g": "deep"}}}}}}}
        result = hardened_agent.validate_mcp_response(response)
        assert result.valid == False
        assert any("depth limit" in r.lower() for r in result.reasons)
        hardened_agent.MAX_RESPONSE_DEPTH = 50  # Reset
    
    def test_response_sanitization(self, hardened_agent):
        """Test that dangerous patterns are sanitized."""
        response = "some text with eval('bad') in it"
        result = hardened_agent.validate_mcp_response(response)
        assert "[SANITIZED]" in result.sanitized_output
    
    def test_nested_response_sanitization(self, hardened_agent):
        """Test sanitization of nested responses."""
        response = {"data": {"code": "eval('bad')"}, "list": ["exec('bad')"]}
        result = hardened_agent.validate_mcp_response(response)
        # Check sanitized output
        assert "[SANITIZED]" in result.sanitized_output["data"]["code"]
        assert "[SANITIZED]" in result.sanitized_output["list"][0]


# ============== Safe MCP Call Tests ==============

class TestSafeMCPCall:
    """Tests for safe_mcp_call method."""
    
    @pytest.mark.asyncio
    async def test_safe_call_valid_tool(self, hardened_agent):
        """Test safe call with valid tool."""
        result = await hardened_agent.safe_mcp_call(
            "read_file",
            {"path": "/test/file.txt"}
        )
        assert result["status"] == "success"
        assert result["tool"] == "read_file"
    
    @pytest.mark.asyncio
    async def test_safe_call_blocked_tool(self, hardened_agent):
        """Test safe call with blocked tool."""
        with pytest.raises(ValueError) as exc_info:
            await hardened_agent.safe_mcp_call(
                "malicious_tool",
                {"arg": "value"}
            )
        assert "not in whitelist" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_safe_call_dangerous_args(self, hardened_agent):
        """Test safe call with dangerous arguments."""
        with pytest.raises(ValueError) as exc_info:
            await hardened_agent.safe_mcp_call(
                "run_command",
                {"cmd": "eval('malicious')"}
            )
        assert "Invalid arguments" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_safe_call_audit_logged(self, hardened_agent):
        """Test that safe call is logged to audit."""
        await hardened_agent.safe_mcp_call(
            "read_file",
            {"path": "/test/file.txt"}
        )
        
        audit_log = hardened_agent.get_audit_log()
        assert len(audit_log) > 0
        assert audit_log[-1].tool_name == "read_file"
        assert audit_log[-1].result_status == "SUCCESS"
    
    @pytest.mark.asyncio
    async def test_safe_call_blocked_audit_logged(self, hardened_agent):
        """Test that blocked calls are logged to audit."""
        try:
            await hardened_agent.safe_mcp_call(
                "malicious_tool",
                {"arg": "value"}
            )
        except ValueError:
            pass
        
        audit_log = hardened_agent.get_audit_log()
        assert len(audit_log) > 0
        assert audit_log[-1].tool_name == "malicious_tool"
        assert audit_log[-1].result_status == "BLOCKED"
    
    @pytest.mark.asyncio
    async def test_safe_call_statistics(self, hardened_agent):
        """Test that statistics are tracked."""
        # Make a successful call
        await hardened_agent.safe_mcp_call("read_file", {"path": "/test"})
        
        # Make a failed call
        try:
            await hardened_agent.safe_mcp_call("bad_tool", {})
        except ValueError:
            pass
        
        stats = hardened_agent.get_mcp_statistics()
        assert stats["total_calls"] == 2
        assert stats["successful_calls"] == 1
        assert stats["failed_calls"] == 1
        assert stats["success_rate"] == 50.0


# ============== Audit Logging Tests ==============

class TestAuditLogging:
    """Tests for audit logging functionality."""
    
    def test_audit_entry_creation(self, hardened_agent):
        """Test audit entry creation."""
        hardened_agent.audit_mcp_call(
            "read_file",
            {"path": "/test"},
            "SUCCESS",
            "TestAgent",
            {"duration_ms": 100}
        )
        
        audit_log = hardened_agent.get_audit_log()
        assert len(audit_log) == 1
        
        entry = audit_log[0]
        assert entry.tool_name == "read_file"
        assert entry.result_status == "SUCCESS"
        assert entry.caller == "TestAgent"
        assert entry.duration_ms == 100
    
    def test_audit_log_limit(self, hardened_agent):
        """Test audit log limit parameter."""
        # Add multiple entries
        for i in range(150):
            hardened_agent.audit_mcp_call(
                f"tool_{i}",
                {},
                "SUCCESS",
                "TestAgent"
            )
        
        # Get with default limit
        log_100 = hardened_agent.get_audit_log(limit=100)
        assert len(log_100) == 100
        
        # Get with custom limit
        log_50 = hardened_agent.get_audit_log(limit=50)
        assert len(log_50) == 50
    
    def test_audit_args_hashing(self, hardened_agent):
        """Test that arguments are hashed in audit."""
        hardened_agent.audit_mcp_call(
            "read_file",
            {"secret": "sensitive_data"},
            "SUCCESS",
            "TestAgent"
        )
        
        entry = hardened_agent.get_audit_log()[-1]
        # Args should be hashed, not stored in plain text
        assert "sensitive_data" not in entry.args_hash
        assert len(entry.args_hash) == 16  # SHA256 truncated


# ============== Hardened Call Tests ==============

class TestHardenedCall:
    """Tests for _hardened_call method with retries."""
    
    @pytest.mark.asyncio
    async def test_hardened_call_success(self, hardened_agent):
        """Test successful hardened call."""
        async def success_func():
            return "success"
        
        result = await hardened_agent._hardened_call("test_op", success_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_hardened_call_retry(self, hardened_agent):
        """Test hardened call with retries."""
        call_count = 0
        
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        hardened_agent.BASE_DELAY = 0.01  # Fast retry for testing
        result = await hardened_agent._hardened_call("test_op", fail_then_succeed)
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_hardened_call_timeout(self, hardened_agent):
        """Test hardened call timeout."""
        async def slow_func():
            await asyncio.sleep(10)
            return "never reached"
        
        with pytest.raises(RuntimeError) as exc_info:
            await hardened_agent._hardened_call(
                "test_op",
                slow_func,
                timeout=0.1
            )
        assert "failed after" in str(exc_info.value)


# ============== Integration Tests ==============

class TestMCPHardeningIntegration:
    """Integration tests for complete MCP hardening flow."""
    
    @pytest.mark.asyncio
    async def test_full_hardening_flow(self, hardened_agent):
        """Test complete hardening flow."""
        # 1. Valid call
        result = await hardened_agent.safe_mcp_call(
            "read_file",
            {"path": "/test/file.txt"},
            caller="IntegrationTest"
        )
        assert result["status"] == "success"
        
        # 2. Check audit
        audit = hardened_agent.get_audit_log()
        assert len(audit) >= 1
        assert audit[-1].caller == "IntegrationTest"
        
        # 3. Check statistics
        stats = hardened_agent.get_mcp_statistics()
        assert stats["successful_calls"] >= 1
    
    @pytest.mark.asyncio
    async def test_security_hardening_coverage(self, hardened_agent):
        """Test that all security features are active."""
        # Tool whitelist
        with pytest.raises(ValueError):
            await hardened_agent.safe_mcp_call("bad_tool", {})
        
        # Argument validation
        with pytest.raises(ValueError):
            await hardened_agent.safe_mcp_call("run_command", {"cmd": "eval('x')"})
        
        # Response validation
        validation = hardened_agent.validate_mcp_response("exec('bad')")
        assert validation.valid == False
        
        # Audit logging
        assert len(hardened_agent.get_audit_log()) > 0
        
        # Statistics
        stats = hardened_agent.get_mcp_statistics()
        assert stats["total_calls"] > 0
    
    @pytest.mark.asyncio
    async def test_multiple_agents_isolation(self):
        """Test that multiple agents have isolated state."""
        agent1 = TestHardenedAgent()
        agent2 = TestHardenedAgent()
        
        await agent1.safe_mcp_call("read_file", {"path": "/test1"})
        await agent2.safe_mcp_call("read_file", {"path": "/test2"})
        await agent2.safe_mcp_call("read_file", {"path": "/test3"})
        
        # Each agent has its own audit log
        assert len(agent1.get_audit_log()) == 1
        assert len(agent2.get_audit_log()) == 2
        
        # Each agent has its own statistics
        assert agent1.get_mcp_statistics()["total_calls"] == 1
        assert agent2.get_mcp_statistics()["total_calls"] == 2


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
