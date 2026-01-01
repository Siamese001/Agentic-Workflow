"""Test the ultra-hardened TestSovereigntyAgent."""
import asyncio
from agentic_core.L5_safety.validators.TestSovereigntyAgent import TestSovereigntyAgent


async def main():
    print("=" * 70)
    print("TESTING ULTRA TEST SOVEREIGNTY AGENT")
    print("=" * 70)
    
    agent = TestSovereigntyAgent()
    
    # Test basic execution
    print("\n1. Testing basic execution...")
    result = await agent.execute({"type": "basic"})
    print(f"   Passed: {result['passed']}")
    print(f"   Coverage: {result['coverage']}%")
    print(f"   Tests: {len(result['tests'])} run")
    
    # Show test results
    for test in result['tests']:
        status = "✓" if test.get('passed', False) else "✗"
        print(f"   {status} {test['name']}")
    
    print("\n2. Testing with artifact...")
    artifact = """
def test_basic():
    assert True

def test_addition():
    assert 1 + 1 == 2
"""
    result = await agent.execute({
        "type": "basic",
        "artifact": artifact
    })
    print(f"   Passed: {result['passed']}")
    
    print("\n" + "=" * 70)
    print("ULTRA TEST SOVEREIGNTY AGENT VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
