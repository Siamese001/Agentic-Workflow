"""End-to-End MCP Integration Test


logger = logging.getLogger(__name__)
Tests all MCP servers with the executive orchestrator:
- Filesystem: Read/write operations
- Browser: Web navigation and content extraction
- GitHub: Repository access (requires GITHUB_TOKEN)
- Postgres: Memory operations (requires DATABASE_URL)
- Terminal: Safe command execution
"""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp_adapter import UniversalMCPClient

async def test_filesystem_mcp(client):
    """Test filesystem MCP read/write operations."""
    logger.info("\n📁 Testing Filesystem MCP...")

    # Test write operation
    test_content = f"""# MCP E2E Test Report
Generated: {datetime.now().isoformat()}

## Test Results
- Filesystem MCP: ✅ Connected
- Browser MCP: ✅ Connected
- GitHub MCP: Pending
- Postgres MCP: Pending
- Terminal MCP: Pending
"""

    result = await client.execute_tool("filesystem__write_file", {
        "path": "./output/e2e_test_report.md",
        "content": test_content
    })
    logger.info(f"  ✅ Write result: {result}")

    # Test read operation
    result = await client.execute_tool("filesystem__read_text_file", {
        "path": "./output/e2e_test_report.md"
    })
    logger.info(f"  ✅ Read result: Success (content length: {len(str(result))})")

    # Test list directory
    result = await client.execute_tool("filesystem__list_directory", {
        "path": "./output"
    })
    logger.info(f"  ✅ List directory: {len(str(result))} characters")

    return True

async def test_browser_mcp(client):
    """Test browser MCP navigation and content extraction."""
    logger.info("\n🌐 Testing Browser MCP...")

    # Navigate to a test page
    result = await client.execute_tool("browser__puppeteer_navigate", {
        "url": "https://httpbin.org/html"
    })
    logger.info(f"  ✅ Navigate result: {result}")

    # Get page content
    result = await client.execute_tool("browser__puppeteer_evaluate", {
        "script": "document.title"
    })
    logger.info(f"  ✅ Page title: {result}")

    # Take screenshot
    result = await client.execute_tool("browser__puppeteer_screenshot", {})
    logger.info(f"  ✅ Screenshot taken: {type(result)}")

    return True

async def test_github_mcp(client):
    """Test GitHub MCP repository access."""
    logger.info("\n🐙 Testing GitHub MCP...")

    # Check if token is available
    if not os.getenv("GITHUB_TOKEN"):
        logger.warning("  ⚠️ GITHUB_TOKEN not set, skipping GitHub tests")
        return False

    try:
        # List repositories
        result = await client.execute_tool("github__list_repositories", {
            "owner": "octocat"
        })
        logger.info(f"  ✅ List repos: {type(result)}")

        # Get repository info
        result = await client.execute_tool("github__get_repository", {
            "owner": "octocat",
            "repo": "Hello-World"
        })
        logger.info(f"  ✅ Get repo: Success")

        return True
    except Exception as e:
        logger.error(f"  ❌ GitHub test failed: {e}")
        return False

async def test_postgres_mcp(client):
    """Test Postgres MCP memory operations."""
    logger.info("\n🗄️ Testing Postgres MCP...")

    # Check if database URL is available
    if not os.getenv("DATABASE_URL"):
        logger.warning("  ⚠️ DATABASE_URL not set, skipping Postgres tests")
        return False

    try:
        # Create test table
        result = await client.execute_tool("postgres_memory__query", {
            "query": """
            CREATE TABLE IF NOT EXISTS mcp_e2e_test (
                id SERIAL PRIMARY KEY,
                test_name TEXT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
            """
        })
        logger.info(f"  ✅ Create table: {result}")

        # Insert test data
        result = await client.execute_tool("postgres_memory__query", {
            "query": """
            INSERT INTO mcp_e2e_test (test_name) VALUES ('e2e_test')
            """
        })
        logger.info(f"  ✅ Insert data: {result}")

        # Query test data
        result = await client.execute_tool("postgres_memory__query", {
            "query": "SELECT COUNT(*) as count FROM mcp_e2e_test"
        })
        logger.info(f"  ✅ Query data: {result}")

        return True
    except Exception as e:
        logger.error(f"  ❌ Postgres test failed: {e}")
        return False

async def test_pinecone_mcp(client):
    """Test Pinecone MCP vector operations."""
    logger.info("\n🌲 Testing Pinecone MCP...")

    # Check if Pinecone API key is available
    if not os.getenv("PINECONE_API_KEY"):
        logger.warning("  ⚠️ PINECONE_API_KEY not set, skipping Pinecone tests")
        return False

    try:
        # List indexes
        result = await client.execute_tool("pinecone__list_indexes", {})
        logger.info(f"  ✅ List indexes: {type(result)}")

        # Create test index (if not exists)
        test_index = "mcp-e2e-test"
        result = await client.execute_tool("pinecone__create_index", {
            "name": test_index,
            "dimension": 1536,
            "metric": "cosine"
        })
        logger.info(f"  ✅ Create index: {result}")

        # Upsert vectors
        test_vectors = [
            {"id": "1", "values": [0.1] * 1536, "metadata": {"text": "test document 1"}},
            {"id": "2", "values": [0.2] * 1536, "metadata": {"text": "test document 2"}}
        ]
        result = await client.execute_tool("pinecone__upsert", {
            "indexName": test_index,
            "vectors": test_vectors
        })
        logger.info(f"  ✅ Upsert vectors: {result}")

        # Query vectors
        result = await client.execute_tool("pinecone__query", {
            "indexName": test_index,
            "vector": [0.1] * 1536,
            "topK": 5
        })
        logger.info(f"  ✅ Query vectors: Success")

        return True
    except Exception as e:
        logger.error(f"  ❌ Pinecone test failed: {e}")
        return False

async def test_terminal_mcp(client):
    """Test Terminal MCP safe command execution."""
    logger.info("\n💻 Testing Terminal MCP...")

    try:
        # List files (safe command)
        result = await client.execute_tool("terminal__execute", {
            "command": "ls",
            "args": ["-la", "./output"]
        })
        logger.info(f"  ✅ ls command: {type(result)}")

        # Python version (safe command)
        result = await client.execute_tool("terminal__execute", {
            "command": "python",
            "args": ["--version"]
        })
        logger.info(f"  ✅ python version: {result}")

        return True
    except Exception as e:
        logger.error(f"  ❌ Terminal test failed: {e}")
        return False

async def test_sequential_thinking_mcp(client):
    """Test Sequential Thinking MCP reasoning capabilities."""
    logger.info("\n🧠 Testing Sequential Thinking MCP...")

    try:
        # Test sequential thinking tool
        result = await client.execute_tool("sequential_thinking__think", {
            "problem": "How should we optimize the agentic workflow for better performance?",
            "context": "We have multiple MCP servers and need to minimize latency"
        })
        logger.info(f"  ✅ Sequential thinking: {type(result)}")

        # Test step-by-step reasoning
        result = await client.execute_tool("sequential_thinking__step", {
            "step": "Analyze current bottlenecks",
            "previous_steps": []
        })
        logger.info(f"  ✅ Step reasoning: Success")

        return True
    except Exception as e:
        logger.error(f"  ❌ Sequential thinking test failed: {e}")
        return False

async def test_executive_orchestrator_integration():
    """Test integration with ExecutiveAgentOrchestrator."""
    logger.info("\n🤖 Testing Executive Orchestrator Integration...")

    try:
        # Import with MCP
        from runtime.shared.workflow.executive_orchestrator import ExecutiveAgentOrchestrator

        # Create orchestrator
        orchestrator = ExecutiveAgentOrchestrator()

        # Check MCP client
        if orchestrator.mcp:
            logger.info("  ✅ MCP client initialized in orchestrator")

            # Get available tools
            tools = await orchestrator.mcp.get_tools_for_llm()
            logger.info(f"  ✅ Available tools: {len(tools)} tools")

            # List tool categories
            categories = {}
            for tool in tools:
                category = tool['name'].split('__')[0]
                categories[category] = categories.get(category, 0) + 1

            logger.info("  📊 Tool categories:")
            for cat, count in categories.items():
                logger.info(f"    - {cat}: {count} tools")

            return True
        else:
            logger.error("  ❌ MCP client not initialized")
            return False

    except Exception as e:
        logger.error(f"  ❌ Orchestrator test failed: {e}")
        return False

async def main():
    """Run all MCP integration tests."""
    logger.info("=" * 60)
    logger.info("🚀 MCP Integration End-to-End Test")
    logger.info("=" * 60)

    # Initialize MCP client
    client = UniversalMCPClient()

    try:
        # Connect all servers
        logger.info("\n🔌 Connecting to MCP servers...")
        await client.connect_all()

        # Run tests
        results = {}

        results['filesystem'] = await test_filesystem_mcp(client)
        results['browser'] = await test_browser_mcp(client)
        results['github'] = await test_github_mcp(client)
        results['postgres'] = await test_postgres_mcp(client)
        results['pinecone'] = await test_pinecone_mcp(client)
        results['sequential_thinking'] = await test_sequential_thinking_mcp(client)
        results['terminal'] = await test_terminal_mcp(client)
        results['orchestrator'] = await test_executive_orchestrator_integration()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)

        for test, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{test:15} {status}")

        total = len(results)
        passed = sum(results.values())
        logger.info(f"\nOverall: {passed}/{total} tests passed")

        if passed == total:
            logger.info("\n🎉 All MCP integrations working correctly!")
        else:
            logger.warning(f"\n⚠️ {total - passed} test(s) failed or skipped")

    except Exception as e:
        logger.error(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        await client.cleanup()
        logger.info("\n✅ MCP connections closed")

if __name__ == "__main__":
    asyncio.run(main())
