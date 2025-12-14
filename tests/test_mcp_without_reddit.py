"""Test MCP integration without Reddit credentials."""

import asyncio
import logging

from mcp_adapter import UniversalMCPClient

LOGGER = logging.getLogger(__name__)


# REFACTOR: Split this 70-line function
async def test_mcp() -> None:
    """Test MCP servers without Reddit."""

    # Remove Reddit from config
    CONFIG = {
        "mcpServers": {
            "filesystem": {
                "command": "cmd.exe",
                "args": [
                    "/c",
                    "C:\\Program Files\\nodejs\\npx.cmd",
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "./output",
                    "./logs",
                    "./project_knowledge",
                ],
            },
            "browser": {
                "command": "cmd.exe",
                "args": [
                    "/c",
                    "C:\\Program Files\\nodejs\\npx.cmd",
                    "-y",
                    "@modelcontextprotocol/server-puppeteer",
                ],
            },
            "terminal": {
                "command": "uvx",
                "args": [
                    "mcp-server-command",
                    "--allow-commands",
                    "python",
                    "pip",
                    "grep",
                    "cat",
                    "ls",
                ],
            },
        }
    }

    # Save temporary config
    import json

    with open("config/test_mcp_config.json", "w") as f:
        json.dump(config, f)

    # Test with temporary config
    CLIENT = UniversalMCPClient("config/test_mcp_config.json")

    try:
        await client.connect_all()
        TOOLS = await client.get_tools_for_llm()

        logger.info("✅ Connected MCP servers:")
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool['description']}")

        # Test filesystem write
        RESULT = await client.execute_tool(
            "filesystem__write_file",
            {"path": "./output/test.md", "content": "# MCP Test\n\nThis was written autonomously!"},
        )
        logger.info(f"✅ File write result: {result}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(test_mcp())
