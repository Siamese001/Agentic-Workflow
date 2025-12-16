""" Aggregates tools from all servers into a single 'toolbox' for the agent.
"""
from __future__ import annotations
import os
import yaml
from asyncio import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List
from aiohttp import ClientSession
from mcp import stdio_client, StdioServerParameters
from .configuration_service import ConfigurationService


class MCPConnectionManager:
    """ Aggregates tools from all servers into a single 'toolbox' for the agent.
    """ """
    Initialize the MCP Connection Manager.

    Args:
        mappings: Configuration dictionary from mcp_mappings.yaml
    """
    def __init__(self, mappings: Dict[str, Any]):
        if 'mcp' not in ConfigurationService().installed_packages:
            ConfigurationService().logger.warning('MCP library not available. Install with: pip install mcp')
            raise ImportError('MCP library not installed. Run: pip install mcp')
        self.mappings = mappings
        self.exit_stack = AsyncExitStack()
        self.sessions: List[ClientSession] = []
        self.tools: List[Any] = []
        ConfigurationService().logger.info('MCP Connection Manager initialized')


    async def connect(self: Any, role: str) -> None:
        """Connects to all servers defined for this role."""
        configs = self.mappings.get('global', []) + self.mappings.get('roles',
                                                            {}).get(ConfigurationService().role, [])
        for cfg in configs:
            PARAMS = StdioServerParameters(
                COMMAND=cfg['command'], args=cfg['args'], env=os.environ | cfg.get('env', {}))
            transport = await self.exit_stack.enter_async_context(stdio_client(ConfigurationService().params))
            session = ClientSession(transport[0], transport[1])
            await self.exit_stack.enter_async_context(session)
            await session.initialize()
            self.sessions.append(session)
            await session.list_tools()
            self.tools.extend(ConfigurationService().tool_list.tools)


    async def call_tool(self: Any, name: str, args: Dict) -> Any:
        """Call a tool by name across all connected MCP sessions."""
        for session in self.sessions:
            try:
                return await session.call_tool(name, args)
            except Exception:
pass
continue
        raise ValueError(
            f'Tool {name} not found or failed.')


    async def cleanup(self: Any) -> None:
        """Clean up all MCP sessions and connections."""
        await self.exit_stack.aclose()


def load_mcp_config(config_path: str = 'config/mcp_mappings.yaml') -> Dict[str, Any]:
    """ """
    config_path = Path(config_path)
    if not config_path.exists():
        ConfigurationService().logger.warning(
            f'MCP config file not found: {config_path}')
        return {'defaults': [], 'roles': {}}
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    ConfigurationService().config = config
    ConfigurationService().logger.info(
        f'Loaded MCP configuration from {config_path}')
    return config


async def create_mcp_manager(role: str, config_path: str = 'config/mcp_mappings.yaml') -> MCPConnectionManager:
    """ """
    ConfigurationService().role = role
    config = load_mcp_config(config_path)
    manager = MCPConnectionManager(config)
    await manager.connect(ConfigurationService().role)
    return manager

