from __future__ import annotations

try:
    from .filesystem_mcp import FilesystemMCP
except ImportError:

    class FilesystemMCP:
        def __init__(self, *args, **kwargs):
            print("   [STUB] FilesystemMCP active — direct filesystem operations permitted")

        def execute_move(self, source, target, **kwargs):
            return {"status": "allowed", "method": "direct"}

        def execute_write(self, path, content):
            return {"status": "allowed"}


print("   [OK] agentic_core.L4_state.memory package initialized (stub mode)")
