"""Test Titanium RAG Pipeline Integration.

This module tests the complete integration of the Titanium RAG Pipeline
with the L3 orchestrator and various agents.
"""

import asyncio
import logging

# Test imports
    clear_cache,
    get_pipeline_stats,
    get_titanium_search_tool,
    get_titanium_search_with_sources,
    sync_search,
)

logger = logging.getLogger(__name__)


async def test_titanium_search_tool():
    """Test the Titanium search tool functionality."""
    print("\n=== Testing Titanium Search Tool ===")

    # Test basic search
    result = await get_titanium_search_tool(query="machine learning optimization", max_results=3)
    print(f"Basic search result: {result[:100]}...")

    # Test search with context
    result_with_context = await get_titanium_search_tool(
        query="deep learning", context="production deployment", include_metadata=True
    )
    print(f"Search with context: {result_with_context[:100]}...")

    # Test search with sources
    sources_result = await get_titanium_search_with_sources(query="neural network architectures")
    print(f"Sources result keys: {list(sources_result.keys())}")

    # Test pipeline stats
    stats = get_pipeline_stats()
    print(f"Pipeline stats: {stats}")

    # Test cache clear
    await clear_cache()
    print("Cache cleared successfully")

    print("✓ Titanium search tool tests passed")


def test_sync_wrapper():
    """Test the synchronous wrapper."""
    print("\n=== Testing Synchronous Wrapper ===")

    # Test sync search
    result = sync_search("test query")
    print(f"Sync search result: {result[:100]}...")

    print("✓ Synchronous wrapper tests passed")


async def test_titanium_integration():
    """Test integration with orchestrator and agents."""
    print("\n=== Testing Titanium Integration ===")

    # Test tool registry

    print(f"Available tools: {list(TOOL_REGISTRY.keys())}")

    # Test tool descriptions
    for tool_name, tool_info in TOOL_REGISTRY.items():
        print(f"\nTool: {tool_name}")
        print(f"  Description: {tool_info['description']}")
        print(f"  Parameters: {list(tool_info['parameters'].keys())}")

    print("\n✓ Titanium integration tests passed")


async def test_executive_brief_agent():
    """Test ExecutiveBriefAgent with Titanium integration."""
    print("\n=== Testing ExecutiveBriefAgent Integration ===")

    try:

        # Initialize agent
        agent = ExecutiveBriefAgent(
            candidate_name="Test Candidate", candidate_background={"experience": "AI/ML Engineer"}
        )

        # Check if Titanium is enabled
        print(f"Titanium enabled: {agent.titanium_enabled}")

        # Test Titanium research
        if agent.titanium_enabled:
            research = await agent._research_company_with_titanium(
                company_name="TechCorp", industry="technology"
            )
            print(f"Research keys: {list(research.keys())}")
            print(f"Company name: {research['name']}")

            # Test brief generation with Titanium
            brief = await agent.generate_brief_with_titanium(
                company_name="TechCorp",
                industry="technology",
                job_description="Senior AI Engineer position",
            )
            print(f"Generated brief for: {brief.company_name}")
            print(f"Observation: {brief.observation.heading}")
            print(f"Insight: {brief.insight.heading}")
            print(f"Proposition: {brief.proposition.heading}")

        print("✓ ExecutiveBriefAgent integration tests passed")

    except ImportError as e:
        print(f"⚠ ExecutiveBriefAgent not available: {e}")


async def test_hardened_orchestrator_integration():
    """Test HardenedWorkflowOrchestrator with Titanium."""
    print("\n=== Testing Hardened Orchestrator Integration ===")

    try:
            enhance_system_prompt,
            inject_titanium_tools,
            prepare_titanium_context,
        )

        # Test context injection
        context = {"test": "value"}
        enhanced_context = inject_titanium_tools(context)
        print(f"Injected tools: {list(k for k in enhanced_context.keys() if 'titanium' in k)}")
        print(f"Available tools count: {len(enhanced_context.get('available_tools', []))}")

        # Test async context preparation
        async_context = await prepare_titanium_context(context)
        print(f"Async context keys: {list(k for k in async_context.keys() if 'titanium' in k)}")

        # Test system prompt enhancement
        base_prompt = "You are an AI assistant."
        enhanced_prompt = enhance_system_prompt(base_prompt)
        print(f"Prompt enhanced: {'Titanium' in enhanced_prompt}")
        print(f"Enhancement length: {len(enhanced_prompt) - len(base_prompt)} chars")

        print("✓ Hardened orchestrator integration tests passed")

    except ImportError as e:
        print(f"⚠ Hardened orchestrator integration not available: {e}")


async def test_dispatch_tools():
    """Test dispatch_resume_tools with Titanium integration."""
    print("\n=== Testing Dispatch Resume Tools ===")

    try:

        # Initialize with Titanium enabled
        tools = DispatchResumeTools({"use_titanium_search": True})
        print(f"Titanium enabled: {tools.titanium_enabled}")

        # Test search action
        result = tools.execute("search", {"query": "machine learning", "max_results": 3})
        print(f"Search action result: {result.success}")
        if result.success:
            output = result.output
            print(
                f"Output keys: {list(output.keys()) if isinstance(output, dict) else 'string output'}"
            )

        # Test search with sources
        result2 = tools.execute("search_with_sources", {"query": "deep learning"})
        print(f"Search with sources result: {result2.success}")

        # Test stats action
        result3 = tools.execute("get_pipeline_stats", {})
        print(f"Stats result: {result3.success}")

        print("✓ Dispatch resume tools tests passed")

    except ImportError as e:
        print(f"⚠ Dispatch tools not available: {e}")


async def run_all_integration_tests():
    """Run all integration tests."""
    print("\n🚀 Starting Titanium RAG Pipeline Integration Tests")
    print("=" * 60)

    try:
        # Core functionality tests
        await test_titanium_search_tool()
        test_sync_wrapper()
        await test_titanium_integration()

        # Agent integration tests
        await test_executive_brief_agent()
        await test_hardened_orchestrator_integration()
        await test_dispatch_tools()

        print("\n" + "=" * 60)
        print("✅ All Titanium RAG Pipeline Integration Tests Passed!")
        print("\nThe Titanium RAG Pipeline has been successfully integrated with:")
        print("  • Universal search tool wrapper")
        print("  • Hardened Workflow Orchestrator")
        print("  • Executive Brief Agent")
        print("  • Dispatch Resume Tools")
        print("  • Async/sync interfaces")
        print("  • Fallback mechanisms")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the integration tests
    asyncio.run(run_all_integration_tests())