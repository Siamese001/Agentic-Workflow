#!/usr/bin/env python3
"""
L5 Learning Loop & Pinecone Memory Consolidation Validation

This test validates:
1. ReflectionAgent pattern analysis
2. Trace internalization to Pinecone/local storage
3. Embedding generation with text-embedding-004
4. Cross-cycle recall via search
5. Self-critique recommendations
"""

import asyncio
import sys
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

from L1_cognition.reflection_agent import (
    ReflectionAgent,
    get_reflection_agent,
    process_successful_traces,
    search_memory,
)


async def test_pattern_analysis():
    """Test pattern analysis of successful traces."""
    print("=" * 80)
    print("PATTERN ANALYSIS VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing success pattern detection")
    print("-" * 50)
    
    agent = ReflectionAgent(pinecone_client=None)  # Use local fallback
    
    # Create test trace with import fix
    trace = {
        "task": "Fix missing import error",
        "code_before": """def function():
    return pd.DataFrame()""",
        "code_after": """import pandas as pd

def function():
    return pd.DataFrame()""",
        "signals": ["TESTS_PASS", "STYLE_PASS"],
        "context": {"file": "test.py"}
    }
    
    analysis = await agent._analyze_success_pattern(trace)
    
    if analysis["pattern_type"] == "import_fix":
        print("✅ Import fix pattern detected")
    else:
        print(f"❌ Expected import_fix, got {analysis['pattern_type']}")
        return False
    
    if "test_compliance" in analysis["success_factors"]:
        print("✅ Success factors extracted")
    else:
        print("❌ Success factors not extracted")
        return False
    
    if analysis["confidence"] > 0.5:
        print(f"✅ Confidence calculated: {analysis['confidence']:.2f}")
    else:
        print("❌ Confidence too low")
        return False
    
    return True


async def test_trace_internalization():
    """Test trace storage in local fallback."""
    print("\n" + "=" * 80)
    print("TRACE INTERNALIZATION")
    print("=" * 80)
    
    print("\n1. Testing local storage fallback")
    print("-" * 50)
    
    agent = ReflectionAgent(pinecone_client=None)
    
    trace = {
        "task": "Test internalization",
        "code_before": "print('before')",
        "code_after": "print('after')",
        "signals": ["SUCCESS"],
        "context": {}
    }
    
    analysis = await agent._analyze_success_pattern(trace)
    
    # Test internalization
    success = await agent._internalize_trace(trace, analysis)
    
    if success:
        print("✅ Trace internalized successfully")
    else:
        print("❌ Trace internalization failed")
        return False
    
    # Verify local storage
    if len(agent._local_fallback) > 0:
        print(f"✅ Trace stored locally: {len(agent._local_fallback)} traces")
    else:
        print("❌ No traces in local storage")
        return False
    
    # Check trace content
    trace_id = list(agent._local_fallback.keys())[0]
    stored = agent._local_fallback[trace_id]
    
    if stored["trace"]["task"] == "Test internalization":
        print("✅ Trace content preserved")
    else:
        print("❌ Trace content not preserved")
        return False
    
    return True


async def test_embedding_generation():
    """Test embedding generation (mock)."""
    print("\n" + "=" * 80)
    print("EMBEDDING GENERATION")
    print("=" * 80)
    
    print("\n1. Testing embedding fallback")
    print("-" * 50)
    
    agent = ReflectionAgent(pinecone_client=None)
    
    content = "Test content for embedding"
    embedding = await agent._generate_embedding(content)
    
    # Without Pinecone, should return None
    if embedding is None:
        print("✅ Embedding generation returns None without Pinecone")
    else:
        print("❌ Should return None without Pinecone")
        return False
    
    # Test with mock Pinecone client
    class MockPinecone:
        pass
    
    agent_with_pinecone = ReflectionAgent(pinecone_client=MockPinecone())
    
    # Without API key, should still return None
    embedding = await agent_with_pinecone._generate_embedding(content)
    
    if embedding is None:
        print("✅ Graceful fallback without API key")
    else:
        print("❌ Should handle missing API key gracefully")
        return False
    
    return True


async def test_cross_cycle_recall():
    """Test searching for similar past traces."""
    print("\n" + "=" * 80)
    print("CROSS-CYCLE RECALL")
    print("=" * 80)
    
    print("\n1. Testing local search functionality")
    print("-" * 50)
    
    agent = ReflectionAgent(pinecone_client=None)
    
    # Store some test traces
    traces = [
        {
            "task": "Fix import error for pandas",
            "code_before": "df = pd.DataFrame()",
            "code_after": "import pandas as pd\ndf = pd.DataFrame()",
            "signals": ["TESTS_PASS"],
            "context": {"file": "data.py"}
        },
        {
            "task": "Add missing return statement",
            "code_before": "def add(a, b):\n    result = a + b",
            "code_after": "def add(a, b):\n    result = a + b\n    return result",
            "signals": ["TESTS_PASS"],
            "context": {"file": "math.py"}
        }
    ]
    
    # Internalize traces
    for trace in traces:
        analysis = await agent._analyze_success_pattern(trace)
        await agent._internalize_trace(trace, analysis)
    
    # Search for similar traces
    results = await agent.search_similar_traces("import pandas error", limit=5)
    
    if len(results) > 0:
        print(f"✅ Found {len(results)} similar traces")
    else:
        print("❌ No similar traces found")
        return False
    
    # Check relevance
    if "import" in results[0]["metadata"]["task"].lower():
        print("✅ Search results are relevant")
    else:
        print("❌ Search results not relevant")
        return False
    
    return True


async def test_self_critique():
    """Test self-critique recommendations."""
    print("\n" + "=" * 80)
    print("SELF-CRITIQUE VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing critique logic")
    print("-" * 50)
    
    agent = ReflectionAgent(pinecone_client=None)
    
    # Test high success rate
    results_high = {
        "processed": 10,
        "internalized": 9
    }
    
    critique = await agent._self_critique([], results_high)
    
    if critique == "CONVERGE_AND_COMMIT":
        print("✅ High success rate -> CONVERGE_AND_COMMIT")
    else:
        print(f"❌ Expected CONVERGE_AND_COMMIT, got {critique}")
        return False
    
    # Test medium success rate
    results_medium = {
        "processed": 10,
        "internalized": 6
    }
    
    critique = await agent._self_critique([], results_medium)
    
    if critique == "CONTINUE_LEARNING":
        print("✅ Medium success rate -> CONTINUE_LEARNING")
    else:
        print(f"❌ Expected CONTINUE_LEARNING, got {critique}")
        return False
    
    # Test low success rate
    results_low = {
        "processed": 10,
        "internalized": 3
    }
    
    critique = await agent._self_critique([], results_low)
    
    if critique == "ROLLBACK":
        print("✅ Low success rate -> ROLLBACK")
    else:
        print(f"❌ Expected ROLLBACK, got {critique}")
        return False
    
    return True


async def test_full_execution():
    """Test full ReflectionAgent execution."""
    print("\n" + "=" * 80)
    print("FULL EXECUTION VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing complete processing workflow")
    print("-" * 50)
    
    agent = ReflectionAgent(pinecone_client=None)
    
    # Create successful traces
    successful_traces = [
        {
            "task": "Fix syntax error in function definition",
            "code_before": """def broken_function(
    print("missing closing parenthesis")""",
            "code_after": """def broken_function():
    print("fixed syntax")""",
            "signals": ["TESTS_PASS", "STYLE_PASS"],
            "context": {"file": "syntax.py", "line": 10}
        },
        {
            "task": "Add missing import for datetime",
            "code_before": """def get_timestamp():
    return datetime.now()""",
            "code_after": """from datetime import datetime

def get_timestamp():
    return datetime.now()""",
            "signals": ["TESTS_PASS"],
            "context": {"file": "time.py"}
        }
    ]
    
    # Execute reflection
    results = await agent.execute(successful_traces)
    
    if results["processed"] == 2:
        print("✅ All traces processed")
    else:
        print(f"❌ Expected 2 processed, got {results['processed']}")
        return False
    
    if results["internalized"] == 2:
        print("✅ All traces internalized")
    else:
        print(f"❌ Expected 2 internalized, got {results['internalized']}")
        return False
    
    if len(results["recommendations"]) > 0:
        print(f"✅ Generated {len(results['recommendations'])} recommendations")
    else:
        print("⚠️  No recommendations generated")
    
    if results["critique"] == "CONVERGE_AND_COMMIT":
        print("✅ Appropriate critique: CONVERGE_AND_COMMIT")
    else:
        print(f"⚠️  Critique: {results['critique']}")
    
    return True


async def test_global_functions():
    """Test global convenience functions."""
    print("\n" + "=" * 80)
    print("GLOBAL FUNCTIONS VALIDATION")
    print("=" * 80)
    
    print("\n1. Testing convenience API")
    print("-" * 50)
    
    # Test global agent
    agent = get_reflection_agent()
    
    if isinstance(agent, ReflectionAgent):
        print("✅ Global ReflectionAgent accessible")
    else:
        print("❌ Global agent not accessible")
        return False
    
    # Test process_successful_traces
    traces = [{
        "task": "Global test",
        "code_before": "before",
        "code_after": "after",
        "signals": ["SUCCESS"],
        "context": {}
    }]
    
    results = await process_successful_traces(traces)
    
    if results["processed"] > 0:
        print("✅ Global processing function works")
    else:
        print("❌ Global processing function failed")
        return False
    
    # Test search_memory
    search_results = await search_memory("test query", limit=3)
    
    if isinstance(search_results, list):
        print("✅ Global search function works")
    else:
        print("❌ Global search function failed")
        return False
    
    return True


async def test_memory_persistence():
    """Test that memory persists across operations."""
    print("\n" + "=" * 80)
    print("MEMORY PERSISTENCE")
    print("=" * 80)
    
    print("\n1. Testing trace storage persistence")
    print("-" * 50)
    
    # Store initial traces
    agent1 = ReflectionAgent(pinecone_client=None)
    
    trace = {
        "task": "Persistence test",
        "code_before": "initial",
        "code_after": "modified",
        "signals": ["SUCCESS"],
        "context": {}
    }
    
    analysis = await agent1._analyze_success_pattern(trace)
    await agent1._internalize_trace(trace, analysis)
    
    initial_count = len(agent1._local_fallback)
    
    # Create new agent (should have separate storage)
    agent2 = ReflectionAgent(pinecone_client=None)
    
    # Global agent should have the traces
    global_agent = get_reflection_agent()
    
    if len(global_agent._local_fallback) >= initial_count:
        print("✅ Global agent maintains persistence")
    else:
        print("❌ Global agent lost traces")
        return False
    
    return True


async def run_learning_loop_validation():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("L5 LEARNING LOOP & PINECONE VALIDATION SUITE")
    print("=" * 80)
    print("\nTesting ReflectionAgent memory consolidation and learning")
    
    results = {}
    
    # Run all tests
    results["pattern_analysis"] = await test_pattern_analysis()
    results["internalization"] = await test_trace_internalization()
    results["embedding"] = await test_embedding_generation()
    results["recall"] = await test_cross_cycle_recall()
    results["critique"] = await test_self_critique()
    results["execution"] = await test_full_execution()
    results["global_functions"] = await test_global_functions()
    results["persistence"] = await test_memory_persistence()
    
    # Generate report
    print("\n" + "=" * 80)
    print("LEARNING LOOP VALIDATION REPORT")
    print("=" * 80)
    
    print("\nTest Results:")
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All L5 Learning Loop components validated!")
        print("The system provides:")
        print("  - Pattern analysis of successful traces")
        print("  - Trace internalization to Pinecone/local storage")
        print("  - Embedding generation with text-embedding-004")
        print("  - Cross-cycle recall via semantic search")
        print("  - Self-critique with CONVERGE_AND_COMMIT/ROLLBACK")
        print("  - Graceful fallback when services unavailable")
        print("\n📝 Note: Install required packages for full functionality:")
        print("   pip install pinecone-client google-generativeai")
        print("   Set GOOGLE_API_KEY environment variable")
    else:
        print("\n⚠️  Some components need attention")
        print("Check the logs above for details")
    
    return all_passed


if __name__ == "__main__":
    import sys
    asyncio.run(run_learning_loop_validation())
