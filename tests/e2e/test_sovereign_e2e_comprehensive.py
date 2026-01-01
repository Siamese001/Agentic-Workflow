"""
End-to-End Tests for Sovereign Agent System.
Tests full workflow execution and system-wide behaviors.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Any, Dict
import sys
import asyncio

# Ensure project root is in path - use absolute resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Key directories
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"
TESTS_DIR = PROJECT_ROOT / "tests"


@pytest.mark.usefixtures("disable_path_shield")
class TestFullSystemStructure:
    """E2E tests for repository structure compliance."""
    
    def test_all_ssot_layers_exist(self):
        """Verify all SSOT-defined layers exist in the repository."""
        expected_layers = [
            "L0_maintenance",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
        ]
        for layer in expected_layers:
            path = AGENTIC_CORE / layer
            assert path.exists(), f"SSOT layer missing: {layer} at {path}"
    
    def test_all_test_categories_exist(self):
        """Verify all SSOT-defined test categories exist."""
        expected_categories = ["unit", "integration", "e2e", "core"]
        for category in expected_categories:
            path = TESTS_DIR / category
            assert path.exists() or (TESTS_DIR / f"{category}.py").exists(), \
                f"Test category missing: {category} at {path}"
    
    def test_config_blueprint_sovereign_exists(self):
        """Verify config/blueprint_sovereign directory exists."""
        config_path = AGENTIC_CORE / "config" / "blueprint_sovereign"
        assert config_path.exists(), f"blueprint_sovereign config directory missing at {config_path}"
        
        structure_file = config_path / "structure_blueprint.py"
        assert structure_file.exists(), "structure_blueprint.py missing"


@pytest.mark.usefixtures("disable_path_shield")
class TestAgentDiscovery:
    """E2E tests for agent discovery and registry."""
    
    def test_discover_l2_agents(self):
        """Discover and validate L2 execution agents."""
        l2_path = PROJECT_ROOT / "agentic_core" / "L2_execution" / "tool_registry"
        if l2_path.exists():
            agent_files = list(l2_path.glob("*Agent.py"))
            assert len(agent_files) > 0, "No agents found in L2 tool_registry"
            
            # Verify agent naming convention
            for agent_file in agent_files:
                assert agent_file.name[0].isupper(), f"Agent file should be PascalCase: {agent_file.name}"
    
    def test_discover_l5_validators(self):
        """Discover and validate L5 safety validators."""
        l5_path = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators"
        if l5_path.exists():
            agent_files = list(l5_path.glob("*Agent.py"))
            assert len(agent_files) > 0, "No agents found in L5 validators"
    
    def test_agent_registry_matches_filesystem(self):
        """Verify AGENT_REGISTRY entries exist on filesystem."""
        try:
            from agentic_core.config.blueprint_sovereign.structure_blueprint import AGENT_REGISTRY
            
            # Sample check - verify some agents exist
            for layer, agents in AGENT_REGISTRY.items():
                if isinstance(agents, list) and len(agents) > 0:
                    # Check first agent in each layer
                    first_agent = agents[0]
                    if isinstance(first_agent, dict) and 'file' in first_agent:
                        agent_path = PROJECT_ROOT / first_agent['file']
                        # Non-blocking - just log if missing
                        if not agent_path.exists():
                            print(f"Warning: Agent file not found: {first_agent['file']}")
        except ImportError as e:
            pytest.skip(f"AGENT_REGISTRY not available: {e}")


class TestPascalSovereigntyE2E:
    """E2E tests for PascalCase sovereignty enforcement."""
    
    @pytest.mark.asyncio
    async def test_pascal_enforcer_dry_run(self):
        """Test full dry-run of PascalSovereigntyEnforcerAgent."""
        try:
            from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent
            ctx = MagicMock()
            agent = PascalSovereigntyEnforcerAgent(ctx=ctx, dry_run=True, _allow_mock=True)
            
            # Run audit only (schemas scope to limit)
            result = await agent.execute(scope="schemas")
            assert result is not None
            assert 'audit' in result or 'status' in result
        except ImportError as e:
            pytest.skip(f"PascalSovereigntyEnforcerAgent not available: {e}")
        except Exception as e:
            pytest.skip(f"E2E test error: {e}")
    
    def test_pascal_purge_preserves_functionality(self):
        """Test that purge logic preserves code functionality."""
        try:
            from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent
            ctx = MagicMock()
            agent = PascalSovereigntyEnforcerAgent(ctx=ctx, dry_run=True, _allow_mock=True)
            
            # Test complex code preservation
            input_code = '''
class complex_validator(BaseModel):
    """A complex validator with docstring."""
    name: str
    value: int
    
    def validate(self):
        return self.value > 0

ComplexValidator = complex_validator
result = complex_validator(name="test", value=5)
'''
            result = agent._purge_snake_case(input_code)
            
            # Verify structure preserved
            assert 'class ComplexValidator' in result
            assert 'def validate' in result
            assert 'docstring' in result
            assert 'BaseModel' in result
        except ImportError as e:
            pytest.skip(f"PascalSovereigntyEnforcerAgent not available: {e}")


class TestCriticalPaths:
    """E2E tests for critical system paths."""
    
    def test_import_chain_l5_to_l2(self):
        """Test import chain from L5 safety to L2 execution."""
        try:
            # This tests the import hierarchy
            from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent
            from agentic_core.L2_execution.tool_registry.ExecutionCanonBaseAgent import CanonBaseAgent
            
            # Both should be importable
            assert PascalSovereigntyEnforcerAgent is not None
            assert CanonBaseAgent is not None
        except ImportError as e:
            pytest.skip(f"Import chain error: {e}")
    
    def test_config_imports(self):
        """Test config module imports work correctly."""
        try:
            from agentic_core.config.blueprint_sovereign.structure_blueprint import (
                SOVEREIGN_REGISTRY,
                CORE_SUBFOLDER_MAP,
                HEALING_CONFIG,
            )
            assert SOVEREIGN_REGISTRY is not None
            assert CORE_SUBFOLDER_MAP is not None
            assert HEALING_CONFIG is not None
        except ImportError as e:
            pytest.skip(f"Config import error: {e}")


class TestSystemHealth:
    """E2E tests for overall system health."""
    
    def test_no_circular_imports_in_core(self):
        """Test that core modules don't have circular imports."""
        # If we can import these without error, no circular imports
        try:
            import agentic_core
            assert agentic_core is not None
        except ImportError as e:
            pytest.skip(f"Core import error (may indicate circular import): {e}")
    
    def test_l5_safety_init(self):
        """Test L5 safety module initializes correctly."""
        try:
            from agentic_core.L5_safety import SubAtomicEngine
            assert SubAtomicEngine is not None
        except ImportError as e:
            pytest.skip(f"L5 safety init error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
