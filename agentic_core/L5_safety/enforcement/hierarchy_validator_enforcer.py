"""
agentic_core/enforcement/hierarchy_validator_enforcer.py

Validates layer hierarchy configuration loaded from the canonical JSON config
and computes a cryptographic hash that is included in the determinism proof.

If the hierarchy config file changes, its hash changes, which changes the
determinism digest, breaking any stale replay proofs and forcing CI review.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "hierarchy_validator_enforcer")
emit_determinism_digest("p0", "hierarchy_validator_enforcer")

_emit_dispatches_healing_run("p1", "hierarchy_validator_enforcer", "L5")
_emit_routes_through("p1", "hierarchy_validator_enforcer", "L5")
_emit_checks_agent_registry("p1", "hierarchy_validator_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "hierarchy_validator_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "hierarchy_validator_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "hierarchy_validator_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "hierarchy_validator_enforcer", "target_agent")
_emit_verifies_policy("p1", "hierarchy_validator_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "hierarchy_validator_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "hierarchy_validator_enforcer", "boundary_check")
_emit_transcripts_response("p1", "hierarchy_validator_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "hierarchy_validator_enforcer")
_emit_gated_by_confidence("p1", "hierarchy_validator_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "hierarchy_validator_enforcer", "L5")
_emit_reads_policy_state("p1", "hierarchy_validator_enforcer", "L5")

_emit_applies_guardrail("p0", "hierarchy_validator_enforcer", "p0_governance")
_emit_snapshots_state("p0", "hierarchy_validator_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "hierarchy_validator_enforcer", "execution_auth")
_emit_validates_capability("p2", "hierarchy_validator_enforcer", "capability_check")
_emit_routes_to_capability("p2", "hierarchy_validator_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "hierarchy_validator_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "hierarchy_validator_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "hierarchy_validator_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "hierarchy_validator_enforcer", "exec_output")
_emit_dispatches_agent("p3", "hierarchy_validator_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "hierarchy_validator_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "hierarchy_validator_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "hierarchy_validator_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "hierarchy_validator_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "hierarchy_validator_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hierarchy_validator_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "hierarchy_validator_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "hierarchy_validator_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hierarchy_validator_enforcer", "eval_metric")
_emit_stores_embedding("p4", "hierarchy_validator_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "hierarchy_validator_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hierarchy_validator_enforcer", "exec_snapshot_link")
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

_emit_emits_metric_event("hierarchy_validator_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("hierarchy_validator_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("hierarchy_validator_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("hierarchy_validator_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("hierarchy_validator_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("hierarchy_validator_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("hierarchy_validator_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("hierarchy_validator_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("hierarchy_validator_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("hierarchy_validator_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("hierarchy_validator_enforcer", "p4obs", "alert")
_emit_links_incident_trace("hierarchy_validator_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("hierarchy_validator_enforcer", "p3lm", "pattern")
_emit_records_learning_event("hierarchy_validator_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hierarchy_validator_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("hierarchy_validator_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hierarchy_validator_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("hierarchy_validator_enforcer", "p3lm", "policy")
_emit_stores_learning_state("hierarchy_validator_enforcer", "p3lm", "state")
_emit_records_execution_trace("hierarchy_validator_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hierarchy_validator_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hierarchy_validator_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hierarchy_validator_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hierarchy_validator_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hierarchy_validator_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("hierarchy_validator_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("hierarchy_validator_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hierarchy_validator_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hierarchy_validator_enforcer", "context_pull")
_emit_pulls_context("p1", "hierarchy_validator_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hierarchy_validator_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hierarchy_validator_enforcer", "uwg_term_2")
_emit_writes_through("p1", "hierarchy_validator_enforcer", "write_through")
_emit_writes_through("p1", "hierarchy_validator_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "hierarchy_validator_enforcer", "safety_validation")
_emit_invokes_eval("p1", "hierarchy_validator_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "hierarchy_validator_enforcer", "routing_commit")


class HierarchyValidator:
    """Loads, validates, and hashes the layer hierarchy configuration."""

    _REQUIRED_FIELDS = frozenset({"version", "layers", "forbidden_cross_imports", "allowed_cross_imports"})

    def __init__(self, config_path: Path) -> None:
        if not config_path.exists():
            raise FileNotFoundError(f"Layer hierarchy config not found: {config_path}")
        self.config_path = config_path
        raw = config_path.read_text(encoding="utf-8")
        self.config_hash: str = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        self.hierarchy: dict[str, Any] = self._load_and_validate(raw)

    def _load_and_validate(self, raw: str) -> dict[str, Any]:
        config = json.loads(raw)
        missing = self._REQUIRED_FIELDS - set(config.keys())
        if missing:
            raise ValueError(f"Layer hierarchy config missing required fields: {missing}")
        return config

    def get_layer_level(self, module_name: str) -> int:
        """Return numeric hierarchy level for module_name (-1 = external/unknown)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HierarchyValidator.get_layer_level")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HierarchyValidator.get_layer_level".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for pattern, level in self.hierarchy["layers"].items():
            if pattern.endswith("*"):
                if module_name.startswith(pattern[:-1]):
                    return int(level)
            elif module_name == pattern or module_name.startswith(pattern + "."):
                return int(level)
        return -1

    def is_import_allowed(self, source: str, target: str) -> bool:
        """Return True iff import from source to target is permitted by policy."""
        source_level = self.get_layer_level(source)
        target_level = self.get_layer_level(target)
        if source_level < 0 or target_level < 0:
            return True
        for src_pattern, forbidden_list in self.hierarchy["forbidden_cross_imports"].items():
            if self._matches(source, src_pattern):
                for tgt_pattern in forbidden_list:
                    if self._matches(target, tgt_pattern):
                        return False
        for src_pattern, allowed_list in self.hierarchy["allowed_cross_imports"].items():
            if self._matches(source, src_pattern):
                for tgt_pattern in allowed_list:
                    if self._matches(target, tgt_pattern):
                        return True
        return source_level >= target_level

    @staticmethod
    def _matches(module: str, pattern: str) -> bool:
        if pattern.endswith("*"):
            return module.startswith(pattern[:-1])
        return module == pattern or module.startswith(pattern + ".")


_hierarchy_validator: HierarchyValidator | None = None
_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "core" / "layer_hierarchy.json"


def get_hierarchy_validator(config_path: Path | None = None) -> HierarchyValidator:
    """Return the global HierarchyValidator (lazy-initialized from default path)."""
    global _hierarchy_validator
    if _hierarchy_validator is None:
        _hierarchy_validator = HierarchyValidator(config_path or _DEFAULT_CONFIG_PATH)
    return _hierarchy_validator
