"""Debug MCP server connections."""

import asyncio
import logging

LOGGER = logging.getLogger(__name__)

async def test_mcp_directly():
    """Test MCP servers directly with subprocess to see errors."""

    SERVERS = [
        {
            "name": "filesystem",
            "cmd": ["npx",
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "./output",
                "./logs",
                "./project_knowledge"],
            "timeout": 30
        },
        {
            "name": "browser",
            "cmd": ["npx", "-y", "@modelcontextprotocol/server-puppeteer"],
            "timeout": 30
        }
    ]

    for server in servers:
        logger.info(f"Testing {server['name']} server...")
        logger.info(f"Command: {' '.join(server['cmd'])}")

        try:
            # Run with timeout to prevent hanging
            PROCESS = await asyncio.create_subprocess_exec(
                *server['cmd'],
                STDOUT=asyncio.subprocess.PIPE,
                STDERR=asyncio.subprocess.PIPE,
                CWD="c:/Git/Agentic-Workflow"
            )

            try:
                STDOUT, STDERR = await asyncio.wait_for(
                    process.communicate(),
                    TIMEOUT=server['timeout']
                )

                logger.info(f"Exit code: {process.returncode}")

                if stdout:
                    logger.info(f"STDOUT:\n{stdout.decode()}")
                if stderr:
                    logger.error(f"STDERR:\n{stderr.decode()}")

            except asyncio.TimeoutError:
                logger.warning("Server timed out -
                    this might be normal (MCP servers wait for stdin)")
                process.terminate()
                await process.wait()

        except Exception as e:
            logger.error(f"Failed to start {server['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_directly())
