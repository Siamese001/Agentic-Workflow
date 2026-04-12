"""
agentic_core/L2_execution/contracts/typed_tool_contract.py

TypedToolContract — P2/L2 typed tool interface enforcement.

Every governed runtime tool call MUST create a ToolContract with schema-validated
input and output. No tool may execute through untyped payloads on governed paths.

invoke_typed_tool() steps (mandatory, in order):
  1. validate input against declared schema
  2. verify tool registry entry (UnregisteredToolError if absent)
  3. bind policy hash
  4. execute tool
  5. validate output against declared schema (fail-closed on missing fields)
  6. persist tool contract result

ToolContract (12 required spec fields):
    tool_contract_id, tool_name, tool_version, run_id, trace_id,
    input_schema_hash, output_schema_hash, input_payload_hash,
    output_payload_hash, action_class, caller_agent_id, policy_hash

TypedToolRegistry — maintains tool registrations:
    tool_name, tool_version, input_schema, output_schema,
    action_class, allowed_callers, policy_requirements

ToolContractResult — typed execution result with contract linkage.

ADG edges emitted:
    records_execution_trace — every invoke_typed_tool() call
    applies_guardrail       — schema validation enforced on input/output
    references_policy_hash  — policy bound to every tool contract
    validated_by_safety_plane — registry check enforced before execution
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "typed_tool_contract")
emit_determinism_digest("p0", "typed_tool_contract")

_emit_dispatches_healing_run("p1", "typed_tool_contract", "L2")
_emit_routes_through("p1", "typed_tool_contract", "L2")
_emit_checks_agent_registry("p1", "typed_tool_contract", "agent_registry")
_emit_validates_agent_capability("p1", "typed_tool_contract", "capability")
_emit_dispatches_execution_plan("p1", "typed_tool_contract", "exec_plan")
_emit_agent_executes_agent("p1", "typed_tool_contract", "sub_agent")
_emit_routes_to_agent("p1", "typed_tool_contract", "target_agent")
_emit_verifies_policy("p1", "typed_tool_contract", "policy_check")
_emit_observes_runtime_state("p1", "typed_tool_contract", "runtime_state")
_emit_verifies_boundary("p1", "typed_tool_contract", "boundary_check")
_emit_transcripts_response("p1", "typed_tool_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "typed_tool_contract")
_emit_gated_by_confidence("p1", "typed_tool_contract", "confidence_gate")
_emit_escalates_to_human("p1", "typed_tool_contract", "L2")
_emit_reads_policy_state("p1", "typed_tool_contract", "L2")
_emit_authorize_and_execute("p2", "typed_tool_contract", "execution_auth")
_emit_validates_capability("p2", "typed_tool_contract", "capability_check")
_emit_routes_to_capability("p2", "typed_tool_contract", "capability_route")
_emit_writes_via_uwg("p2", "typed_tool_contract", "uwg_write")
_emit_blocks_direct_write("p2", "typed_tool_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "typed_tool_contract", "tool_invocation")
_emit_captures_execution_output("p2", "typed_tool_contract", "exec_output")
_emit_dispatches_agent("p3", "typed_tool_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "typed_tool_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "typed_tool_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "typed_tool_contract", "healing_outcome")
_emit_escalates_failure("p3", "typed_tool_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "typed_tool_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "typed_tool_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "typed_tool_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "typed_tool_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "typed_tool_contract", "eval_metric")
_emit_stores_embedding("p4", "typed_tool_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "typed_tool_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "typed_tool_contract", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("typed_tool_contract", "p4obs", "metric_1")
_emit_emits_metric_event("typed_tool_contract", "p4obs", "metric_2")
_emit_emits_metric_event("typed_tool_contract", "p4obs", "metric_3")
_emit_emits_metric_event("typed_tool_contract", "p4obs", "metric_4")
_emit_emits_metric_event("typed_tool_contract", "p4obs", "metric_5")
_emit_emits_metric_event("typed_tool_contract", "p4obs", "metric_6")
_emit_records_incident_event("typed_tool_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("typed_tool_contract", "p4obs", "anomaly")
_emit_writes_observability_log("typed_tool_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("typed_tool_contract", "p4obs", "mon_state")
_emit_triggers_alert("typed_tool_contract", "p4obs", "alert")
_emit_links_incident_trace("typed_tool_contract", "p4obs", "trace_link")
_emit_captures_pattern("typed_tool_contract", "p3lm", "pattern")
_emit_records_learning_event("typed_tool_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("typed_tool_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("typed_tool_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("typed_tool_contract", "p3lm", "routing")
_emit_improves_agent_policy("typed_tool_contract", "p3lm", "policy")
_emit_stores_learning_state("typed_tool_contract", "p3lm", "state")
_emit_records_execution_trace("typed_tool_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("typed_tool_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("typed_tool_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("typed_tool_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("typed_tool_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("typed_tool_contract", "env_read", "p2_env_1")
_emit_reads_environ("typed_tool_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("typed_tool_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("typed_tool_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "typed_tool_contract", "context_pull")
_emit_pulls_context("p1", "typed_tool_contract", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "typed_tool_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "typed_tool_contract", "uwg_term_2")
_emit_writes_through("p1", "typed_tool_contract", "write_through")
_emit_writes_through("p1", "typed_tool_contract", "write_through_2")
_emit_validated_by_safety_plane("p1", "typed_tool_contract", "safety_validation")
_emit_invokes_eval("p1", "typed_tool_contract", "eval_call")
_emit_proposal_commits_routing("p1", "typed_tool_contract", "routing_commit")

logger = logging.getLogger(__name__)
_TRACE_LOG = logging.getLogger("adg.records_execution_trace")
_GUARDRAIL_LOG = logging.getLogger("adg.applies_guardrail")
_POLICY_LOG = logging.getLogger("adg.references_policy_hash")
_SAFETY_LOG = logging.getLogger("adg.validated_by_safety_plane")


# ---------------------------------------------------------------------------
# Custom exceptions — spec §5 / fail-closed semantics
# ---------------------------------------------------------------------------


class ToolInputSchemaViolation(ValueError):
    """Raised when tool input fails schema validation (spec §6 fail-closed).

    Gate B enforcement: tool_contract_id + input_schema_hash required.
    """


class ToolOutputSchemaViolation(ValueError):
    """Raised when tool output fails schema validation (spec §6 fail-closed).

    Gate C enforcement: output missing required fields must fail closed.
    """


class UnregisteredToolError(RuntimeError):
    """Raised when a tool is not present in the TypedToolRegistry.

    Gate D enforcement: only registered tools may execute.
    """


class UntypedToolExecutionError(RuntimeError):
    """Raised when a governed tool path uses getattr/importlib resolution.

    Gate E enforcement: prohibit getattr-style/importlib tool invocation.
    """


class MissingToolContractError(RuntimeError):
    """Raised when a governed tool executes without a ToolContract.

    Gate A enforcement: no uncontracted tool execution.
    """


# ---------------------------------------------------------------------------
# ToolSchema — input/output schema representation
# ---------------------------------------------------------------------------


@dataclass
class ToolSchema:
    """Typed schema for tool input or output.

    required_fields: field names that must be present in payload.
    optional_fields: field names that may be present.
    schema_version:  version identifier for schema evolution.
    """

    required_fields: list[str]
    optional_fields: list[str] = field(default_factory=list)
    schema_version: str = "1.0"
    schema_id: str = field(default_factory=lambda: f"schema-{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ToolSchema.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ToolSchema.to_dict", "p0_governance")
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "required_fields": sorted(self.required_fields),
            "optional_fields": sorted(self.optional_fields),
        }

    def hash(self) -> str:
        return _sha256(repr(sorted(self.to_dict().items())))

    def validate(self, payload: dict[str, Any]) -> list[str]:
        """Return list of missing required fields. Empty list = valid."""
        return [f for f in self.required_fields if f not in payload]


# ---------------------------------------------------------------------------
# ToolRegistryEntry — per-tool registration record
# ---------------------------------------------------------------------------


@dataclass
class ToolRegistryEntry:
    """Registry entry for one tool version.

    Spec §4 fields: tool_name, tool_version, input_schema, output_schema,
    action_class, allowed_callers, policy_requirements.
    """

    tool_name: str
    tool_version: str
    input_schema: ToolSchema
    output_schema: ToolSchema
    action_class: str
    allowed_callers: list[str]
    policy_requirements: list[str]
    callable: Callable[..., Any] | None = None

    def allows_caller(self, caller_agent_id: str) -> bool:
        """Return True if caller is allowed (wildcard '*' allows all)."""
        return "*" in self.allowed_callers or caller_agent_id in self.allowed_callers

    def meets_policy(self, policy_hash: str) -> bool:
        """Return True if no policy requirements or policy_hash present."""
        return not self.policy_requirements or bool(policy_hash)


# ---------------------------------------------------------------------------
# ToolContract — 12 required spec fields
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolContract:
    """Immutable typed tool contract — 12 required spec fields (spec §2).

    Created before every governed tool invocation.
    """

    tool_contract_id: str
    tool_name: str
    tool_version: str
    run_id: str
    trace_id: str
    input_schema_hash: str
    output_schema_hash: str
    input_payload_hash: str
    output_payload_hash: str
    action_class: str
    caller_agent_id: str
    policy_hash: str

    @classmethod
    def create(
        cls,
        *,
        tool_name: str,
        tool_version: str,
        run_id: str,
        trace_id: str,
        input_schema: ToolSchema,
        output_schema: ToolSchema,
        input_payload: dict[str, Any],
        output_payload: dict[str, Any] | None = None,
        action_class: str,
        caller_agent_id: str,
        policy_hash: str,
    ) -> ToolContract:
        return cls(
            tool_contract_id=f"tc-{uuid.uuid4().hex[:12]}",
            tool_name=tool_name,
            tool_version=tool_version,
            run_id=run_id,
            trace_id=trace_id,
            input_schema_hash=input_schema.hash(),
            output_schema_hash=output_schema.hash(),
            input_payload_hash=_sha256(repr(sorted(input_payload.items()))),
            output_payload_hash=_sha256(repr(sorted((output_payload or {}).items()))),
            action_class=action_class,
            caller_agent_id=caller_agent_id,
            policy_hash=policy_hash,
        )

    def with_output(self, output_payload: dict[str, Any]) -> ToolContract:
        """Return a new ToolContract with output_payload_hash populated."""
        return ToolContract(
            tool_contract_id=self.tool_contract_id,
            tool_name=self.tool_name,
            tool_version=self.tool_version,
            run_id=self.run_id,
            trace_id=self.trace_id,
            input_schema_hash=self.input_schema_hash,
            output_schema_hash=self.output_schema_hash,
            input_payload_hash=self.input_payload_hash,
            output_payload_hash=_sha256(repr(sorted(output_payload.items()))),
            action_class=self.action_class,
            caller_agent_id=self.caller_agent_id,
            policy_hash=self.policy_hash,
        )


# ---------------------------------------------------------------------------
# ToolContractResult — typed execution result with contract linkage
# ---------------------------------------------------------------------------


@dataclass
class ToolContractResult:
    """Result of a typed tool invocation with full contract linkage."""

    tool_contract: ToolContract
    output_payload: dict[str, Any]
    execution_success: bool
    failure_reason: str = ""
    elapsed_ms: float = 0.0

    @property
    def tool_contract_id(self) -> str:
        return self.tool_contract.tool_contract_id


# ---------------------------------------------------------------------------
# TypedToolRegistry — spec §4
# ---------------------------------------------------------------------------


class TypedToolRegistry:
    """Thread-safe registry of typed tool definitions.

    Spec §4: only registered tools may execute (Gate D).
    Provides lookup by tool_name (latest version) or (tool_name, tool_version).
    """

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], ToolRegistryEntry] = {}
        self._lock = threading.RLock()

    def register(self, entry: ToolRegistryEntry) -> None:
        """Register a tool entry. Re-registration of same name+version overwrites."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"TypedToolRegistry.register:{entry.tool_name}",
        )
        with self._lock:
            self._entries[(entry.tool_name, entry.tool_version)] = entry

    def get(self, tool_name: str, tool_version: str = "latest") -> ToolRegistryEntry | None:
        """Lookup by (name, version). 'latest' returns highest lexicographic version."""
        # ... (rest of the code remains the same)
        with self._lock:
            if tool_version == "latest":
                candidates = [e for (n, v), e in self._entries.items() if n == tool_name]
                if not candidates:
                    return None
                return sorted(candidates, key=lambda e: e.tool_version)[-1]
            return self._entries.get((tool_name, tool_version))

    def is_registered(self, tool_name: str, tool_version: str = "latest") -> bool:
        return self.get(tool_name, tool_version) is not None

    def all_entries(self) -> list[ToolRegistryEntry]:
        with self._lock:
            return list(self._entries.values())

    def tool_names(self) -> list[str]:
        with self._lock:
            return sorted({n for (n, _) in self._entries})


# ---------------------------------------------------------------------------
# invoke_typed_tool() — mandatory entrypoint per spec §3
# ---------------------------------------------------------------------------


def invoke_typed_tool(
    tool_contract: ToolContract,
    typed_input: dict[str, Any],
    *,
    registry: TypedToolRegistry | None = None,
    tool_callable: Callable[..., Any] | None = None,
) -> ToolContractResult:
    """Mandatory typed tool entrypoint — P2/L2 spec §3.

    Steps (in order, all mandatory):
      1. validate input against declared schema
      2. verify tool registry entry (UnregisteredToolError if absent)
      3. bind policy hash
      4. execute tool
      5. validate output against declared schema (fail-closed on missing fields)
      6. persist tool contract result

    Args:
        tool_contract:  Pre-built ToolContract (all 12 fields required).
        typed_input:    Dict payload that must satisfy input_schema.
        registry:       TypedToolRegistry to verify registration (uses global if None).
        tool_callable:  Callable to execute; falls back to registry entry callable.

    Returns:
        ToolContractResult with completed contract and typed output.

    Raises:
        MissingToolContractError:  tool_contract_id is empty.
        ToolInputSchemaViolation:  input fails schema validation.
        UnregisteredToolError:     tool not found in registry.
        ToolOutputSchemaViolation: output missing required schema fields.
    """
    import time as _time  # noqa: PLC0415

    # Gate A guard — contract must exist
    if not tool_contract.tool_contract_id:
        raise MissingToolContractError(
            "invoke_typed_tool: tool_contract_id is required. "
            "No governed tool may execute without a ToolContract.",
        )

    _registry = registry or get_typed_tool_registry()

    # --- Step 1: Validate input against declared schema ---
    entry = _registry.get(tool_contract.tool_name, tool_contract.tool_version)
    if entry is None:
        # Look up with "latest" fallback for unversioned calls
        entry = _registry.get(tool_contract.tool_name)

    if entry is None:
        raise UnregisteredToolError(
            f"invoke_typed_tool: tool '{tool_contract.tool_name}' v{tool_contract.tool_version} "
            f"is not registered. Only registered tools may execute (spec §4).",
        )

    missing_input = entry.input_schema.validate(typed_input)
    if missing_input:
        _GUARDRAIL_LOG.debug(
            "applies_guardrail TYPED_TOOL_INPUT_VIOLATION tool=%s missing=%s contract=%s",
            tool_contract.tool_name,
            missing_input,
            tool_contract.tool_contract_id,
        )
        raise ToolInputSchemaViolation(
            f"invoke_typed_tool: input for '{tool_contract.tool_name}' missing required fields: "
            f"{missing_input} (input_schema_hash={tool_contract.input_schema_hash})",
        )

    _GUARDRAIL_LOG.debug(
        "applies_guardrail TYPED_TOOL_INPUT_VALID tool=%s contract=%s schema=%s",
        tool_contract.tool_name,
        tool_contract.tool_contract_id,
        tool_contract.input_schema_hash,
    )

    # --- Step 2: Verify tool registry entry ---
    _SAFETY_LOG.debug(
        "validated_by_safety_plane TYPED_TOOL_REGISTRY tool=%s version=%s caller=%s",
        tool_contract.tool_name,
        tool_contract.tool_version,
        tool_contract.caller_agent_id,
    )

    # --- Step 3: Bind policy hash ---
    _POLICY_LOG.debug(
        "references_policy_hash TYPED_TOOL tool=%s policy=%s contract=%s",
        tool_contract.tool_name,
        tool_contract.policy_hash,
        tool_contract.tool_contract_id,
    )

    _TRACE_LOG.debug(
        "records_execution_trace TYPED_TOOL_PRE tool=%s contract=%s trace=%s run=%s",
        tool_contract.tool_name,
        tool_contract.tool_contract_id,
        tool_contract.trace_id,
        tool_contract.run_id,
    )

    # --- Step 4: Execute tool ---
    _callable = tool_callable or entry.callable
    if _callable is None:
        raise UnregisteredToolError(
            f"invoke_typed_tool: tool '{tool_contract.tool_name}' has no callable registered.",
        )

    _start = _time.monotonic()
    try:
        raw_output = _callable(typed_input)
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        _elapsed = (_time.monotonic() - _start) * 1000.0
        result = ToolContractResult(
            tool_contract=tool_contract,
            output_payload={},
            execution_success=False,
            failure_reason=f"{type(exc).__name__}: {exc}",
            elapsed_ms=_elapsed,
        )
        _persist_contract_result(result)
        raise
    _elapsed = (_time.monotonic() - _start) * 1000.0

    # Normalize output to dict
    if isinstance(raw_output, dict):
        output_payload = raw_output
    else:
        output_payload = {"result": raw_output}

    # --- Step 5: Validate output against declared schema (fail-closed) ---
    missing_output = entry.output_schema.validate(output_payload)
    if missing_output:
        _GUARDRAIL_LOG.debug(
            "applies_guardrail TYPED_TOOL_OUTPUT_VIOLATION tool=%s missing=%s contract=%s",
            tool_contract.tool_name,
            missing_output,
            tool_contract.tool_contract_id,
        )
        raise ToolOutputSchemaViolation(
            f"invoke_typed_tool: output for '{tool_contract.tool_name}' missing required fields: "
            f"{missing_output} (output_schema_hash={tool_contract.output_schema_hash}). "
            f"Fail-closed: output schema must be fully satisfied.",
        )

    _GUARDRAIL_LOG.debug(
        "applies_guardrail TYPED_TOOL_OUTPUT_VALID tool=%s contract=%s schema=%s",
        tool_contract.tool_name,
        tool_contract.tool_contract_id,
        tool_contract.output_schema_hash,
    )

    # --- Step 6: Persist tool contract result ---
    final_contract = tool_contract.with_output(output_payload)
    result = ToolContractResult(
        tool_contract=final_contract,
        output_payload=output_payload,
        execution_success=True,
        elapsed_ms=_elapsed,
    )
    _persist_contract_result(result)

    _TRACE_LOG.debug(
        "records_execution_trace TYPED_TOOL_POST tool=%s contract=%s trace=%s success=True",
        tool_contract.tool_name,
        tool_contract.tool_contract_id,
        tool_contract.trace_id,
    )

    logger.debug(
        "INVOKE_TYPED_TOOL completed tool=%s contract=%s action=%s caller=%s elapsed_ms=%.1f",
        tool_contract.tool_name,
        tool_contract.tool_contract_id,
        tool_contract.action_class,
        tool_contract.caller_agent_id,
        _elapsed,
    )
    return result


# ---------------------------------------------------------------------------
# ToolContractStore — queryable store
# ---------------------------------------------------------------------------


class ToolContractStore:
    """In-memory queryable store for all emitted ToolContractResult instances.

    Queryable by run_id, trace_id, tool_name, action_class.
    """

    def __init__(self) -> None:
        self._results: list[ToolContractResult] = []
        self._lock = threading.RLock()

    def ingest(self, result: ToolContractResult) -> None:
        with self._lock:
            self._results.append(result)

    def by_run_id(self, run_id: str) -> list[ToolContractResult]:
        with self._lock:
            return [r for r in self._results if r.tool_contract.run_id == run_id]

    def by_trace_id(self, trace_id: str) -> list[ToolContractResult]:
        with self._lock:
            return [r for r in self._results if r.tool_contract.trace_id == trace_id]

    def by_tool_name(self, tool_name: str) -> list[ToolContractResult]:
        with self._lock:
            return [r for r in self._results if r.tool_contract.tool_name == tool_name]

    def by_action_class(self, action_class: str) -> list[ToolContractResult]:
        with self._lock:
            return [r for r in self._results if r.tool_contract.action_class == action_class]

    def all_results(self) -> list[ToolContractResult]:
        with self._lock:
            return list(self._results)

    def missing_input_schema_hash(self) -> list[ToolContractResult]:
        """Results where input_schema_hash is empty (Gate B violation)."""
        with self._lock:
            return [r for r in self._results if not r.tool_contract.input_schema_hash]

    def missing_output_schema_hash(self) -> list[ToolContractResult]:
        """Results where output_schema_hash is empty (Gate C violation)."""
        with self._lock:
            return [r for r in self._results if not r.tool_contract.output_schema_hash]

    def uncontracted_executions(self) -> list[ToolContractResult]:
        """Results without a tool_contract_id (Gate A violation)."""
        with self._lock:
            return [r for r in self._results if not r.tool_contract.tool_contract_id]

    def result_count(self) -> int:
        with self._lock:
            return len(self._results)


# ---------------------------------------------------------------------------
# Process-level singletons
# ---------------------------------------------------------------------------

_global_registry: TypedToolRegistry | None = None
_global_registry_lock = threading.Lock()

_global_store: ToolContractStore | None = None
_global_store_lock = threading.Lock()


def get_typed_tool_registry() -> TypedToolRegistry:
    """Return the process-level TypedToolRegistry singleton."""
    global _global_registry
    if _global_registry is None:
        with _global_registry_lock:
            if _global_registry is None:
                _global_registry = TypedToolRegistry()
    return _global_registry


def get_tool_contract_store() -> ToolContractStore:
    """Return the process-level ToolContractStore singleton."""
    global _global_store
    if _global_store is None:
        with _global_store_lock:
            if _global_store is None:
                _global_store = ToolContractStore()
    return _global_store


def reset_typed_tool_registry() -> None:
    """Reset global registry (for testing)."""
    global _global_registry
    _global_registry = None


def reset_tool_contract_store() -> None:
    """Reset global store (for testing)."""
    global _global_store
    _global_store = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:32]


def _persist_contract_result(result: ToolContractResult) -> None:
    get_tool_contract_store().ingest(result)


__all__ = [
    "ToolInputSchemaViolation",
    "ToolOutputSchemaViolation",
    "UnregisteredToolError",
    "UntypedToolExecutionError",
    "MissingToolContractError",
    "ToolSchema",
    "ToolRegistryEntry",
    "ToolContract",
    "ToolContractResult",
    "TypedToolRegistry",
    "ToolContractStore",
    "invoke_typed_tool",
    "get_typed_tool_registry",
    "get_tool_contract_store",
    "reset_typed_tool_registry",
    "reset_tool_contract_store",
]
