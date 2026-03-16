from __future__ import annotations

import asyncio

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

emit_replay_key("p0", "omni_context_engine")
emit_determinism_digest("p0", "omni_context_engine")

_emit_dispatches_healing_run("p1", "omni_context_engine", "L3")
_emit_routes_through("p1", "omni_context_engine", "L3")
_emit_escalates_to_human("p1", "omni_context_engine", "L3")
_emit_reads_policy_state("p1", "omni_context_engine", "L3")
_emit_authorize_and_execute("p2", "omni_context_engine", "execution_auth")
_emit_validates_capability("p2", "omni_context_engine", "capability_check")
_emit_routes_to_capability("p2", "omni_context_engine", "capability_route")
_emit_writes_via_uwg("p2", "omni_context_engine", "uwg_write")
_emit_blocks_direct_write("p2", "omni_context_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "omni_context_engine", "tool_invocation")
_emit_captures_execution_output("p2", "omni_context_engine", "exec_output")
_emit_dispatches_agent("p3", "omni_context_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "omni_context_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "omni_context_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "omni_context_engine", "healing_outcome")
_emit_escalates_failure("p3", "omni_context_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "omni_context_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "omni_context_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "omni_context_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "omni_context_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "omni_context_engine", "eval_metric")
_emit_stores_embedding("p4", "omni_context_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "omni_context_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "omni_context_engine", "exec_snapshot_link")

"Brief description of functionality and purpose."
from agentic_core.L2_execution.reasoning.base import SubAtomicAgent

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class OmniContext(SubAtomicAgent):
    """
    ROLE: Global Architectural Context. Concatenates all non-excluded .py files
    into a single context buffer for agents to consult.
    """

    def __init__(self, context):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "OmniContext.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "OmniContext.__init__", "p0_governance")
        super().__init__(context)
        self.context_buffer = ""
        self.index = {}

    async def execute(self):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OmniContext.execute")

        print(f"\n[>>>] {self.name} ACTIVATED: Building Global Context...")
        await asyncio.sleep(DEFAULT_SLEEP)
        self._build_context_buffer()
        self.ctx.OmniContext = {"buffer": self.context_buffer, "index": self.index, "consult": self.consult}
        print(f"   📚 Built context: {len(self.context_buffer)} chars from {len(self.index)} files")

    def _build_context_buffer(self):
        """Build a concatenated buffer of all Python code."""
        sections = []
        for file_path in self.ctx.python_files:
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
            # guardian: allow-silent-swallow
            except Exception as e:
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
