"""
Layer Integrity Tests - Phase 6 Compliance Verification

Tests to ensure prompt_governance maintains Anti-Gravity compliance
with zero upward import violations to higher layers.
"""

import pytest
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_governance_gravity_compliance():
    """
    Test that prompt_governance directory has ZERO upward import violations.
    MANDATORY: 100% pass required for architectural convergence.
    """
    # Import the enforcement function
    from agentic_core.prompt_governance.scripts.enforce_layer_boundaries import enforce_layer_boundaries
    
    governance_path = Path("agentic_core/prompt_governance")
    
    # Run the boundary enforcement
    violations = enforce_layer_boundaries(governance_path)
    
    # Filter for upward imports specifically (violations that import from higher layers)
    upward_violations = []
    for violation in violations:
        if violation.get('violation_type') == 'UPWARD_IMPORT':
            upward_violations.append(violation)
    
    # Assert zero upward violations for Anti-Gravity compliance
    assert len(upward_violations) == 0, f"""
Anti-Gravity Violation Detected: {len(upward_violations)} violations found
Violations: {upward_violations}
Phase 6 architectural compliance FAILED!
"""

def test_registry_initialization_no_l5():
    """
    Verify PromptRegistryAgent can initialize without L5 safety modules present.
    Ensures decoupling is successful and dependency injection works.
    """
    from agentic_core.prompt_governance.PromptRegistryAgent import PromptRegistryAgent
    
    # Initialization should succeed without raising ImportError for LocationAgent
    try:
        agent = PromptRegistryAgent()
        assert agent is not None
        # Verify default validator is used
        assert hasattr(agent, 'validator')
        assert agent.validator.__name__ == "_default_placement_validator"
    except ImportError as e:
        pytest.fail(f"PromptRegistryAgent initialization failed with ImportError: {e}")

def test_registry_injection_works():
    """Verify we can still inject high-level validators from the top down."""
    from agentic_core.prompt_governance.PromptRegistryAgent import PromptRegistryAgent
    
    def custom_validator(path, root):
        return False, "Injected Failure Test"
    
    try:
        # Test with injected validator
        agent = PromptRegistryAgent(placement_validator=custom_validator)
        assert agent.validator == custom_validator
        
        # Test the injected validator works
        result = agent.validator(Path.cwd(), Path.cwd())
        assert result == (False, "Injected Failure Test")
    except Exception as e:
        pytest.fail(f"Dependency injection test failed: {e}")

def test_dashboard_suite_no_l5_imports():
    """
    Verify DashboardTestSuite can run without L5 imports.
    Tests mock implementation works correctly.
    """
    from agentic_core.prompt_governance.DashboardTestSuite import MockLocationValidator
    
    # Test mock validator works
    mock_validator = MockLocationValidator()
    result = mock_validator.validate_file_location(Path("test"))
    assert result == (True, "Mock Pass")
    
    # Test DashboardTestSuite can be imported without L5 dependencies
    try:
        from agentic_core.prompt_governance.DashboardTestSuite import DashboardTestSuite
        suite = DashboardTestSuite()
        assert suite is not None
        assert hasattr(suite, 'passed')
        assert hasattr(suite, 'failed')
    except ImportError as e:
        pytest.fail(f"DashboardTestSuite import failed: {e}")

def test_architectural_layer_boundaries():
    """
    Comprehensive test to ensure no upward imports exist anywhere in prompt_governance.
    This is the ultimate Anti-Gravity compliance test.
    """
    governance_path = Path("agentic_core/prompt_governance")
    
    # Forbidden patterns (upward imports)
    forbidden_patterns = [
        "from agentic_core.L1_cognition",
        "from agentic_core.L2_resources", 
        "from agentic_core.L3_orchestration",
        "from agentic_core.L4_coordination",
        "from agentic_core.L5_safety",
        "from agentic_core.L6_observability",
        "import agentic_core.L1_cognition",
        "import agentic_core.L2_resources",
        "import agentic_core.L3_orchestration", 
        "import agentic_core.L4_coordination",
        "import agentic_core.L5_safety",
        "import agentic_core.L6_observability"
    ]
    
    violations_found = []
    
    # Scan all Python files
    for py_file in governance_path.rglob("*.py"):
        if py_file.is_file():
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in forbidden_patterns:
                    if pattern in content:
                        violations_found.append({
                            'file': str(py_file.relative_to(project_root)),
                            'pattern': pattern
                        })
            except Exception as e:
                pytest.fail(f"Failed to read {py_file}: {e}")
    
    assert len(violations_found) == 0, f"""
Anti-Gravity Violations Found: {len(violations_found)}
{violations_found}
Phase 6 architectural compliance FAILED!
"""

if __name__ == "__main__":
    # Run tests directly
    test_governance_gravity_compliance()
    test_registry_initialization_no_l5()
    test_registry_injection_works()
    test_dashboard_suite_no_l5_imports()
    test_architectural_layer_boundaries()
    print("✅ All Phase 6 architectural compliance tests PASSED!")
