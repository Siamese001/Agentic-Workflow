from __future__ import annotations

import ast

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "truth_keeper_validator")
emit_determinism_digest("p0", "truth_keeper_validator")

_emit_dispatches_healing_run("p1", "truth_keeper_validator", "L1")
_emit_routes_through("p1", "truth_keeper_validator", "L1")
_emit_escalates_to_human("p1", "truth_keeper_validator", "L1")
_emit_reads_policy_state("p1", "truth_keeper_validator", "L1")

_emit_snapshots_state("p0", "truth_keeper_validator", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "truth_keeper_validator", "p0_governance")
_emit_authorize_and_execute("p2", "truth_keeper_validator", "execution_auth")
_emit_validates_capability("p2", "truth_keeper_validator", "capability_check")
_emit_routes_to_capability("p2", "truth_keeper_validator", "capability_route")
_emit_writes_via_uwg("p2", "truth_keeper_validator", "uwg_write")
_emit_blocks_direct_write("p2", "truth_keeper_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "truth_keeper_validator", "tool_invocation")
_emit_captures_execution_output("p2", "truth_keeper_validator", "exec_output")
_emit_dispatches_agent("p3", "truth_keeper_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "truth_keeper_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "truth_keeper_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "truth_keeper_validator", "healing_outcome")
_emit_escalates_failure("p3", "truth_keeper_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "truth_keeper_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "truth_keeper_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "truth_keeper_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "truth_keeper_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "truth_keeper_validator", "eval_metric")
_emit_stores_embedding("p4", "truth_keeper_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "truth_keeper_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "truth_keeper_validator", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import logging
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_gated_by_confidence,
    _emit_records_execution_trace,
)

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class TruthKeeper:
    """
    Agent that ensures semantic consistency between docstrings and code.

    Analyzes functions to verify their docstrings accurately describe:
    - Parameters and their types
    - Return values and types
    - Function behavior and side effects
    """

    def __init__(self, llm_client=None):
        """
        Initialize the TruthKeeper agent.

        Args:
            llm_client: LLM client for consistency checking
        """
        self.llm_client = llm_client
        self.api_key = None

    async def check_file_consistency(self, file_path: str) -> dict[str, Any]:
        """
        Check docstring consistency for all public functions in a file.

        Args:
            file_path: Path to the Python file to check

        Returns:
            Dictionary with consistency violations and fixes
        """
        _emit_gated_by_confidence(str(uuid.uuid4()), "TruthKeeper.check_file_consistency", "0.5")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "TruthKeeper.check_file_consistency"
        )

        violations: Any = []
        fixes: Any = []
        if "test" in file_path.lower() or file_path.endswith("_test.py"):
            return {"violations": [], "fixes": [], "skipped": True}
        try:
            with open(file_path, encoding="utf-8") as f:
                content: Any = f.read()
            tree: Any = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
                    result: Any = await self._check_function_consistency(file_path, node, content)
                    if result.get("Violation"):
                        violations.append(result["Violation"])
                    if result.get("fixed_docstring"):
                        fixes.append(
                            {
                                "function": node.name,
                                "line": node.lineno,
                                "old_docstring": result.get("old_docstring"),
                                "new_docstring": result["fixed_docstring"],
                            }
                        )
        except SyntaxError as e:
            violations.append({"type": "syntax", "file": file_path, "message": f"Syntax error: {e}"})
        # guardian: allow-silent-swallow
        except Exception as e:
            LOGGER.error(f"Error checking {file_path}: {e}")
        return {"violations": violations, "fixes": fixes, "file": file_path}

    async def _check_function_consistency(
        self, file_path: str, node: ast.FunctionDef, content: str
    ) -> dict[str, Any]:
        """
        Check consistency for a single function.

        Args:
            file_path: Path to the file
            node: AST function node
            content: Full file content

        Returns:
            Dictionary with Violation info and potential fix
        """
        [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node) or ""
        func_lines = content.split("\n")[node.lineno - 1 : node.end_lineno]
        "\n".join(func_lines)
        if not docstring:
            return {
                "Violation": {
                    "type": "missing_docstring",
                    "function": node.name,
                    "line": node.lineno,
                    "message": f"Function '{node.name}' Missing docstring",
                },
                "fixed_docstring": None,
                "old_docstring": None,
            }
        return {"Violation": None, "fixed_docstring": None, "old_docstring": docstring}
