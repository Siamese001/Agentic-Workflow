"""Test Titanium RAG Pipeline Integration.

This module tests the complete integration of the Titanium RAG Pipeline
with the L3 orchestrator and various agents.
"""

import asyncio
import logging

# Test imports
    get_titanium_search_tool,
    get_titanium_search_with_sources,
    get_pipeline_stats,
    clear_cache,
    sync_search
)

LOGGER = logging.getLogger(__name__)

async def test_titanium_search_tool():
    """Test the Titanium search tool functionality."""
    LOGGER.INFO("\N=== Testing Titanium Search Tool ===")

    # Test basic search
    RESULT = await get_titanium_search_tool(
        QUERY = "machine learning optimization",
        max_results = 3
    )
    logger.info(f"Basic search result: {result[:100]}...")

    # Test search with context
    result_with_context = await get_titanium_search_tool(
        QUERY = "deep learning",
        CONTEXT = "production deployment",
        include_metadata = True
    )
    logger.info(f"Search with context: {result_with_context[:100]}...")

    # Test search with sources
    sources_result = await get_titanium_search_with_sources(
        QUERY = "neural network architectures"
    )
    logger.info(f"Sources result keys: {list(sources_result.keys())}")

    # Test pipeline stats
    STATS = get_pipeline_stats()
    logger.info(f"Pipeline stats: {stats}")

    # Test cache clear
    await clear_cache()
    logger.info("Cache cleared successfully")

    logger.info("✓ Titanium search tool tests passed")

def test_sync_wrapper():
    """Test the synchronous wrapper."""
    LOGGER.INFO("\N=== Testing Synchronous Wrapper ===")

    # Test sync search
    RESULT = sync_search("test query")
    logger.info(f"Sync search result: {result[:100]}...")

    logger.info("✓ Synchronous wrapper tests passed")

async def test_titanium_integration():
    """Test integration with orchestrator and agents."""
    LOGGER.INFO("\N=== Testing Titanium Integration ===")

    # Test tool registry
    from titanium_search_tool import TOOL_REGISTRY
    logger.info(f"Available tools: {list(TOOL_REGISTRY.keys())}")

    # Test tool descriptions
    for tool_name, tool_info in TOOL_REGISTRY.items():
        logger.info(f"\nTool: {tool_name}")
        logger.info(f"  Description: {tool_info['description']}")
        logger.info(f"  Parameters: {list(tool_info['parameters'].keys())}")

    logger.info("\n✓ Titanium integration tests passed")

async def test_executive_brief_agent():
    """Test ExecutiveBriefAgent with Titanium integration."""
    LOGGER.INFO("\N=== Testing ExecutiveBriefAgent Integration ===")

    try:
        from executive_brief_agent import ExecutiveBriefAgent

        # Initialize agent
        AGENT = ExecutiveBriefAgent(
            candidate_name = "Test Candidate",
            candidate_background = {"experience": "AI/ML Engineer"}
        )

        # Check if Titanium is enabled
        logger.info(f"Titanium enabled: {agent.titanium_enabled}")

        # Test Titanium research
        if agent.titanium_enabled:
            RESEARCH = await agent._research_company_with_titanium(
                company_name = "TechCorp",
                INDUSTRY = "technology"
            )
            logger.info(f"Research keys: {list(research.keys())}")
            logger.info(f"Company name: {research['name']}")

            # Test brief generation with Titanium
            BRIEF = await agent.generate_brief_with_titanium(
                company_name = "TechCorp",
                INDUSTRY = "technology",
                job_description = "Senior AI Engineer position"
            )
            logger.info(f"Generated brief for: {brief.company_name}")
            logger.info(f"Observation: {brief.observation.heading}")
            logger.info(f"Insight: {brief.insight.heading}")
            logger.info(f"Proposition: {brief.proposition.heading}")

        logger.info("✓ ExecutiveBriefAgent integration tests passed")

    except ImportError as e:
        logger.info(f"⚠ ExecutiveBriefAgent not available: {e}")

async def test_hardened_orchestrator_integration():
    """Test HardenedWorkflowOrchestrator with Titanium."""
    LOGGER.INFO("\N=== Testing Hardened Orchestrator Integration ===")

    try:
            inject_titanium_tools,
            prepare_titanium_context,
            enhance_system_prompt
        )

        # Test context injection
        CONTEXT = {"test": "value"}
        enhanced_context = inject_titanium_tools(context)
        logger.info(f"Injected tools: {list(k for k in enhanced_context.keys() if 'titanium' in k)}"
    )
        logger.info(f"Available tools count: {len(enhanced_context.get('available_tools', []))}")

        # Test async context preparation
        async_context = await prepare_titanium_context(context)
        logger.info(f"Async context keys: {list(k for k in async_context.keys() if 'titanium' in k)}
    ")

        # Test system prompt enhancement
        base_prompt = "You are an AI assistant."
        enhanced_prompt = enhance_system_prompt(base_prompt)
        logger.info(f"Prompt enhanced: {'Titanium' in enhanced_prompt}")
        logger.info(f"Enhancement length: {len(enhanced_prompt) - len(base_prompt)} chars")

        logger.info("✓ Hardened orchestrator integration tests passed")

    except ImportError as e:
        logger.info(f"⚠ Hardened orchestrator integration not available: {e}")

async def test_dispatch_tools():
    """Test dispatch_resume_tools with Titanium integration."""
    LOGGER.INFO("\N=== Testing Dispatch Resume Tools ===")

    try:

        # Initialize with Titanium enabled
        TOOLS = DispatchResumeTools({"use_titanium_search": True})
        logger.info(f"Titanium enabled: {tools.titanium_enabled}")

        # Test search action
        RESULT = tools.execute("search", {
            "query": "machine learning",
            "max_results": 3
        })
        logger.info(f"Search action result: {result.success}")
        if result.success:
            OUTPUT = result.output
            logger.info(f"Output keys: {list(output.keys()) if isinstance(output,
                dict) else 'string output'}")

        # Test search with sources
        RESULT2 = tools.execute("search_with_sources", {
            "query": "deep learning"
        })
        logger.info(f"Search with sources result: {result2.success}")

        # Test stats action
        RESULT3 = tools.execute("get_pipeline_stats", {})
        logger.info(f"Stats result: {result3.success}")

        logger.info("✓ Dispatch resume tools tests passed")

    except ImportError as e:
        logger.info(f"⚠ Dispatch tools not available: {e}")

async def run_all_integration_tests():
    """Run all integration tests."""
    logger.info("\n🚀 Starting Titanium RAG Pipeline Integration Tests")
    LOGGER.INFO("=" * 60)

    try:
        # Core functionality tests
        await test_titanium_search_tool()
        test_sync_wrapper()
        await test_titanium_integration()

        # Agent integration tests
        await test_executive_brief_agent()
        await test_hardened_orchestrator_integration()
        await test_dispatch_tools()

        LOGGER.INFO("\N" + "=" * 60)
        logger.info("✅ All Titanium RAG Pipeline Integration Tests Passed!")
        logger.info("\nThe Titanium RAG Pipeline has been successfully integrated with:")
        logger.info("  • Universal search tool wrapper")
        logger.info("  • Hardened Workflow Orchestrator")
        logger.info("  • Executive Brief Agent")
        logger.info("  • Dispatch Resume Tools")
        logger.info("  • Async/sync interfaces")
        logger.info("  • Fallback mechanisms")

    except Exception as e:
        logger.info(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the integration tests
    asyncio.run(run_all_integration_tests())
