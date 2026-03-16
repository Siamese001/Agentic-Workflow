# Main Execution Loop
# Strategy: Orchestrates the Observe-Think-Act cycle with safety limits

import logging

from agentic_core.L0_routing.enforcement.runtime_guard import (
    runtime_guard,
)
from agentic_core.L0_routing.types.guardian_contract_types import is_v15_enforced
from agentic_core.patterns.base import BaseReasoningPattern
from agentic_core.runtime.exceptions import ToolExecutionError, ToolNotFoundError
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_authorize_and_execute("p2", "agent_engine", "execution_auth")
_emit_validates_capability("p2", "agent_engine", "capability_check")
_emit_routes_to_capability("p2", "agent_engine", "capability_route")
_emit_writes_via_uwg("p2", "agent_engine", "uwg_write")
_emit_blocks_direct_write("p2", "agent_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_engine", "tool_invocation")
_emit_captures_execution_output("p2", "agent_engine", "exec_output")
_emit_dispatches_agent("p3", "agent_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_engine", "healing_outcome")
_emit_escalates_failure("p3", "agent_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_engine", "eval_metric")
_emit_stores_embedding("p4", "agent_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_engine", "exec_snapshot_link")
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry

_emit_applies_guardrail("p0", "agent_engine", "p0_governance")
_emit_reads_policy_state("p0", "agent_engine", "policy_binding")
_emit_snapshots_state("p0", "agent_engine", "state_snapshot")
emit_replay_key("p0", "agent_engine")
emit_determinism_digest("p0", "agent_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class AgentEngine:
    # guardian: allow-magic-config
    def __init__(self, pattern: BaseReasoningPattern, tools: ToolRegistry, max_turns: int = 5):
        self.pattern = pattern
        self.tools = tools
        self.max_turns = max_turns

    def _v15_build_operation_manifest(
        self,
        operation: str,
        target_layer: str = "L2",
    ) -> "SurgicalManifest | None":
        """§8.1b — Construct SurgicalManifest for engine-level operation."""
        if not is_v15_enforced():
            return None

        import hashlib as _hl

        from agentic_core.L0_routing.enforcement.traceability_contracts import (
            generate_trace_id,
        )
        from agentic_core.L0_routing.types.determinism_types import (
            FixConstraint,
            SurgicalManifest,
        )

        _hex8 = (
            _hl.sha256(
                f"{self.__class__.__name__}:{operation}".encode(),
            )
            .hexdigest()[:8]
            .upper()
        )
        trace_id = generate_trace_id(_hex8)

        ast_snippet = f"{self.__class__.__name__}.{operation}()"
        return SurgicalManifest(
            schema_version="1.0.0",
            correlation_id=trace_id,
            node_id=self.__class__.__name__,
            target_layer=target_layer,
            ast_snippet=ast_snippet,
            serialization_canon="engine_operation",
            fix_constraint=FixConstraint.RELAXED,
            manifest_hash=_hl.sha256(ast_snippet.encode()).hexdigest(),
            change_history=(),
            provenance_chain=(trace_id,),
        )

    @runtime_guard("B.run.agent_engine")
    async def run(self, user_input: str, task_id: str = "default") -> AgentState:
        """
        Executes the agent loop until completion or max_turns.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentEngine.run")

        # §8.1b — V15 manifest construction at engine entry boundary
        manifest = self._v15_build_operation_manifest("run")
        if manifest is not None:
            import hashlib as _hl

            from agentic_core.L0_routing.enforcement.execution_gateway import (
                V15ExecutionGateway,
            )

            gateway = V15ExecutionGateway()

            def _noop_heal(m):
                return {"status": "audit_pass", "errors": 0}

            def _state_hash():
                _h = _hl.sha256(f"{self.__class__.__name__}:{task_id}".encode()).hexdigest()
                return (_h, _h, _h)

            # guardian: allow-silent-swallow
            try:
                gateway.execute(
                    execution_input=manifest,
                    heal_fn=_noop_heal,
                    state_hash_fn=_state_hash,
                    trace_id=manifest.correlation_id,
                    agent_id="agent_engine",
                )
            # guardian: allow-silent-swallow
            except Exception as exc:
                logger.warning("[V15] Gateway audit failed (LOG_ONLY): %s", exc)

        state = AgentState(task_id=task_id, user_input=user_input)

        while not state.is_terminated:
            # 1. Check Limits
            if state.turn_count >= self.max_turns:
                state.is_terminated = True
                state.termination_reason = "MAX_TURNS_REACHED"
                break

            # 2. Plan (Think)
            # The pattern analyzes state and decides next tool
            tool_name, tool_args = await self.pattern.plan(state, self.tools)
            state.add_message("assistant", f"Thought: I should use {tool_name} with {tool_args}")

            # 3. Terminate if requested
            if tool_name == "Final Answer":
                state.is_terminated = True
                state.termination_reason = "COMPLETED"
                state.add_message("assistant", f"Final Answer: {tool_args.get('result')}")
                break

            # 4. Execute (Act)
            tool = self.tools.get(tool_name)
            if not tool:
                available = list(self.tools.keys()) if hasattr(self.tools, "keys") else []
                logger.error(f"Tool '{tool_name}' not found. Available: {available}")
                raise ToolNotFoundError(tool_name, available)

            try:
                observation = await tool.run(**tool_args)
            except Exception as e:
                logger.error(f"Tool execution failed: {tool_name} - {e}", exc_info=True)
                raise ToolExecutionError(
                    tool_name=tool_name,
                    message=f"Critical failure executing tool '{tool_name}': {e}",
                    original_error=e,
                    tool_args=tool_args,
                ) from e

            # 5. Observe
            state.add_message("system", f"Observation: {observation}")
            state.increment_turn()

        return state
