"""Debug MCP server connections."""

import asyncio
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

async def test_mcp_directly():
    """Test MCP servers directly with subprocess to see errors."""

    servers = [
        {
            "name": "filesystem",
            "cmd": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "./output", "./logs", "./project_knowledge"],
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
            process = await asyncio.create_subprocess_exec(
                *server['cmd'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="c:/Git/Agentic-Workflow"
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=server['timeout']
                )

                logger.info(f"Exit code: {process.returncode}")

                if stdout:
                    logger.info(f"STDOUT:\n{stdout.decode()}")
                if stderr:
                    logger.error(f"STDERR:\n{stderr.decode()}")

            except asyncio.TimeoutError:
                logger.warning("Server timed out - this might be normal (MCP servers wait for stdin)")
                process.terminate()
                await process.wait()

        except Exception as e:
            logger.error(f"Failed to start {server['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_directly())
