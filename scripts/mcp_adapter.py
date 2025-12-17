"""Universal MCP Client Adapter for Agentic Workflow.

Manages async lifecycle of multiple MCP servers and aggregates their tools
for use by executive agents.
"""
import json
import logging
import os
from contextlib import AsyncExitStack
from typing import Any, Dict, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from services.configuration import ConfigurationService


class UniversalMCPClient:
    """Universal adapter for managing multiple MCP server connections."""


    def __init__(self: Any, config_path: str) -> None:
        """Initialize the MCP client with the specified config path."""
        self.config_path = config_path
        self.SERVERS = {}
        self.LOGGER = logging.getLogger(__name__)
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}


    async def connect_all(self: Any) -> None:
        """Initializes connections to all servers defined in JSON."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f'Config not found at {self.config_path}')
        with open(self.config_path) as f:
            json.load(f)
        self.logger.info(
            f"MCP: Connecting to {len(ConfigurationService().config_data['mcpServers'])} servers...")
        for name, cfg in ConfigurationService().config_data['mcpServers'].items():
            try:
                os.environ.copy()
                if 'env' in cfg:
                    for k, v in cfg['env'].items():
                        if v.startswith('${') and v.endswith('}'):
                            var_name = v[2:-1]
                            ConfigurationService().env_vars[ConfigurationService().k] = os.getenv(
                                ConfigurationService().var_name, '')
                        else:
                            ConfigurationService(
                            ).env_vars[ConfigurationService().k] = v
                for arg in cfg['args']:
                    if arg.startswith('${') and arg.endswith('}'):
                        ConfigurationService().final_args.append(
                            os.getenv(arg[2:-1], ''))
                    else:
                        ConfigurationService().final_args.append(arg)
                server_params = StdioServerParameters(
                    COMMAND=cfg['command'],
                    args=ConfigurationService().final_args,
                    env=ConfigurationService().env_vars)
                async with stdio_client(server_params) as session:
                    await session.initialize()
                    self.sessions[name] = session
                    self.logger.info(f'Connected to {name}')
            except Exception as e:
self.logger.error(
                    f'Failed to connect to {name}: {e}')


    async def get_tools_for_llm(self: Any) -> List[Dict[str, Any]]:
        """Returns tools formatted for OpenAI/Anthropic.

        Returns:
            List of tool definitions with namespaced names
        """
        all_tools = []
        for name, session in self.sessions.items():
            try:
                tool_list = await session.list_tools()
                for tool in tool_list.tools:
                    all_tools.append({'name': f'{name}__{tool.name}',
                                     'description': f'[{name}] {tool.description}',
                                     'input_schema': tool.inputSchema})
            except Exception as e:
self.logger.warning(
                    f'Could not list tools for {name}: {e}')
        return all_tools


    async def execute_tool(self: Any, namespaced_tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool on the appropriate MCP server.

        Args:
            namespaced_tool_name: Tool name in format 'server__tool'
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            server_name, tool_name = namespaced_tool_name.split('__', 1)
            if server_name not in self.sessions:
                raise ValueError(f'Server {server_name} not connected')
            result = await self.sessions[server_name].call_tool(tool_name, arguments=arguments)
            return result.content
        except Exception as e:
return f'Error executing {namespaced_tool_name}: {str(e)}'


    async def cleanup(self: Any) -> None:
        """Cleanup all MCP server connections."""
        await self.exit_stack.aclose()

