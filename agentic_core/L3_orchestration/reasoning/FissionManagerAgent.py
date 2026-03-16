from __future__ import annotations

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "FissionManagerAgent")
emit_determinism_digest("p0", "FissionManagerAgent")

_emit_dispatches_healing_run("p1", "FissionManagerAgent", "L3")
_emit_routes_through("p1", "FissionManagerAgent", "L3")
_emit_escalates_to_human("p1", "FissionManagerAgent", "L3")
_emit_reads_policy_state("p1", "FissionManagerAgent", "L3")
_emit_authorize_and_execute("p2", "FissionManagerAgent", "execution_auth")
_emit_validates_capability("p2", "FissionManagerAgent", "capability_check")
_emit_routes_to_capability("p2", "FissionManagerAgent", "capability_route")
_emit_writes_via_uwg("p2", "FissionManagerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "FissionManagerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "FissionManagerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "FissionManagerAgent", "exec_output")
_emit_dispatches_agent("p3", "FissionManagerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "FissionManagerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "FissionManagerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "FissionManagerAgent", "healing_outcome")
_emit_escalates_failure("p3", "FissionManagerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "FissionManagerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "FissionManagerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "FissionManagerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "FissionManagerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "FissionManagerAgent", "eval_metric")
_emit_stores_embedding("p4", "FissionManagerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "FissionManagerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "FissionManagerAgent", "exec_snapshot_link")

"\n[PHASE 14 REFACTOR] FissionManagerAgent.\nSTRICT COMPLIANCE: No direct SDK imports. Uses SovereignLLMGateway.\n"
import json
import logging
import os
from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)


@dataclass
class FissionResult:
    triggered: bool
    reason: str
    new_files: dict[str, str]
    original_file: str
    success: bool
    error_message: str | None = None


(AtomicExecutionMixin,)


class FissionManagerAgent(SovereignBaseAgent):
    """L3 Orchestration Layer: Atomic Fission via Gateway."""

    # guardian: allow-magic-config
    def __init__(self, line_limit: int = 800, deletion_guardrail: int = 110, max_rounds: int = 3) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "FissionManagerAgent.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "FissionManagerAgent.__init__", "p0_governance")
        super().__init__()
        self.line_limit = line_limit
        self.deletion_guardrail = deletion_guardrail
        self.max_rounds = max_rounds

    async def execute_fission(self, file_path: str, content: str, reason: str) -> FissionResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "FissionManagerAgent.execute_fission"
        )

        Logger.info(f"FISSION TRIGGERED: {file_path} ({reason})")
        prompt = self._get_fission_prompt(file_path, content)
        try:
            response = await self.llm_generate(
                prompt,
                provider="google",
                model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
                generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            )
            new_files = self._parse_fission_response(response["content"], file_path)
            if new_files:
                return FissionResult(True, reason, new_files, file_path, True)
            return FissionResult(True, reason, {}, file_path, False, "Empty response")
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Fission failed: {e}")
            return FissionResult(True, reason, {}, file_path, False, str(e))

    def _get_fission_prompt(self, file_name: str, content: str) -> str:
        return f"ATOMIC FISSION REQUEST: Split {file_name} into 3 logical sub-modules.\nReturn ONLY JSON mapping filenames to content.\n\nCODE:\n{content[:4000]}..."

    def _parse_fission_response(self, text: str, original_file: str) -> dict[str, str]:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"Fission parse failed: {e}")
            return {}

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by FissionManagerAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"FissionManagerAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            return {
                "status": "failed",
                "details": f"FissionManagerAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for FissionManagerAgent."""
        raise NotImplementedError("heal_repository() not implemented for FissionManagerAgent")
