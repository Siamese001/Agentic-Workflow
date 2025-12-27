"""Test MCP integration without Reddit credentials."""

import asyncio
import logging
import pytest

from mcp_adapter import UniversalMCPClient

LOGGER = logging.getLogger(__name__)


# REFACTOR: Split this 70-line function
@pytest.mark.skip(reason="Requires UniversalMCPClient stub")
@pytest.mark.asyncio
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
        json.dump(CONFIG, f)

    # Test with temporary config
    client = UniversalMCPClient("config/test_mcp_config.json")

    try:
        await client.connect_all()
        tools = await client.get_tools_for_llm()

        LOGGER.info("✅ Connected MCP servers:")
        for tool in tools:
            LOGGER.info(f"  - {tool['name']}: {tool['description']}")

        # Test filesystem write
        result = await client.execute_tool(
            "filesystem__write_file",
            {"path": "./output/test.md", "content": "# MCP Test\n\nThis was written autonomously!"},
        )
        LOGGER.info(f"✅ File write result: {result}")

    except Exception as e:
        LOGGER.error(f"❌ Error: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(test_mcp())
