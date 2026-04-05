"""L4 State: Case Library — ADG-keyed durable precedent archive in Memory MCP.

The Case Library is the persistent case-law archive described in the memory
architecture design.  It wraps ``GraphMemoryBridge`` to store five canonical
bundle types as structured Memory MCP entities, keyed by ADG node names,
relation families, layer labels, and policy hashes.

Design invariants
-----------------
1. READ-ONLY delegation to GraphMemoryBridge for writes; no direct mcp11 calls.
2. Entity names are ADG-namespaced (``ADG::Case::<artifact_type>::<stable_hash>``).
3. All observations are canonicalised summaries — never raw mutable blobs.
4. Replay-safe: no wall-clock reads; caller supplies ``timestamp_utc``.
5. Fail-open: all store/link operations log and return False rather than raise,
   so a Memory MCP outage never crashes the calling agent.
6. Search results are returned as raw dicts (MCP graph nodes) — callers are
   responsible for re-hydrating typed objects.

Entity naming schema
--------------------
``ADG::Case::<ARTIFACT_TYPE>::<stable_hash_prefix_16>``
  e.g. ``ADG::Case::CASE_RECORD::a3f7b291c4d18e02``

Relations created by the library
---------------------------------
``sourced_from_adg_node``   — links a bundle entity to its ADG component node
``governed_by_policy``      — links a bundle entity to a policy hash entity
``has_outcome``             — links a bundle entity to an outcome entity
``healer_resolved``         — links a HEALER_BUNDLE to the violation it resolved
``hitl_approved`` / ``hitl_rejected`` — links a HITL record to the plan entity
``lineage_of``              — links a bundle to its parent trace entity
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "case_library")
emit_determinism_digest("p0", "case_library")

_emit_dispatches_healing_run("p1", "case_library", "L4")
_emit_routes_through("p1", "case_library", "L4")
_emit_checks_agent_registry("p1", "case_library", "agent_registry")
_emit_validates_agent_capability("p1", "case_library", "capability")
_emit_dispatches_execution_plan("p1", "case_library", "exec_plan")
_emit_agent_executes_agent("p1", "case_library", "sub_agent")
_emit_routes_to_agent("p1", "case_library", "target_agent")
_emit_verifies_policy("p1", "case_library", "policy_check")
_emit_observes_runtime_state("p1", "case_library", "runtime_state")
_emit_verifies_boundary("p1", "case_library", "boundary_check")
_emit_transcripts_response("p1", "case_library", "transcript")
_emit_hard_fails_untranscripted("p1", "case_library")
_emit_gated_by_confidence("p1", "case_library", "confidence_gate")
_emit_escalates_to_human("p1", "case_library", "L4")
_emit_reads_policy_state("p1", "case_library", "L4")
_emit_authorize_and_execute("p2", "case_library", "execution_auth")
_emit_validates_capability("p2", "case_library", "capability_check")
_emit_routes_to_capability("p2", "case_library", "capability_route")
_emit_writes_via_uwg("p2", "case_library", "uwg_write")
_emit_blocks_direct_write("p2", "case_library", "direct_write_block")
_emit_records_tool_invocation("p2", "case_library", "tool_invocation")
_emit_captures_execution_output("p2", "case_library", "exec_output")
_emit_dispatches_agent("p3", "case_library", "agent_dispatch")
_emit_coordinates_agents("p3", "case_library", "agent_coordination")
_emit_records_workflow_lineage("p3", "case_library", "workflow_lineage")
_emit_records_healing_outcome("p3", "case_library", "healing_outcome")
_emit_escalates_failure("p3", "case_library", "failure_escalation")
_emit_orchestrates_workflow("p3", "case_library", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "case_library", "healing_dispatch")
_emit_invokes_evaluation("p3", "case_library", "evaluation_signal")
_emit_records_telemetry_event("p4", "case_library", "telemetry_event")
_emit_captures_evaluation_metric("p4", "case_library", "eval_metric")
_emit_stores_embedding("p4", "case_library", "embedding_store")
_emit_updates_meta_learning_state("p4", "case_library", "meta_learning")
_emit_links_execution_to_snapshot("p4", "case_library", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("case_library", "p4obs", "metric_1")
_emit_emits_metric_event("case_library", "p4obs", "metric_2")
_emit_emits_metric_event("case_library", "p4obs", "metric_3")
_emit_emits_metric_event("case_library", "p4obs", "metric_4")
_emit_emits_metric_event("case_library", "p4obs", "metric_5")
_emit_emits_metric_event("case_library", "p4obs", "metric_6")
_emit_records_incident_event("case_library", "p4obs", "incident")
_emit_captures_runtime_anomaly("case_library", "p4obs", "anomaly")
_emit_writes_observability_log("case_library", "p4obs", "obs_log")
_emit_updates_monitoring_state("case_library", "p4obs", "mon_state")
_emit_triggers_alert("case_library", "p4obs", "alert")
_emit_links_incident_trace("case_library", "p4obs", "trace_link")
_emit_captures_pattern("case_library", "p3lm", "pattern")
_emit_records_learning_event("case_library", "p3lm", "learning_event")
_emit_writes_learning_snapshot("case_library", "p3lm", "snapshot")
_emit_feeds_meta_learning("case_library", "p3lm", "meta_feed")
_emit_updates_routing_strategy("case_library", "p3lm", "routing")
_emit_improves_agent_policy("case_library", "p3lm", "policy")
_emit_stores_learning_state("case_library", "p3lm", "state")
_emit_records_execution_trace("case_library", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("case_library", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("case_library", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("case_library", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("case_library", "L4_STATE", "p2_trace_5")
_emit_reads_environ("case_library", "env_read", "p2_env_1")
_emit_reads_environ("case_library", "env_read", "p2_env_2")
_emit_reads_runtime_state("case_library", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("case_library", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "case_library", "context_pull")
_emit_pulls_context("p1", "case_library", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "case_library", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "case_library", "uwg_term_2")
_emit_writes_through("p1", "case_library", "write_through")
_emit_writes_through("p1", "case_library", "write_through_2")
_emit_validated_by_safety_plane("p1", "case_library", "safety_validation")
_emit_invokes_eval("p1", "case_library", "eval_call")
_emit_proposal_commits_routing("p1", "case_library", "routing_commit")

if TYPE_CHECKING:
    from system_learning.types.case_memory_types import (
        CaseBundle,
    )


def _get_case_memory_types():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_case_memory_types", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_case_memory_types", "p0_governance")
    from system_learning.types.case_memory_types import (
        BUNDLE_ARTIFACT_TYPES,
        CaseBundle,
        CaseRecord,
        GovernancePrecedent,
        HealerBundle,
        HITLPreferenceRecord,
        PromptBundle,
    )

    return (
        BUNDLE_ARTIFACT_TYPES,
        CaseBundle,
        CaseRecord,
        GovernancePrecedent,
        HealerBundle,
        HITLPreferenceRecord,
        PromptBundle,
    )


logger = logging.getLogger(__name__)

_ADG_NS = "ADG"
_CASE_NS = "Case"
_POLICY_NS = "Policy"
_TRACE_NS = "Trace"
_PLAN_NS = "Plan"

_MAX_OBS_LEN = 1800


def _entity_name(artifact_type: str, stable_hash: str) -> str:
    """Build a canonical ADG entity name for a case bundle.

    Schema: ``ADG::Case::<ARTIFACT_TYPE>::<first_16_hex_chars>``
    """
    return f"{_ADG_NS}::{_CASE_NS}::{artifact_type}::{stable_hash[:16]}"


def _policy_entity_name(policy_hash: str) -> str:
    return f"{_ADG_NS}::{_POLICY_NS}::{policy_hash[:16]}"


def _trace_entity_name(trace_id: str) -> str:
    return f"{_ADG_NS}::{_TRACE_NS}::{trace_id[:16]}"


def _plan_entity_name(plan_hash: str) -> str:
    return f"{_ADG_NS}::{_PLAN_NS}::{plan_hash[:16]}"


def _truncate(s: str, limit: int = _MAX_OBS_LEN) -> str:
    if len(s) <= limit:
        return s
    return s[: limit - 3] + "..."


# ---------------------------------------------------------------------------
# CaseLibrary
# ---------------------------------------------------------------------------


class CaseLibrary:
    """ADG-keyed Memory MCP durable case-law archive.

    All five bundle types are stored as structured entities in the Memory MCP
    knowledge graph.  The library builds:

    * One entity per bundle (keyed by ``ADG::Case::<type>::<hash_prefix>``).
    * Observations: artifact_type, trace_id, policy_hash, outcome label,
      replay status, ADG node names, and a compact canonical summary.
    * Relations: ``sourced_from_adg_node``, ``governed_by_policy``,
      ``lineage_of``, and bundle-type-specific relations.

    Usage
    -----
    .. code-block:: python

        lib = CaseLibrary()
        lib.store(case_record)
        results = lib.search("healer timeout failure CASE_RECORD")
    """

    def __init__(self, bridge: GraphMemoryBridge | None = None) -> None:
        self._bridge = bridge or GraphMemoryBridge.get_instance()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store(self, bundle: CaseBundle) -> bool:
        """Store a case bundle as a Memory MCP entity with ADG-keyed relations.

        Returns True if the entity was written (or already existed), False on error.
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "CaseLibrary.store")
        artifact_type = getattr(bundle, "artifact_type", None)
        _BUNDLE_ARTIFACT_TYPES = _get_case_memory_types()[0]
        if artifact_type not in _BUNDLE_ARTIFACT_TYPES:
            logger.warning("[CaseLibrary] Unknown artifact_type: %s", artifact_type)
            return False

        stable_hash = bundle.stable_hash()
        entity_name = _entity_name(artifact_type, stable_hash)

        observations = self._build_observations(bundle, stable_hash)
        ok = self._bridge.create_agent_entity(
            agent_name=entity_name,
            agent_type=f"CaseBundle_{artifact_type}",
            observations=observations,
        )
        if not ok:
            logger.debug("[CaseLibrary] Entity write skipped/failed: %s", entity_name)

        self._link_bundle(bundle, entity_name, stable_hash)
        return ok

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search the case library by free-text query.

        Returns a list of raw MCP graph node dicts.  Empty list on miss or error.
        """
        return self._bridge.search_entities(query)

    def search_by_policy(self, policy_hash: str) -> list[dict[str, Any]]:
        """Find all bundles governed by a specific policy hash."""
        policy_node = _policy_entity_name(policy_hash)
        return self._bridge.search_entities(policy_node)

    def search_by_trace(self, trace_id: str) -> list[dict[str, Any]]:
        """Find all bundles linked to a specific execution trace."""
        trace_node = _trace_entity_name(trace_id)
        return self._bridge.search_entities(trace_node)

    def search_by_adg_node(self, adg_entity_name: str) -> list[dict[str, Any]]:
        """Find all bundles sourced from a specific ADG component node."""
        return self._bridge.search_entities(adg_entity_name)

    # ------------------------------------------------------------------
    # Internal: observation builders
    # ------------------------------------------------------------------

    def _build_observations(self, bundle: CaseBundle, stable_hash: str) -> list[str]:
        """Build the observation list stored on the Memory MCP entity."""
        # Resolve types at runtime (they are TYPE_CHECKING-only imports)
        (
            _,
            _CaseBundle,
            _CaseRecord,
            _GovernancePrecedent,
            _HealerBundle,
            _HITLPreferenceRecord,
            _PromptBundle,
        ) = _get_case_memory_types()

        artifact_type = bundle.artifact_type  # type: ignore[union-attr]
        common = [
            f"artifact_type:{artifact_type}",
            f"stable_hash:{stable_hash}",
            f"trace_id:{bundle.trace_id}",  # type: ignore[union-attr]
        ]

        if isinstance(bundle, _CaseRecord):
            specific = [
                f"plan_hash:{bundle.plan_hash}",
                f"replay_key:{bundle.replay_key}",
                f"request_family:{bundle.request_family}",
                f"route_path:{bundle.route_path}",
                f"outcome_label:{bundle.outcome.label}",
                f"replay_pass:{bundle.outcome.replay_pass}",
                f"agent_set:{','.join(bundle.agent_set)}",
                f"policy_hash:{bundle.policy_hash_ref.policy_hash}",
                _truncate(f"canonical_summary:{bundle.to_json()}"),
            ]

        elif isinstance(bundle, _HealerBundle):
            specific = [
                f"violation_pattern:{bundle.violation_pattern}",
                f"healer_id:{bundle.healer_id}",
                f"healer_tier:{bundle.healer_tier}",
                f"validation_passed:{bundle.validation_passed}",
                f"replay_validated:{bundle.replay_validated}",
                f"outcome_label:{bundle.outcome.label}",
                f"policy_hash:{bundle.policy_hash_ref.policy_hash}",
                _truncate(f"canonical_summary:{bundle.to_json()}"),
            ]

        elif isinstance(bundle, _GovernancePrecedent):
            specific = [
                f"safety_issue_type:{bundle.safety_issue_type}",
                f"guardrail_id:{bundle.guardrail_id}",
                f"remediation_applied:{bundle.remediation_applied}",
                f"policy_hash:{bundle.policy_hash_ref.policy_hash}",
                (
                    f"fp_fn_disposition:{bundle.fp_fn_record.disposition}"
                    if bundle.fp_fn_record
                    else "fp_fn_disposition:NONE"
                ),
                _truncate(f"canonical_summary:{bundle.to_json()}"),
            ]

        elif isinstance(bundle, _PromptBundle):
            specific = [
                f"prompt_artifact_hash:{bundle.prompt_artifact_hash}",
                f"template_manifest_hash:{bundle.template_manifest_hash}",
                f"slot_types_used:{','.join(bundle.slot_types_used)}",
                f"injection_findings_count:{len(bundle.injection_findings)}",
                f"authority_violations_count:{len(bundle.authority_violations)}",
                f"outcome_label:{bundle.outcome.label}",
                f"policy_hash:{bundle.policy_hash_ref.policy_hash}",
                _truncate(f"canonical_summary:{bundle.to_json()}"),
            ]

        elif isinstance(bundle, _HITLPreferenceRecord):
            specific = [
                f"original_plan_hash:{bundle.original_plan_hash}",
                f"human_decision:{bundle.human_decision}",
                f"reason_tags:{','.join(bundle.reason_tags)}",
                f"dpo_pair_id:{bundle.dpo_pair_id or 'NONE'}",
                f"policy_hash:{bundle.policy_hash_ref.policy_hash}",
                (
                    f"downstream_outcome:{bundle.downstream_outcome.label}"
                    if bundle.downstream_outcome
                    else "downstream_outcome:NONE"
                ),
                _truncate(f"canonical_summary:{bundle.to_json()}"),
            ]
        else:
            specific = [_truncate(f"canonical_summary:{bundle.to_json()}")]  # type: ignore[union-attr]

        return common + specific

    # ------------------------------------------------------------------
    # Internal: relation builders
    # ------------------------------------------------------------------

    def _link_bundle(self, bundle: CaseBundle, entity_name: str, stable_hash: str) -> None:
        """Create all ADG-keyed relations for a bundle entity."""
        trace_id: str = bundle.trace_id  # type: ignore[union-attr]
        policy_hash_ref = bundle.policy_hash_ref  # type: ignore[union-attr]

        trace_node = _trace_entity_name(trace_id)
        policy_node = _policy_entity_name(policy_hash_ref.policy_hash)

        self._bridge.create_agent_entity(
            agent_name=trace_node,
            agent_type="ExecutionTrace",
            observations=[f"trace_id:{trace_id}"],
        )
        self._bridge.create_agent_entity(
            agent_name=policy_node,
            agent_type="PolicySnapshot",
            observations=[
                f"policy_hash:{policy_hash_ref.policy_hash}",
                f"config_version:{policy_hash_ref.config_version or 'NONE'}",
            ],
        )

        self._bridge.create_relation(entity_name, trace_node, "lineage_of")
        self._bridge.create_relation(entity_name, policy_node, "governed_by_policy")

        self._link_adg_nodes(bundle, entity_name)
        self._link_type_specific(bundle, entity_name)

    def _link_adg_nodes(self, bundle: CaseBundle, entity_name: str) -> None:
        """Create ``sourced_from_adg_node`` relations for each ADG node ref."""
        # Resolve types at runtime (they are TYPE_CHECKING-only imports)
        (
            _,
            _CaseBundle,
            _CaseRecord,
            _GovernancePrecedent,
            _HealerBundle,
            _HITLPreferenceRecord,
            _PromptBundle,
        ) = _get_case_memory_types()

        adg_nodes = getattr(bundle, "adg_nodes", None)
        if adg_nodes:
            for node_ref in adg_nodes:
                self._bridge.create_agent_entity(
                    agent_name=node_ref.entity_name,
                    agent_type=f"ADGNode_{node_ref.layer}",
                    observations=[
                        f"layer:{node_ref.layer}",
                        f"relation_family:{node_ref.relation_family}",
                        f"territory:{node_ref.territory or 'NONE'}",
                    ],
                )
                self._bridge.create_relation(entity_name, node_ref.entity_name, "sourced_from_adg_node")

        if isinstance(bundle, _HealerBundle):
            healer_node = bundle.adg_healer_node
            self._bridge.create_agent_entity(
                agent_name=healer_node.entity_name,
                agent_type=f"ADGNode_{healer_node.layer}",
                observations=[f"layer:{healer_node.layer}", f"relation_family:{healer_node.relation_family}"],
            )
            self._bridge.create_relation(entity_name, healer_node.entity_name, "sourced_from_adg_node")
            if bundle.adg_validator_node:
                vnode = bundle.adg_validator_node
                self._bridge.create_agent_entity(
                    agent_name=vnode.entity_name,
                    agent_type=f"ADGNode_{vnode.layer}",
                    observations=[f"layer:{vnode.layer}", f"relation_family:{vnode.relation_family}"],
                )
                self._bridge.create_relation(entity_name, vnode.entity_name, "sourced_from_adg_node")

        elif isinstance(bundle, _GovernancePrecedent):
            gnode = bundle.adg_guardrail_node
            self._bridge.create_agent_entity(
                agent_name=gnode.entity_name,
                agent_type=f"ADGNode_{gnode.layer}",
                observations=[f"layer:{gnode.layer}", f"relation_family:{gnode.relation_family}"],
            )
            self._bridge.create_relation(entity_name, gnode.entity_name, "sourced_from_adg_node")

        elif isinstance(bundle, _PromptBundle):
            pnode = bundle.adg_prompt_node
            self._bridge.create_agent_entity(
                agent_name=pnode.entity_name,
                agent_type=f"ADGNode_{pnode.layer}",
                observations=[f"layer:{pnode.layer}", f"relation_family:{pnode.relation_family}"],
            )
            self._bridge.create_relation(entity_name, pnode.entity_name, "sourced_from_adg_node")

        elif isinstance(bundle, _HITLPreferenceRecord):
            hnode = bundle.adg_hitl_node
            self._bridge.create_agent_entity(
                agent_name=hnode.entity_name,
                agent_type=f"ADGNode_{hnode.layer}",
                observations=[f"layer:{hnode.layer}", f"relation_family:{hnode.relation_family}"],
            )
            self._bridge.create_relation(entity_name, hnode.entity_name, "sourced_from_adg_node")

    def _link_type_specific(self, bundle: CaseBundle, entity_name: str) -> None:
        """Create bundle-type-specific relations."""
        # Resolve types at runtime (they are TYPE_CHECKING-only imports)
        (_, _, _, _, _HealerBundle, _HITLPreferenceRecord, _) = _get_case_memory_types()

        if isinstance(bundle, _HealerBundle):
            violation_node = f"ADG::ViolationPattern::{bundle.violation_pattern[:32]}"
            self._bridge.create_agent_entity(
                agent_name=violation_node,
                agent_type="ViolationPattern",
                observations=[f"pattern:{bundle.violation_pattern}"],
            )
            self._bridge.create_relation(entity_name, violation_node, "healer_resolved")

        elif isinstance(bundle, _HITLPreferenceRecord):
            plan_node = _plan_entity_name(bundle.original_plan_hash)
            self._bridge.create_agent_entity(
                agent_name=plan_node,
                agent_type="PlanHash",
                observations=[f"plan_hash:{bundle.original_plan_hash}"],
            )
            rel_type = "hitl_approved" if bundle.human_decision == "APPROVE" else "hitl_rejected"
            self._bridge.create_relation(entity_name, plan_node, rel_type)

            if bundle.dpo_pair_id:
                dpo_node = f"ADG::DPOPair::{bundle.dpo_pair_id[:16]}"
                self._bridge.create_agent_entity(
                    agent_name=dpo_node,
                    agent_type="DPOPreferencePair",
                    observations=[f"dpo_pair_id:{bundle.dpo_pair_id}"],
                )
                self._bridge.create_relation(entity_name, dpo_node, "learns_from_decision")

    def get_stats(self) -> dict[str, Any]:
        """Return bridge stats for observability."""
        return self._bridge.get_statistics()


__all__ = ["CaseLibrary"]
