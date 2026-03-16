from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "CodeFormatterAgent")
emit_determinism_digest("p0", "CodeFormatterAgent")

_emit_dispatches_healing_run("p1", "CodeFormatterAgent", "L5")
_emit_routes_through("p1", "CodeFormatterAgent", "L5")
_emit_escalates_to_human("p1", "CodeFormatterAgent", "L5")
_emit_reads_policy_state("p1", "CodeFormatterAgent", "L5")

_emit_applies_guardrail("p0", "CodeFormatterAgent", "p0_governance")
_emit_snapshots_state("p0", "CodeFormatterAgent", "state_snapshot")

'Code Formatter Agent - Enforces consistent formatting using Black + Ruff.\n\nThis module provides an atomic agent that enforces consistent code formatting\nacross Python files using Black for formatting and Ruff for linting auto-fixes.\n\nTypical usage:\n    agent = CodeFormatterAgent(project_root="/path/to/project", ctx=context)\n    result = await agent.execute(file_path="src/module.py")\n'
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.utils.security_util import safe_execute

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_tool_runner_core_util import CodeToolRunnerCapability
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass
class CodeFormatterAgent(CodeToolRunnerCapability, SovereignBaseAgent):
    """L5 Safety agent that enforces consistent formatting using Black + Ruff.

    This atomic agent applies Black formatting and Ruff lint auto-fixes to
    Python files, ensuring consistent code style across the project.

    Architecture (Composition over Inheritance):
        - SovereignBaseAgent: Provides sovereign infrastructure (config, healing, telemetry)
        - CodeToolRunnerCapability: Provides shared heal_repository, heal plumbing
        - This class: Provides execute() with Black + Ruff logic
    """

    ctx: Any = field(default=None)

    # guardian: allow-type-erasure
    async def execute(self, file_path: str) -> dict[str, Any]:
        """Format a single file using Black and Ruff.

        Applies Black formatting first, then Ruff lint auto-fixes.
        Reports errors through the context if available.

        Args:
            file_path: Path to the Python file to format.

        Returns:
            Dictionary with formatting results:
                - healed: Whether any changes were made
                - action: Description of action taken (if healed)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "CodeFormatterAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CodeFormatterAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        file: Path = Path(file_path)
        if not file.exists():
            return {"healed": False}
        changed: bool = False
        try:
            black_result = safe_execute(
                ["black", "--quiet", str(file)], capture_output=True, text=True, check=False
            )
            if black_result.returncode == 0 and "reformatted" in black_result.stderr:
                changed = True
            ruff_result = safe_execute(
                ["ruff", "check", "--fix", "--quiet", str(file)], capture_output=True, check=False
            )
            if ruff_result.returncode == 0:
                pass
            if changed:
                print(f"   [OK] Formatted: {file_path}")
                return {"healed": True, "action": "formatted"}
        except FileNotFoundError as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report("CodeFormatterAgent", 0, False, f"Tool Missing: {e.filename}")
        # guardian: allow-silent-swallow
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report("CodeFormatterAgent", 0, False, f"Format error: {e}")
        return {"healed": changed}

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for CodeFormatterAgent."""
        raise NotImplementedError("heal_repository() not implemented for CodeFormatterAgent")
