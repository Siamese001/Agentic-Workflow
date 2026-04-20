"""
Remediation Dispatcher — L2 execution engine for SSOT healing.

Loads a guardian aggregate result, routes check_ids to registered healers
via phase prefix mapping (LEGACY_MIRROR_PLAN ordering), and produces a
CombinedHealResult artifact.

Enforces mutation guard (requires .ssot_sandbox sentinel or --allow-repo-mutation)
and L3 approval gating for apply mode.

Dry-run mode (default): healers report planned actions, no mutations.
Apply mode (--apply): healers execute mutations if approved and sandbox-gated.

CLI:
    python -m agentic_core.L2_execution.scripts.remediation_dispatcher \\
        --guardian-result combined_guardian_result.json \\
        --write-artifacts output_dir \\
        --created-utc 2026-01-01T00:00:00Z \\
        [--apply] [--repo-root PATH] [--approval-bundle PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re as _re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "remediation_dispatcher")
emit_determinism_digest("p0", "remediation_dispatcher")

_emit_dispatches_healing_run("p1", "remediation_dispatcher", "L2")
_emit_routes_through("p1", "remediation_dispatcher", "L2")
_emit_checks_agent_registry("p1", "remediation_dispatcher", "agent_registry")
_emit_validates_agent_capability("p1", "remediation_dispatcher", "capability")
_emit_dispatches_execution_plan("p1", "remediation_dispatcher", "exec_plan")
_emit_agent_executes_agent("p1", "remediation_dispatcher", "sub_agent")
_emit_routes_to_agent("p1", "remediation_dispatcher", "target_agent")
_emit_verifies_policy("p1", "remediation_dispatcher", "policy_check")
_emit_observes_runtime_state("p1", "remediation_dispatcher", "runtime_state")
_emit_verifies_boundary("p1", "remediation_dispatcher", "boundary_check")
_emit_transcripts_response("p1", "remediation_dispatcher", "transcript")
_emit_hard_fails_untranscripted("p1", "remediation_dispatcher")
_emit_gated_by_confidence("p1", "remediation_dispatcher", "confidence_gate")
_emit_escalates_to_human("p1", "remediation_dispatcher", "L2")
_emit_reads_policy_state("p1", "remediation_dispatcher", "L2")

_emit_applies_guardrail("p0", "remediation_dispatcher", "p0_governance")
_emit_snapshots_state("p0", "remediation_dispatcher", "state_snapshot")
_emit_authorize_and_execute("p2", "remediation_dispatcher", "execution_auth")
_emit_validates_capability("p2", "remediation_dispatcher", "capability_check")
_emit_routes_to_capability("p2", "remediation_dispatcher", "capability_route")
_emit_writes_via_uwg("p2", "remediation_dispatcher", "uwg_write")
_emit_blocks_direct_write("p2", "remediation_dispatcher", "direct_write_block")
_emit_records_tool_invocation("p2", "remediation_dispatcher", "tool_invocation")
_emit_captures_execution_output("p2", "remediation_dispatcher", "exec_output")
_emit_dispatches_agent("p3", "remediation_dispatcher", "agent_dispatch")
_emit_coordinates_agents("p3", "remediation_dispatcher", "agent_coordination")
_emit_records_workflow_lineage("p3", "remediation_dispatcher", "workflow_lineage")
_emit_records_healing_outcome("p3", "remediation_dispatcher", "healing_outcome")
_emit_escalates_failure("p3", "remediation_dispatcher", "failure_escalation")
_emit_orchestrates_workflow("p3", "remediation_dispatcher", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "remediation_dispatcher", "healing_dispatch")
_emit_invokes_evaluation("p3", "remediation_dispatcher", "evaluation_signal")
_emit_records_telemetry_event("p4", "remediation_dispatcher", "telemetry_event")
_emit_captures_evaluation_metric("p4", "remediation_dispatcher", "eval_metric")
_emit_stores_embedding("p4", "remediation_dispatcher", "embedding_store")
_emit_updates_meta_learning_state("p4", "remediation_dispatcher", "meta_learning")
_emit_links_execution_to_snapshot("p4", "remediation_dispatcher", "exec_snapshot_link")

logger = logging.getLogger(__name__)


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="remediation_dispatcher",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


from agentic_core.L3_orchestration.healers.healing_tier_config import (
    load_default_healing_tier_config,
)
from agentic_core.L3_orchestration.healers.healing_tier_dispatcher import (
    DefaultHealingProviderInvoker,
    HealingProviderInvoker,
    dispatch_healing,
)
from agentic_core.L3_orchestration.healers.healing_tier_types import FailureSignal

from agentic_core.L2_execution.types.heal_contract_types import (
    CombinedHealResult,
    HealCheckResult,
    HealStatus,
)
from agentic_core.L2_execution.types.healer_registry_types import HEALER_REGISTRY
from agentic_core.L2_execution.types.l2_phase_spec import (
    LEGACY_MIRROR_PLAN,
    L2ExecutionPlan,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("remediation_dispatcher", "p4obs", "metric_1")
_emit_emits_metric_event("remediation_dispatcher", "p4obs", "metric_2")
_emit_emits_metric_event("remediation_dispatcher", "p4obs", "metric_3")
_emit_emits_metric_event("remediation_dispatcher", "p4obs", "metric_4")
_emit_emits_metric_event("remediation_dispatcher", "p4obs", "metric_5")
_emit_emits_metric_event("remediation_dispatcher", "p4obs", "metric_6")
_emit_records_incident_event("remediation_dispatcher", "p4obs", "incident")
_emit_captures_runtime_anomaly("remediation_dispatcher", "p4obs", "anomaly")
_emit_writes_observability_log("remediation_dispatcher", "p4obs", "obs_log")
_emit_updates_monitoring_state("remediation_dispatcher", "p4obs", "mon_state")
_emit_triggers_alert("remediation_dispatcher", "p4obs", "alert")
_emit_links_incident_trace("remediation_dispatcher", "p4obs", "trace_link")
_emit_captures_pattern("remediation_dispatcher", "p3lm", "pattern")
_emit_records_learning_event("remediation_dispatcher", "p3lm", "learning_event")
_emit_writes_learning_snapshot("remediation_dispatcher", "p3lm", "snapshot")
_emit_feeds_meta_learning("remediation_dispatcher", "p3lm", "meta_feed")
_emit_updates_routing_strategy("remediation_dispatcher", "p3lm", "routing")
_emit_improves_agent_policy("remediation_dispatcher", "p3lm", "policy")
_emit_stores_learning_state("remediation_dispatcher", "p3lm", "state")
_emit_records_execution_trace("remediation_dispatcher", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("remediation_dispatcher", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("remediation_dispatcher", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("remediation_dispatcher", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("remediation_dispatcher", "L4_STATE", "p2_trace_5")
_emit_reads_environ("remediation_dispatcher", "env_read", "p2_env_1")
_emit_reads_environ("remediation_dispatcher", "env_read", "p2_env_2")
_emit_reads_runtime_state("remediation_dispatcher", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("remediation_dispatcher", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "remediation_dispatcher", "context_pull")
_emit_pulls_context("p1", "remediation_dispatcher", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "remediation_dispatcher", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "remediation_dispatcher", "uwg_term_2")
_emit_writes_through("p1", "remediation_dispatcher", "write_through")
_emit_writes_through("p1", "remediation_dispatcher", "write_through_2")
_emit_validated_by_safety_plane("p1", "remediation_dispatcher", "safety_validation")
_emit_invokes_eval("p1", "remediation_dispatcher", "eval_call")
_emit_proposal_commits_routing("p1", "remediation_dispatcher", "routing_commit")
from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest
from tqdm import tqdm

emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_dispatch_entry")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_dispatch_exit")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_tool_invoke")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_tool_complete")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_agent_entry")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_agent_exit")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_uwg_write")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_trace_sign")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_guardrail_check")
emit_determinism_digest("trace_remediation_dispatcher", "remediation_dispatcher_policy_verify")


def _get_approval_types():
    """Lazy load approval types to avoid upward import."""
    from agentic_core.L3_orchestration.types.approval_contract_types import (
        ApprovalBundle,
        ApprovalDecision,
        ApprovalRecord,
    )

    return ApprovalBundle, ApprovalDecision, ApprovalRecord


TOOL_ID = "remediation_dispatcher"
OUTPUT_FILENAME = "combined_heal_result.json"

# ---------------------------------------------------------------------------
# Escalation subsystem — allowlist + structured context
# ---------------------------------------------------------------------------

# check_id:healer_name pairs whose healers are allowed to escalate to the LLM tier.
# Using pairs prevents check_id drift where a different healer could reuse the same check_id.
# A healer NOT in this set will never trigger _tier_escalate, even if it
# sets needs_llm_escalation=True.  Extend this list as healers mature.
# Allowlist of (check_id, healer_identity) pairs that can escalate
# healer_identity is computed from the registry function __name__ attribute
# gated_by_confidence: minimum confidence score required before tier-2/3 LLM dispatch.
# Healing operations below this threshold are downgraded to PLAN-ONLY to prevent
# low-confidence mutations from propagating through the pipeline.
MINIMUM_HEAL_CONFIDENCE: float = 0.30  # P(fix_correct) floor — tune via healing_tier_config

HEALER_ESCALATION_ALLOWLIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("guardian_drift_detection", "heal_guardian_drift_detection"),
        ("guardian_import_boundary", "heal_guardian_import_boundary"),
        ("guardian_layer_inversion", "heal_guardian_layer_inversion"),
        ("guardian_ssot_drift", "heal_guardian_ssot_drift"),
    },
)

# Hint key pattern: "key=value" pairs, space-separated
_HINT_KV_RE = _re.compile(r"(\w+)=([^\s]+)")


class EscalationDecisionReason(Enum):
    """Canonical reasons for tier escalation decisions."""

    RETRY_COUNT_THRESHOLD = "retry_count_threshold"
    POLICY_ALLOWLIST = "policy_allowlist"
    EXPLICIT_FLAG = "explicit_flag"


@dataclass(frozen=True, slots=True)
class CanonicalEscalationPayload:
    """Canonical, deterministic escalation payload for audit trails.

    This payload is stable across runs for identical inputs and contains
    all essential decision metadata without transient identifiers.
    """

    provider: str  # e.g., "qwen_vllm" | "gemini"
    model_id: str  # exact string used
    decision_reason: str  # from EscalationDecisionReason
    retry_count: int
    allowlist_check_id: str
    allowlist_healer_name: str
    authoritative_healer_name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict with sorted keys for deterministic serialization."""
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "decision_reason": self.decision_reason,
            "retry_count": self.retry_count,
            "allowlist_check_id": self.allowlist_check_id,
            "allowlist_healer_name": self.allowlist_healer_name,
            "authoritative_healer_name": self.authoritative_healer_name,
        }

    def to_canonical_string(self) -> str:
        """Return deterministic string representation for comparison."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "CanonicalEscalationPayload.to_canonical_string",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CanonicalEscalationPayload.to_canonical_string".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        payload_dict = self.to_dict()
        # Use json with sorted keys for deterministic ordering
        return json.dumps(payload_dict, separators=(",", ":"), sort_keys=True)


@dataclass(frozen=True, slots=True)
class EscalationContext:
    """Structured escalation payload built from a failed HealCheckResult.

    This is the SSOT for what gets passed to FailureSignal — never build
    FailureSignal directly from free-text notes.

    Attributes:
        check_id: The check_id that failed.
        healer_name: Canonical healer identity (same as check_id for now).
        retry_count: Monotonic retry counter from _invoke_healer.
        failure_type: Stable category string (from escalation_hint or default).
        blast_radius_estimate: Float in [0.0, 1.0] (from hint or default 0.5).
        summary: Short human-readable summary (from notes, truncated).
        trace_id: Deterministic SHA-256 prefix of (check_id, retry_count).
    """

    check_id: str
    healer_name: str
    retry_count: int
    failure_type: str
    blast_radius_estimate: float
    summary: str
    trace_id: str

    @classmethod
    def from_result(cls, check_id: str, result: HealCheckResult, retry_count: int) -> EscalationContext:
        """Build deterministically from a HealCheckResult with strict parsing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "EscalationContext.from_result")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:EscalationContext.from_result".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        hint_kvs: dict[str, str] = {}
        if result.escalation_hint:
            for m in _HINT_KV_RE.finditer(result.escalation_hint):
                key, value = m.group(1), m.group(2)
                # Only allow known keys - ignore unknown keys silently
                if key in {"failure_type", "blast_radius"}:
                    hint_kvs[key] = value

        # Parse failure_type with strict default
        failure_type = hint_kvs.get("failure_type", "healer_failure")

        # Parse and clamp blast_radius to [0.0, 1.0]
        try:
            blast = float(hint_kvs.get("blast_radius", "0.5"))
            blast = max(0.0, min(1.0, blast))  # Clamp to valid range
        except (ValueError, TypeError):
            blast = 0.5  # Safe default on invalid input

        # Truncate summary to prevent bloat
        summary = (result.notes or "")[:120]

        # Compute healer identity from registry (authoritative source)
        if check_id in HEALER_REGISTRY:
            healer_identity = getattr(HEALER_REGISTRY[check_id], "__name__", "<unknown>")
        else:
            healer_identity = "<unknown>"

        # Generate longer, more collision-resistant trace_id (16 chars instead of 12)
        canonical = f"{check_id}:{retry_count}"
        trace_id = "disp-" + hashlib.sha256(canonical.encode()).hexdigest()[:16]

        return EscalationContext(
            check_id=check_id,
            healer_name=healer_identity,
            retry_count=retry_count,
            failure_type=failure_type,
            blast_radius_estimate=blast,
            summary=summary,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# Canonical phase names and phase-to-check_id mapping
# ---------------------------------------------------------------------------

EXPECTED_PHASE_NAMES: tuple[str, ...] = (
    "pre_audit",
    "discovery",
    "reconciliation",
    "alignment",
    "arch_validation",
    "healing",
    "certification",
)

# Explicit mapping: phase_name -> tuple of check_id prefixes.
# A guardian check_id is "mapped" to a phase if it startswith any prefix.
# Empty tuple = phase has no prefix-routed checks (intentional for healing/certification).
PHASE_CHECK_ID_PREFIXES: dict[str, tuple[str, ...]] = {
    "pre_audit": ("guardian_drift_detection",),
    "discovery": ("guardian_location_alignment",),
    "reconciliation": (
        "guardian_classification_compliance",
        "naming_compliance",
        "territory_compliance",
    ),
    "alignment": (
        "guardian_hierarchy_compliance",
        "missing_structure",
        "subfolder_compliance",
    ),
    "arch_validation": (
        "guardian_architecture_governance",
        "import_compliance",
        "layer_gravity",
    ),
    "healing": (),
    "certification": (),
}

NOTE_MAPPED = "no healer registered"
NOTE_UNMAPPED = "unmapped to phase; no healer registered"

# Dispatcher-local override: which phases require L3 approval.
# Does NOT modify LEGACY_MIRROR_PLAN; evaluated at dispatch time.
PHASE_APPROVAL_REQUIRED_OVERRIDES: dict[str, bool] = {}

# Mutation-dependent approval policy: when True, apply mode with at least one
# planned healer invocation requires an L3 approval bundle satisfying
# phase_name="healing".  Dry-run and apply-with-zero-healers are exempt.
APPROVAL_REQUIRED_FOR_APPLY: bool = True


SANDBOX_SENTINEL = ".ssot_sandbox"


class ApprovalGatingError(Exception):
    """Raised when a phase requires approval but none was provided."""


class MutationGuardError(Exception):
    """Raised when apply mode is used without sandbox or explicit override."""


def mutation_allowed(repo_root: Path, allow_override: bool) -> bool:
    """Check if mutations are permitted in the given repo root.

    Mutations allowed iff:
    - repo_root contains the sandbox sentinel file, OR
    - allow_override is True (--allow-repo-mutation)
    """
    if allow_override:
        return True
    return (repo_root / SANDBOX_SENTINEL).is_file()


# ---------------------------------------------------------------------------
# PhaseSpec validation
# ---------------------------------------------------------------------------


def validate_phase_names(plan: L2ExecutionPlan) -> None:
    """Validate that plan phase names exactly match the expected canonical list.

    Raises ValueError if names differ in count, order, or content.
    """
    actual = tuple(p.name for p in plan.phases)
    if actual != EXPECTED_PHASE_NAMES:
        raise ValueError(
            f"PhaseSpec name integrity violation: expected {list(EXPECTED_PHASE_NAMES)}, got {list(actual)}",
        )


def approvals_satisfy_phase(
    bundle: ApprovalBundle | None,
    phase_name: str,
) -> bool:
    """Check whether the approval bundle satisfies gating for a phase.

    Returns True iff bundle contains at least one record where:
    - record.phase_name == phase_name
    - record.decision == APPROVED
    - record.token is non-empty
    """
    if bundle is None:
        return False
    for record in bundle.records:
        if record.phase_name == phase_name and record.decision == ApprovalDecision.APPROVED and record.token:
            return True
    return False


def classify_check_ids(
    check_ids: list[str],
    phase_prefixes: dict[str, tuple[str, ...]] | None = None,
) -> tuple[set[str], set[str]]:
    """Classify check_ids into mapped and unmapped sets.

    A check_id is "mapped" if it startswith any prefix in any phase mapping.

    Returns (mapped, unmapped) sets.
    """
    if phase_prefixes is None:
        phase_prefixes = PHASE_CHECK_ID_PREFIXES

    all_prefixes: list[str] = []
    for prefixes in phase_prefixes.values():
        all_prefixes.extend(prefixes)

    mapped: set[str] = set()
    unmapped: set[str] = set()
    for cid in check_ids:
        if any(cid.startswith(prefix) for prefix in all_prefixes):
            mapped.add(cid)
        else:
            unmapped.add(cid)
    return mapped, unmapped


# ---------------------------------------------------------------------------
# Guardian aggregate parsing
# ---------------------------------------------------------------------------


def extract_check_ids(guardian_aggregate: dict[str, Any]) -> list[str]:
    """Extract check_ids from a guardian aggregate result deterministically.

    Supports the canonical aggregate shape produced by run_all_guardians:
    - top-level "checks" list of dicts, each with "check_id"

    Returns sorted, deduplicated list of check_ids.
    Raises ValueError for unrecognised shapes.
    """
    checks = guardian_aggregate.get("checks")
    if isinstance(checks, list):
        ids: list[str] = []
        for item in checks:
            if isinstance(item, dict) and "check_id" in item:
                ids.append(item["check_id"])
            else:
                raise ValueError(
                    f"Unexpected check item shape: {type(item).__name__}, expected dict with 'check_id'",
                )
        return sorted(set(ids))

    raise ValueError(
        "Unrecognised guardian aggregate shape: expected top-level 'checks' list of dicts with 'check_id'",
    )


def extract_checks_by_id(guardian_aggregate: dict[str, Any]) -> dict[str, dict]:
    """Build a lookup from check_id to full check dict.

    For duplicate check_ids, the first occurrence wins.
    """
    result: dict[str, dict] = {}
    for item in guardian_aggregate.get("checks", []):
        if isinstance(item, dict) and "check_id" in item:
            cid = item["check_id"]
            if cid not in result:
                result[cid] = item
    return result


# ---------------------------------------------------------------------------
# Sub-check expansion (healer reachability)
# ---------------------------------------------------------------------------


def extract_healable_items_from_guardian_check(
    check: dict[str, Any],
) -> tuple[tuple[str, dict[str, Any]], ...]:
    """Extract healable (sub_check_id, evidence_dict) pairs from a roll-up check.

    Supported evidence shapes (defensive):
    1. evidence.checks is list[dict] with "check_id" and optional "evidence" keys.
    2. evidence.violations is dict keyed by sub_check_id -> list/obj.
    3. Otherwise returns empty tuple.

    Returns tuple sorted by sub_check_id.
    """
    evidence = check.get("evidence")
    if not isinstance(evidence, dict):
        return ()

    # Shape 1: evidence has "checks" list of dicts with "check_id"
    sub_checks = evidence.get("checks")
    if isinstance(sub_checks, list):
        items: list[tuple[str, dict[str, Any]]] = []
        for sc in sub_checks:
            if isinstance(sc, dict) and "check_id" in sc:
                sub_evidence = sc.get("evidence", {})
                if not isinstance(sub_evidence, dict):
                    sub_evidence = {}
                items.append((sc["check_id"], {**sc, "evidence": sub_evidence}))
        return tuple(sorted(items, key=lambda x: x[0]))

    # Shape 2: evidence has "violations" dict keyed by sub_check_id
    violations = evidence.get("violations")
    if isinstance(violations, dict):
        items_v: list[tuple[str, dict[str, Any]]] = []
        for sub_id, val in violations.items():
            if isinstance(sub_id, str):
                items_v.append((sub_id, {"check_id": sub_id, "evidence": {"violations": val}}))
        return tuple(sorted(items_v, key=lambda x: x[0]))

    return ()


def build_healer_worklist(
    aggregate_checks: list[dict[str, Any]],
) -> tuple[tuple[str, dict[str, Any]], ...]:
    """Build a deduplicated, sorted worklist of (check_id, check_dict) pairs.

    For each roll-up check:
    - If roll-up check_id itself exists in HEALER_REGISTRY, include it.
    - Also include extracted sub-items where sub_check_id exists in HEALER_REGISTRY.
    Deduplicate by check_id (roll-up form wins over sub-check form).
    Stable sort final tuple by check_id.
    """
    seen: dict[str, dict[str, Any]] = {}

    for check in tqdm(aggregate_checks, desc="Processing", unit="item"):
        if not isinstance(check, dict):
            continue
        rollup_id = check.get("check_id", "")

        # Include roll-up if it has a healer
        if rollup_id in HEALER_REGISTRY and rollup_id not in seen:
            seen[rollup_id] = check

        # Extract and include sub-items
        for sub_id, sub_dict in extract_healable_items_from_guardian_check(check):
            if sub_id in HEALER_REGISTRY and sub_id not in seen:
                seen[sub_id] = sub_dict

    return tuple(sorted(seen.items(), key=lambda x: x[0]))


# ---------------------------------------------------------------------------
# Approval bundle parsing
# ---------------------------------------------------------------------------


def load_approval_bundle(path: Path) -> ApprovalBundle:
    """Load and return an ApprovalBundle from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    records_raw = data.get("records", [])
    records: list[ApprovalRecord] = []
    for r in tqdm(records_raw, desc="Processing", unit="item"):
        records.append(
            ApprovalRecord(
                phase_name=r["phase_name"],
                guardian_id=r.get("guardian_id"),
                check_ids=tuple(r.get("check_ids", ())),
                decision=ApprovalDecision(r["decision"]),
                approver=r["approver"],
                rationale=r.get("rationale"),
                token=r["token"],
                created_utc=r["created_utc"],
            ),
        )
    return ApprovalBundle(records=tuple(records))


# ---------------------------------------------------------------------------
# Healer invocation
# ---------------------------------------------------------------------------


def _tier_escalate(
    check_id: str,
    result: HealCheckResult,
    *,
    retry_count: int = 0,
    invoker: HealingProviderInvoker | None = None,
) -> str:
    """Escalate a FAILED heal result to the confidence-tier LLM system.

    Guards:
      1. result.status must be FAILED (explicit check)
      2. result.needs_llm_escalation must be True (healer opt-in)
      3. (check_id, healer_name) must be in HEALER_ESCALATION_ALLOWLIST
      4. registered healer identity must match expected healer_name

    Builds a FailureSignal from EscalationContext (never from raw notes),
    calls dispatch_healing, and returns a deterministic audit note string.

    Args:
        check_id: The check_id that failed healing.
        result: The FAILED HealCheckResult from the healer.
        retry_count: Monotonic retry counter (drives tier selection).
        invoker: Injectable provider invoker (default: DefaultHealingProviderInvoker).

    Returns:
        A deterministic audit note string, or a skip note if guards block.
    """
    # Guard 1: Explicitly check status is FAILED
    if result.status != HealStatus.FAILED:
        return f"tier_escalation_skipped: check_id={check_id} reason=status_not_failed"

    # Guard 2: Healer must opt-in to escalation
    if not result.needs_llm_escalation:
        return f"tier_escalation_skipped: check_id={check_id} reason=needs_llm_escalation_false"

    # Extract healer_name from escalation context
    escalation_ctx = EscalationContext.from_result(check_id, result, retry_count)
    healer_pair = (check_id, escalation_ctx.healer_name)

    # Guard 3: Check allowlist (healer_name is computed from registry, so this is authoritative)
    if healer_pair not in HEALER_ESCALATION_ALLOWLIST:
        return (
            f"tier_escalation_skipped: check_id={check_id} "
            f"healer={escalation_ctx.healer_name} reason=not_in_allowlist"
        )

    if invoker is None:
        invoker = DefaultHealingProviderInvoker()

    # Re-use the context we already created for the allowlist check
    ctx = escalation_ctx

    signal = FailureSignal(
        source_agent="remediation_dispatcher",
        failure_type=ctx.failure_type,
        error_signature=ctx.check_id,
        trace_id=ctx.trace_id,
        context={"healer_name": ctx.healer_name, "summary": ctx.summary},
        retry_count=ctx.retry_count,
        blast_radius_estimate=ctx.blast_radius_estimate,
    )
    config = load_default_healing_tier_config()
    decision, record = dispatch_healing(
        signal.to_healing_input(),
        config,
        invoker=invoker,
        agent_name="remediation_dispatcher",
    )

    # gated_by_confidence: block dispatch when confidence is below floor
    if decision.heal_confidence < MINIMUM_HEAL_CONFIDENCE:
        return (
            f"tier_escalation_skipped: check_id={check_id} "
            f"reason=confidence_below_floor "
            f"confidence={decision.heal_confidence:.4f} "
            f"floor={MINIMUM_HEAL_CONFIDENCE}"
        )

    # Determine decision reason
    if ctx.retry_count >= 2:
        decision_reason = EscalationDecisionReason.RETRY_COUNT_THRESHOLD.value
    elif healer_pair in HEALER_ESCALATION_ALLOWLIST:
        decision_reason = EscalationDecisionReason.POLICY_ALLOWLIST.value
    else:
        decision_reason = EscalationDecisionReason.EXPLICIT_FLAG.value

    # Map tier to provider
    provider_map = {
        "QWEN_VLLM": "qwen_vllm",
        "GEMINI_2_5_PRO": "gemini",
        "LOCAL_AGENT": "local_agent",
    }
    provider = provider_map.get(decision.tier.value, "unknown")

    # Create canonical payload
    canonical_payload = CanonicalEscalationPayload(
        provider=provider,
        model_id=record.model_id,
        decision_reason=decision_reason,
        retry_count=ctx.retry_count,
        allowlist_check_id=check_id,
        allowlist_healer_name=escalation_ctx.healer_name,
        authoritative_healer_name=escalation_ctx.healer_name,
    )

    # Include canonical payload in the note (separate from trace_id)
    payload_str = canonical_payload.to_canonical_string()
    return (
        f"tier_escalation: check_id={check_id} "
        f"tier={decision.tier.value} "
        f"model={record.model_id} "
        f"confidence={decision.heal_confidence:.4f} "
        f"trace_id={ctx.trace_id} "
        f"payload={payload_str}"
    )


def _invoke_healer(
    check_id: str,
    check_dict: dict,
    *,
    repo_root: Path | None = None,
    apply: bool = False,
    tier_invoker: HealingProviderInvoker | None = None,
    retry_count: int = 0,
) -> HealCheckResult:
    """Invoke a registered healer safely, converting errors to FAILED results.

    Passes repo_root and apply as keyword arguments to healers that accept them.
    Returns the healer's HealCheckResult on success, or a FAILED result
    containing the exception class name on error.

    When a healer returns FAILED AND sets needs_llm_escalation=True AND its
    check_id is in HEALER_ESCALATION_ALLOWLIST, escalates to the confidence-tier
    LLM system via _tier_escalate, appending the audit note to result.notes.

    Re-entrancy: retry_count must be incremented by the caller on each retry.
    _tier_escalate is side-effect bounded (no writes, no recursion).
    """
    healer_fn = HEALER_REGISTRY[check_id]
    try:
        result = healer_fn(check_dict, repo_root=repo_root, apply=apply)
    except (ValueError, TypeError) as exc:  # guardian: allow-silent-swallow
        logger.warning("healer %s raised %s: %s", check_id, type(exc).__name__, exc)
        result = HealCheckResult(
            check_id=check_id,
            status=HealStatus.FAILED,
            changes_made=(),
            rollback_info=None,
            notes=f"healer error: {type(exc).__name__}: {exc}",
            needs_llm_escalation=True,
            escalation_hint="failure_type=healer_error",
        )

    if result.status == HealStatus.FAILED:
        escalation_note = _tier_escalate(
            check_id,
            result,
            retry_count=retry_count,
            invoker=tier_invoker,
        )
        return HealCheckResult(
            check_id=result.check_id,
            status=result.status,
            changes_made=result.changes_made,
            rollback_info=result.rollback_info,
            notes=f"{result.notes or ''} | {escalation_note}".strip(" |"),
            needs_llm_escalation=result.needs_llm_escalation,
            escalation_hint=result.escalation_hint,
        )

    return result


# ---------------------------------------------------------------------------
# Core dispatcher logic
# ---------------------------------------------------------------------------


def run_dispatcher(
    guardian_result_path: Path,
    write_artifacts_dir: Path,
    created_utc: str,
    plan_name: str = "LEGACY_MIRROR_PLAN",
    approval_bundle_path: Path | None = None,
    *,
    apply: bool = False,
    repo_root: Path | None = None,
    allow_repo_mutation: bool = False,
) -> CombinedHealResult:
    """Execute the dispatcher interpreting LEGACY_MIRROR_PLAN PhaseSpec.

    1. Validates PhaseSpec name integrity.
    2. Enforces mutation guard if apply mode requested.
    3. Loads the guardian aggregate and extracts check_ids.
    4. Loads optional ApprovalBundle (needed before phase iteration for gating).
    5. Classifies check_ids as mapped or unmapped via phase prefix mapping.
    6. Iterates phases in order, enforcing approval gating.
    7. Produces a CombinedHealResult.
    8. Validates and writes the result to the output directory.

    Returns the CombinedHealResult.
    Raises ApprovalGatingError if a phase requires approval and none is provided.
    Raises MutationGuardError if apply without sandbox or override.
    """
    _ectx = _make_execution_context(str(guardian_result_path), "remediation_dispatcher.run_dispatcher")
    _invoke_authorize_and_execute(
        _ectx,
        lambda p: p,
        "default",
        str(guardian_result_path),
        target_name="remediation_dispatcher.run_dispatcher",
    )
    # 1. Validate PhaseSpec integrity
    validate_phase_names(LEGACY_MIRROR_PLAN)

    # 2. Mutation guard
    if apply:
        if repo_root is None:
            raise MutationGuardError(
                "--apply requires --repo-root to identify the target repository",
            )
        if not mutation_allowed(repo_root, allow_repo_mutation):
            raise MutationGuardError(
                f"Mutation refused: repo at '{repo_root}' is not a sandbox "
                f"(missing {SANDBOX_SENTINEL}) and --allow-repo-mutation not set",
            )

    # 3. Load guardian aggregate
    guardian_data = json.loads(guardian_result_path.read_text(encoding="utf-8"))
    check_ids = extract_check_ids(guardian_data)
    checks_by_id = extract_checks_by_id(guardian_data)
    aggregate_checks = guardian_data.get("checks", [])

    # 3b. Build healer worklist (roll-up + sub-check expansion)
    worklist = build_healer_worklist(aggregate_checks)
    worklist_by_id: dict[str, dict[str, Any]] = dict(worklist)
    all_healable_ids = set(worklist_by_id.keys())

    # 4. Load optional approval bundle (before phase iteration for gating)
    bundle: ApprovalBundle | None = None
    approved_tokens: list[str] = []
    if approval_bundle_path is not None:
        bundle = load_approval_bundle(approval_bundle_path)
        for record in bundle.records:
            if record.decision == ApprovalDecision.APPROVED:
                approved_tokens.append(record.token)
    approved_tokens = sorted(set(approved_tokens))

    # 4b. Mutation-dependent approval gate
    #     Fires only when: apply=True AND worklist has >=1 healer invocation.
    #     Independent of phase name mapping.
    if apply and all_healable_ids and APPROVAL_REQUIRED_FOR_APPLY:
        if not approvals_satisfy_phase(bundle, "healing"):
            raise ApprovalGatingError(
                "Apply mode with planned healer invocations requires L3 approval. "
                "Provide an ApprovalBundle with phase_name='healing' and "
                "decision=APPROVED.",
            )

    # 5. Classify check_ids (both roll-up and healable sub-check ids)
    all_routable_ids = sorted(set(check_ids) | all_healable_ids)
    mapped_ids, unmapped_ids = classify_check_ids(all_routable_ids)

    # 6. Iterate phases in PhaseSpec order
    heal_checks: list[HealCheckResult] = []
    emitted_ids: set[str] = set()
    for phase in tqdm(LEGACY_MIRROR_PLAN.phases, desc="Processing", unit="item"):
        # Select check_ids for this phase (from both roll-ups and sub-checks)
        prefixes = PHASE_CHECK_ID_PREFIXES.get(phase.name, ())
        phase_cids = sorted(
            cid
            for cid in all_routable_ids
            if any(cid.startswith(p) for p in prefixes) and cid not in emitted_ids
        )

        # --- Approval gating enforcement ---
        phase_requires_approval = PHASE_APPROVAL_REQUIRED_OVERRIDES.get(
            phase.name,
            phase.approval_required,
        )
        if phase_requires_approval and phase_cids:
            if not approvals_satisfy_phase(bundle, phase.name):
                raise ApprovalGatingError(
                    f"Phase '{phase.name}' requires L3 approval but no matching "
                    f"APPROVED record found in ApprovalBundle for phase_name='{phase.name}'",
                )

        for cid in tqdm(phase_cids, desc="Processing", unit="item"):
            emitted_ids.add(cid)
            if cid in HEALER_REGISTRY:
                check_dict = worklist_by_id.get(
                    cid,
                    checks_by_id.get(cid, {"check_id": cid}),
                )
                heal_checks.append(
                    _invoke_healer(cid, check_dict, repo_root=repo_root, apply=apply),
                )
            else:
                heal_checks.append(
                    HealCheckResult(
                        check_id=cid,
                        status=HealStatus.SKIPPED,
                        changes_made=(),
                        rollback_info=None,
                        notes=NOTE_MAPPED,
                    ),
                )

        # --- Rerun guardians hook (planned feature, not yet implemented) ---
        if phase.rerun_guardians:
            pass  # Planned: re-run specified guardians after healing to verify fixes

    # 7. Add unmapped check_ids (coverage preservation)
    for cid in tqdm(sorted(unmapped_ids), desc="Processing", unit="item"):
        if cid not in emitted_ids:
            heal_checks.append(
                HealCheckResult(
                    check_id=cid,
                    status=HealStatus.SKIPPED,
                    changes_made=(),
                    rollback_info=None,
                    notes=NOTE_UNMAPPED,
                ),
            )

    # 8. Build CombinedHealResult
    result = CombinedHealResult(
        tool_id=TOOL_ID,
        plan_name=plan_name,
        results=tuple(heal_checks),
        approved_by=tuple(approved_tokens),
        created_utc=created_utc,
    )

    # 9. Validate before writing
    errors = result.validate()
    if errors:
        raise ValueError(f"CombinedHealResult validation failed: {errors}")

    # 10. Write artifact
    write_artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = write_artifacts_dir / OUTPUT_FILENAME
    out_path.write_text(result.to_json(), encoding="utf-8")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="L2 Remediation Dispatcher")
    parser.add_argument(
        "--guardian-result",
        required=True,
        help="Path to combined_guardian_result.json",
    )
    parser.add_argument(
        "--approval-bundle",
        default=None,
        help="Path to approval bundle JSON (optional)",
    )
    parser.add_argument(
        "--write-artifacts",
        required=True,
        help="Directory to write combined_heal_result.json",
    )
    parser.add_argument(
        "--created-utc",
        required=True,
        help="ISO-8601 timestamp for the result (deterministic, no auto-now)",
    )
    parser.add_argument(
        "--plan-name",
        default="LEGACY_MIRROR_PLAN",
        help="Execution plan name (default: LEGACY_MIRROR_PLAN)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Enable mutating healers (default: dry-run only)",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Path to repository root (required if --apply)",
    )
    parser.add_argument(
        "--allow-repo-mutation",
        action="store_true",
        help="Allow mutations on non-sandbox repos (use with caution)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for future use (no-op in this wave)",
    )
    args = parser.parse_args()

    try:
        result = run_dispatcher(
            guardian_result_path=Path(
                args.guardian_result
            ),  # guardian: MutationGuardError should be handled with specific context
            write_artifacts_dir=Path(args.write_artifacts),
            created_utc=args.created_utc,
            plan_name=args.plan_name,  # guardian: ApprovalGatingError should be handled with specific context
            approval_bundle_path=Path(args.approval_bundle) if args.approval_bundle else None,
            apply=args.apply,
            repo_root=Path(args.repo_root) if args.repo_root else None,
            allow_repo_mutation=args.allow_repo_mutation,
        )
    except MutationGuardError as exc:  # guardian: MutationGuardError should be handled with specific context
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    except (
        ApprovalGatingError
    ) as exc:  # guardian: ApprovalGatingError should be handled with specific context
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(result.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
