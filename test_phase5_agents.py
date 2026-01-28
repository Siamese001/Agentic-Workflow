#!/usr/bin/env python3
"""Quick test script for Phase 5 Cognitive Sovereignty agents."""

from pathlib import Path
from agentic_core.L5_safety.policy_engine.ComplexityAnalyzerAgent import (
    ComplexityAnalyzerAgent,
    ComplexityConfig,
)
from agentic_core.L5_safety.policy_engine.CodeDetectorAgent import (
    CodeDetectorAgent,
    DetectorConfig,
)

def test_complexity_analyzer():
    """Test ComplexityAnalyzerAgent with @standard_heal decorator."""
    print("\n=== Testing ComplexityAnalyzerAgent ===")
    config = ComplexityConfig(project_root=Path("."), max_cyclomatic_complexity=10)
    agent = ComplexityAnalyzerAgent(config=config)
    
    result = agent.heal_repository(dry_run=True)
    
    print(f"✅ violations_found: {result.get('violations_found')}")
    print(f"✅ violations_fixed: {result.get('violations_fixed')}")
    print(f"✅ status: {result.get('status')}")
    print(f"✅ execution_time_ms: {result.get('execution_time_ms'):.2f}")
    
    # Verify canonical schema compliance
    assert "violations_found" in result
    assert "violations_fixed" in result
    assert "status" in result
    assert "execution_time_ms" in result
    print("✅ Canonical schema compliance verified")

def test_code_detector():
    """Test CodeDetectorAgent with @standard_heal decorator."""
    print("\n=== Testing CodeDetectorAgent ===")
    config = DetectorConfig(project_root=Path("."))
    agent = CodeDetectorAgent(config=config)
    
    result = agent.heal_repository(dry_run=True)
    
    print(f"✅ violations_found: {result.get('violations_found')}")
    print(f"✅ violations_fixed: {result.get('violations_fixed')}")
    print(f"✅ status: {result.get('status')}")
    print(f"✅ execution_time_ms: {result.get('execution_time_ms'):.2f}")
    
    # Verify canonical schema compliance
    assert "violations_found" in result
    assert "violations_fixed" in result
    assert "status" in result
    assert "execution_time_ms" in result
    print("✅ Canonical schema compliance verified")

if __name__ == "__main__":
    test_complexity_analyzer()
    test_code_detector()
    print("\n✅ All Phase 5 Cognitive Sovereignty tests passed!")
