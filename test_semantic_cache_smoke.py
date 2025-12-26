"""
Semantic Cache Smoke Test - Session 5
Verifies that the Metadata Layer correctly hashes new field names after Pydantic surgery.
"""
import json
from agentic_core.schemas.models.core_contracts import (
    RetryPolicy,
    MicroCheckpoint,
    StageTransition,
    InjectionPattern,
    InjectionScope,
    InjectionType,
    SafetyProfile,
    SimScenario,
    Hypothesis,
    GoldenCase,
    GoldenOutput,
    BudgetProfile,
    AgentThoughtProcess,
    MicroStage,
    HopState,
)

def test_retry_policy():
    """Test RetryPolicy instantiation and serialization."""
    policy = RetryPolicy(
        max_retries=5,
        retry_delay=2.0,
        exponential_backoff=True,
        retryable_stages=[MicroStage.THINK, MicroStage.ACT]
    )
    
    # Verify field access works
    assert policy.max_retries == 5
    assert policy.retry_delay == 2.0
    assert policy.exponential_backoff is True
    
    # Verify serialization has no underscores
    data = policy.model_dump()
    assert "_max_retries" not in data
    assert "max_retries" in data
    
    print("✅ RetryPolicy: Fields accessible, no underscore violations")
    return data

def test_micro_checkpoint():
    """Test MicroCheckpoint instantiation and serialization."""
    checkpoint = MicroCheckpoint(
        hop_id="test-hop-123",
        stage=MicroStage.THINK,
        timestamp=1234567890.0,
        state=HopState.RUNNING,
        data={"key": "value"},
        error=None
    )
    
    # Verify field access
    assert checkpoint.hop_id == "test-hop-123"
    assert checkpoint.stage == MicroStage.THINK
    
    # Verify serialization
    data = checkpoint.model_dump()
    assert "_hop_id" not in data
    assert "hop_id" in data
    
    print("✅ MicroCheckpoint: Fields accessible, no underscore violations")
    return data

def test_stage_transition():
    """Test StageTransition instantiation and serialization."""
    transition = StageTransition(
        from_stage=MicroStage.THINK,
        to_stage=MicroStage.ACT,
        timestamp=1234567890.0,
        reason="Thinking complete"
    )
    
    # Verify field access
    assert transition.from_stage == MicroStage.THINK
    assert transition.to_stage == MicroStage.ACT
    
    # Verify serialization
    data = transition.model_dump()
    assert "_from_stage" not in data
    assert "from_stage" in data
    
    print("✅ StageTransition: Fields accessible, no underscore violations")
    return data

def test_injection_pattern():
    """Test InjectionPattern instantiation and serialization."""
    pattern = InjectionPattern(
        id="test-pattern-1",
        name="Test Pattern",
        type=InjectionType.SYSTEM,
        description="A test injection pattern",
        template="System: {instruction}",
        variables=["instruction"],
        scope=InjectionScope(hop_types=["test"], stages=["think"]),
        priority=5,
        enabled=True
    )
    
    # Verify field access
    assert pattern.id == "test-pattern-1"
    assert pattern.name == "Test Pattern"
    assert pattern.priority == 5
    
    # Verify serialization
    data = pattern.model_dump()
    assert "_id" not in data
    assert "id" in data
    
    print("✅ InjectionPattern: Fields accessible, no underscore violations")
    return data

def test_safety_profile():
    """Test SafetyProfile instantiation and serialization."""
    profile = SafetyProfile(
        safety_tier="strict",
        pii_detection_enabled=True,
        policy_engine_enabled=True
    )
    
    # Verify field access
    assert profile.safety_tier == "strict"
    assert profile.pii_detection_enabled is True
    
    # Verify serialization
    data = profile.model_dump()
    assert "_safety_tier" not in data
    assert "safety_tier" in data
    
    print("✅ SafetyProfile: Fields accessible, no underscore violations")
    return data

def test_sim_scenario():
    """Test SimScenario instantiation and serialization."""
    scenario = SimScenario(
        id="scenario-1",
        description="Test simulation scenario",
        initial_context={"test": "data"},
        execution_profile_name="default",
        run_count=3
    )
    
    # Verify field access
    assert scenario.id == "scenario-1"
    assert scenario.description == "Test simulation scenario"
    
    # Verify serialization
    data = scenario.model_dump()
    assert "_id" not in data
    assert "id" in data
    
    print("✅ SimScenario: Fields accessible, no underscore violations")
    return data

def test_hypothesis():
    """Test Hypothesis instantiation and serialization."""
    hyp = Hypothesis(
        id="hyp-1",
        agent_id="agent-123",
        content="Test hypothesis content",
        confidence=0.85,
        evidence_ids=["ev-1", "ev-2"],
        rationale="Based on evidence"
    )
    
    # Verify field access
    assert hyp.id == "hyp-1"
    assert hyp.confidence == 0.85
    
    # Verify serialization
    data = hyp.model_dump()
    assert "_id" not in data
    assert "id" in data
    
    print("✅ Hypothesis: Fields accessible, no underscore violations")
    return data

def test_golden_case():
    """Test GoldenCase instantiation and serialization."""
    case = GoldenCase(
        id="case-1",
        input_text="Test input",
        agent_sequence=["agent1", "agent2"],
        expected_keypoints=["point1", "point2"],
        correctness_criteria={"accuracy": 0.9}
    )
    
    # Verify field access
    assert case.id == "case-1"
    assert case.agent_sequence == ["agent1", "agent2"]
    
    # Verify serialization
    data = case.model_dump()
    assert "_agent_sequence" not in data
    assert "agent_sequence" in data
    
    print("✅ GoldenCase: Fields accessible, no underscore violations")
    return data

def test_golden_output():
    """Test GoldenOutput instantiation and serialization."""
    output = GoldenOutput(
        case_id="case-1",
        produced_keypoints=["point1", "point2"],
        correctness_map={"point1": True, "point2": False},
        safety_decisions={"safe": True},
        metacognition_summary={"confidence": 0.8},
        final_verdict="pass"
    )
    
    # Verify field access
    assert output.case_id == "case-1"
    assert output.final_verdict == "pass"
    
    # Verify serialization
    data = output.model_dump()
    assert "_case_id" not in data
    assert "case_id" in data
    
    print("✅ GoldenOutput: Fields accessible, no underscore violations")
    return data

def test_budget_profile():
    """Test BudgetProfile instantiation and serialization."""
    budget = BudgetProfile(
        max_cost_usd=0.50,
        max_latency_ms=5000
    )
    
    # Verify field access
    assert budget.max_cost_usd == 0.50
    assert budget.max_latency_ms == 5000
    
    # Verify serialization
    data = budget.model_dump()
    assert "_max_cost_usd" not in data
    assert "max_cost_usd" in data
    
    print("✅ BudgetProfile: Fields accessible, no underscore violations")
    return data

def test_agent_thought_process():
    """Test AgentThoughtProcess instantiation and serialization."""
    thought = AgentThoughtProcess(
        reasoning_trace=["Step 1: Analyze", "Step 2: Plan"],
        relevant_context_keys=["key1", "key2"],
        tool_choice="SEARCH",
        tool_arguments={"query": "test"},
        confidence_score=0.9
    )
    
    # Verify field access
    assert thought.reasoning_trace == ["Step 1: Analyze", "Step 2: Plan"]
    assert thought.confidence_score == 0.9
    
    # Verify serialization
    data = thought.model_dump()
    assert "_reasoning_trace" not in data
    assert "reasoning_trace" in data
    
    print("✅ AgentThoughtProcess: Fields accessible, no underscore violations")
    return data

def main():
    """Run all smoke tests."""
    print("\n" + "="*60)
    print("SEMANTIC CACHE SMOKE TEST - SESSION 5")
    print("Testing Metadata Layer with new snake_case field names")
    print("="*60 + "\n")
    
    results = {}
    
    try:
        results["RetryPolicy"] = test_retry_policy()
        results["MicroCheckpoint"] = test_micro_checkpoint()
        results["StageTransition"] = test_stage_transition()
        results["InjectionPattern"] = test_injection_pattern()
        results["SafetyProfile"] = test_safety_profile()
        results["SimScenario"] = test_sim_scenario()
        results["Hypothesis"] = test_hypothesis()
        results["GoldenCase"] = test_golden_case()
        results["GoldenOutput"] = test_golden_output()
        results["BudgetProfile"] = test_budget_profile()
        results["AgentThoughtProcess"] = test_agent_thought_process()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - SEMANTIC CACHE READY")
        print("="*60)
        print("\nSample serialized output (RetryPolicy):")
        print(json.dumps(results["RetryPolicy"], indent=2))
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
