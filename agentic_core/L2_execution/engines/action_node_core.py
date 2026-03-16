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

emit_replay_key("p0", "action_node_core")
emit_determinism_digest("p0", "action_node_core")

_emit_dispatches_healing_run("p1", "action_node_core", "L2")
_emit_routes_through("p1", "action_node_core", "L2")
_emit_escalates_to_human("p1", "action_node_core", "L2")
_emit_reads_policy_state("p1", "action_node_core", "L2")

_emit_applies_guardrail("p0", "action_node_core", "p0_governance")
_emit_snapshots_state("p0", "action_node_core", "state_snapshot")

"\nCore Executor - Atomic Module\nExtracted from ActionNode.py via Atomic Fission Protocol\nHandles plan execution and step orchestration\n"
import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_transcripts_response,
)

Logger: Any = logging.getLogger("ActionNode.CoreExecutor")


class ActionNodeCore:
    """
    Core execution logic for ActionNode.
    Handles plan parsing and step orchestration.
    """

    TOOL_MAP: dict[str, str] = {
        "write_file": "write_file",
        "create_file": "write_file",
        "read_file": "read_file",
        "read": "read_file",
        "list_files": "list_files",
        "ls": "list_files",
        "run_command": "run_command",
        "execute": "run_command",
    }

    def __init__(self, work_dir: str, allowed_tools: dict[str, Any]):
        """
        Initialize core executor.

        Args:
            work_dir (str): Working directory path
            allowed_tools (Dict[str, Any]): Map of tool names to implementations
        """
        self.work_dir = Path(work_dir).resolve()
        self.allowed_tools = allowed_tools

    def execute_plan(self, plan: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a full plan sequence from the Cognitive Node.

        Args:
            plan (Dict[str, Any]): A dictionary representing the plan,
                                   expected to contain 'goal' and 'steps'.

        Returns:
            Dict[str, Any]: A dictionary containing the overall status and results
                            of each executed step.
        """
        _emit_transcripts_response(str(uuid.uuid4()), "ActionNodeCore.execute_plan", "model")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ActionNodeCore.execute_plan")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ActionNodeCore.execute_plan".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info(f"⚙️ Action Node received plan for goal: {plan.get('goal', 'N/A')}")
        results: list[dict[str, Any]] = []
        steps: list[dict[str, Any]] = plan.get("steps") or plan.get("plan", {}).get("steps", [])
        if not steps:
            Logger.warning("[!] Received empty plan. No actions taken.")
            return {"status": "skipped", "results": []}
        for step in steps:
            result: Any = self._execute_single_step(step)
            results.append(result)
            if result.get("status") == "error":
                Logger.error(f"🛑 Execution halted at step {step.get('step', 'N/A')}: {result.get('output')}")
                return {"status": "failed", "results": results}
        Logger.info("[OK] Plan execution completed successfully.")
        return {"status": "success", "results": results}

    def _execute_single_step(self, step: dict[str, Any]) -> dict[str, Any]:
        """
        Parses a single step, validates the tool, and executes it.

        Args:
            step (Dict[str, Any]): A dictionary representing a single action step,
                                   expected to contain 'action' and 'params'.

        Returns:
            Dict[str, Any]: A dictionary containing the step number, status, and output.
        """
        action_name: str = step.get("action", "").lower().replace(" ", "_")
        params: dict[str, Any] = step.get("params", {})
        step_number: int | str = step.get("step", "N/A")
        tool_key: str | None = self.TOOL_MAP.get(action_name)
        if not tool_key or tool_key not in self.allowed_tools:
            msg = f"[X] Tool '{action_name}' (mapped to '{tool_key}') is NOT whitelisted or recognized."
            Logger.warning(msg)
            return {"step": step_number, "status": "blocked", "output": msg}
        Logger.info(f"🔨 Executing Tool '{tool_key}' for step {step_number} with params: {params}")
        try:
            output: str = self.allowed_tools[tool_key](**params)
            return {"step": step_number, "status": "success", "output": output}
        except Exception as e:
            Logger.error(f"[X] Tool '{tool_key}' execution failed for step {step_number}: {e}", exc_info=True)
            return {"step": step_number, "status": "error", "output": str(e)}


__all__ = ["ActionNodeCore"]
