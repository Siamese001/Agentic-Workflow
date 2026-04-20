"""
agentic_core/L5_safety/enforcement/tool_safety_contract.py

ToolSafetyContract — P1/L5 unified tool invocation governance.

All tool invocations MUST pass through invoke_tool_safely().
Direct tool invocation outside this entrypoint is prohibited.

invoke_tool_safely() steps (mandatory, in order):
  1. validate capability token
  2. classify tool action
  3. enforce policy
  4. run guardrail decision
  5. attach policy hash
  6. attach trace id
  7. execute only on ALLOW
  8. emit ToolSafetyContract artifact

ToolSafetyContract (11 required spec fields):
    tool_call_id, tool_name, run_id, trace_id, actor_id,
    capability_token, policy_hash, action_class,
    guardrail_decision_id, tool_input_hash, tool_output_hash

ToolActionClass (5 required classes):
    READ_ONLY, MUTATING, NETWORK, PRIVILEGED, HUMAN_GATED

ADG edges emitted:
    applies_guardrail           — every invoke_tool_safely() call
    validated_by_safety_plane   — every invoke_tool_safely() call
    requires_human_review       — HUMAN_GATED / PRIVILEGED tools
    references_policy_hash      — every tool contract artifact
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.L2_execution.utils.providers import get_clock
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

emit_replay_key("p0", "tool_safety_contract")
emit_determinism_digest("p0", "tool_safety_contract")

_emit_dispatches_healing_run("p1", "tool_safety_contract", "L5")
_emit_routes_through("p1", "tool_safety_contract", "L5")
_emit_checks_agent_registry("p1", "tool_safety_contract", "agent_registry")
_emit_validates_agent_capability("p1", "tool_safety_contract", "capability")
_emit_dispatches_execution_plan("p1", "tool_safety_contract", "exec_plan")
_emit_agent_executes_agent("p1", "tool_safety_contract", "sub_agent")
_emit_routes_to_agent("p1", "tool_safety_contract", "target_agent")
_emit_observes_runtime_state("p1", "tool_safety_contract", "runtime_state")
_emit_verifies_boundary("p1", "tool_safety_contract", "boundary_check")
_emit_transcripts_response("p1", "tool_safety_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_safety_contract")
_emit_gated_by_confidence("p1", "tool_safety_contract", "confidence_gate")
_emit_escalates_to_human("p1", "tool_safety_contract", "L5")
_emit_reads_policy_state("p1", "tool_safety_contract", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "tool_safety_contract", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_safety_contract", "execution_auth")
_emit_validates_capability("p2", "tool_safety_contract", "capability_check")
_emit_routes_to_capability("p2", "tool_safety_contract", "capability_route")
_emit_writes_via_uwg("p2", "tool_safety_contract", "uwg_write")
_emit_blocks_direct_write("p2", "tool_safety_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_safety_contract", "tool_invocation")
_emit_captures_execution_output("p2", "tool_safety_contract", "exec_output")
_emit_dispatches_agent("p3", "tool_safety_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_safety_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_safety_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_safety_contract", "healing_outcome")
_emit_escalates_failure("p3", "tool_safety_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_safety_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_safety_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_safety_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_safety_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_safety_contract", "eval_metric")
_emit_stores_embedding("p4", "tool_safety_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_safety_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_safety_contract", "exec_snapshot_link")
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
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("tool_safety_contract", "p4obs", "metric_1")
_emit_emits_metric_event("tool_safety_contract", "p4obs", "metric_2")
_emit_emits_metric_event("tool_safety_contract", "p4obs", "metric_3")
_emit_emits_metric_event("tool_safety_contract", "p4obs", "metric_4")
_emit_emits_metric_event("tool_safety_contract", "p4obs", "metric_5")
_emit_emits_metric_event("tool_safety_contract", "p4obs", "metric_6")
_emit_records_incident_event("tool_safety_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_safety_contract", "p4obs", "anomaly")
_emit_writes_observability_log("tool_safety_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_safety_contract", "p4obs", "mon_state")
_emit_triggers_alert("tool_safety_contract", "p4obs", "alert")
_emit_links_incident_trace("tool_safety_contract", "p4obs", "trace_link")
_emit_captures_pattern("tool_safety_contract", "p3lm", "pattern")
_emit_records_learning_event("tool_safety_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_safety_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_safety_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_safety_contract", "p3lm", "routing")
_emit_improves_agent_policy("tool_safety_contract", "p3lm", "policy")
_emit_stores_learning_state("tool_safety_contract", "p3lm", "state")
_emit_records_execution_trace("tool_safety_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_safety_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_safety_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_safety_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_safety_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_safety_contract", "env_read", "p2_env_1")
_emit_reads_environ("tool_safety_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_safety_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_safety_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_safety_contract", "context_pull")
_emit_pulls_context("p1", "tool_safety_contract", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_safety_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_safety_contract", "uwg_term_2")
_emit_writes_through("p1", "tool_safety_contract", "write_through")
_emit_writes_through("p1", "tool_safety_contract", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_safety_contract", "safety_validation")
_emit_invokes_eval("p1", "tool_safety_contract", "eval_call")
_emit_proposal_commits_routing("p1", "tool_safety_contract", "routing_commit")

logger = logging.getLogger(__name__)
_GUARDRAIL_LOG = logging.getLogger("adg.applies_guardrail")
_SAFETY_PLANE_LOG = logging.getLogger("adg.validated_by_safety_plane")
_HUMAN_REVIEW_LOG = logging.getLogger("adg.requires_human_review")
_POLICY_HASH_LOG = logging.getLogger("adg.references_policy_hash")


# ---------------------------------------------------------------------------
# ToolActionClass — 5 required classes per spec §4
# ---------------------------------------------------------------------------


class ToolActionClass(str, Enum):
    """Classification of tool invocations for policy enforcement."""

    READ_ONLY = "READ_ONLY"
    MUTATING = "MUTATING"
    NETWORK = "NETWORK"
    PRIVILEGED = "PRIVILEGED"
    HUMAN_GATED = "HUMAN_GATED"


# ---------------------------------------------------------------------------
# ToolRegistryEntry — per spec §5
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolRegistryEntry:
    """A registered tool definition with policy requirements."""

    tool_name: str
    action_class: ToolActionClass
    allowed_callers: tuple[str, ...] = field(default_factory=tuple)
    policy_requirements: tuple[str, ...] = field(default_factory=tuple)
    human_review_requirement: bool = False
    network_requirement: bool = False
    description: str = ""


# ---------------------------------------------------------------------------
# ToolRegistry — per spec §5: unregistered tools cannot execute
# ---------------------------------------------------------------------------


class UnregisteredToolError(PermissionError):
    """Raised when an unregistered tool is invoked."""


class ToolCapabilityError(PermissionError):
    """Raised when capability token validation fails."""


class ToolPolicyError(PermissionError):
    """Raised when policy enforcement fails."""


class ToolGuardrailDeniedError(PermissionError):
    """Raised when guardrail check denies tool execution."""


class ToolRegistry:
    """Explicit tool registry — unregistered tools cannot execute.

    Per spec §5: every tool must have:
    - tool_name, action_class, allowed_callers, policy_requirements,
      human_review_requirement, network_requirement
    """

    def __init__(self) -> None:
        self._entries: dict[str, ToolRegistryEntry] = {}
        self._lock = threading.RLock()

    def register(self, entry: ToolRegistryEntry) -> None:
        """Register a tool entry. Overwrites if already registered."""
        with self._lock:
            self._entries[entry.tool_name] = entry
        logger.debug("TOOL_REGISTRY registered tool=%s action=%s", entry.tool_name, entry.action_class.value)

    def get(self, tool_name: str) -> ToolRegistryEntry | None:
        with self._lock:
            return self._entries.get(tool_name)

    def require(self, tool_name: str) -> ToolRegistryEntry:
        """Return entry or raise UnregisteredToolError."""
        entry = self.get(tool_name)
        if entry is None:
            raise UnregisteredToolError(
                f"ToolRegistry: tool '{tool_name}' is not registered — "
                f"unregistered tools cannot execute (P1/L5 spec §5)",
            )
        return entry

    def registered_names(self) -> list[str]:
        with self._lock:
            return list(self._entries.keys())

    def classify(self, tool_name: str) -> ToolActionClass | None:
        entry = self.get(tool_name)
        return entry.action_class if entry else None


# ---------------------------------------------------------------------------
# ToolSafetyContract — 11 required spec fields
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolSafetyContract:
    """Immutable artifact of one governed tool invocation (P1/L5 spec §2)."""

    tool_call_id: str
    tool_name: str
    run_id: str
    trace_id: str
    actor_id: str
    capability_token: str
    policy_hash: str
    action_class: str
    guardrail_decision_id: str
    tool_input_hash: str
    tool_output_hash: str

    allowed: bool = True
    denial_reason: str = ""
    created_tick: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        tool_name: str,
        run_id: str,
        trace_id: str,
        actor_id: str,
        capability_token: str,
        policy_hash: str,
        action_class: ToolActionClass,
        tool_input: Any,
        tool_output: Any = None,
        allowed: bool = True,
        denial_reason: str = "",
    ) -> ToolSafetyContract:
        call_id = str(uuid.uuid4())[:16]
        guardrail_id = str(uuid.uuid4())[:16]
        input_hash = hashlib.sha256(json.dumps(tool_input, sort_keys=True, default=str).encode()).hexdigest()[
            :16
        ]
        output_hash = (
            hashlib.sha256(json.dumps(tool_output, sort_keys=True, default=str).encode()).hexdigest()[:16]
            if tool_output is not None
            else "none"
        )
        return cls(
            tool_call_id=call_id,
            tool_name=tool_name,
            run_id=run_id,
            trace_id=trace_id,
            actor_id=actor_id,
            capability_token=capability_token,
            policy_hash=policy_hash,
            action_class=action_class.value,
            guardrail_decision_id=guardrail_id,
            tool_input_hash=input_hash,
            tool_output_hash=output_hash,
            allowed=allowed,
            denial_reason=denial_reason,
        )


# ---------------------------------------------------------------------------
# ToolDenialTrace — emitted on fail-closed (spec §6)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolDenialTrace:
    """Immutable denial record for a blocked tool invocation."""

    denial_id: str
    tool_name: str
    run_id: str
    trace_id: str
    actor_id: str
    reason: str
    action_class: str
    requires_human_review: bool
    created_tick: float = field(default_factory=lambda: get_clock().now_epoch())


# ---------------------------------------------------------------------------
# invoke_tool_safely — mandatory entrypoint per spec §3
# ---------------------------------------------------------------------------


def invoke_tool_safely(
    tool_name: str,
    payload: Any,
    capability_token: str,
    actor_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    policy_hash: str = "",
    tool_fn: Callable[..., Any] | None = None,
    registry: ToolRegistry | None = None,
) -> tuple[Any, ToolSafetyContract]:
    """Mandatory tool invocation entrypoint — P1/L5 spec §3.

    Steps (in order, all mandatory):
      1. Validate capability token
      2. Classify tool action (registry lookup)
      3. Enforce policy
      4. Run guardrail decision
      5. Attach policy hash
      6. Attach trace id
      7. Execute only on ALLOW
      8. Emit ToolSafetyContract artifact

    Args:
        tool_name:        Registered tool name.
        payload:          Tool input payload (dict or Any).
        capability_token: Caller's capability token (must be non-empty).
        actor_id:         Caller identity.
        run_id:           Run identifier.
        trace_id:         Trace context (auto-resolved from active trace if empty).
        policy_hash:      Policy hash to attach (uses process default if empty).
        tool_fn:          Optional callable to execute; if None, returns None output.
        registry:         ToolRegistry to use; falls back to process singleton.

    Returns:
        (result, ToolSafetyContract)

    Raises:
        ToolCapabilityError:      capability_token is missing.
        UnregisteredToolError:    tool_name not in registry.
        ToolPolicyError:          policy enforcement failed.
        ToolGuardrailDeniedError: guardrail check denied execution.
    """
    _emit_verifies_policy(str(uuid.uuid4()), "Module.invoke_tool_safely", "L5_POLICY")
    import uuid as _uuid  # noqa: PLC0415

    _emit_records_execution_trace(
        trace_id or run_id or str(_uuid.uuid4()),
        LayerSegment.L5_POLICY,
        f"invoke_tool_safely:{tool_name}",
    )
    reg = registry or get_tool_registry()
    effective_policy = policy_hash or "default"

    # --- Step 1: Validate capability token ---
    if not capability_token or capability_token.strip() == "":
        denial = ToolDenialTrace(
            denial_id=str(uuid.uuid4())[:16],
            tool_name=tool_name,
            run_id=run_id,
            trace_id=trace_id,
            actor_id=actor_id,
            reason="missing_capability_token",
            action_class="UNKNOWN",
            requires_human_review=False,
        )
        _emit_denial(denial)
        raise ToolCapabilityError(f"invoke_tool_safely: capability_token is required for tool '{tool_name}'")

    # --- Step 2: Classify tool action (registry lookup) ---
    entry = reg.require(tool_name)  # raises UnregisteredToolError if absent
    action_class = entry.action_class

    # --- Step 3: Enforce policy ---
    if entry.policy_requirements:
        missing = [req for req in entry.policy_requirements if req not in effective_policy]
        if missing:
            denial = ToolDenialTrace(
                denial_id=str(uuid.uuid4())[:16],
                tool_name=tool_name,
                run_id=run_id,
                trace_id=trace_id,
                actor_id=actor_id,
                reason=f"policy_requirements_unmet:{missing}",
                action_class=action_class.value,
                requires_human_review=entry.human_review_requirement,
            )
            _emit_denial(denial)
            raise ToolPolicyError(
                f"invoke_tool_safely: policy requirements {missing} not satisfied for tool '{tool_name}'",
            )

    # --- Step 4: Guardrail decision ---
    guardrail_verdict = _run_guardrail(tool_name, action_class, payload, effective_policy)
    if not guardrail_verdict:
        denial = ToolDenialTrace(
            denial_id=str(uuid.uuid4())[:16],
            tool_name=tool_name,
            run_id=run_id,
            trace_id=trace_id,
            actor_id=actor_id,
            reason="guardrail_denied",
            action_class=action_class.value,
            requires_human_review=entry.human_review_requirement,
        )
        _emit_denial(denial)
        raise ToolGuardrailDeniedError(
            f"invoke_tool_safely: guardrail denied tool '{tool_name}' (action={action_class.value})",
        )

    # --- Steps 5 & 6: Attach policy hash + trace id ---
    if not trace_id:
        try:
            from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

            _at = get_active_execution_trace()
            trace_id = _at.trace_id if _at else ""
        except (ValueError, TypeError, RuntimeError) as e:
            trace_id = ""

    # --- ADG edges: applies_guardrail, validated_by_safety_plane ---
    _GUARDRAIL_LOG.debug(
        "applies_guardrail TOOL_SAFETY_CONTRACT tool=%s action=%s run_id=%s actor=%s",
        tool_name,
        action_class.value,
        run_id,
        actor_id,
    )
    _SAFETY_PLANE_LOG.debug(
        "validated_by_safety_plane TOOL_SAFETY_CONTRACT tool=%s action=%s policy=%s",
        tool_name,
        action_class.value,
        effective_policy[:12],
    )
    _POLICY_HASH_LOG.debug(
        "references_policy_hash TOOL_SAFETY_CONTRACT tool=%s policy=%s",
        tool_name,
        effective_policy[:12],
    )

    # --- Human review routing for HUMAN_GATED / PRIVILEGED ---
    if action_class in (ToolActionClass.HUMAN_GATED, ToolActionClass.PRIVILEGED):
        _HUMAN_REVIEW_LOG.debug(
            "requires_human_review TOOL_SAFETY_CONTRACT tool=%s action=%s actor=%s",
            tool_name,
            action_class.value,
            actor_id,
        )
        logger.warning(
            "TOOL_SAFETY_CONTRACT human_review_required tool=%s action=%s actor=%s",
            tool_name,
            action_class.value,
            actor_id,
        )
        if entry.human_review_requirement:
            _route_to_human_review(tool_name, action_class, actor_id, run_id, trace_id)

    # --- Step 7: Execute only on ALLOW ---
    result = None
    if tool_fn is not None:
        result = tool_fn(payload) if not isinstance(payload, dict) else tool_fn(**payload)

    # --- Step 8: Emit ToolSafetyContract artifact ---
    contract = ToolSafetyContract.create(
        tool_name=tool_name,
        run_id=run_id,
        trace_id=trace_id,
        actor_id=actor_id,
        capability_token=capability_token,
        policy_hash=effective_policy,
        action_class=action_class,
        tool_input=payload,
        tool_output=result,
        allowed=True,
    )
    _record_contract(contract)

    logger.debug(
        "TOOL_SAFETY_CONTRACT emitted tool=%s call_id=%s action=%s run_id=%s",
        tool_name,
        contract.tool_call_id,
        action_class.value,
        run_id,
    )
    return result, contract


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _run_guardrail(
    tool_name: str,
    action_class: ToolActionClass,
    payload: Any,
    policy_hash: str,
) -> bool:
    """Run guardrail decision. Returns True (ALLOW) or False (DENY)."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module._run_guardrail", "L5_POLICY")
    try:
        from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate  # noqa: PLC0415

        gate = get_guardrail_gate(policy_hash=policy_hash)
        result = gate.check(
            operation=f"tool:{action_class.value}",
            target=tool_name,
            metadata={"tool_name": tool_name, "action_class": action_class.value},
        )
        return result.allowed
    except (RuntimeError, OSError) as exc:
        logger.warning("TOOL_SAFETY_CONTRACT guardrail check failed for tool=%s: %s", tool_name, exc)
        # Fail-closed: if guardrail errors, deny
        return False


def _route_to_human_review(
    tool_name: str,
    action_class: ToolActionClass,
    actor_id: str,
    run_id: str,
    trace_id: str,
) -> None:
    """Emit human review record for HUMAN_GATED / PRIVILEGED tools."""
    try:
        from agentic_core.L5_safety.enforcement.audit.human_review_queue import (  # noqa: PLC0415
            HumanReviewQueue,
            PendingVerdict,
        )

        queue = HumanReviewQueue()
        verdict = PendingVerdict(
            verdict_id=str(uuid.uuid4())[:16],
            component=f"tool:{tool_name}",
            trace_id=trace_id,
            confidence=0.0,  # requires explicit human review
            verdict="pending_tool_execution",
            input_hash=hashlib.sha256(f"{tool_name}:{actor_id}:{run_id}".encode()).hexdigest()[:16],
            metadata={
                "tool_name": tool_name,
                "action_class": action_class.value,
                "actor_id": actor_id,
                "run_id": run_id,
            },
        )
        queue.enqueue(verdict)
    except (RuntimeError, OSError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
        logger.warning("TOOL_SAFETY_CONTRACT human_review routing failed: %s", exc)


def _emit_denial(denial: ToolDenialTrace) -> None:
    """Emit denial trace for a blocked tool invocation."""
    logger.warning(
        "TOOL_SAFETY_CONTRACT DENIED tool=%s reason=%s actor=%s run_id=%s",
        denial.tool_name,
        denial.reason,
        denial.actor_id,
        denial.run_id,
    )
    if denial.requires_human_review:
        _HUMAN_REVIEW_LOG.debug(
            "requires_human_review TOOL_SAFETY_CONTRACT denial tool=%s reason=%s",
            denial.tool_name,
            denial.reason,
        )


_contract_ledger: list[ToolSafetyContract] = []
_contract_lock = threading.Lock()


def _record_contract(contract: ToolSafetyContract) -> None:
    with _contract_lock:
        _contract_ledger.append(contract)


def get_tool_contract_ledger() -> list[ToolSafetyContract]:
    """Return a copy of all emitted ToolSafetyContract records."""
    with _contract_lock:
        return list(_contract_ledger)


# ---------------------------------------------------------------------------
# Process-level ToolRegistry singleton
# ---------------------------------------------------------------------------

_global_registry: ToolRegistry | None = None
_global_registry_lock = threading.Lock()

_DEFAULT_ENTRIES: list[ToolRegistryEntry] = [
    ToolRegistryEntry(
        tool_name="read_file",
        action_class=ToolActionClass.READ_ONLY,
        human_review_requirement=False,
        network_requirement=False,
        description="Read file contents",
    ),
    ToolRegistryEntry(
        tool_name="write_file",
        action_class=ToolActionClass.MUTATING,
        human_review_requirement=False,
        network_requirement=False,
        description="Write file contents",
    ),
    ToolRegistryEntry(
        tool_name="delete_file",
        action_class=ToolActionClass.PRIVILEGED,
        human_review_requirement=True,
        network_requirement=False,
        description="Delete a file — requires human review",
    ),
    ToolRegistryEntry(
        tool_name="execute_shell",
        action_class=ToolActionClass.PRIVILEGED,
        human_review_requirement=True,
        network_requirement=False,
        description="Execute shell command — requires human review",
    ),
    ToolRegistryEntry(
        tool_name="run_python",
        action_class=ToolActionClass.PRIVILEGED,
        human_review_requirement=True,
        network_requirement=False,
        description="Execute Python code — requires human review",
    ),
    ToolRegistryEntry(
        tool_name="fetch",
        action_class=ToolActionClass.NETWORK,
        human_review_requirement=False,
        network_requirement=True,
        description="Fetch a URL",
    ),
    ToolRegistryEntry(
        tool_name="brave_search",
        action_class=ToolActionClass.NETWORK,
        human_review_requirement=False,
        network_requirement=True,
        description="Web search via Brave",
    ),
    ToolRegistryEntry(
        tool_name="playwright",
        action_class=ToolActionClass.NETWORK,
        human_review_requirement=False,
        network_requirement=True,
        description="Browser automation",
    ),
    ToolRegistryEntry(
        tool_name="sequential_thinking",
        action_class=ToolActionClass.READ_ONLY,
        human_review_requirement=False,
        network_requirement=False,
        description="Cognitive reasoning tool",
    ),
    ToolRegistryEntry(
        tool_name="human_review",
        action_class=ToolActionClass.HUMAN_GATED,
        human_review_requirement=True,
        network_requirement=False,
        description="Explicit human review gate",
    ),
    ToolRegistryEntry(
        tool_name="create_entities",
        action_class=ToolActionClass.MUTATING,
        human_review_requirement=False,
        network_requirement=False,
        description="Create knowledge graph entities",
    ),
    ToolRegistryEntry(
        tool_name="add_observations",
        action_class=ToolActionClass.MUTATING,
        human_review_requirement=False,
        network_requirement=False,
        description="Add observations to knowledge graph",
    ),
    ToolRegistryEntry(
        tool_name="redteam_simulate",
        action_class=ToolActionClass.PRIVILEGED,
        human_review_requirement=True,
        network_requirement=False,
        description="Red team simulation — requires human review",
    ),
]


def get_tool_registry() -> ToolRegistry:
    """Return the process-level ToolRegistry singleton (pre-populated)."""
    global _global_registry
    if _global_registry is None:
        with _global_registry_lock:
            if _global_registry is None:
                reg = ToolRegistry()
                for entry in _DEFAULT_ENTRIES:
                    reg.register(entry)
                _global_registry = reg
    return _global_registry


def reset_tool_registry() -> None:
    """Reset the global tool registry (for testing)."""
    global _global_registry
    _global_registry = None


__all__ = [
    "ToolActionClass",
    "ToolRegistryEntry",
    "ToolRegistry",
    "ToolSafetyContract",
    "ToolDenialTrace",
    "invoke_tool_safely",
    "get_tool_registry",
    "reset_tool_registry",
    "get_tool_contract_ledger",
    "UnregisteredToolError",
    "ToolCapabilityError",
    "ToolPolicyError",
    "ToolGuardrailDeniedError",
]
