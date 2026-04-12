#!/usr/bin/env python3
"""
Terminal MCP Server - Safe command execution with repo restrictions
Provides terminal access for Windsurf with safety guards and command whitelisting
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.lowlevel.server import NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError:
    print("MCP SDK not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging - use stderr to avoid interfering with MCP protocol on stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Safety configuration
ALLOWED_COMMANDS = {
    "python",
    "pytest",
    "git",
    "ls",
    "cat",
    "pwd",
    "cd",
    "echo",
    "find",
    "grep",
    "head",
    "tail",
    "wc",
    "sort",
    "uniq",
    "cut",
    "mkdir",
    "touch",
    "cp",
    "mv",
    "rm",
    "chmod",
    "chown",
    "pip",
    "uv",
    "node",
    "npm",
}

DANGEROUS_PATTERNS = {
    "rm -rf /",
    "rm -rf /*",
    "sudo rm",
    "format",
    "fdisk",
    "mkfs",
    "dd if=",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    ">:>",
    ">>/dev/",
    ">/dev/null",
    "curl | sh",
    "wget | sh",
}

# Repo root restriction
REPO_ROOT = Path(__file__).parent.parent.parent
MAX_EXECUTION_TIME = 30  # seconds
MAX_OUTPUT_SIZE = 10000  # characters


class TerminalMCPServer:
    def __init__(self):
        self.server = Server("terminal")
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available terminal tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="execute_command",
                        description="Execute a terminal command with safety restrictions",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Command to execute",
                                },
                                "cwd": {
                                    "type": "string",
                                    "description": "Working directory (must be within repo)",
                                    "default": str(REPO_ROOT),
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds (max 30)",
                                    "default": 10,
                                    "maximum": 30,
                                },
                            },
                            "required": ["command"],
                        },
                    ),
                    Tool(
                        name="check_command_safety",
                        description="Check if a command is safe to execute",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Command to check",
                                },
                            },
                            "required": ["command"],
                        },
                    ),
                    Tool(
                        name="list_allowed_commands",
                        description="List all allowed commands",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                ],
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "execute_command":
                    return await self._execute_command(arguments)
                elif name == "check_command_safety":
                    return await self._check_command_safety(arguments)
                elif name == "list_allowed_commands":
                    return await self._list_allowed_commands()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    async def _execute_command(self, args: dict[str, Any]) -> CallToolResult:
        """Execute a command with safety checks"""
        command = args["command"]
        cwd = Path(args.get("cwd", str(REPO_ROOT)))
        timeout = min(args.get("timeout", 10), MAX_EXECUTION_TIME)

        # Safety checks
        safety_result = await self._check_command_safety({"command": command})
        if "UNSAFE" in safety_result.content[0].text:
            return safety_result

        # Verify working directory is within repo
        try:
            cwd.resolve().relative_to(REPO_ROOT.resolve())
        except ValueError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"ERROR: Working directory {cwd} is outside repository root {REPO_ROOT}",
                    )
                ],
                isError=True,
            )

        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True,
                check=False,
            )

            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

            # Truncate output if too large
            if len(output) > MAX_OUTPUT_SIZE:
                output = output[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Exit Code: {result.returncode}\n\nOutput:\n{output}",
                    )
                ],
            )

        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Command timed out after {timeout} seconds",
                    )
                ],
                isError=True,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Execution error: {str(e)}")],
                isError=True,
            )

    async def _check_command_safety(self, args: dict[str, Any]) -> CallToolResult:
        """Check if a command is safe to execute"""
        command = args["command"].lower()

        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern in command:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"UNSAFE: Command contains dangerous pattern: {pattern}",
                        )
                    ],
                    isError=True,
                )

        # Check if command starts with allowed command
        first_word = command.split()[0] if command.split() else ""
        if first_word not in ALLOWED_COMMANDS:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"UNSAFE: Command '{first_word}' not in allowed commands",
                    )
                ],
                isError=True,
            )

        # Check for path traversal attempts
        if "../" in command or "..\\" in command:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="UNSAFE: Path traversal detected",
                    )
                ],
                isError=True,
            )

        return CallToolResult(
            content=[TextContent(type="text", text="SAFE: Command passed safety checks")],
        )

    async def _list_allowed_commands(self, args: dict[str, Any]) -> CallToolResult:
        """List all allowed commands"""
        commands = sorted(ALLOWED_COMMANDS)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Allowed commands:\n" + "\n".join(f"- {cmd}" for cmd in commands),
                )
            ],
        )


async def main():
    """Main entry point"""
    server_instance = TerminalMCPServer()

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="terminal",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(
                        prompts_changed=False,
                        resources_changed=False,
                        tools_changed=False,
                    ),
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Terminal MCP Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
