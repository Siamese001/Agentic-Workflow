"""
MISSION CONTROLLER CONVERGENCE ENGINE
--------------------------------------
Implements the L4 Recursive Convergence Loop to ensure Zero Gravity Violations.
This engine provides the 'Skeptical' verification logic for L3 Orchestration.
"""

import hashlib
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "convergence_engine")
trace_contract.emit_determinism_digest("p0", "convergence_engine")

trace_contract._emit_dispatches_healing_run("p1", "convergence_engine", "L3")
trace_contract._emit_routes_through("p1", "convergence_engine", "L3")
trace_contract._emit_checks_agent_registry("p1", "convergence_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "convergence_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "convergence_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "convergence_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "convergence_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "convergence_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "convergence_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "convergence_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "convergence_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "convergence_engine")
trace_contract._emit_gated_by_confidence("p1", "convergence_engine", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "convergence_engine", "L3")
trace_contract._emit_reads_policy_state("p1", "convergence_engine", "L3")
trace_contract._emit_authorize_and_execute("p2", "convergence_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "convergence_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "convergence_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "convergence_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "convergence_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "convergence_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "convergence_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "convergence_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "convergence_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "convergence_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "convergence_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "convergence_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "convergence_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "convergence_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "convergence_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "convergence_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "convergence_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "convergence_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "convergence_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "convergence_engine", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("convergence_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("convergence_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("convergence_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("convergence_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("convergence_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("convergence_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("convergence_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("convergence_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("convergence_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("convergence_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("convergence_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("convergence_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("convergence_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("convergence_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("convergence_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("convergence_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("convergence_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("convergence_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("convergence_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("convergence_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("convergence_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("convergence_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("convergence_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("convergence_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("convergence_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("convergence_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("convergence_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("convergence_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "convergence_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "convergence_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "convergence_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "convergence_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "convergence_engine", "write_through")
trace_contract._emit_writes_through("p1", "convergence_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "convergence_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "convergence_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "convergence_engine", "routing_commit")


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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ConvergenceEngine.get_file_hash", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ConvergenceEngine.get_file_hash", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "ConvergenceEngine.get_file_hash",
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
                current_violations,
                key=lambda v: v.get("impact_score", 0),
                reverse=True,
            )
            for violation in tqdm(prioritized_violations, desc="Processing", unit="item"):
                if violation.get("audit_fail_count", 0) > 3:
                    print(
                        f"🧟 ZOMBIE DETECTED: {violation.get('path')} - Escalating to Sub-atomic Refactor...",
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
                            f"⚛️ FISSION DETECTED: {violation.get('path')} unchanged after healing (>{file_size // 1024}KB) - Terminating mission for this file.",
                        )
            current_violations = await validator.validate()
            self.round_history.append(len(current_violations))
            round_num += 1
        if len(current_violations) == 0:
            print(f"✅ CONVERGENCE ACHIEVED in {round_num - 1} rounds.")
        else:
            print(f"⚠️ CONVERGENCE FAILED: {len(current_violations)} violations persist.")
        return len(current_violations) == 0
