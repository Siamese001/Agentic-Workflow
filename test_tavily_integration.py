#!/usr/bin/env python3
"""
Test script to verify Tavily API integration with K.11 Shadow Audit.
"""

import os
import sys
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from runtime.shared.workflow.executive_agents import ExecutiveAgentOrchestrator

async def test_automated_search():
    """Test the automated search functionality."""
    print("🔍 Testing Tavily API Integration for K.11 Shadow Audit")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ TAVILY_API_KEY not found in environment")
        print("Please set: export TAVILY_API_KEY=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")
        return False
    
    # Initialize orchestrator
    orchestrator = ExecutiveAgentOrchestrator()
    
    # Test automated research
    print("\n📊 Testing automated research for 'Snowflake'...")
    search_results = orchestrator.data_sources.automated_company_research("Snowflake")
    
    if search_results and "[MOCK]" not in search_results:
        print("✅ Automated search successful!")
        print(f"\nSample results (first 500 chars):")
        print("-" * 40)
        print(search_results[:500] + "..." if len(search_results) > 500 else search_results)
        print("-" * 40)
        return True
    else:
        print("❌ Automated search failed or returned mock data")
        return False

async def test_k11_execution():
    """Test full K.11 execution with automated search."""
    print("\n🎯 Testing full K.11 Shadow Audit execution...")
    
    # Check for LLM API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  No LLM API keys found - will test in mock mode")
    
    orchestrator = ExecutiveAgentOrchestrator()
    
    try:
        # Execute K.11 with automated search (no manual context)
        result = await orchestrator.execute_k11_shadow_audit(
            company_name="Snowflake",
            search_context=None,  # This triggers automated search
            config={}
        )
        
        print("✅ K.11 execution successful!")
        print(f"\n📋 Technical Stack Found:")
        for item in result.current_stack[:3]:  # Show first 3 items
            print(f"  • {item.tool_name} ({item.category}) - {item.confidence_score*100:.0f}% confidence")
        
        print(f"\n⚠️  Suspected Bottlenecks:")
        for bottleneck in result.suspected_bottlenecks[:3]:
            print(f"  • {bottleneck}")
        
        print(f"\n💡 Strategic Opportunity: {result.strategic_opportunity}")
        
        return True
        
    except Exception as e:
        print(f"❌ K.11 execution failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("\n🚀 Starting Tavily Integration Tests\n")
    
    # Test 1: Automated search
    search_ok = await test_automated_search()
    
    # Test 2: Full K.11 execution
    k11_ok = await test_k11_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Automated Search: {'✅ PASS' if search_ok else '❌ FAIL'}")
    print(f"K.11 Execution:   {'✅ PASS' if k11_ok else '❌ FAIL'}")
    
    if search_ok and k11_ok:
        print("\n🎉 All tests passed! Tavily integration is ready.")
        print("\nTo use in War Room:")
        print("1. Set TAVILY_API_KEY environment variable")
        print("2. Run: python war_room.py")
        print("3. Select 'Shadow Audit Only' and choose 'y' for automated search")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
    
    return search_ok and k11_ok

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
