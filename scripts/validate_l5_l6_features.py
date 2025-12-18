#!/usr/bin/env python3
"""
L5/L6 Features Validation Suite

Runs all validation tests for the implemented features:
- L6 Deterministic Pre-Flight Sanitation
- L5 Hot-Brain Resilience (Redis)
- L5 Learning Loop (Pinecone)
- L6 Conversational Repair (Multi-Agent Debate)
"""

import asyncio
import sys
import time
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))


async def run_test_suite(name: str, test_file: str) -> bool:
    """
    Run a single test suite.
    
    Args:
        name: Name of the test suite
        test_file: Path to the test file
        
    Returns:
        True if all tests passed
    """
    print(f"\n{'='*80}")
    print(f"RUNNING: {name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Import and run the test
        spec = __import__(f"scripts.{test_file}", fromlist=["run_validation"])
        
        if hasattr(spec, "run_validation"):
            passed = await spec.run_validation()
        elif hasattr(spec, "run_sanitization_and_redis_validation"):
            passed = await spec.run_sanitization_and_redis_validation()
        elif hasattr(spec, "run_learning_loop_validation"):
            passed = await spec.run_learning_loop_validation()
        elif hasattr(spec, "run_conversational_repair_validation"):
            passed = await spec.run_conversational_repair_validation()
        else:
            print(f"❌ No validation function found in {test_file}")
            return False
        
        duration = time.time() - start_time
        
        if passed:
            print(f"\n✅ {name} - PASSED ({duration:.1f}s)")
        else:
            print(f"\n❌ {name} - FAILED ({duration:.1f}s)")
        
        return passed
        
    except Exception as e:
        print(f"\n❌ {name} - ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all validation suites."""
    print("\n" + "="*80)
    print("L5/L6 FEATURES VALIDATION SUITE")
    print("="*80)
    print("\nValidating all implemented features with fallback support")
    
    # Define test suites
    test_suites = [
        ("L6 Deterministic Sanitation & L5 Hot-Brain Resilience", "test_sanitization_redis"),
        ("L5 Learning Loop & Pinecone Memory", "test_learning_loop"),
        ("L6 Conversational Repair & Multi-Agent Debate", "test_conversational_repair")
    ]
    
    # Run all suites
    results = {}
    total_start = time.time()
    
    for name, test_file in test_suites:
        results[name] = await run_test_suite(name, test_file)
    
    total_duration = time.time() - total_start
    
    # Generate final report
    print("\n" + "="*80)
    print("FINAL VALIDATION REPORT")
    print("="*80)
    
    print("\nFeature Status:")
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nTotal Duration: {total_duration:.1f} seconds")
    
    if all_passed:
        print("\n🎉 ALL FEATURES VALIDATED SUCCESSFULLY!")
        print("\nThe Agentic-Workflow system now includes:")
        print("\nL6 Features:")
        print("  ✅ Deterministic Pre-Flight Sanitation")
        print("    - isort and autopep8 formatting")
        print("    - Markdown artifact scrubbing")
        print("    - AST syntax validation")
        print("    - Root directory hygiene enforcement")
        print("  ✅ Conversational Repair")
        print("    - 4 specialist agents (Sherlock, SafetyInspector, DependencySentinel, ArchitectureGovernor)")
        print("    - Multi-round debate mechanism")
        print("    - Consensus building for complex failures")
        print("\nL5 Features:")
        print("  ✅ Hot-Brain Resilience")
        print("    - Redis distributed locking")
        print("    - Redis hot caching with TTL")
        print("    - Local fallback when Redis unavailable")
        print("  ✅ Learning Loop")
        print("    - ReflectionAgent for trace analysis")
        print("    - Pinecone vector storage for embeddings")
        print("    - Cross-cycle recall via semantic search")
        print("    - Self-critique with CONVERGE_AND_COMMIT/ROLLBACK")
        
        print("\n📦 Setup Requirements:")
        print("  pip install isort autopep8          # For deterministic sanitation")
        print("  pip install redis                   # For distributed systems")
        print("  pip install pinecone-client         # For vector storage")
        print("  pip install google-generativeai     # For embeddings")
        print("  pip install openai                  # For conversational repair")
        print("\nEnvironment Variables:")
        print("  export GOOGLE_API_KEY=your_key      # For embeddings")
        print("  export OPENAI_API_KEY=your_key      # For LLM debate")
        print("  export REDIS_URL=redis://localhost:6379  # For Redis")
        print("  export PINECONE_API_KEY=your_key    # For Pinecone")
        
        print("\n🚀 All features gracefully degrade when services are unavailable!")
        
    else:
        print("\n⚠️  SOME VALIDATIONS FAILED")
        print("Please check the logs above for details")
        print("\n💡 Tip: Features work with fallbacks even without external services")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
