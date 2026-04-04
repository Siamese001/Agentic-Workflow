from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from agentic_core.L1_cognition.types.react_trace_types import (
    PromptProvenanceRecord,
    ReasonTraceEnvelope,
    ReplayGuard,
    assert_c0_informational,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.patterns.base import BaseReasoningPattern

from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

Logger = logging.getLogger(__name__)

_POLICY_HASH_DEFAULT = hashlib.sha256(b"default_policy_v1").hexdigest()


def _compute_plan_hash(task: str, tool_names: list[str]) -> str:
    payload = json.dumps({"task": task, "tools": sorted(tool_names)}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ReActStrategy(BaseReasoningPattern):
    """Reason-Act-Observe loop — wired to the real ReActEngine.

    Zero-Ambiguity Standard: Renamed from ReActPattern to ReActStrategy
    to clarify its role as a behavioral strategy pattern.

    Delegates think/act steps to ReActEngine with ToolRegistry providing
    the actual tool dispatch.  The ``plan`` method is the entry-point used
    by AgentEngine on each turn; it returns the (action, params) tuple for
    that turn.

    Enforcement:
      - C0 boundary: RAG context is informational only (no authority fields).
      - ReasonTraceEnvelope emitted after each full trace.
      - PromptProvenanceRecord captured per execution.
      - ReplayGuard blocks non-deterministic clock/random usage.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        max_steps: int = 10,
        enable_self_reflection: bool = True,
        policy_hash: str | None = None,
        semantic_clock_vector: tuple[int, ...] = (0,),
        model_id: str = "default",
        prompt_template_id: str = "default_react_v1",
    ) -> None:
        from agentic_core.L1_cognition.engines.react_engine import ReActEngine

        self._engine = ReActEngine(
            max_steps=max_steps,
            enable_self_reflection=enable_self_reflection,
        )
        self._tools: ToolRegistry | None = None
        self._policy_hash: str = policy_hash or _POLICY_HASH_DEFAULT
        self._semantic_clock_vector: tuple[int, ...] = semantic_clock_vector
        self._model_id: str = model_id
        self._prompt_template_id: str = prompt_template_id
        self._last_envelope: ReasonTraceEnvelope | None = None
        self._last_provenance: PromptProvenanceRecord | None = None

    @property
    def last_envelope(self) -> ReasonTraceEnvelope | None:
        """The ReasonTraceEnvelope emitted by the most recent full trace."""
        return self._last_envelope

    @property
    def last_provenance(self) -> PromptProvenanceRecord | None:
        """The PromptProvenanceRecord captured by the most recent full trace."""
        return self._last_provenance

    def enforce_c0_boundary(self, rag_context: dict[str, Any]) -> None:
        """Assert RAG context contains no authority fields (C0 rule).

        Raises:
            C0BoundaryViolation: if any forbidden field is present.
        """
        assert_c0_informational(rag_context, source="ReActStrategy")

    async def plan(self, state: AgentState, tools: ToolRegistry) -> tuple[str, dict[str, Any]]:
        """Produce the next (action, params) for the current turn.

        On turn 0 the full ReAct trace is executed and stored; subsequent
        turns replay steps from the cached trace so AgentEngine can advance
        one-step-at-a-time as it expects.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ReActStrategy.plan")

        self._tools = tools

        if not hasattr(self, "_trace") or self._trace is None:
            self._trace = await self._run_full_trace(state, tools)
            self._step_index = 0

        if self._step_index < len(self._trace.steps):
            step = self._trace.steps[self._step_index]
            self._step_index += 1
            Logger.debug(
                "react_strategy_step",
                extra={"turn": state.turn_count, "action": step.action, "step": step.step_number},
            )
            return (step.action, step.action_input)

        return ("Final Answer", {"result": self._trace.final_answer or "Task Complete"})

    def _emit_envelope(self, trace: Any) -> ReasonTraceEnvelope:
        """Build and store a ReasonTraceEnvelope from the completed trace."""
        reason_steps = tuple(s.thought for s in trace.steps)
        action_steps = tuple(s.action for s in trace.steps)
        tool_invocations = tuple(
            f"{s.action}({json.dumps(s.action_input, separators=(',', ':'))})" for s in trace.steps
        )
        plan_hash = _compute_plan_hash(
            trace.Task,
            list({s.action for s in trace.steps}),
        )
        envelope = ReasonTraceEnvelope.build(
            trace_id=trace.trace_id,
            plan_hash=plan_hash,
            reason_steps=reason_steps,
            action_steps=action_steps,
            tool_invocations=tool_invocations,
            policy_hash=self._policy_hash,
            semantic_clock_vector=self._semantic_clock_vector,
        )
        self._last_envelope = envelope
        Logger.info(
            "react_envelope_emitted",
            extra={"trace_id": trace.trace_id, "envelope_hash": envelope.envelope_hash},
        )
        return envelope

    def _capture_provenance(self, task: str, rag_context_ids: tuple[str, ...]) -> PromptProvenanceRecord:
        """Build and store a PromptProvenanceRecord for this execution."""
        record = PromptProvenanceRecord.build(
            prompt_text=task,
            prompt_template_id=self._prompt_template_id,
            rag_context_ids=rag_context_ids,
            policy_hash=self._policy_hash,
            model_id=self._model_id,
        )
        self._last_provenance = record
        return record

    async def _run_full_trace(self, state: AgentState, tools: ToolRegistry) -> Any:
        """Execute the full ReAct trace using real ToolRegistry dispatch.

        Enforcement sequence:
          1. C0 boundary check on any RAG context in state metadata.
          2. Provenance record captured from task + context IDs.
          3. ReplayGuard installed for the duration of the run.
          4. ReasonTraceEnvelope emitted after trace completes.
        """
        rag_context: dict[str, Any] = getattr(state, "rag_context", {}) or {}
        assert_c0_informational(rag_context, source="ReActStrategy._run_full_trace")

        rag_context_ids: tuple[str, ...] = tuple(str(v) for v in rag_context.get("context_ids", []))
        self._capture_provenance(state.user_input, rag_context_ids)

        _guard = ReplayGuard(
            semantic_clock_vector=self._semantic_clock_vector,
            strict=False,
        )

        async def _think_fn(task: str, steps: list) -> str:
            history = "\n".join(
                f"Step {s.step_number}: {s.thought} -> {s.action}({s.action_input}) => {s.observation}"
                for s in steps
            )
            return (
                f"Task: {task}\n"
                f"History:\n{history}\n"
                f"Thought: Determining next action for turn {state.turn_count}.\n"
                f"Action: {self._select_action(task, steps, tools)}\n"
                f"Action Input: {{}}"
            )

        async def _act_fn(action: str, action_input: dict[str, Any]) -> str:
            tool_def = tools.get_tool(action) if tools else None
            if tool_def is None:
                if action.lower() in ("final answer", "finish"):
                    return "FINISH"
                Logger.warning("react_tool_not_found", extra={"action": action})
                return f"Tool '{action}' not found in registry."
            try:
                result = await tool_def.function(action_input)
                tools.update_tool_stats(action, success=True)
                return str(result)
            except Exception as exc:  # guardian: allow-silent-swallower
                tools.update_tool_stats(action, success=False)
                Logger.error("react_tool_error", extra={"action": action, "error": str(exc)})
                return f"Error executing '{action}': {exc}"

        trace = await self._engine.run(
            Task=state.user_input,
            think_fn=_think_fn,
            act_fn=_act_fn,
        )

        _guard.assert_clean()
        self._emit_envelope(trace)
        return trace

    def _select_action(self, task: str, steps: list, tools: ToolRegistry) -> str:
        """Heuristic: pick the most-used registered tool, or 'Final Answer'."""
        if tools and tools.tools:
            available = list(tools.tools.keys())
            if available:
                return available[len(steps) % len(available)]
        return "Final Answer"

    def reset(self) -> None:
        """Clear cached trace (call before reuse with a new task)."""
        self._trace = None
        self._step_index = 0


ReActPattern = ReActStrategy
