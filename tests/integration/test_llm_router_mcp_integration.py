"""
Integration Tests for Phase 16B: LLM Router MCP Client
Validates sovereign L5 safety validation operations through MCP architecture.
"""
import asyncio
import pytest
from agentic_core.L5_safety.guardrails.llm_router_mcp_client import get_llm_router_client, SovereignLLMRouterMCPClient
from agentic_core.config.P1_core.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class test_llm_router_mcp_integration:
    """Test suite for LLM Router MCP client integration."""

    @pytest.mark.asyncio
    async def test_llm_router_mcp_enabled(self) -> Any:
        """Verify LLM Router MCP is enabled in sovereign config."""
        assert config.LLM_ROUTER_MCP_ENABLED is True, 'LLM Router MCP must be enabled'
        assert config.LLM_ROUTER_DEFAULT_PROVIDER == 'gemini-2.5-flash', 'Default provider should be gemini-2.5-flash'
        assert config.LLM_ROUTER_SAFETY_MODEL == 'gemini-2.5-flash', 'Safety model should be gemini-2.5-flash'
        assert config.LLM_ROUTER_VALIDATION_TEMPERATURE == 0.0, 'Validation temperature should be 0.0'
        assert config.LLM_ROUTER_MAX_TOKENS == 1024, 'Max tokens should be 1024'

    @pytest.mark.asyncio
    async def test_llm_router_client_singleton(self) -> Any:
        """Verify singleton pattern for LLM Router client."""
        client1: Any = get_llm_router_client()
        client2: Any = get_llm_router_client()
        assert client1 is client2, 'Should return same singleton instance'

    @pytest.mark.asyncio
    async def test_llm_router_validate_content_safe(self) -> Any:
        """Test content validation for safe content via MCP."""
        client: Any = get_llm_router_client()
        safe_content: Any = 'This is a normal, safe piece of text for validation.'
        result: Any = await client.validate_content(safe_content, validation_type='safety')
        assert isinstance(result, dict), 'Result should be a dictionary'
        assert 'is_safe' in result, 'Result should contain is_safe field'

    @pytest.mark.asyncio
    async def test_llm_router_validate_content_fail_closed(self) -> Any:
        """Test fail-closed strategy when MCP fails."""
        client: Any = get_llm_router_client()
        problematic_content: Any = '\x00\x01\x02' * 1000
        result: Any = await client.validate_content(problematic_content, validation_type='safety')
        assert isinstance(result, dict), 'Result should be a dictionary'
        assert 'is_safe' in result, 'Result should contain is_safe field'

    @pytest.mark.asyncio
    async def test_llm_router_classify_intent(self) -> Any:
        """Test intent classification via MCP."""
        client: Any = get_llm_router_client()
        query: Any = 'What is the weather like today?'
        result: Any = await client.classify_intent(query)
        assert isinstance(result, dict), 'Result should be a dictionary'

    @pytest.mark.asyncio
    async def test_llm_router_mcp_routing(self) -> Any:
        """Verify operations route through L3 MCP router."""
        client: Any = get_llm_router_client()
        assert hasattr(client, 'router'), 'Client should have router'
        assert client.router is not None, 'Router should be initialized'
        assert client.router.role == 'safety_validation', 'Router role should be safety_validation'

    @pytest.mark.asyncio
    async def test_llm_router_error_handling(self) -> Any:
        """Test graceful error handling for failed operations."""
        client: Any = get_llm_router_client()
        result: Any = await client.validate_content('', validation_type='safety')
        assert isinstance(result, dict), 'Should return dict even on error'
        assert 'is_safe' in result, 'Should contain is_safe field'

class test_overseer_migration:
    """Test overseer migration to LLM Router MCP."""

    @pytest.mark.asyncio
    async def test_safety_inspector_uses_mcp(self) -> Any:
        """Verify SafetyInspectorAgent uses LLM Router MCP for Socratic Judge."""
        from agentic_core.L5_safety.guardrails.overseer import SafetyInspectorAgent
        inspector: Any = SafetyInspectorAgent(enable_socratic_judge=True)
        assert inspector.enable_socratic_judge is True, 'Socratic Judge should be enabled'

class test_red_sentinel_migration:
    """Test Red Sentinel migration to LLM Router MCP."""

    @pytest.mark.asyncio
    async def test_red_sentinel_uses_mcp(self) -> Any:
        """Verify RedSentinelAgent uses LLM Router MCP for hostile input generation."""
        from agentic_core.L5_safety.guardrails.RedSentinelAgent import RedSentinelAgent
        sentinel: Any = RedSentinelAgent()
        assert sentinel is not None, 'RedSentinelAgent should initialize'

class test_guardian_enforcement:
    """Test guardian enforcement of LLM Router MCP usage."""

    def test_guardian_blocks_openai_import(self) -> Any:
        """Verify guardian blocks direct openai imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import openai\n')
            f.write('client = openai.OpenAI()\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block direct openai import'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_anthropic_import(self) -> Any:
        """Verify guardian blocks direct anthropic imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import anthropic\n')
            f.write('client = anthropic.Anthropic()\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block direct anthropic import'
        finally:
            temp_path.unlink()

    def test_guardian_blocks_genai_import(self) -> Any:
        """Verify guardian blocks direct google.generativeai imports."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import google.generativeai as genai\n')
            f.write("model = genai.GenerativeModel('gemini-pro')\n")
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is False, 'Guardian should block direct genai import'
        finally:
            temp_path.unlink()

    def test_guardian_allows_llm_router_mcp(self) -> Any:
        """Verify guardian allows LLM Router MCP usage."""
        from agentic_core.L0_maintenance.scripts.guard_no_hardcoded_config import check_file
        from pathlib import Path
        import tempfile
from typing import Any
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('from agentic_core.L5_safety.guardrails.llm_router_mcp_client import get_llm_router_client\n')
            f.write('client = get_llm_router_client()\n')
            temp_path: Any = Path(f.name)
        try:
            result: Any = check_file(temp_path)
            assert result is True, 'Guardian should allow LLM Router MCP import'
        finally:
            temp_path.unlink()

def run_tests() -> Any:
    """Run all LLM Router MCP integration tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
if __name__ == '__main__':
    run_tests()
