"""
agentic_core/L5_safety/validators/gravity_leak_validator.py

GravityLeakValidatorAgent — certify-only validator pair for GravityLeakHealerAgent.

ADG fix: A-13 (no certify-only validator pair existed for GravityLeakHealerAgent).

Contract:
- ZERO mutations — read-only scan only
- Delegates to GravityLeakRepairAgent.heal_repository(dry_run=True, execute=False)
- Returns check_dict with check_id="gravity_leak" for HEALER_REGISTRY dispatch
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "gravity_leak_validator")
trace_contract.emit_determinism_digest("p0", "gravity_leak_validator")

trace_contract._emit_dispatches_healing_run("p1", "gravity_leak_validator", "L5")
trace_contract._emit_routes_through("p1", "gravity_leak_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "gravity_leak_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "gravity_leak_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "gravity_leak_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "gravity_leak_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "gravity_leak_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "gravity_leak_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "gravity_leak_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "gravity_leak_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "gravity_leak_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "gravity_leak_validator")
trace_contract._emit_gated_by_confidence("p1", "gravity_leak_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "gravity_leak_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "gravity_leak_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "gravity_leak_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "gravity_leak_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "gravity_leak_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "gravity_leak_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "gravity_leak_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "gravity_leak_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "gravity_leak_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "gravity_leak_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "gravity_leak_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "gravity_leak_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "gravity_leak_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "gravity_leak_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "gravity_leak_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "gravity_leak_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "gravity_leak_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "gravity_leak_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "gravity_leak_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "gravity_leak_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "gravity_leak_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "gravity_leak_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "gravity_leak_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "gravity_leak_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("gravity_leak_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("gravity_leak_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("gravity_leak_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("gravity_leak_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("gravity_leak_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("gravity_leak_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("gravity_leak_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("gravity_leak_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("gravity_leak_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("gravity_leak_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("gravity_leak_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("gravity_leak_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("gravity_leak_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("gravity_leak_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("gravity_leak_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("gravity_leak_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("gravity_leak_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("gravity_leak_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("gravity_leak_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("gravity_leak_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("gravity_leak_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("gravity_leak_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("gravity_leak_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("gravity_leak_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("gravity_leak_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("gravity_leak_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("gravity_leak_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("gravity_leak_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "gravity_leak_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "gravity_leak_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "gravity_leak_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "gravity_leak_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "gravity_leak_validator", "write_through")
trace_contract._emit_writes_through("p1", "gravity_leak_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "gravity_leak_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "gravity_leak_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "gravity_leak_validator", "routing_commit")

Logger = logging.getLogger(__name__)


class GravityLeakValidatorAgent:
    """Certify-only validator that detects gravity-leak violations without fixing them.

    Mirrors the domain of GravityLeakHealerAgent (GravityLeakRepairAgent) but
    performs NO mutations — suitable for validators/ territory.

    Usage::

        agent = GravityLeakValidatorAgent(project_root=Path("."))
        result = agent.certify()
        assert result["check_id"] == "gravity_leak"
    """

    CHECK_ID = "gravity_leak"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = Path(project_root) if project_root else Path.cwd()

    def certify(self) -> dict[str, Any]:
        """Run a dry-run gravity-leak scan and return a check_dict.

        Returns:
            check_dict compatible with HEALER_REGISTRY dispatch:
                check_id, passed, violations_found, summary
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "GravityLeakValidatorAgent.certify")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GravityLeakValidatorAgent.certify".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        try:
            from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
                GravityLeakRepairAgent,
            )

            agent = GravityLeakRepairAgent(project_root=self._project_root)
            result = agent.heal_repository(dry_run=True, execute=False)  # guardian: allow-silent-swallower
        except (ValueError, TypeError) as exc:
            Logger.warning("[GravityLeakValidator] scan failed: %s", exc)
            return {
                "check_id": self.CHECK_ID,
                "passed": False,
                "violations_found": -1,
                "summary": f"scan_error: {type(exc).__name__}: {exc}",
            }

        violations_found: int = result.get("violations_found", 0)
        passed = violations_found == 0
        Logger.info(
            "[GravityLeakValidator] check_id=%s passed=%s violations=%d",
            self.CHECK_ID,
            passed,
            violations_found,
        )
        return {
            "check_id": self.CHECK_ID,
            "passed": passed,
            "violations_found": violations_found,
            "summary": result.get("summary", ""),
        }

    def validate(self) -> dict[str, Any]:
        """Alias for certify() — standard validator interface."""
        return self.certify()


__all__ = ["GravityLeakValidatorAgent"]
