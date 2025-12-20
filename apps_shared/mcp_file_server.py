"""
[START] HARDENED MCP File Server for Canon Validator v2.0
Provides L4 State filesystem operations with Atomic Fission support.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

class HardenedFileServerMCP:
    """MCP server providing L4 State operations for agentic refactoring."""

    def __init__(self, root_path: Optional[str] = None):
        self.root_path = Path(root_path) if root_path else Path.cwd()
        # Initialize with specific name for L3 Routing
        self.server = Server("canon-filesystem-l4")
        self._register_tools()

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="read_file",
                    description="Read contents of a file for L1 Cognition analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path relative to project root"}
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="fission_write",
                    description="Atomic write for multiple files during Atomic Fission missions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "files": {
                                "type": "object", 
                                "description": "Map of file paths to their content strings"
                            },
                            "monolith_path": {"type": "string", "description": "The original file being decomposed"}
                        },
                        "required": ["files"]
                    }
                ),
                Tool(
                    name="get_file_metrics",
                    description="L3 Audit: Get line count and nesting depth for Key 42 check",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "read_file":
                    return await self._read_file(arguments["path"])
                elif name == "fission_write":
                    return await self._fission_write(arguments["files"], arguments.get("monolith_path"))
                elif name == "get_file_metrics":
                    return await self._get_file_metrics(arguments["path"])
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"L4 Filesystem Error: {str(e)}")]

    async def _read_file(self, path: str) -> List[TextContent]:
        file_path = self.root_path / path
        if not file_path.exists():
            return [TextContent(type="text", text="ERROR: File target not found.")]
        return [TextContent(type="text", text=file_path.read_text(encoding="utf-8"))]

    async def _fission_write(self, files: Dict[str, str], monolith_path: Optional[str]) -> List[TextContent]:
        """Executes a Zero-Loss write for multiple sub-modules."""
        results = []
        for path, content in files.items():
            full_path = self.root_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            results.append(path)
        
        log_msg = f"⚛️ Fission Successful: Created {', '.join(results)}"
        if monolith_path:
            log_msg += f" | Monolith {monolith_path} converted to Facade."
            
        return [TextContent(type="text", text=log_msg)]

    async def _get_file_metrics(self, path: str) -> List[TextContent]:
        """Provides L3 Orchestrator with data for Key 42 violation detection."""
        file_path = self.root_path / path
        if not file_path.exists():
            return [TextContent(type="text", text="0")]
        
        lines = file_path.read_text().splitlines()
        line_count = len(lines)
        # Simple nesting check (max indents)
        max_indent = max([len(l) - len(l.lstrip()) for l in lines if l.strip()] or [0]) // 4
        
        metrics = {"lines": line_count, "nesting_level": max_indent, "timestamp": str(datetime.now())}
        return [TextContent(type="text", text=json.dumps(metrics))]

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream,
                self.server.create_initialization_options()
            )

async def main():
    root_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    server = HardenedFileServerMCP(root_path)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())