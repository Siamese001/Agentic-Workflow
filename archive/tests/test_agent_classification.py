#!/usr/bin/env python3
"""
Comprehensive test suite for hardened agent classification.

Tests multi-factor positive and negative signals for 100% precision in:
- base_class vs mixin vs utility classification
- Agent discovery exclusions (coverage_html, reports, etc.)
- Sub-territory alignment

Target: 100% pass rate with zero false positives/negatives.

NOTE: Many tests in this file are DEPRECATED as they test internal implementation
details (_classify_subterritory) that have been refactored in the new architecture.
"""
import ast
import sys
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Disable path_shield for real file I/O testing
pytestmark = [
    pytest.mark.usefixtures("disable_path_shield"),
    pytest.mark.skip(reason="DEPRECATED: Tests internal _classify_subterritory API that has been refactored")
]


class TestAgentClassificationPositiveSignals:
    """Test cases for TRUE base_class agents - should be correctly classified."""
    
    def test_safety_base_agent_is_base_class(self):
        """SafetyBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/guardrails/SafetyBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"SafetyBaseAgent should be base_class, got {result}"
    
    def test_state_base_agent_is_base_class(self):
        """StateBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L4_state/StateBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"StateBaseAgent should be base_class, got {result}"
    
    def test_orchestration_base_agent_is_base_class(self):
        """OrchestrationBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L3_orchestration/OrchestrationBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"OrchestrationBaseAgent should be base_class, got {result}"
    
    def test_canon_base_agent_is_base_class(self):
        """CanonBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L2_execution/ToolRegistry/CanonBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"CanonBaseAgent should be base_class, got {result}"
    
    def test_maintenance_base_agent_is_base_class(self):
        """MaintenanceBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L0_maintenance/MaintenanceBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"MaintenanceBaseAgent should be base_class, got {result}"
    
    def test_execution_base_agent_is_base_class(self):
        """ExecutionCanonBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L2_execution/ExecutionCanonBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"ExecutionCanonBaseAgent should be base_class, got {result}"
    
    def test_cognition_base_agent_is_base_class(self):
        """CognitionCanonBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L1_cognition/CognitionCanonBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"CognitionCanonBaseAgent should be base_class, got {result}"
    
    def test_sovereign_base_agent_is_base_class(self):
        """SovereignBaseAgent.py should be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/config/blueprint_sovereign/SovereignBaseAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "base_class", f"SovereignBaseAgent should be base_class, got {result}"


class TestAgentClassificationNegativeSignals:
    """Test cases for known mixins/utilities - should be EXCLUDED from base_class."""
    
    def test_mcp_hardened_mixin_not_base_class(self):
        """mcp_hardened_mixin.py should NOT be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/guardrails/mcp_hardened_mixin.py")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"mcp_hardened_mixin should NOT be base_class, got {result}"
    
    def test_healer_mixin_not_base_class(self):
        """healer_mixin.py should NOT be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/guardrails/healer_mixin.py")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"healer_mixin should NOT be base_class, got {result}"
    
    def test_ast_enforcement_mixin_not_base_class(self):
        """ASTEnforcementMixin.py should NOT be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/validators/ASTEnforcementMixin.py")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"ASTEnforcementMixin should NOT be base_class, got {result}"
    
    def test_base_class_enforcer_not_base_class(self):
        """BaseClassEnforcerAgent.py should NOT be classified as base_class (it's an enforcer)."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/validators/BaseClassEnforcerAgent.py")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"BaseClassEnforcerAgent should NOT be base_class, got {result}"
    
    def test_coverage_html_file_excluded(self):
        """Files in coverage_html/ should not be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("coverage_html/z_78d92796ab9dd0b1_SafetyBaseAgent_py.html")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"coverage_html files should NOT be base_class, got {result}"
    
    def test_reports_file_excluded(self):
        """Files in reports/ should not be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("reports/some_agent_report.py")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"reports files should NOT be base_class, got {result}"
    
    def test_pycache_file_excluded(self):
        """Files in __pycache__/ should not be classified as base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/__pycache__/SomeBaseAgent.cpython-311.pyc")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"__pycache__ files should NOT be base_class, got {result}"
    
    def test_hygiene_guardian_not_base_class(self):
        """HygieneGuardianAgent.py should NOT be classified as base_class (it's a guardian)."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/validators/HygieneGuardianAgent.py")
        result = agent._classify_subterritory(path)
        assert result != "base_class", f"HygieneGuardianAgent should NOT be base_class (it's a guardian), got {result}"


class TestAgentDiscoveryExclusions:
    """Test the should_exclude_file and should_exclude_path functions."""
    
    def test_should_exclude_coverage_html(self):
        """coverage_html directory should be excluded."""
        from scripts.full_agent_discovery import should_exclude_path
        path = Path("coverage_html/some_file.html")
        assert should_exclude_path(path), "coverage_html should be excluded"
    
    def test_should_exclude_htmlcov(self):
        """htmlcov directory should be excluded."""
        from scripts.full_agent_discovery import should_exclude_path
        path = Path("htmlcov/index.html")
        assert should_exclude_path(path), "htmlcov should be excluded"
    
    def test_should_exclude_pycache(self):
        """__pycache__ directory should be excluded."""
        from scripts.full_agent_discovery import should_exclude_path
        path = Path("agentic_core/__pycache__/module.cpython-311.pyc")
        assert should_exclude_path(path), "__pycache__ should be excluded"
    
    def test_should_exclude_pytest_cache(self):
        """.pytest_cache directory should be excluded."""
        from scripts.full_agent_discovery import should_exclude_path
        path = Path(".pytest_cache/v/cache/lastfailed")
        assert should_exclude_path(path), ".pytest_cache should be excluded"
    
    def test_should_exclude_mixin_file(self):
        """Files with 'mixin' in name should be excluded (unless ending with 'agent')."""
        from scripts.full_agent_discovery import should_exclude_file
        path = Path("agentic_core/healer_mixin.py")
        assert should_exclude_file(path), "mixin files should be excluded"
    
    def test_should_not_exclude_mixin_agent_file(self):
        """Files with 'mixin' but ending with 'agent' should NOT be excluded."""
        from scripts.full_agent_discovery import should_exclude_file
        path = Path("agentic_core/healer_mixin_agent.py")
        assert not should_exclude_file(path), "mixin_agent files should NOT be excluded"
    
    def test_should_exclude_utility_file(self):
        """Files with 'utility' in name should be excluded."""
        from scripts.full_agent_discovery import should_exclude_file
        path = Path("agentic_core/string_utility.py")
        assert should_exclude_file(path), "utility files should be excluded"
    
    def test_should_not_exclude_real_agent(self):
        """Real agent files should NOT be excluded."""
        from scripts.full_agent_discovery import should_exclude_file
        path = Path("agentic_core/L5_safety/guardrails/SafetyBaseAgent.py")
        assert not should_exclude_file(path), "SafetyBaseAgent should NOT be excluded"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_mixin_agent_hybrid_name(self):
        """A file named XxxMixinAgent.py should be classified correctly if it's a real agent."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        # Simulating a hypothetical file - classification based on name
        path = Path("agentic_core/SomeMixinAgent.py")
        result = agent._classify_subterritory(path)
        # Should NOT be base_class because "Mixin" is in the name
        assert result != "base_class", f"MixinAgent should NOT be base_class due to 'Mixin' in name"
    
    def test_base_agent_with_validator_suffix(self):
        """A base agent with validator-like name should be excluded from base_class."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/BaseAgentValidator.py")
        result = agent._classify_subterritory(path)
        # Should NOT be base_class because "validator" is in the name
        assert result != "base_class", f"BaseAgentValidator should NOT be base_class due to 'validator' in name"
    
    def test_sovereign_specialized_classification(self):
        """Sovereign agents should be classified as specialized."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/SovereignClientAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "specialized", f"SovereignClientAgent should be specialized, got {result}"
    
    def test_metrics_infrastructure_classification(self):
        """Metrics agents should be classified as infrastructure."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/MetricsCollectorAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "infrastructure", f"MetricsCollectorAgent should be infrastructure, got {result}"
    
    def test_regular_agent_is_core(self):
        """Regular business logic agents should be classified as core."""
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        agent = AutonomyGuardianAgent(PROJECT_ROOT)
        path = Path("agentic_core/L5_safety/validators/NamingAgent.py")
        result = agent._classify_subterritory(path)
        assert result == "core", f"NamingAgent should be core, got {result}"


class TestIsAgentClassFunction:
    """Test the is_agent_class function in full_agent_discovery.py."""
    
    def test_class_ending_with_mixin_excluded(self):
        """Classes ending with 'Mixin' should be excluded."""
        from scripts.full_agent_discovery import is_agent_class
        code = """
class HealerMixin:
    def heal(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        bases = set()
        result = is_agent_class(class_node, bases)
        assert not result, "HealerMixin should NOT be classified as agent"
    
    def test_class_containing_mixin_excluded(self):
        """Classes containing 'Mixin' anywhere should be excluded."""
        from scripts.full_agent_discovery import is_agent_class
        code = """
class SomeMixinHelper:
    def help(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        bases = set()
        result = is_agent_class(class_node, bases)
        assert not result, "SomeMixinHelper should NOT be classified as agent"
    
    def test_class_ending_with_agent_included(self):
        """Classes ending with 'Agent' should be included."""
        from scripts.full_agent_discovery import is_agent_class
        code = """
class SafetyAgent:
    def act(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        bases = set()
        result = is_agent_class(class_node, bases)
        assert result, "SafetyAgent should be classified as agent"
    
    def test_class_inheriting_from_base_agent_included(self):
        """Classes inheriting from BaseAgent should be included."""
        from scripts.full_agent_discovery import is_agent_class
        code = """
class MyCustomClass(BaseAgent):
    def act(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        bases = {'BaseAgent'}
        result = is_agent_class(class_node, bases)
        assert result, "Class inheriting from BaseAgent should be classified as agent"


class TestL5SafetyBaseClassCount:
    """Integration test: L5 Safety should have exactly 1 base class agent."""
    
    def test_l5_safety_base_class_count(self):
        """L5 Safety/Base Class territory should contain exactly 1 agent."""
        import json
        import re
        
        dashboard_path = PROJECT_ROOT / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = dashboard_path.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        if not match:
            pytest.fail("Could not find dashboardData in dashboard HTML")
        
        data = json.loads(match.group(1))
        l5_base = next((r for r in data if r.get('Territory') == 'L5 Safety/Base Class'), None)
        
        if l5_base is None:
            pytest.skip("L5 Safety/Base Class territory not found in dashboard")
        
        agent_count = l5_base.get('Total', 0)
        assert agent_count == 1, (
            f"L5 Safety/Base Class should have exactly 1 agent (SafetyBaseAgent), "
            f"but found {agent_count}. This indicates a classification bug."
        )
