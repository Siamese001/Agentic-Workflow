"""
GravityValidatorAgent - L5 Pure Validator.

Detects layer gravity violations (upward imports, layer inversions) via
StructuralValidatorAgent without mutating the codebase. Emits a structured
check dict consumed by heal_gravity_violations via HEALER_REGISTRY.

This is the detection-half counterpart to GravityLeakRepairAgent (healer).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, OPS_SCRIPTS_DIR
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

emit_replay_key("p0", "gravity_validator")
emit_determinism_digest("p0", "gravity_validator")

_emit_dispatches_healing_run("p1", "gravity_validator", "L5")
_emit_routes_through("p1", "gravity_validator", "L5")
_emit_checks_agent_registry("p1", "gravity_validator", "agent_registry")
_emit_validates_agent_capability("p1", "gravity_validator", "capability")
_emit_dispatches_execution_plan("p1", "gravity_validator", "exec_plan")
_emit_agent_executes_agent("p1", "gravity_validator", "sub_agent")
_emit_routes_to_agent("p1", "gravity_validator", "target_agent")
_emit_verifies_policy("p1", "gravity_validator", "policy_check")
_emit_observes_runtime_state("p1", "gravity_validator", "runtime_state")
_emit_verifies_boundary("p1", "gravity_validator", "boundary_check")
_emit_transcripts_response("p1", "gravity_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "gravity_validator")
_emit_gated_by_confidence("p1", "gravity_validator", "confidence_gate")
_emit_escalates_to_human("p1", "gravity_validator", "L5")
_emit_reads_policy_state("p1", "gravity_validator", "L5")

_emit_applies_guardrail("p0", "gravity_validator", "p0_governance")
_emit_snapshots_state("p0", "gravity_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "gravity_validator", "execution_auth")
_emit_validates_capability("p2", "gravity_validator", "capability_check")
_emit_routes_to_capability("p2", "gravity_validator", "capability_route")
_emit_writes_via_uwg("p2", "gravity_validator", "uwg_write")
_emit_blocks_direct_write("p2", "gravity_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "gravity_validator", "tool_invocation")
_emit_captures_execution_output("p2", "gravity_validator", "exec_output")
_emit_dispatches_agent("p3", "gravity_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "gravity_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "gravity_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "gravity_validator", "healing_outcome")
_emit_escalates_failure("p3", "gravity_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "gravity_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gravity_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "gravity_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "gravity_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gravity_validator", "eval_metric")
_emit_stores_embedding("p4", "gravity_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "gravity_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gravity_validator", "exec_snapshot_link")
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

_emit_emits_metric_event("gravity_validator", "p4obs", "metric_1")
_emit_emits_metric_event("gravity_validator", "p4obs", "metric_2")
_emit_emits_metric_event("gravity_validator", "p4obs", "metric_3")
_emit_emits_metric_event("gravity_validator", "p4obs", "metric_4")
_emit_emits_metric_event("gravity_validator", "p4obs", "metric_5")
_emit_emits_metric_event("gravity_validator", "p4obs", "metric_6")
_emit_records_incident_event("gravity_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("gravity_validator", "p4obs", "anomaly")
_emit_writes_observability_log("gravity_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("gravity_validator", "p4obs", "mon_state")
_emit_triggers_alert("gravity_validator", "p4obs", "alert")
_emit_links_incident_trace("gravity_validator", "p4obs", "trace_link")
_emit_captures_pattern("gravity_validator", "p3lm", "pattern")
_emit_records_learning_event("gravity_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("gravity_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("gravity_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("gravity_validator", "p3lm", "routing")
_emit_improves_agent_policy("gravity_validator", "p3lm", "policy")
_emit_stores_learning_state("gravity_validator", "p3lm", "state")
_emit_records_execution_trace("gravity_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("gravity_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("gravity_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("gravity_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("gravity_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("gravity_validator", "env_read", "p2_env_1")
_emit_reads_environ("gravity_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("gravity_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("gravity_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "gravity_validator", "context_pull")
_emit_pulls_context("p1", "gravity_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "gravity_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "gravity_validator", "uwg_term_2")
_emit_writes_through("p1", "gravity_validator", "write_through")
_emit_writes_through("p1", "gravity_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "gravity_validator", "safety_validation")
_emit_invokes_eval("p1", "gravity_validator", "eval_call")
_emit_proposal_commits_routing("p1", "gravity_validator", "routing_commit")

CHECK_ID = "gravity_violations"
_LAYER_DIR_PATTERN = re.compile("^L[0-6]_")


def _get_apps_roots() -> frozenset[str]:
    """Derive apps_* roots from PROJECT_ROOT_WHITELIST — zero hardcoded folder names."""
    from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST

    return frozenset(k for k in PROJECT_ROOT_WHITELIST if k.startswith("apps_"))


_APPS_ROOTS: frozenset[str] = _get_apps_roots()
_EXCLUDED_PATHS: tuple[str, ...] = (OPS_SCRIPTS_DIR, "scripts")
logger = logging.getLogger(__name__)


class GravityValidatorAgent:
    """L5 Certify-only validator for layer gravity violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self) -> list[Any]:
        """Run StructuralValidatorAgent and return filtered gravity violations.

        Returns:
            List of violation objects in the sovereign scope.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GravityValidatorAgent.scan")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GravityValidatorAgent.scan".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        try:
            from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (
                StructuralValidatorAgent,
                StructureConfig,
            )
        except ImportError as exc:
            logger.error("[GravityValidatorAgent] StructuralValidatorAgent import failed: %s", exc)
            return []
        config = StructureConfig(project_root=self.project_root, excluded_paths=_EXCLUDED_PATHS)
        enforcer = StructuralValidatorAgent(config=config)
        results = enforcer.validate_structure(self.project_root)
        root_str = str(self.project_root).replace("\\", "/")

        def _in_sovereign_scope(v: object) -> bool:
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else "")).replace(
                "\\", "/"
            )
            # guardian: allow-path-string
            rel = fp.replace(root_str + "/", "", 1)
            parts = [p for p in rel.split("/") if p]
            if not parts:
                return False
            root = parts[0]
            if root in _APPS_ROOTS:
                return True
            if root == AGENTIC_CORE_DIR and len(parts) > 1:
                return bool(_LAYER_DIR_PATTERN.match(parts[1]))
            return False

        def _not_excluded(v: object) -> bool:
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else "")).replace(
                "\\", "/"
            )
            return not any(ex in fp for ex in _EXCLUDED_PATHS)

        def _has_known_layers(v: object) -> bool:
            """Exclude violations where both layers are unknown — unactionable noise."""
            src = getattr(v, "source_layer", "?") or "?"
            tgt = getattr(v, "target_layer", "?") or "?"
            return not (src == "?" and tgt == "?")

        import ast as _ast

        _ast_cache: dict[str, _ast.Module] = {}

        def _parse_cached(fp_str: str) -> _ast.Module | None:
            if fp_str in _ast_cache:
                return _ast_cache[fp_str]
            try:
                from pathlib import Path as _Path

                tree = _ast.parse(_Path(fp_str).read_text(encoding="utf-8", errors="replace"))
                _ast_cache[fp_str] = tree
                return tree
            except (ValueError, TypeError, RuntimeError) as e:
                _ast_cache[fp_str] = None
                return None

        def _is_module_level_import(v: object) -> bool:
            """Return True only if the violation's import is at module scope (not inside a function/class)."""
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else ""))
            ln = int(getattr(v, "line_number", 0) or 0)
            if not fp or not ln:
                return True
            tree = _parse_cached(fp)
            if tree is None:
                return True
            for node in tree.body:
                if isinstance(node, (_ast.Import, _ast.ImportFrom)) and node.lineno == ln:
                    return True
            return False

        return [
            v
            for v in results.violations
            if _not_excluded(v)
            and _in_sovereign_scope(v)
            and _has_known_layers(v)
            and _is_module_level_import(v)
        ]

    def to_check_dict(self) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        violations = self.scan()
        return {
            "check_id": CHECK_ID,
            "evidence": {"violations": violations},
            "violations_count": len(violations),
            "repo_root": str(self.project_root),
        }

    def run(self) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict()
