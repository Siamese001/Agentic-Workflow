"""Case memory types — durable precedent library for Memory MCP.

Defines the five canonical bundle types that form the persistent case-law archive:

  - CaseRecord          — execution trace + route + outcome + replay status
  - HealerBundle        — violation → healer → patch → validation → replay linkage
  - GovernancePrecedent — safety block/remediate outcome + policy hash + FP/FN history
  - PromptBundle        — PromptBOM + template manifest + injection findings + outcome
  - HITLPreferenceRecord — Path-D decision + patch + reason tags + DPO linkage

All types are frozen dataclasses with deterministic ``to_dict()`` / ``to_json()`` /
``stable_hash()`` methods.  No wall-clock reads; ``timestamp_utc`` is caller-supplied.
No mutable state.  Safe to hash, sign, and store as Memory MCP entities.

ADG relation families used as memory keys:
  routing | healing | prompt_generation | guardrail | hitl | replay | retrieval
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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

_emit_authorize_and_execute("p2", "case_memory_types", "execution_auth")
_emit_validates_capability("p2", "case_memory_types", "capability_check")
_emit_routes_to_capability("p2", "case_memory_types", "capability_route")
_emit_writes_via_uwg("p2", "case_memory_types", "uwg_write")
_emit_blocks_direct_write("p2", "case_memory_types", "direct_write_block")
_emit_records_tool_invocation("p2", "case_memory_types", "tool_invocation")
_emit_captures_execution_output("p2", "case_memory_types", "exec_output")
_emit_dispatches_agent("p3", "case_memory_types", "agent_dispatch")
_emit_coordinates_agents("p3", "case_memory_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "case_memory_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "case_memory_types", "healing_outcome")
_emit_escalates_failure("p3", "case_memory_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "case_memory_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "case_memory_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "case_memory_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "case_memory_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "case_memory_types", "eval_metric")
_emit_stores_embedding("p4", "case_memory_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "case_memory_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "case_memory_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.L6_system_learning.enforcement.determinism import deterministic_json, stable_sha256_json

_emit_emits_metric_event("case_memory_types", "p4obs", "metric_1")
_emit_emits_metric_event("case_memory_types", "p4obs", "metric_2")
_emit_emits_metric_event("case_memory_types", "p4obs", "metric_3")
_emit_emits_metric_event("case_memory_types", "p4obs", "metric_4")
_emit_emits_metric_event("case_memory_types", "p4obs", "metric_5")
_emit_emits_metric_event("case_memory_types", "p4obs", "metric_6")
_emit_records_incident_event("case_memory_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("case_memory_types", "p4obs", "anomaly")
_emit_writes_observability_log("case_memory_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("case_memory_types", "p4obs", "mon_state")
_emit_triggers_alert("case_memory_types", "p4obs", "alert")
_emit_links_incident_trace("case_memory_types", "p4obs", "trace_link")
_emit_captures_pattern("case_memory_types", "p3lm", "pattern")
_emit_records_learning_event("case_memory_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("case_memory_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("case_memory_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("case_memory_types", "p3lm", "routing")
_emit_improves_agent_policy("case_memory_types", "p3lm", "policy")
_emit_stores_learning_state("case_memory_types", "p3lm", "state")
_emit_records_execution_trace("case_memory_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("case_memory_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("case_memory_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("case_memory_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("case_memory_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("case_memory_types", "env_read", "p2_env_1")
_emit_reads_environ("case_memory_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("case_memory_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("case_memory_types", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "case_memory_types")
_emit_applies_guardrail("p0", "case_memory_types", "p0_governance")
_emit_snapshots_state("p0", "case_memory_types", "state_snapshot")
_emit_pulls_context("p1", "case_memory_types", "context_pull")
_emit_pulls_context("p1", "case_memory_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "case_memory_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "case_memory_types", "uwg_term_secondary")
_emit_writes_through("p1", "case_memory_types", "write_through")
_emit_writes_through("p1", "case_memory_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "case_memory_types", "safety_validation")
_emit_invokes_eval("p1", "case_memory_types", "eval_call")
_emit_proposal_commits_routing("p1", "case_memory_types", "routing_commit")
_emit_escalates_to_human("p1", "case_memory_types", "human_escalation")
_emit_routes_through("p1", "case_memory_types", "route_through")
_emit_checks_agent_registry("p1", "case_memory_types", "agent_registry")
_emit_validates_agent_capability("p1", "case_memory_types", "capability")
_emit_dispatches_execution_plan("p1", "case_memory_types", "exec_plan")
_emit_agent_executes_agent("p1", "case_memory_types", "sub_agent")
_emit_routes_to_agent("p1", "case_memory_types", "target_agent")
_emit_verifies_policy("p1", "case_memory_types", "policy_check")
_emit_observes_runtime_state("p1", "case_memory_types", "runtime_state")
_emit_verifies_boundary("p1", "case_memory_types", "boundary_check")
_emit_transcripts_response("p1", "case_memory_types", "transcript")
_emit_hard_fails_untranscripted("p1", "case_memory_types")
_emit_gated_by_confidence("p1", "case_memory_types", "confidence_gate")
emit_replay_key("p0", "case_memory_types")
emit_determinism_digest("p0", "case_memory_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Shared leaf types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OutcomeClass:
    """Terminal outcome classification for a case or bundle.

    Attributes
    ----------
    label:
        Coarse class — one of SUCCESS | FAILURE | PARTIAL | UNKNOWN.
    sub_label:
        Optional fine-grained sub-classification (e.g. ``HEALER_TIMEOUT``).
    replay_pass:
        True if the deterministic replay validation passed for this outcome.
    """

    label: Literal["SUCCESS", "FAILURE", "PARTIAL", "UNKNOWN"]
    sub_label: str | None = None
    replay_pass: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "replay_pass": self.replay_pass,
            "sub_label": self.sub_label,
        }


@dataclass(frozen=True)
class PolicyHashRef:
    """Immutable reference to a governing policy snapshot.

    Attributes
    ----------
    policy_hash:
        SHA-256 hexdigest of the policy config at decision time.
    config_version:
        Human-readable version tag (e.g. ``"v3.2.1"``).
    """

    policy_hash: str
    config_version: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "config_version": self.config_version,
            "policy_hash": self.policy_hash,
        }


@dataclass(frozen=True)
class ADGNodeRef:
    """Compact reference to an ADG node used as a memory indexing key.

    Attributes
    ----------
    entity_name:
        Canonical ADG entity name, e.g. ``ADG::Module::agentic_core/L0_routing/...``.
    layer:
        Layer label, e.g. ``L0``, ``L4``, ``L_SL``.
    relation_family:
        ADG relation family that contextualises this reference
        (routing | healing | prompt_generation | guardrail | hitl | replay | retrieval).
    territory:
        Optional sovereign territory label (e.g. ``L4_state``, ``L5_safety``).
    """

    entity_name: str
    layer: str
    relation_family: str
    territory: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "entity_name": self.entity_name,
            "layer": self.layer,
            "relation_family": self.relation_family,
            "territory": self.territory,
        }


# ---------------------------------------------------------------------------
# CaseRecord — execution case memory
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CaseRecord:
    """Durable execution case record keyed by trace_id.

    Stores the normalised summary of one request execution for the persistent
    precedent library.  Designed to be stored as a Memory MCP entity with
    ADG-derived entity names as indexing keys.

    Fields must align with the replay core: ``plan_hash``, ``policy_hash``,
    and ``replay_key`` are required for replay-safe lookups.

    Attributes
    ----------
    artifact_type:
        Always ``CASE_RECORD``.
    trace_id:
        Deterministic SHA-256 trace identifier for this execution.
    plan_hash:
        SHA-256 of the request/plan that was executed.
    policy_hash_ref:
        Reference to the governing policy snapshot.
    replay_key:
        Deterministic replay key emitted by the execution core.
    request_family:
        Coarse request family label (e.g. ``"rg_resume"``, ``"lic_campaign"``).
    route_path:
        Execution path taken (e.g. ``"PATH_A"``, ``"PATH_D"``).
    agent_set:
        Tuple of canonical agent identifiers involved in this execution.
    prompt_artifact_hash:
        SHA-256 of the CompiledPromptArtifact used (if any).
    healer_actions:
        Tuple of healer IDs that fired during this execution (empty if none).
    validator_actions:
        Tuple of validator IDs that ran during this execution (empty if none).
    outcome:
        Terminal outcome classification.
    adg_nodes:
        ADG node references used as memory indexing keys.
    timestamp_utc:
        Unix timestamp provided by the caller (no wall-clock reads here).
    """

    artifact_type: Literal["CASE_RECORD"]
    trace_id: str
    plan_hash: str
    policy_hash_ref: PolicyHashRef
    replay_key: str
    request_family: str
    route_path: str
    agent_set: tuple[str, ...]
    prompt_artifact_hash: str | None
    healer_actions: tuple[str, ...]
    validator_actions: tuple[str, ...]
    outcome: OutcomeClass
    adg_nodes: tuple[ADGNodeRef, ...]
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "CASE_RECORD":
            raise ValueError(f"artifact_type must be 'CASE_RECORD', got {self.artifact_type!r}")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not self.plan_hash:
            raise ValueError("plan_hash must not be empty")
        if not self.replay_key:
            raise ValueError("replay_key must not be empty")
        if not self.request_family:
            raise ValueError("request_family must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "adg_nodes": [n.to_dict() for n in self.adg_nodes],
            "agent_set": list(self.agent_set),
            "artifact_type": self.artifact_type,
            "healer_actions": list(self.healer_actions),
            "outcome": self.outcome.to_dict(),
            "plan_hash": self.plan_hash,
            "policy_hash_ref": self.policy_hash_ref.to_dict(),
            "prompt_artifact_hash": self.prompt_artifact_hash,
            "replay_key": self.replay_key,
            "request_family": self.request_family,
            "route_path": self.route_path,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "validator_actions": list(self.validator_actions),
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# ---------------------------------------------------------------------------
# HealerBundle — healer outcome memory
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HealerBundle:
    """Durable healer lineage record: violation → healer → patch → validation.

    Stored in Memory MCP to improve future healer selection.  The combination
    of ``violation_pattern`` + ``policy_hash_ref`` forms a natural lookup key
    for case-based reasoning ("we saw this failure shape before").

    Attributes
    ----------
    artifact_type:
        Always ``HEALER_BUNDLE``.
    bundle_id:
        Deterministic SHA-256 ID for this bundle (stable_sha256_json of payload).
    trace_id:
        Parent execution trace identifier.
    violation_pattern:
        Stable string describing the violation type/category.
    healer_id:
        Canonical healer identifier that was dispatched.
    healer_tier:
        Healing tier used (e.g. ``LOCAL_AGENT``, ``QWEN_VLLM``).
    patch_hash:
        SHA-256 of the applied patch/diff (if any).
    validation_passed:
        Whether the validator confirmed the patch succeeded.
    replay_validated:
        Whether deterministic replay confirmed the patch is idempotent.
    policy_hash_ref:
        Policy snapshot active when the healer fired.
    adg_healer_node:
        ADG node reference for the healer agent.
    adg_validator_node:
        ADG node reference for the validator (if known).
    outcome:
        Terminal outcome for this healing attempt.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["HEALER_BUNDLE"]
    bundle_id: str
    trace_id: str
    violation_pattern: str
    healer_id: str
    healer_tier: str
    patch_hash: str | None
    validation_passed: bool
    replay_validated: bool
    policy_hash_ref: PolicyHashRef
    adg_healer_node: ADGNodeRef
    adg_validator_node: ADGNodeRef | None
    outcome: OutcomeClass
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "HEALER_BUNDLE":
            raise ValueError(f"artifact_type must be 'HEALER_BUNDLE', got {self.artifact_type!r}")
        if not self.bundle_id:
            raise ValueError("bundle_id must not be empty")
        if not self.healer_id:
            raise ValueError("healer_id must not be empty")
        if not self.violation_pattern:
            raise ValueError("violation_pattern must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "adg_healer_node": self.adg_healer_node.to_dict(),
            "adg_validator_node": (
                self.adg_validator_node.to_dict() if self.adg_validator_node is not None else None
            ),
            "artifact_type": self.artifact_type,
            "bundle_id": self.bundle_id,
            "healer_id": self.healer_id,
            "healer_tier": self.healer_tier,
            "outcome": self.outcome.to_dict(),
            "patch_hash": self.patch_hash,
            "policy_hash_ref": self.policy_hash_ref.to_dict(),
            "replay_validated": self.replay_validated,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "valid_ation_passed": self.validation_passed,
            "violation_pattern": self.violation_pattern,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# ---------------------------------------------------------------------------
# GovernancePrecedent — policy incident memory
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FalsePositiveNegativeRecord:
    """Disposition of a single FP/FN safety decision.

    Attributes
    ----------
    disposition:
        One of ``FALSE_POSITIVE``, ``FALSE_NEGATIVE``, ``CORRECT``.
    later_policy_adjusted:
        True if a subsequent policy update addressed this finding.
    adjustment_trace_id:
        Trace ID of the policy adjustment (if any).
    """

    disposition: Literal["FALSE_POSITIVE", "FALSE_NEGATIVE", "CORRECT"]
    later_policy_adjusted: bool = False
    adjustment_trace_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "adjustment_trace_id": self.adjustment_trace_id,
            "disposition": self.disposition,
            "later_policy_adjusted": self.later_policy_adjusted,
        }


@dataclass(frozen=True)
class GovernancePrecedent:
    """Durable policy incident memory: block/remediate → precedent.

    Links safety classifier outputs and block/remediate/reject outcomes to
    a policy hash, enabling policy tuning and audit trail reconstruction.

    Attributes
    ----------
    artifact_type:
        Always ``GOVERNANCE_PRECEDENT``.
    precedent_id:
        Deterministic SHA-256 ID for this precedent.
    trace_id:
        Source execution trace.
    safety_issue_type:
        Stable category of the safety issue (e.g. ``PROMPT_INJECTION``,
        ``POLICY_VIOLATION``, ``UWG_BYPASS``).
    guardrail_id:
        Canonical identifier of the guardrail that fired.
    remediation_applied:
        Canonical description of the remediation (e.g. ``BLOCK``,
        ``REWRITE``, ``REJECT``, ``ESCALATE``).
    safety_classifier_outputs:
        Tuple of (classifier_id, score) pairs from all classifiers that ran.
    policy_hash_ref:
        Policy snapshot at decision time.
    fp_fn_record:
        FP/FN disposition (if subsequently reviewed).
    adg_guardrail_node:
        ADG node reference for the guardrail.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["GOVERNANCE_PRECEDENT"]
    precedent_id: str
    trace_id: str
    safety_issue_type: str
    guardrail_id: str
    remediation_applied: str
    safety_classifier_outputs: tuple[tuple[str, float], ...]
    policy_hash_ref: PolicyHashRef
    fp_fn_record: FalsePositiveNegativeRecord | None
    adg_guardrail_node: ADGNodeRef
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "GOVERNANCE_PRECEDENT":
            raise ValueError(f"artifact_type must be 'GOVERNANCE_PRECEDENT', got {self.artifact_type!r}")
        if not self.precedent_id:
            raise ValueError("precedent_id must not be empty")
        if not self.safety_issue_type:
            raise ValueError("safety_issue_type must not be empty")
        if not self.guardrail_id:
            raise ValueError("guardrail_id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "adg_guardrail_node": self.adg_guardrail_node.to_dict(),
            "artifact_type": self.artifact_type,
            "fp_fn_record": (self.fp_fn_record.to_dict() if self.fp_fn_record is not None else None),
            "guardrail_id": self.guardrail_id,
            "policy_hash_ref": self.policy_hash_ref.to_dict(),
            "precedent_id": self.precedent_id,
            "remediation_applied": self.remediation_applied,
            "safety_classifier_outputs": [list(pair) for pair in self.safety_classifier_outputs],
            "safety_issue_type": self.safety_issue_type,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# ---------------------------------------------------------------------------
# PromptBundle — prompt artifact memory
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptBundle:
    """Durable prompt artifact memory for provenance and reuse.

    Persists the association between a prompt assembly, its template manifest,
    injection findings, and the downstream outcome class so future assemblies
    can avoid patterns that caused drift or safety issues.

    Attributes
    ----------
    artifact_type:
        Always ``PROMPT_BUNDLE``.
    bundle_id:
        Deterministic SHA-256 ID for this bundle.
    trace_id:
        Source execution trace.
    prompt_artifact_hash:
        SHA-256 of the CompiledPromptArtifact.
    template_manifest_hash:
        SHA-256 of the template manifest used.
    slot_types_used:
        Tuple of prompt slot types used (e.g. ``("S0", "C0", "U0")``).
    injection_findings:
        Tuple of injection finding strings (empty if clean).
    authority_violations:
        Tuple of slot authority violation descriptions (empty if clean).
    outcome:
        Terminal outcome for this prompt assembly.
    policy_hash_ref:
        Policy snapshot at assembly time.
    adg_prompt_node:
        ADG node reference for the prompt assembly component.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["PROMPT_BUNDLE"]
    bundle_id: str
    trace_id: str
    prompt_artifact_hash: str
    template_manifest_hash: str
    slot_types_used: tuple[str, ...]
    injection_findings: tuple[str, ...]
    authority_violations: tuple[str, ...]
    outcome: OutcomeClass
    policy_hash_ref: PolicyHashRef
    adg_prompt_node: ADGNodeRef
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "PROMPT_BUNDLE":
            raise ValueError(f"artifact_type must be 'PROMPT_BUNDLE', got {self.artifact_type!r}")
        if not self.bundle_id:
            raise ValueError("bundle_id must not be empty")
        if not self.prompt_artifact_hash:
            raise ValueError("prompt_artifact_hash must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "adg_prompt_node": self.adg_prompt_node.to_dict(),
            "artifact_type": self.artifact_type,
            "authority_violations": list(self.authority_violations),
            "bundle_id": self.bundle_id,
            "injection_findings": list(self.injection_findings),
            "outcome": self.outcome.to_dict(),
            "policy_hash_ref": self.policy_hash_ref.to_dict(),
            "prompt_artifact_hash": self.prompt_artifact_hash,
            "slot_types_used": list(self.slot_types_used),
            "template_manifest_hash": self.template_manifest_hash,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# ---------------------------------------------------------------------------
# HITLPreferenceRecord — human preference memory
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HITLPreferenceRecord:
    """Durable HITL human preference record — human judgment survives sessions.

    Stores Path-D decisions, patch schemas, approval/reject reasons, and DPO
    linkage so the system can reason from prior human review decisions.

    Attributes
    ----------
    artifact_type:
        Always ``HITL_PREFERENCE_RECORD``.
    record_id:
        Deterministic SHA-256 ID for this record.
    trace_id:
        Source execution trace (Path-D decision context).
    original_plan_hash:
        SHA-256 of the plan that triggered human review.
    human_decision:
        ``APPROVE`` or ``REJECT``.
    reason_tags:
        Tuple of stable reason tag strings (e.g. ``("SAFETY_CONCERN",
        "PROMPT_DRIFT")``).
    patch_schema_hash:
        SHA-256 of the patch schema submitted for review (if any).
    dpo_pair_id:
        DPO preference pair identifier generated from this decision (if any).
    downstream_outcome:
        Outcome observed after the human decision was applied (if known).
    policy_hash_ref:
        Policy snapshot at review time.
    adg_hitl_node:
        ADG node reference for the HITL checkpoint.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["HITL_PREFERENCE_RECORD"]
    record_id: str
    trace_id: str
    original_plan_hash: str
    human_decision: Literal["APPROVE", "REJECT"]
    reason_tags: tuple[str, ...]
    patch_schema_hash: str | None
    dpo_pair_id: str | None
    downstream_outcome: OutcomeClass | None
    policy_hash_ref: PolicyHashRef
    adg_hitl_node: ADGNodeRef
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "HITL_PREFERENCE_RECORD":
            raise ValueError(f"artifact_type must be 'HITL_PREFERENCE_RECORD', got {self.artifact_type!r}")
        if not self.record_id:
            raise ValueError("record_id must not be empty")
        if not self.original_plan_hash:
            raise ValueError("original_plan_hash must not be empty")
        if self.human_decision not in ("APPROVE", "REJECT"):
            raise ValueError(f"human_decision must be 'APPROVE' or 'REJECT', got {self.human_decision!r}")

    def to_dict(self) -> dict[str, object]:
        return {
            "adg_hitl_node": self.adg_hitl_node.to_dict(),
            "artifact_type": self.artifact_type,
            "downstream_outcome": (
                self.downstream_outcome.to_dict() if self.downstream_outcome is not None else None
            ),
            "dpo_pair_id": self.dpo_pair_id,
            "human_decision": self.human_decision,
            "original_plan_hash": self.original_plan_hash,
            "patch_schema_hash": self.patch_schema_hash,
            "policy_hash_ref": self.policy_hash_ref.to_dict(),
            "reason_tags": list(self.reason_tags),
            "record_id": self.record_id,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# ---------------------------------------------------------------------------
# Union alias for bundle dispatch
# ---------------------------------------------------------------------------

CaseBundle = CaseRecord | HealerBundle | GovernancePrecedent | PromptBundle | HITLPreferenceRecord

BUNDLE_ARTIFACT_TYPES: frozenset[str] = frozenset(
    {
        "CASE_RECORD",
        "HEALER_BUNDLE",
        "GOVERNANCE_PRECEDENT",
        "PROMPT_BUNDLE",
        "HITL_PREFERENCE_RECORD",
    },
)

__all__ = [
    "ADGNodeRef",
    "BUNDLE_ARTIFACT_TYPES",
    "CaseBundle",
    "CaseRecord",
    "FalsePositiveNegativeRecord",
    "GovernancePrecedent",
    "HealerBundle",
    "HITLPreferenceRecord",
    "OutcomeClass",
    "PolicyHashRef",
    "PromptBundle",
]
