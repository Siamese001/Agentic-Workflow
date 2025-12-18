#!/usr/bin/env python3
"""
L6 Conversational Repair & Multi-Agent Debate Validation

This test validates:
1. Specialist agent role definitions
2. Debate loop functionality
3. Consensus building mechanism
4. Integration with TestPilot
5. Trigger logic for complex failures
"""

import asyncio
import json
import sys
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

from L3_orchestration.conversational_repair import (
    ConversationalRepair, get_conversational_repair,
    debate_complex_failure
)
from L3_orchestration.test_pilot import TestPilot


async def test_specialist_roles():
    """Test specialist agent role definitions."""
    print("=" * 80)
    print("SPECIALIST ROLES VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing specialist configuration")
    print("-" * 50)
    
    repair = ConversationalRepair(llm_client=None)
    
    # Check all specialists are defined
    expected_specialists = ["sherlock", "safety", "dependency", "architecture"]
    
    if set(repair.specialists.keys()) == set(expected_specialists):
        print("✅ All 4 specialists defined")
    else:
        print(f"❌ Missing specialists: {set(expected_specialists) - set(repair.specialists.keys())}")
        return False
    
    # Check specialist configurations
    for specialist_id, config in repair.specialists.items():
        if "name" in config and "role" in config and "prompt_template" in config:
            print(f"✅ {config['name']} properly configured")
        else:
            print(f"❌ {specialist_id} missing configuration")
            return False
    
    # Verify specific roles
    if repair.specialists["sherlock"]["role"] == "Root Cause Analysis":
        print("✅ Sherlock role correct")
    else:
        print("❌ Sherlock role incorrect")
        return False
    
    return True


async def test_debate_loop():
    """Test the debate loop mechanism."""
    print("\n" + "=" * 80)
    print("DEBATE LOOP VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing multi-round debate")
    print("-" * 50)
    
    repair = ConversationalRepair(llm_client=None)
    
    # Create test failure context
    failure_context = {
        "error": "ImportError: No module named 'pandas'",
        "file": "data_analysis.py",
        "code": "import pandas as pd\ndf = pd.DataFrame()",
        "traceback": "ImportError at line 1"
    }
    
    # Run debate
    result = await repair.debate_failure(failure_context)
    
    # Check structure
    if "success" in result and "debate_log" in result:
        print("✅ Debate result has correct structure")
    else:
        print("❌ Debate result missing required fields")
        return False
    
    # Check debate log
    debate_log = result["debate_log"]
    
    if len(debate_log) >= 8:  # 4 specialists x 2 rounds
        print(f"✅ Debate conducted with {len(debate_log)} entries")
    else:
        print(f"❌ Expected at least 8 debate entries, got {len(debate_log)}")
        return False
    
    # Check rounds
    round_1_entries = [e for e in debate_log if e["round"] == 1]
    round_2_entries = [e for e in debate_log if e["round"] == 2]
    
    if len(round_1_entries) == 4 and len(round_2_entries) == 4:
        print("✅ Both rounds completed with all specialists")
    else:
        print(f"❌ Round entries incorrect: R1={len(round_1_entries)}, R2={len(round_2_entries)}")
        return False
    
    # Check specialist participation
    specialists_in_round = set(e["specialist"] for e in round_1_entries)
    expected_specialists = {"Sherlock", "SafetyInspector", "DependencySentinel", "ArchitectureGovernor"}
    
    if specialists_in_round == expected_specialists:
        print("✅ All specialists participated")
    else:
        print(f"❌ Missing specialists: {expected_specialists - specialists_in_round}")
        return False
    
    return True


async def test_consensus_building():
    """Test consensus building mechanism."""
    print("\n" + "=" * 80)
    print("CONSENSUS BUILDING VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing consensus extraction")
    print("-" * 50)
    
    repair = ConversationalRepair(llm_client=None)
    
    # Test code block extraction
    response_with_code = """CONSENSUS: The fix requires adding the missing import.

CODE:
```python
import pandas as pd

def analyze_data():
    df = pd.DataFrame()
    return df
```
"""
    
    code = repair._extract_code_block(response_with_code)
    
    if code and "import pandas as pd" in code:
        print("✅ Code block extracted correctly")
    else:
        print("❌ Code block not extracted")
        return False
    
    # Test section extraction
    response_with_sections = """ANALYSIS: The error is due to missing import.

PROPOSAL: Add the import statement at the top of the file.
"""
    
    analysis = repair._extract_section(response_with_sections, "ANALYSIS")
    proposal = repair._extract_section(response_with_sections, "PROPOSAL")
    
    if analysis and "missing import" in analysis:
        print("✅ Analysis section extracted")
    else:
        print("❌ Analysis section not extracted")
        return False
    
    if proposal and "import statement" in proposal:
        print("✅ Proposal section extracted")
    else:
        print("❌ Proposal section not extracted")
        return False
    
    return True


async def test_specialist_queries():
    """Test individual specialist queries."""
    print("\n" + "=" * 80)
    print("SPECIALIST QUERIES VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing specialist responses")
    print("-" * 50)
    
    repair = ConversationalRepair(llm_client=None)
    
    failure_context = {
        "error": "SyntaxError: invalid syntax",
        "file": "broken.py",
        "code": "def broken_function(\n    print('test')",
        "traceback": "SyntaxError at line 2"
    }
    
    # Test each specialist
    for specialist_id in repair.specialists:
        response = await repair._query_specialist(
            specialist_id,
            failure_context,
            previous_responses=[]
        )
        
        if "analysis" in response and "proposal" in response:
            print(f"✅ {repair.specialists[specialist_id]['name']} responded")
        else:
            print(f"❌ {repair.specialists[specialist_id]['name']} response incomplete")
            return False
    
    return True


async def test_testpilot_integration():
    """Test integration with TestPilot."""
    print("\n" + "=" * 80)
    print("TESTPILOT INTEGRATION")
    print("=" * 80)
    
    print("\n1. Testing TestPilot with conversational repair")
    print("-" * 50)
    
    # Create TestPilot with repair enabled
    pilot = TestPilot(enable_conversational_repair=True)
    
    if pilot.enable_conversational_repair:
        print("✅ Conversational repair enabled in TestPilot")
    else:
        print("❌ Conversational repair not enabled")
        return False
    
    if hasattr(pilot, 'conversational_repair'):
        print("✅ ConversationalRepair instance available")
    else:
        print("❌ ConversationalRepair instance not found")
        return False
    
    # Test trigger logic
    test_results = {
        "standard_tests": {
            "passed": False,
            "failures": 3,  # Multiple failures to trigger repair
            "details": ["Complex error in multiple modules"]
        },
        "property_tests": {
            "passed": False,
            "violations": 2
        }
    }
    
    if pilot._needs_conversational_repair(test_results):
        print("✅ Trigger logic correctly identifies need for repair")
    else:
        print("❌ Trigger logic not working")
        return False
    
    # Test simple case (should not trigger)
    simple_results = {
        "standard_tests": {
            "passed": False,
            "failures": 1,
            "details": ["Simple test failure"]
        },
        "property_tests": {
            "passed": True,
            "violations": 0
        }
    }
    
    if not pilot._needs_conversational_repair(simple_results):
        print("✅ Simple failures don't trigger repair")
    else:
        print("❌ Simple failures incorrectly trigger repair")
        return False
    
    return True


async def test_mock_llm_responses():
    """Test mock LLM responses for validation."""
    print("\n" + "=" * 80)
    print("MOCK LLM RESPONSES")
    print("=" * 80)
    
    print("\n1. Testing fallback behavior without LLM")
    print("-" * 50)
    
    repair = ConversationalRepair(llm_client=None)
    
    # Test LLM query fallback
    response = await repair._query_llm("Test prompt")
    
    if "Mock response" in response:
        print("✅ Mock LLM response working")
    else:
        print("❌ Mock LLM response not working")
        return False
    
    # Test full debate with mock responses
    failure_context = {
        "error": "Test error",
        "file": "test.py",
        "code": "print('test')",
        "traceback": "Error at line 1"
    }
    
    result = await repair.debate_failure(failure_context)
    
    if result["success"] and result["consensus_code"]:
        print("✅ Full debate works with mock LLM")
    else:
        print("⚠️  Full debate limited by mock responses")
    
    return True


async def test_global_functions():
    """Test global convenience functions."""
    print("\n" + "=" * 80)
    print("GLOBAL FUNCTIONS VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing convenience API")
    print("-" * 50)
    
    # Test global instance
    global_repair = get_conversational_repair()
    
    if isinstance(global_repair, ConversationalRepair):
        print("✅ Global ConversationalRepair accessible")
    else:
        print("❌ Global instance not accessible")
        return False
    
    # Test debate function
    failure_context = {
        "error": "Global test error",
        "file": "global_test.py",
        "code": "# Test code",
        "traceback": "Test traceback"
    }
    
    result = await debate_complex_failure(failure_context)
    
    if "debate_log" in result:
        print("✅ Global debate function works")
    else:
        print("❌ Global debate function failed")
        return False
    
    return True


async def test_debate_log_structure():
    """Test debate log structure and content."""
    print("\n" + "=" * 80)
    print("DEBATE LOG STRUCTURE")
    print("=" * 80)
    
    print("\n1. Testing log entry structure")
    print("-" * 50)
    
    repair = ConversationalRepair(llm_client=None)
    
    failure_context = {
        "error": "Structure test error",
        "file": "structure.py",
        "code": "def test(): pass",
        "traceback": "Test traceback"
    }
    
    result = await repair.debate_failure(failure_context)
    debate_log = result["debate_log"]
    
    # Check first entry structure
    first_entry = debate_log[0]
    
    required_fields = ["round", "specialist", "analysis", "proposal"]
    
    if all(field in first_entry for field in required_fields):
        print("✅ Debate log entries have required fields")
    else:
        print(f"❌ Missing fields: {required_fields - set(first_entry.keys())}")
        return False
    
    # Check round progression
    rounds = set(entry["round"] for entry in debate_log)
    
    if rounds == {1, 2}:
        print("✅ Correct round progression")
    else:
        print(f"❌ Incorrect rounds: {rounds}")
        return False
    
    # Check specialist responses are tracked
    if "specialist_responses" in result:
        print("✅ Specialist responses tracked")
    else:
        print("❌ Specialist responses not tracked")
        return False
    
    return True


async def run_conversational_repair_validation():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("L6 CONVERSATIONAL REPAIR VALIDATION SUITE")
    print("=" * 80)
    print("\nTesting multi-agent debate and consensus building")
    
    results = {}
    
    # Run all tests
    results["specialist_roles"] = await test_specialist_roles()
    results["debate_loop"] = await test_debate_loop()
    results["consensus"] = await test_consensus_building()
    results["specialist_queries"] = await test_specialist_queries()
    results["testpilot_integration"] = await test_testpilot_integration()
    results["mock_llm"] = await test_mock_llm_responses()
    results["global_functions"] = await test_global_functions()
    results["log_structure"] = await test_debate_log_structure()
    
    # Generate report
    print("\n" + "=" * 80)
    print("CONVERSATIONAL REPAIR VALIDATION REPORT")
    print("=" * 80)
    
    print("\nTest Results:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All L6 Conversational Repair components validated!")
        print("The system provides:")
        print("  - 4 specialist agents with distinct roles")
        print("  - Multi-round debate mechanism")
        print("  - Consensus building from specialist inputs")
        print("  - Integration with TestPilot for complex failures")
        print("  - Proper trigger logic for activation")
        print("  - Detailed debate logging for audit")
        print("\n📝 Note: Install openai package for LLM integration:")
        print("   pip install openai")
        print("   Set OPENAI_API_KEY environment variable")
    else:
        print("\n⚠️  Some components need attention")
        print("Check the logs above for details")
    
    return all_passed


if __name__ == "__main__":
    import sys
    asyncio.run(run_conversational_repair_validation())
