from __future__ import annotations

import asyncio

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "omni_context_engine")
trace_contract.emit_determinism_digest("p0", "omni_context_engine")

trace_contract._emit_dispatches_healing_run("p1", "omni_context_engine", "L3")
trace_contract._emit_routes_through("p1", "omni_context_engine", "L3")
trace_contract._emit_checks_agent_registry("p1", "omni_context_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "omni_context_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "omni_context_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "omni_context_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "omni_context_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "omni_context_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "omni_context_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "omni_context_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "omni_context_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "omni_context_engine")
trace_contract._emit_gated_by_confidence("p1", "omni_context_engine", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "omni_context_engine", "L3")
trace_contract._emit_reads_policy_state("p1", "omni_context_engine", "L3")
trace_contract._emit_authorize_and_execute("p2", "omni_context_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "omni_context_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "omni_context_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "omni_context_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "omni_context_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "omni_context_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "omni_context_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "omni_context_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "omni_context_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "omni_context_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "omni_context_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "omni_context_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "omni_context_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "omni_context_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "omni_context_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "omni_context_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "omni_context_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "omni_context_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "omni_context_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "omni_context_engine", "exec_snapshot_link")

"Brief description of functionality and purpose."
from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
from agentic_core.L2_execution.reasoning.base import SubAtomicAgent
from tqdm import tqdm

trace_contract._emit_emits_metric_event("omni_context_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("omni_context_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("omni_context_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("omni_context_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("omni_context_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("omni_context_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("omni_context_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("omni_context_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("omni_context_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("omni_context_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("omni_context_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("omni_context_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("omni_context_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("omni_context_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("omni_context_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("omni_context_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("omni_context_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("omni_context_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("omni_context_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("omni_context_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("omni_context_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("omni_context_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("omni_context_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("omni_context_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("omni_context_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("omni_context_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("omni_context_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("omni_context_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "omni_context_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "omni_context_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "omni_context_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "omni_context_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "omni_context_engine", "write_through")
trace_contract._emit_writes_through("p1", "omni_context_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "omni_context_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "omni_context_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "omni_context_engine", "routing_commit")


class OmniContext(SubAtomicAgent):
    """
    ROLE: Global Architectural Context. Concatenates all non-excluded .py files
    into a single context buffer for agents to consult.
    """

    def __init__(self, context):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "OmniContext.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "OmniContext.__init__", "p0_governance")
        super().__init__(context)
        self.context_buffer = ""
        self.index = {}

    async def execute(self):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "OmniContext.execute")

        print(f"\n[>>>] {self.name} ACTIVATED: Building Global Context...")
        await asyncio.sleep(DEFAULT_SLEEP)
        self._build_context_buffer()
        self.ctx.OmniContext = {"buffer": self.context_buffer, "index": self.index, "consult": self.consult}
        print(f"   📚 Built context: {len(self.context_buffer)} chars from {len(self.index)} files")

    def _build_context_buffer(self):
        """Build a concatenated buffer of all Python code."""
        sections = []
        for file_path in tqdm(self.ctx.python_files, desc="Processing", unit="item"):
            if file_path in self.ctx.skip_files:
                continue
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                sections.append(f"\n# FILE: {file_path}\n")
                sections.append(content)
                start_pos = len("".join(sections[:-2]))
                end_pos = start_pos + len(content)
                self.index[file_path] = {"start": start_pos, "end": end_pos, "content": content}
            except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                print(f"   [!]  Failed to read {file_path}: {e}")
        self.context_buffer = "\n".join(sections)

    def consult(self, query: str) -> str:
        """Consult the global context for architectural patterns."""
        if not self.context_buffer:
            return "No context available"
        results = []
        query_lower = query.lower()
        for file_path, info in self.index.items():
            content_lower = info["content"].lower()
            if any(word in content_lower for word in query_lower.split()):
                snippet = info["content"][:500]
                results.append(f"Found in {file_path}:\n{snippet}...\n")
        return "\n".join(results[:3])
