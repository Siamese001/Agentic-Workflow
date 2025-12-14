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
        self.available_tools: List[Dict] = []
        self.tool_to_session: Dict[str, ClientSession] = {}
        
        logger.info("MCP Connection Manager initialized")

    async def connect_servers(self, role: str):
        """
        Connects to all MCP servers mapped to this specific role.
        
        Args:
            role: The agent role (e.g., "RESEARCHER", "CODER")
        """
        server_configs = self.mappings.get("defaults", []) + \
                        self.mappings.get("roles", {}).get(role, [])
        
        if not server_configs:
            logger.warning(f"No MCP servers configured for role: {role}")
            return
        
        logger.info(f"Connecting to {len(server_configs)} MCP servers for role: {role}")
        
        for config in server_configs:
            try:
                await self._connect_server(config)
            except Exception as e:
                logger.error(f"Failed to connect to server {config.get('server')}: {e}")
                continue
        
        logger.info(f"Connected to {len(self.sessions)} MCP servers. "
                   f"Discovered {len(self.available_tools)} tools.")

    async def _connect_server(self, config: Dict[str, Any]):
        """
        Connect to a single MCP server.
        
        Args:
            config: Server configuration dictionary
        """
        server_name = config.get("server", "unknown")
        
        env = os.environ.copy()
        env.update(config.get("env", {}))
        
        for key, value in env.items():
            if value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env[key] = os.environ.get(env_var, "")
        
        params = StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env=env
        )
        
        logger.debug(f"Connecting to MCP server: {server_name}")
        
        transport = await self.exit_stack.enter_async_context(stdio_client(params))
        read, write = transport
        
        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        
        await session.initialize()
        self.sessions.append(session)
        
        tools_result = await session.list_tools()
        
        for tool in tools_result.tools:
            tool_dict = {
                "name": tool.name,
                "description": tool.description,
                "server": server_name,
                "input_schema": getattr(tool, 'inputSchema', {})
            }
            self.available_tools.append(tool_dict)
            self.tool_to_session[tool.name] = session
        
        logger.info(f"Connected to {server_name}: {len(tools_result.tools)} tools discovered")

    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        Router: Finds the right server for the requested tool and executes it.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found in any connected server
        """
        session = self.tool_to_session.get(tool_name)
        
        if not session:
            raise ValueError(f"Tool '{tool_name}' not found in any connected MCP server. "
                           f"Available tools: {[t['name'] for t in self.available_tools]}")
        
        logger.debug(f"Executing MCP tool: {tool_name} with args: {arguments}")
        
        try:
            result = await session.call_tool(tool_name, arguments)
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            raise

    def get_tools_schema(self) -> List[Dict]:
        """
        Returns the schema of all available tools for LLM consumption.
        
        Returns:
            List of tool schemas
        """
        return self.available_tools

    async def cleanup(self):
        """Cleanup all MCP connections."""
        logger.info("Cleaning up MCP connections...")
        await self.exit_stack.aclose()
        self.sessions.clear()
        self.available_tools.clear()
        self.tool_to_session.clear()
        logger.info("MCP connections closed")


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
