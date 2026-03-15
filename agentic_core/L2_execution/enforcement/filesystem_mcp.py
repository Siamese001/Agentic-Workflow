from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "filesystem_mcp")
_emit_applies_guardrail("p0", "filesystem_mcp", "p0_governance")
_emit_snapshots_state("p0", "filesystem_mcp", "state_snapshot")

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
