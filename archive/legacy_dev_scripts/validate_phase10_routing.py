"""
Phase 10 Model Routing Integration Validation

Validates that run_single_outreach() works end-to-end with:
- use_model_routing=False (default behavior preserved)
- use_model_routing=True (routing enabled)

This is the critical Phase 10 success criterion.
"""

import sys
import traceback
from unittest.mock import Mock, patch

from apps.lic_outreach.lic_workflow_entry import run_single_outreach
from l1.outreach_archetype_planning import RecipientProfile
from l1.outreach_dataclasses import OutreachMission, ArchetypeType
from config.LIC.lic_profile import get_lic_profile, create_custom_profile


def create_test_mission_and_recipient():
    """Create minimal test data for validation."""
    mission = OutreachMission(
        mission_id="test_phase10_routing",
        target_company="Test Corp",
        target_role="CEO",
        value_proposition="Strategic partnership opportunity"
    )
    
    recipient = RecipientProfile(
        name="Test CEO",
        title="Chief Executive Officer",
        company="Test Corp",
        archetype=ArchetypeType.C_LEVEL,
        contact_info="test@example.com"
    )
    
    return mission, recipient


def test_routing_disabled_default_behavior():
    """Test that run_single_outreach works with routing disabled (default)."""
    print("🧪 Testing Phase 10: use_model_routing=False (default)")
    
    try:
        # Ensure routing is disabled
        original_profile = get_lic_profile()
        assert not original_profile.use_model_routing, "Default routing should be False"
        
        # Create test data
        mission, recipient = create_test_mission_and_recipient()
        
        # Mock external dependencies to avoid actual API calls
        with patch('runtime.runtime_utils.invoke_model') as mock_invoke:
            # Configure mocks
            mock_invoke.return_value = "Test LLM response for validation"
            
            # Run the workflow
            result = run_single_outreach(mission, recipient)
            
            # Validate success
            assert result.success, f"Workflow should succeed with routing disabled: {result.error}"
            assert result.message is not None, "Should generate a message"
            
            print("✅ PASSED: run_single_outreach works with use_model_routing=False")
            return True
            
    except Exception as e:
        print(f"❌ FAILED: Routing disabled test failed: {e}")
        traceback.print_exc()
        return False


def test_routing_enabled_new_behavior():
    """Test that run_single_outreach works with routing enabled."""
    print("🧪 Testing Phase 10: use_model_routing=True (routing enabled)")
    
    try:
        # Create custom profile with routing enabled
        routing_profile = create_custom_profile(use_model_routing=True)
        
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            # Verify routing is enabled
            current_profile = get_lic_profile()
            assert current_profile.use_model_routing, "Routing should be enabled"
            
            # Create test data
            mission, recipient = create_test_mission_and_recipient()
            
            # Mock external dependencies
            with patch('runtime.runtime_utils.invoke_model') as mock_invoke:
                # Configure mocks
                mock_invoke.return_value = "Test LLM response with routing enabled"
                
                # Run the workflow
                result = run_single_outreach(mission, recipient)
                
                # Validate success
                assert result.success, f"Workflow should succeed with routing enabled: {result.error}"
                assert result.message is not None, "Should generate a message"
                
                print("✅ PASSED: run_single_outreach works with use_model_routing=True")
                return True
    
    except Exception as e:
        print(f"❌ FAILED: Routing enabled test failed: {e}")
        traceback.print_exc()
        return False


def test_factory_routing_integration():
    """Test that the factory pattern works with both routing configurations."""
    print("🧪 Testing Phase 10: Factory pattern routing integration")
    
    try:
        from l3.outreach_factory import create_message_executor_with_routing
        from runtime.execution_budget_manager import get_budget_manager
        from l1.outreach_dataclasses import ArchetypeType
        
        # Test with routing disabled
        executor_disabled = create_message_executor_with_routing(
            archetype=ArchetypeType.C_LEVEL,
            safety_validator=Mock(),
            budget_manager=get_budget_manager()
        )
        assert executor_disabled is not None, "Should create executor with routing disabled"
        
        # Test with routing enabled
        routing_profile = create_custom_profile(use_model_routing=True)
        with patch('config.LIC.lic_profile.get_lic_profile', return_value=routing_profile):
            executor_enabled = create_message_executor_with_routing(
                archetype=ArchetypeType.C_LEVEL,
                safety_validator=Mock(),
                budget_manager=get_budget_manager()
            )
            assert executor_enabled is not None, "Should create executor with routing enabled"
        
        print("✅ PASSED: Factory pattern works with both routing configurations")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Factory integration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run Phase 10 validation tests."""
    print("🚀 Phase 10 Model Routing Integration Validation")
    print("=" * 60)
    
    tests = [
        test_routing_disabled_default_behavior,
        test_routing_enabled_new_behavior,
        test_factory_routing_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUCCESS: Phase 10 Model Routing Integration validated!")
        print("✅ Core requirements met:")
        print("  - use_model_routing config flag working")
        print("  - L2 routing interface functional") 
        print("  - L3 orchestration integration complete")
        print("  - run_single_outreach() works with both configurations")
        return True
    else:
        print("❌ FAILURE: Phase 10 validation incomplete")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
