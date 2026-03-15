from __future__ import annotations

'Unused Cleanup Agent - Removes unused imports and variables using autoflake.\n\nThis module provides an atomic agent that removes unused imports and variables\nfrom Python files using the autoflake tool.\n\nTypical usage:\n    agent = UnusedCleanupAgent(project_root="/path/to/project", ctx=context)\n    result = await agent.execute(file_path="src/module.py")\n'
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_tool_runner_core_util import CodeToolRunnerCapability
from agentic_core.utils.security_util import safe_execute
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


@dataclass
class UnusedCleanupAgent(CodeToolRunnerCapability, SovereignBaseAgent):
    """L5 Safety agent that removes unused imports and variables using autoflake.

    This atomic agent uses autoflake to clean up unused imports and variables
    from Python files.

    Architecture (Composition over Inheritance):
        - SovereignBaseAgent: Provides sovereign infrastructure (config, healing, telemetry)
        - CodeToolRunnerCapability: Provides shared heal_repository, heal plumbing
        - This class: Provides execute() with autoflake logic
    """

    ctx: Any = field(default=None)

    # guardian: allow-type-erasure
    async def execute(self, file_path: str) -> dict[str, Any]:
        """
        Remove unused imports and variables from a single file.

        Args:
            file_path: Path to file to clean

        Returns:
            Dict with healed status and action taken
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "UnusedCleanupAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:UnusedCleanupAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        file: Path = Path(file_path)
        if not file.exists():
            return {"healed": False}
        try:
            result = safe_execute(
                [
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    str(file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return {"healed": True, "action": "unused_removed"}
        except FileNotFoundError:
            return {"healed": False, "error": "autoflake not installed"}
        return {"healed": False}

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for UnusedCleanupAgent."""
        raise NotImplementedError("heal_repository() not implemented for UnusedCleanupAgent")
