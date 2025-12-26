"""
Permanent SSOT Smoke Test.
Session 6 - Runtime Integrity Validation
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agentic_core.schemas.models.core_contracts import (
    RetryPolicy, HopSpec, GoldenOutput, MicroStage, HopState
)

def test_ssot_integrity():
    """Verify SSOT models have correct field names and no shadow duplicates."""
    
    # 1. Verify Field Names (No Underscores)
    rp = RetryPolicy(max_retries=3)
    assert rp.max_retries == 3, "RetryPolicy.max_retries should be accessible"
    assert not hasattr(rp, "_max_retries"), "RetryPolicy should not have _max_retries"

    # 2. Verify Dataclass vs Pydantic Resolution
    # RetryPolicy should be a Pydantic model now, ensuring the dataclass duplicate is gone
    assert hasattr(rp, "model_dump") or hasattr(rp, "dict"), "RetryPolicy should be Pydantic BaseModel"

    # 3. Verify HopSpec uses correct field names
    hop = HopSpec(
        id="test-hop",
        script="test.py",
        description="Test hop",
        inputs=[],
        outputs=[],
        retry_policy=rp,
        extra_args=[]
    )
    assert hop.id == "test-hop", "HopSpec.id should be accessible"
    assert not hasattr(hop, "_id"), "HopSpec should not have _id"
    
    # 4. Verify GoldenOutput uses correct field names
    output = GoldenOutput(
        case_id="test-case",
        produced_keypoints=["key1"],
        correctness_map={"key1": True},
        safety_decisions={},
        metacognition_summary={},
        final_verdict="pass"
    )
    assert output.case_id == "test-case", "GoldenOutput.case_id should be accessible"
    assert not hasattr(output, "_case_id"), "GoldenOutput should not have _case_id"

    print("✅ SSOT Runtime Integrity Verified")
    return True

def test_no_duplicate_classes():
    """Verify no duplicate class definitions exist."""
    
    # RetryPolicy should only exist once as a Pydantic BaseModel
    # If a duplicate dataclass existed, it would override the BaseModel
    rp = RetryPolicy()
    
    # Pydantic models have model_dump or dict methods
    assert hasattr(rp, "model_dump") or hasattr(rp, "dict"), \
        "RetryPolicy should be Pydantic BaseModel (no dataclass duplicate)"
    
    # Pydantic models have Field defaults
    assert rp.max_retries == 3, "Default max_retries should be 3"
    assert rp.retry_delay == 1.0, "Default retry_delay should be 1.0"
    assert rp.exponential_backoff is True, "Default exponential_backoff should be True"
    
    print("✅ No Duplicate Class Definitions Detected")
    return True

def test_field_accessibility():
    """Verify all fixed fields are accessible without underscores."""
    
    from agentic_core.schemas.models.core_contracts import (
        MicroCheckpoint, StageTransition, InjectionPattern, InjectionScope, InjectionType,
        SafetyProfile, SimScenario, Hypothesis, GoldenCase, BudgetProfile
    )
    
    # Test MicroCheckpoint
    checkpoint = MicroCheckpoint(
        hop_id="test",
        stage=MicroStage.THINK,
        timestamp=123.0,
        state=HopState.RUNNING
    )
    assert checkpoint.hop_id == "test"
    assert not hasattr(checkpoint, "_hop_id")
    
    # Test StageTransition
    transition = StageTransition(
        to_stage=MicroStage.ACT,
        timestamp=123.0
    )
    assert transition.to_stage == MicroStage.ACT
    assert not hasattr(transition, "_to_stage")
    
    # Test InjectionPattern
    pattern = InjectionPattern(
        id="test",
        name="Test",
        type=InjectionType.SYSTEM,
        description="Test pattern",
        template="Test"
    )
    assert pattern.id == "test"
    assert not hasattr(pattern, "_id")
    
    # Test SafetyProfile
    profile = SafetyProfile()
    assert profile.safety_tier == "standard"
    assert not hasattr(profile, "_safety_tier")
    
    # Test SimScenario
    scenario = SimScenario(
        id="test",
        description="Test",
        initial_context={},
        execution_profile_name="default",
        run_count=1
    )
    assert scenario.id == "test"
    assert not hasattr(scenario, "_id")
    
    # Test Hypothesis
    hyp = Hypothesis(
        id="test",
        agent_id="agent1",
        content="Test hypothesis"
    )
    assert hyp.id == "test"
    assert not hasattr(hyp, "_id")
    
    # Test GoldenCase
    case = GoldenCase(
        id="test",
        input_text="Test",
        agent_sequence=["agent1"],
        expected_keypoints=["key1"],
        correctness_criteria={}
    )
    assert case.agent_sequence == ["agent1"]
    assert not hasattr(case, "_agent_sequence")
    
    # Test BudgetProfile
    budget = BudgetProfile()
    assert budget.max_cost_usd == 0.10
    assert not hasattr(budget, "_max_cost_usd")
    
    print("✅ All Field Accessibility Tests Passed")
    return True

if __name__ == "__main__":
    try:
        test_ssot_integrity()
        test_no_duplicate_classes()
        test_field_accessibility()
        print("\n" + "="*70)
        print("✅ ALL SOVEREIGN SMOKE TESTS PASSED")
        print("="*70)
    except AssertionError as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
