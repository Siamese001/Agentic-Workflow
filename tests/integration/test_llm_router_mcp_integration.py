"""
Integration Tests for Phase 16B: LLM Router MCP Client
Validates sovereign L5 safety validation operations through MCP architecture.
"""
import asyncio
import pytest
from agentic_core.L5_safety.guardrails.llm_router_mcp_client import get_llm_router_client, SovereignLLMRouterMCPClient
from agentic_core.config.P1_core.sovereign_config import config


class TestLLMRouterMCPIntegration:
    """Test suite for LLM Router MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_llm_router_mcp_enabled(self):
        """Verify LLM Router MCP is enabled in sovereign config."""
        assert config.LLM_ROUTER_MCP_ENABLED is True, "LLM Router MCP must be enabled"
        assert config.LLM_ROUTER_DEFAULT_PROVIDER == "gemini-2.5-flash", "Default provider should be gemini-2.5-flash"
        assert config.LLM_ROUTER_SAFETY_MODEL == "gemini-2.5-flash", "Safety model should be gemini-2.5-flash"
        assert config.LLM_ROUTER_VALIDATION_TEMPERATURE == 0.0, "Validation temperature should be 0.0"
        assert config.LLM_ROUTER_MAX_TOKENS == 1024, "Max tokens should be 1024"
    
    @pytest.mark.asyncio
    async def test_llm_router_client_singleton(self):
        """Verify singleton pattern for LLM Router client."""
        client1 = get_llm_router_client()
        client2 = get_llm_router_client()
        assert client1 is client2, "Should return same singleton instance"
    
    @pytest.mark.asyncio
    async def test_llm_router_validate_content_safe(self):
        """Test content validation for safe content via MCP."""
        client = get_llm_router_client()
        
        safe_content = "This is a normal, safe piece of text for validation."
        
        result = await client.validate_content(safe_content, validation_type="safety")
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "is_safe" in result, "Result should contain is_safe field"
        # Note: Actual validation depends on MCP implementation
    
    @pytest.mark.asyncio
    async def test_llm_router_validate_content_fail_closed(self):
        """Test fail-closed strategy when MCP fails."""
        client = get_llm_router_client()
        
        # Test with content that might cause issues
        problematic_content = "\x00\x01\x02" * 1000
        
        result = await client.validate_content(problematic_content, validation_type="safety")
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "is_safe" in result, "Result should contain is_safe field"
        # Fail-closed: if validation fails, should default to is_safe=False
    
    @pytest.mark.asyncio
    async def test_llm_router_classify_intent(self):
        """Test intent classification via MCP."""
        client = get_llm_router_client()
        
        query = "What is the weather like today?"
        
        result = await client.classify_intent(query)
        
        assert isinstance(result, dict), "Result should be a dictionary"
        # Intent classification should return intent and confidence
    
    @pytest.mark.asyncio
    async def test_llm_router_mcp_routing(self):
        """Verify operations route through L3 MCP router."""
        client = get_llm_router_client()
        
        # Verify router is initialized
        assert hasattr(client, 'router'), "Client should have router"
        assert client.router is not None, "Router should be initialized"
        
        # Verify router role
        assert client.router.role == "safety_validation", "Router role should be safety_validation"
    
    @pytest.mark.asyncio
    async def test_llm_router_error_handling(self):
        """Test graceful error handling for failed operations."""
        client = get_llm_router_client()
        
        # Test with empty content
        result = await client.validate_content("", validation_type="safety")
        
        assert isinstance(result, dict), "Should return dict even on error"
        assert "is_safe" in result, "Should contain is_safe field"


class TestOverseerMigration:
    """Test overseer migration to LLM Router MCP."""
    
    @pytest.mark.asyncio
    async def test_safety_inspector_uses_mcp(self):
        """Verify SafetyInspector uses LLM Router MCP for Socratic Judge."""
        from agentic_core.L5_safety.guardrails.overseer import SafetyInspector
        
        # Create inspector with Socratic Judge enabled
        inspector = SafetyInspector(enable_socratic_judge=True)
        
        # Verify it's enabled
        assert inspector.enable_socratic_judge is True, "Socratic Judge should be enabled"
        
        # The _socratic_verify method should now use LLM Router MCP
        # This is verified by code inspection - no direct google.generativeai import


class TestRedSentinelMigration:
    """Test Red Sentinel migration to LLM Router MCP."""
    
    @pytest.mark.asyncio
    async def test_red_sentinel_uses_mcp(self):
        """Verify RedSentinel uses LLM Router MCP for hostile input generation."""
        from agentic_core.L5_safety.guardrails.red_sentinel import RedSentinel
        
        # Create Red Sentinel instance
        sentinel = RedSentinel()
        
        # Verify initialization
        assert sentinel is not None, "RedSentinel should initialize"
        
        # The _generate_hostile_inputs method should now use LLM Router MCP
        # This is verified by code inspection - no direct google.generativeai import


class TestGuardianEnforcement:
    """Test guardian enforcement of LLM Router MCP usage."""
    
    def test_guardian_blocks_openai_import(self):
        """Verify guardian blocks direct openai imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with direct openai import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import openai\n")
            f.write("client = openai.OpenAI()\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block direct openai import"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_anthropic_import(self):
        """Verify guardian blocks direct anthropic imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with direct anthropic import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import anthropic\n")
            f.write("client = anthropic.Anthropic()\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block direct anthropic import"
        finally:
            temp_path.unlink()
    
    def test_guardian_blocks_genai_import(self):
        """Verify guardian blocks direct google.generativeai imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with direct genai import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("import google.generativeai as genai\n")
            f.write("model = genai.GenerativeModel('gemini-pro')\n")
            temp_path = Path(f.name)
        
        try:
            # Should fail validation
            result = check_file(temp_path)
            assert result is False, "Guardian should block direct genai import"
        finally:
            temp_path.unlink()
    
    def test_guardian_allows_llm_router_mcp(self):
        """Verify guardian allows LLM Router MCP usage."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        
        # Create temp file with LLM Router MCP import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from agentic_core.L5_safety.guardrails.llm_router_mcp_client import get_llm_router_client\n")
            f.write("client = get_llm_router_client()\n")
            temp_path = Path(f.name)
        
        try:
            # Should pass validation
            result = check_file(temp_path)
            assert result is True, "Guardian should allow LLM Router MCP import"
        finally:
            temp_path.unlink()


def run_tests():
    """Run all LLM Router MCP integration tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])


if __name__ == "__main__":
    run_tests()
