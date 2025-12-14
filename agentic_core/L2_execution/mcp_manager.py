from typing import Any
"""
MCP Connection Manager

Manages connections to multiple MCP servers simultaneously.
Aggregates tools from all servers into a single 'toolbox' for the agent.
"""

import os
import logging
import yaml
from contextlib import AsyncExitStack
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP library not available. Install with: pip install mcp")


class MCPConnectionManager:
    """
    Manages connections to multiple MCP servers simultaneously.
    Aggregates tools from all servers into a single 'toolbox' for the agent.
    """

    def __init__(self, mappings: Dict[str, Any]):
        """
        Initialize the MCP Connection Manager.

        Args:
            mappings: Configuration dictionary from mcp_mappings.yaml
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP library not installed. Run: pip install mcp")

        self.mappings = mappings
        self.exit_stack = AsyncExitStack()
        self.sessions: List[ClientSession] = []
        self.tools = []

        logger.info("MCP Connection Manager initialized")

    async def connect(self, role: str):
        """Connects to all servers defined for this role."""
        configs = self.mappings.get('global', []) + self.mappings.get('roles', {}).get(role, [])

        for cfg in configs:
            params = StdioServerParameters(
                command=cfg['command'],
                args=cfg['args'],
                env=os.environ | cfg.get('env', {})
            )

            # Context Manager Magic
            transport = await self.exit_stack.enter_async_context(stdio_client(params))
            session = await self.exit_stack.enter_async_context(ClientSession(transport[0], transport[1]))
            await session.initialize()

            self.sessions.append(session)

            # Discovery
            tool_list = await session.list_tools()
            self.tools.extend(tool_list.tools)

    async def call_tool(self, name: str, args: Dict) -> Any:
        for session in self.sessions:
            try:
                # Try to call on every session (simplified router)
                return await session.call_tool(name, args)
            except Exception:
                continue
        raise ValueError(f"Tool {name} not found or failed.")

    async def cleanup(self):
        await self.exit_stack.aclose()


def load_mcp_config(config_path: str = "config/mcp_mappings.yaml") -> Dict[str, Any]:
    """
    Load MCP configuration from YAML file.

    Args:
        config_path: Path to the MCP mappings YAML file

    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)

    if not config_file.exists():
        logger.warning(f"MCP config file not found: {config_path}")
        return {"defaults": [], "roles": {}}

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded MCP configuration from {config_path}")
    return config


async def create_mcp_manager(role: str, config_path: str = "config/mcp_mappings.yaml") -> MCPConnectionManager:
    """
    Factory function to create and connect an MCP manager for a specific role.

    Args:
        role: Agent role
        config_path: Path to MCP configuration file

    Returns:
        Connected MCPConnectionManager instance
    """
    config = load_mcp_config(config_path)
    manager = MCPConnectionManager(config)
    await manager.connect_servers(role)
    return manager
