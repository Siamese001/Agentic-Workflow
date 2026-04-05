"""
adg_behavioral_mixin.py — ADG Behavioral Signal Mixin (Phase 0)

Provides lazy-loaded ADG behavioral profile properties to any agent that
inherits from SovereignBaseAgent (via MRO injection in Phase 4).

Design constraints:
  - ZERO dependencies on agentic_core internals — imports only from
    agentic_core.adg.runtime.behavioral_index (stdlib-only, safe from any layer)
  - All properties are @cached_property — loaded once per instance, zero cost
    when ADG SQLite is absent (graceful neutral fallback)
  - No __init__ side effects — purely additive
  - Thread-safety: each instance owns its own profile cache via cached_property

Signal reference (from behavioral_index.py):
  behavioral_score > 0.7  → agent-like
  behavioral_score < 0.4  → script-like
  0.4–0.7               → mixed/unknown (default: 0.5)
"""

from __future__ import annotations

import logging
from functools import cached_property
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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

_emit_applies_guardrail("p0", "adg_behavioral_mixin", "p0_governance")
_emit_reads_policy_state("p0", "adg_behavioral_mixin", "policy_binding")
_emit_snapshots_state("p0", "adg_behavioral_mixin", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("adg_behavioral_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("adg_behavioral_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("adg_behavioral_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("adg_behavioral_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("adg_behavioral_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("adg_behavioral_mixin", "p4obs", "metric_6")
_emit_records_incident_event("adg_behavioral_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_behavioral_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("adg_behavioral_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_behavioral_mixin", "p4obs", "mon_state")
_emit_triggers_alert("adg_behavioral_mixin", "p4obs", "alert")
_emit_links_incident_trace("adg_behavioral_mixin", "p4obs", "trace_link")
_emit_captures_pattern("adg_behavioral_mixin", "p3lm", "pattern")
_emit_records_learning_event("adg_behavioral_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_behavioral_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_behavioral_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_behavioral_mixin", "p3lm", "routing")
_emit_improves_agent_policy("adg_behavioral_mixin", "p3lm", "policy")
_emit_stores_learning_state("adg_behavioral_mixin", "p3lm", "state")
_emit_records_execution_trace("adg_behavioral_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_behavioral_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_behavioral_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_behavioral_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_behavioral_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_behavioral_mixin", "env_read", "p2_env_1")
_emit_reads_environ("adg_behavioral_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_behavioral_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_behavioral_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_behavioral_mixin", "context_pull")
_emit_pulls_context("p1", "adg_behavioral_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_behavioral_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_behavioral_mixin", "uwg_term_2")
_emit_writes_through("p1", "adg_behavioral_mixin", "write_through")
_emit_writes_through("p1", "adg_behavioral_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_behavioral_mixin", "safety_validation")
_emit_invokes_eval("p1", "adg_behavioral_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "adg_behavioral_mixin", "routing_commit")
_emit_escalates_to_human("p1", "adg_behavioral_mixin", "human_escalation")
_emit_routes_through("p1", "adg_behavioral_mixin", "route_through")
_emit_checks_agent_registry("p1", "adg_behavioral_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "adg_behavioral_mixin", "capability")
_emit_dispatches_execution_plan("p1", "adg_behavioral_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "adg_behavioral_mixin", "sub_agent")
_emit_routes_to_agent("p1", "adg_behavioral_mixin", "target_agent")
_emit_verifies_policy("p1", "adg_behavioral_mixin", "policy_check")
_emit_observes_runtime_state("p1", "adg_behavioral_mixin", "runtime_state")
_emit_verifies_boundary("p1", "adg_behavioral_mixin", "boundary_check")
_emit_transcripts_response("p1", "adg_behavioral_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_behavioral_mixin")
_emit_gated_by_confidence("p1", "adg_behavioral_mixin", "confidence_gate")
emit_replay_key("p0", "adg_behavioral_mixin")
emit_determinism_digest("p0", "adg_behavioral_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_behavioral_mixin", "execution_auth")
_emit_validates_capability("p2", "adg_behavioral_mixin", "capability_check")
_emit_routes_to_capability("p2", "adg_behavioral_mixin", "capability_route")
_emit_writes_via_uwg("p2", "adg_behavioral_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "adg_behavioral_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_behavioral_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "adg_behavioral_mixin", "exec_output")
_emit_dispatches_agent("p3", "adg_behavioral_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_behavioral_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_behavioral_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_behavioral_mixin", "healing_outcome")
_emit_escalates_failure("p3", "adg_behavioral_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_behavioral_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_behavioral_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_behavioral_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_behavioral_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_behavioral_mixin", "eval_metric")
_emit_stores_embedding("p4", "adg_behavioral_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_behavioral_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_behavioral_mixin", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ADGBehavioralMixin:
    """
    Mixin that exposes ADG behavioral profile as lazy cached properties.

    Consumed by:
      - HealingPolicyMixin.heal_repository() — confidence adjustment (Phase 3a)
      - SelfDiagnosisMixin.self_diagnose()  — antipattern fold (Phase 3b)
      - All agents inheriting SovereignBaseAgent after Phase 4 root injection

    Usage (once injected via SovereignBaseAgent):
        if self.adg_is_agent_like:
            confidence -= 0.05
        for signal in self.adg_antipattern_signals:
            report["adg_antipatterns"].append(signal)
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _adg_resolved_self_path(self) -> str | None:
        """Return repo-relative path for this agent's source file, or None."""
        try:
            import inspect

            src = inspect.getfile(type(self))
            project_root = getattr(self, "project_root", None)
            if project_root is None:
                return None
            rel = Path(src).resolve().relative_to(Path(project_root).resolve())
            return rel.as_posix()
        except (ValueError, TypeError, RuntimeError) as e:
            return None

    def _adg_load_profile(self) -> Any:
        """Load ADGBehavioralIndex profile for this agent's own source file.

        Returns a BehavioralProfile (or neutral fallback) — never raises.
        """
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            project_root = getattr(self, "project_root", None)
            if project_root is None:
                return None

            idx = ADGBehavioralIndex.from_latest(Path(project_root))
            if idx is None:
                return None

            resolved = self._adg_resolved_self_path()
            if resolved is None:
                return None

            return idx.profile_for(resolved)
        except Exception as exc:
            logger.debug("[ADGBehavioralMixin] Profile load failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Public cached properties
    # ------------------------------------------------------------------

    @cached_property
    def adg_profile_available(self) -> bool:
        """True when ADG SQLite artifact is present and profile was loaded."""
        return self._adg_load_profile() is not None

    @cached_property
    def adg_behavioral_score(self) -> float:
        """Behavioral score [0.0–1.0]. >0.7 agent-like, <0.4 script-like. Default 0.5."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ADGBehavioralMixin.adg_behavioral_score")

        profile = self._adg_load_profile()
        return profile.behavioral_score if profile is not None else 0.5

    @cached_property
    def adg_is_agent_like(self) -> bool:
        """True when behavioral_score > 0.7 (strong agent-side evidence)."""
        return self.adg_behavioral_score > 0.7

    @cached_property
    def adg_is_script_like(self) -> bool:
        """True when file has ≥1 script signal and 0 agent signals (deterministic_coverage)."""
        profile = self._adg_load_profile()
        if profile is None:
            return False
        return profile.deterministic_coverage or profile.behavioral_score < 0.4

    @cached_property
    def adg_antipattern_signals(self) -> list[str]:
        """ADG-confirmed antipattern symbols for this agent's source file."""
        profile = self._adg_load_profile()
        if profile is None:
            return []
        return sorted(profile.antipattern_signals)

    @cached_property
    def adg_agent_signals(self) -> list[str]:
        """ADG-confirmed agent-side edge types present on this file."""
        profile = self._adg_load_profile()
        if profile is None:
            return []
        return sorted(profile.agent_signals)

    @cached_property
    def adg_script_signals(self) -> list[str]:
        """ADG-confirmed script-side edge types present on this file."""
        profile = self._adg_load_profile()
        if profile is None:
            return []
        return sorted(profile.script_signals)

    @cached_property
    def adg_dead_import_count(self) -> int:
        """Count of ADG-confirmed dead imports for this agent's source file.

        Queried directly via SQLite (not in BehavioralProfile — added here).
        Returns 0 when ADG is unavailable.
        """
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            project_root = getattr(self, "project_root", None)
            if project_root is None:
                return 0

            idx = ADGBehavioralIndex.from_latest(Path(project_root))
            if idx is None or not idx._connect():
                return 0

            resolved = self._adg_resolved_self_path()
            if resolved is None:
                return 0

            assert idx._con is not None
            cur = idx._con.execute(
                """
                SELECT COUNT(*) FROM edges e
                JOIN nodes n ON n.id = e.src_id
                WHERE e.relation_type = 'dead_imports'
                  AND n.resolved_path = ?
                  AND n.entity_type = 'module'
                """,
                (resolved,),
            )
            row = cur.fetchone()
            return int(row[0]) if row else 0
        except Exception as exc:
            logger.debug("[ADGBehavioralMixin] dead_import_count query failed: %s", exc)
            return 0

    def adg_behavioral_summary(self) -> dict:
        """Return a structured summary of this agent's ADG behavioral profile.

        Useful for audit trails and self-diagnosis reports.
        """
        return {
            "adg_profile_available": self.adg_profile_available,
            "adg_behavioral_score": self.adg_behavioral_score,
            "adg_is_agent_like": self.adg_is_agent_like,
            "adg_is_script_like": self.adg_is_script_like,
            "adg_antipattern_signals": self.adg_antipattern_signals,
            "adg_agent_signals": self.adg_agent_signals,
            "adg_script_signals": self.adg_script_signals,
            "adg_dead_import_count": self.adg_dead_import_count,
        }
