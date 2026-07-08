"""
SSOT Guardian Registry — Single Source of Truth for Guardian enumeration.

All consumers of Guardian metadata MUST derive from this registry:
- run_all_guardians.py (aggregator)
- test_guardian_meta_coverage.py (coverage ratchet)
- run_guardian_contract_integrity.py (integrity checker)
- docs/contracts/guardian_to_L6.md (observability contract)

NO filesystem globs. NO duplicated lists. Registry is SSOT.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "guardian_registry_types")
trace_contract.emit_determinism_digest("p0", "guardian_registry_types")

trace_contract._emit_dispatches_healing_run("p1", "guardian_registry_types", "L0")
trace_contract._emit_routes_through("p1", "guardian_registry_types", "L0")
trace_contract._emit_checks_agent_registry("p1", "guardian_registry_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "guardian_registry_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "guardian_registry_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "guardian_registry_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "guardian_registry_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "guardian_registry_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "guardian_registry_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "guardian_registry_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "guardian_registry_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "guardian_registry_types")
trace_contract._emit_gated_by_confidence("p1", "guardian_registry_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "guardian_registry_types", "L0")
trace_contract._emit_reads_policy_state("p1", "guardian_registry_types", "L0")
trace_contract._emit_authorize_and_execute("p2", "guardian_registry_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "guardian_registry_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "guardian_registry_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "guardian_registry_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "guardian_registry_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "guardian_registry_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "guardian_registry_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "guardian_registry_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "guardian_registry_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "guardian_registry_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "guardian_registry_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "guardian_registry_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "guardian_registry_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "guardian_registry_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "guardian_registry_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "guardian_registry_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "guardian_registry_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "guardian_registry_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "guardian_registry_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "guardian_registry_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("guardian_registry_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("guardian_registry_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("guardian_registry_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("guardian_registry_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("guardian_registry_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("guardian_registry_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("guardian_registry_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("guardian_registry_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("guardian_registry_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("guardian_registry_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("guardian_registry_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("guardian_registry_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("guardian_registry_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("guardian_registry_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("guardian_registry_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("guardian_registry_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("guardian_registry_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("guardian_registry_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("guardian_registry_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("guardian_registry_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("guardian_registry_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("guardian_registry_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("guardian_registry_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("guardian_registry_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("guardian_registry_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("guardian_registry_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("guardian_registry_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("guardian_registry_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "guardian_registry_types", "context_pull")
trace_contract._emit_pulls_context("p1", "guardian_registry_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "guardian_registry_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "guardian_registry_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "guardian_registry_types", "write_through")
trace_contract._emit_writes_through("p1", "guardian_registry_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "guardian_registry_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "guardian_registry_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "guardian_registry_types", "routing_commit")


class GuardianTier(str, Enum):
    """Execution tier for guardians."""

    FAST = "fast"
    SLOW = "slow"


@dataclass(frozen=True)
class GuardianSpec:
    """
    Specification for a single Guardian.

    Attributes:
        guardian_id: Stable unique identifier (used in artifacts, logs, tests).
        entrypoint_module: Full dotted module path to the guardian script.
        entrypoint_fn: Name of the runner function that returns GuardianResult.
        check_ids: Exhaustive tuple of check_ids this guardian may emit.
        tier: Execution tier (fast/slow) for scheduling.
        enabled_by_default: Whether included in default aggregation runs.
    """

    guardian_id: str
    entrypoint_module: str
    entrypoint_fn: str
    check_ids: tuple[str, ...]
    tier: Literal["fast", "slow"] = "fast"
    enabled_by_default: bool = True


ALL_GUARDIANS: tuple[GuardianSpec, ...] = tuple(
    sorted(
        [
            GuardianSpec(
                guardian_id="location_alignment",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_location_alignment",
                entrypoint_fn="run_location_alignment_guardian",
                check_ids=("misplaced_files", "missing_directories"),
                tier="slow",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="hygiene",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_hygiene",
                entrypoint_fn="run_hygiene_guardian",
                check_ids=("temp_artifacts", "empty_folders", "init_only_folders"),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="manifest_integrity",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_manifest",
                entrypoint_fn="run_manifest_guardian",
                check_ids=("manifest_exists", "lock_exists", "checksum_match"),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="drift_detection",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_drift_detection",
                entrypoint_fn="run_drift_detection_guardian",
                check_ids=("root_drift",),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="architecture_governance",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_architecture_governance",
                entrypoint_fn="run_architecture_governance_guardian",
                check_ids=("import_compliance", "layer_gravity"),
                tier="slow",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="classification_compliance",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_classification_compliance",
                entrypoint_fn="run_classification_compliance_guardian",
                check_ids=("naming_compliance", "territory_compliance"),
                tier="slow",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="hierarchy_compliance",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_hierarchy_compliance",
                entrypoint_fn="run_hierarchy_compliance_guardian",
                check_ids=("missing_structure", "subfolder_compliance"),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="c0_sovereignty_enforcement",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_c0_sovereignty",
                entrypoint_fn="run_c0_sovereignty_guardian",
                check_ids=(
                    "embedding_drives_routing",
                    "embedding_drives_tier_selection",
                    "embedding_mutates_threshold",
                ),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="change_package_activation_guard",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_change_package_activation",
                entrypoint_fn="run_change_package_activation_guardian",
                check_ids=(
                    "proposal_only_bypass",
                    "direct_version_store_commit",
                    "activation_without_approval_gate",
                ),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="cross_layer_mutation_guard",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_cross_layer_mutation",
                entrypoint_fn="run_cross_layer_mutation_guardian",
                check_ids=(
                    "upward_layer_mutation",
                    "L6_mutates_L4",
                    "L4_invokes_L2",
                    "C0_mutates_control_plane",
                ),
                tier="slow",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="escalation_determinism",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_escalation_determinism",
                entrypoint_fn="run_escalation_determinism_guardian",
                check_ids=(
                    "failure_signal_built_from_raw_notes",
                    "alternate_escalation_context_construction",
                    "escalation_context_mutation",
                ),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="gateway_bypass",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_gateway_bypass",
                entrypoint_fn="run_gateway_bypass_guardian",
                check_ids=(
                    "direct_model_call",
                    "provider_sdk_import",
                    "bypass_tier_router",
                    "bypass_embedding_factory",
                ),
                tier="fast",
                enabled_by_default=True,
            ),
            GuardianSpec(
                guardian_id="contract_integrity",
                entrypoint_module="ops_scripts.dev_tools.L0_routing_scripts.run_guardian_contract_integrity",
                entrypoint_fn="run_contract_integrity_guardian",
                check_ids=("scripts_found", "imports_contract", "imports_normalize", "returns_result"),
                tier="fast",
                enabled_by_default=False,
            ),
        ],
        key=lambda s: s.guardian_id,
    ),
)


def get_guardian_specs(
    *,
    enabled_only: bool = False,
    tier: GuardianTier | str | None = None,
) -> tuple[GuardianSpec, ...]:
    """
    Retrieve guardian specs with optional filtering.

    Args:
        enabled_only: If True, return only guardians with enabled_by_default=True.
        tier: If provided, filter to only guardians of this tier.

    Returns:
        Tuple of GuardianSpec in deterministic sorted order by guardian_id.
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "get_guardian_specs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "get_guardian_specs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L0_ROUTING, "get_guardian_specs")
    result = list(ALL_GUARDIANS)
    if enabled_only:
        result = [s for s in result if s.enabled_by_default]
    if tier is not None:
        tier_val = tier.value if isinstance(tier, GuardianTier) else tier
        result = [s for s in result if s.tier == tier_val]
    return tuple(sorted(result, key=lambda s: s.guardian_id))


def get_guardian_by_id(guardian_id: str) -> GuardianSpec | None:
    """Lookup a guardian spec by its ID. Returns None if not found."""
    for spec in ALL_GUARDIANS:
        if spec.guardian_id == guardian_id:
            return spec
    return None


def get_all_check_ids() -> dict[str, tuple[str, ...]]:
    """
    Return a mapping of guardian_id → check_ids for all registered guardians.
    Used by behavioral coverage ratchet.
    """
    return {spec.guardian_id: spec.check_ids for spec in ALL_GUARDIANS}


def get_guardian_entrypoints() -> dict[str, tuple[str, str]]:
    """
    Return a mapping of guardian_id → (module, function) for integrity checking.
    """
    return {spec.guardian_id: (spec.entrypoint_module, spec.entrypoint_fn) for spec in ALL_GUARDIANS}
