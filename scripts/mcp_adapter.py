from typing import Any
"""Universal MCP Client Adapter for Agentic Workflow.

Manages async lifecycle of multiple MCP servers and aggregates their tools
for use by executive agents.
"""

import os
import json
import logging
from contextlib import AsyncExitStack
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class UniversalMCPClient:
    """Universal adapter for managing multiple MCP server connections."""

    def __init__(self, config_path: str = "config/mcp_server_config.json"):
        self.config_path = config_path
        self.servers = {}
        self.logger = logging.getLogger(__name__)
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}

    async def connect_all(self):
        """Initializes connections to all servers defined in JSON."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config not found at {self.config_path}")

        with open(self.config_path) as f:
            config_data = json.load(f)

        self.logger.info(f"MCP: Connecting to {len(config_data['mcpServers'])} servers...")

        for name, cfg in config_data['mcpServers'].items():
            try:
                # Handle Env Var Expansion
                env_vars = os.environ.copy()
                if "env" in cfg:
                    for k, v in cfg["env"].items():
                        if v.startswith("${") and v.endswith("}"):
                            var_name = v[2:-1]
                            env_vars[k] = os.getenv(var_name, "")
                        else:
                            env_vars[k] = v

                # Expand args if needed
                final_args = []
                for arg in cfg["args"]:
                    if arg.startswith("${") and arg.endswith("}"):
                        final_args.append(os.getenv(arg[2:-1], ""))
                    else:
                        final_args.append(arg)

                server_params = StdioServerParameters(
                    command=cfg["command"],
                    args=final_args,
                    env=env_vars
                )

                transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                read, write = transport
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                self.sessions[name] = session
                self.logger.info(f"Connected to {name}")

            except Exception as e:
                self.logger.error(f"Failed to connect to {name}: {e}")

    async def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Returns tools formatted for OpenAI/Anthropic.

        Returns:
            List of tool definitions with namespaced names
        """
        all_tools = []
        for name, session in self.sessions.items():
            try:
                result = await session.list_tools()
                for tool in result.tools:
                    # Namespace tools: 'browser__navigate', 'filesystem__read_file'
                    all_tools.append({
                        "name": f"{name}__{tool.name}",
                        "description": f"[{name}] {tool.description}",
                        "input_schema": tool.inputSchema
                    })
            except Exception as e:
                self.logger.warning(f"Could not list tools for {name}: {e}")
        return all_tools

    async def execute_tool(self, namespaced_tool_name: str, arguments: Dict[str, Any]):
        """Execute a tool on the appropriate MCP server.

        Args:
            namespaced_tool_name: Tool name in format 'server__tool'
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            server_name, tool_name = namespaced_tool_name.split("__", 1)
            if server_name not in self.sessions:
                raise ValueError(f"Server {server_name} not connected")

            result = await self.sessions[server_name].call_tool(tool_name, arguments=arguments)
            return result.content
        except Exception as e:
            return f"Error executing {namespaced_tool_name}: {str(e)}"

    async def cleanup(self):
        """Cleanup all MCP server connections."""
        await self.exit_stack.aclose()
