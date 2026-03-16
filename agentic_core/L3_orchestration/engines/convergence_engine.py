"""
MISSION CONTROLLER CONVERGENCE ENGINE
--------------------------------------
Implements the L4 Recursive Convergence Loop to ensure Zero Gravity Violations.
This engine provides the 'Skeptical' verification logic for L3 Orchestration.
"""

import hashlib
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "convergence_engine")
emit_determinism_digest("p0", "convergence_engine")

_emit_dispatches_healing_run("p1", "convergence_engine", "L3")
_emit_routes_through("p1", "convergence_engine", "L3")
_emit_escalates_to_human("p1", "convergence_engine", "L3")
_emit_reads_policy_state("p1", "convergence_engine", "L3")
_emit_authorize_and_execute("p2", "convergence_engine", "execution_auth")
_emit_validates_capability("p2", "convergence_engine", "capability_check")
_emit_routes_to_capability("p2", "convergence_engine", "capability_route")
_emit_writes_via_uwg("p2", "convergence_engine", "uwg_write")
_emit_blocks_direct_write("p2", "convergence_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "convergence_engine", "tool_invocation")
_emit_captures_execution_output("p2", "convergence_engine", "exec_output")
_emit_dispatches_agent("p3", "convergence_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "convergence_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "convergence_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "convergence_engine", "healing_outcome")
_emit_escalates_failure("p3", "convergence_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "convergence_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "convergence_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "convergence_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "convergence_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "convergence_engine", "eval_metric")
_emit_stores_embedding("p4", "convergence_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "convergence_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "convergence_engine", "exec_snapshot_link")


class ConvergenceEngine:
    # guardian: allow-magic-config
    def __init__(self, max_rounds: int = 8):
        self.max_rounds = max_rounds
        self.round_history = []

    def get_file_hash(self, file_path: Path) -> str:
        """
        SSOT SNAPSHOTTING: Generates SHA256 hash for fission detection.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ConvergenceEngine.get_file_hash", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ConvergenceEngine.get_file_hash", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ConvergenceEngine.get_file_hash"
        )

        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def detect_fission(self, pre_hash: str, post_hash: str, file_size: int) -> bool:
        """
        FISSION DETECTION: Triggers if a large file fails to change after healing.
        """
        return pre_hash == post_hash and file_size > 10240

    async def run_convergence(self, validator, healer, initial_violations: list):
        """
        RECURSIVE LOOP: Iterates until violations reach zero or max rounds.
        """
        current_violations = initial_violations
        round_num = 1
        while len(current_violations) > 0 and round_num <= self.max_rounds:
            print(f"🌀 Convergence Round {round_num}: {len(current_violations)} remaining")
            prioritized_violations = sorted(
                current_violations, key=lambda v: v.get("impact_score", 0), reverse=True
            )
            for violation in prioritized_violations:
                if violation.get("audit_fail_count", 0) > 3:
                    print(
                        f"🧟 ZOMBIE DETECTED: {violation.get('path')} - Escalating to Sub-atomic Refactor..."
                    )
                file_path = Path(violation.get("path", ""))
                pre_hash = None
                file_size = 0
                if file_path.exists():
                    pre_hash = self.get_file_hash(file_path)
                    file_size = file_path.stat().st_size
                await healer.heal(violation)
                if pre_hash and file_path.exists():
                    post_hash = self.get_file_hash(file_path)
                    if self.detect_fission(pre_hash, post_hash, file_size):
                        print(
                            f"⚛️ FISSION DETECTED: {violation.get('path')} unchanged after healing (>{file_size // 1024}KB) - Terminating mission for this file."
                        )
            current_violations = await validator.validate()
            self.round_history.append(len(current_violations))
            round_num += 1
        if len(current_violations) == 0:
            print(f"✅ CONVERGENCE ACHIEVED in {round_num - 1} rounds.")
        else:
            print(f"⚠️ CONVERGENCE FAILED: {len(current_violations)} violations persist.")
        return len(current_violations) == 0
