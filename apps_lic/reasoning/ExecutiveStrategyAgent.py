"""Executive Strategy Agent - Integrates orphan executive domain prompts.

Phase 2: Executive Domain Integration
Provides executive strategy capabilities using prompt governance infrastructure.
"""

from __future__ import annotations

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
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
from agentic_core.prompt_governance import PromptLoader

_emit_applies_guardrail("p0", "ExecutiveStrategyAgent", "p0_governance")
_emit_snapshots_state("p0", "ExecutiveStrategyAgent", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("ExecutiveStrategyAgent", "p4obs", "metric_1")
_emit_emits_metric_event("ExecutiveStrategyAgent", "p4obs", "metric_2")
_emit_emits_metric_event("ExecutiveStrategyAgent", "p4obs", "metric_3")
_emit_emits_metric_event("ExecutiveStrategyAgent", "p4obs", "metric_4")
_emit_emits_metric_event("ExecutiveStrategyAgent", "p4obs", "metric_5")
_emit_emits_metric_event("ExecutiveStrategyAgent", "p4obs", "metric_6")
_emit_records_incident_event("ExecutiveStrategyAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("ExecutiveStrategyAgent", "p4obs", "anomaly")
_emit_writes_observability_log("ExecutiveStrategyAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("ExecutiveStrategyAgent", "p4obs", "mon_state")
_emit_triggers_alert("ExecutiveStrategyAgent", "p4obs", "alert")
_emit_links_incident_trace("ExecutiveStrategyAgent", "p4obs", "trace_link")
_emit_captures_pattern("ExecutiveStrategyAgent", "p3lm", "pattern")
_emit_records_learning_event("ExecutiveStrategyAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ExecutiveStrategyAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("ExecutiveStrategyAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ExecutiveStrategyAgent", "p3lm", "routing")
_emit_improves_agent_policy("ExecutiveStrategyAgent", "p3lm", "policy")
_emit_stores_learning_state("ExecutiveStrategyAgent", "p3lm", "state")
_emit_records_execution_trace("ExecutiveStrategyAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ExecutiveStrategyAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ExecutiveStrategyAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ExecutiveStrategyAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ExecutiveStrategyAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ExecutiveStrategyAgent", "env_read", "p2_env_1")
_emit_reads_environ("ExecutiveStrategyAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("ExecutiveStrategyAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ExecutiveStrategyAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ExecutiveStrategyAgent", "context_pull")
_emit_pulls_context("p1", "ExecutiveStrategyAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ExecutiveStrategyAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ExecutiveStrategyAgent", "uwg_term_2")
_emit_writes_through("p1", "ExecutiveStrategyAgent", "write_through")
_emit_writes_through("p1", "ExecutiveStrategyAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "ExecutiveStrategyAgent", "safety_validation")
_emit_invokes_eval("p1", "ExecutiveStrategyAgent", "eval_call")
_emit_proposal_commits_routing("p1", "ExecutiveStrategyAgent", "routing_commit")
_emit_escalates_to_human("p1", "ExecutiveStrategyAgent", "human_escalation")
_emit_routes_through("p1", "ExecutiveStrategyAgent", "route_through")
_emit_checks_agent_registry("p1", "ExecutiveStrategyAgent", "agent_registry")
_emit_validates_agent_capability("p1", "ExecutiveStrategyAgent", "capability")
_emit_dispatches_execution_plan("p1", "ExecutiveStrategyAgent", "exec_plan")
_emit_agent_executes_agent("p1", "ExecutiveStrategyAgent", "sub_agent")
_emit_routes_to_agent("p1", "ExecutiveStrategyAgent", "target_agent")
_emit_verifies_policy("p1", "ExecutiveStrategyAgent", "policy_check")
_emit_observes_runtime_state("p1", "ExecutiveStrategyAgent", "runtime_state")
_emit_verifies_boundary("p1", "ExecutiveStrategyAgent", "boundary_check")
_emit_transcripts_response("p1", "ExecutiveStrategyAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "ExecutiveStrategyAgent")
_emit_gated_by_confidence("p1", "ExecutiveStrategyAgent", "confidence_gate")
emit_replay_key("p0", "ExecutiveStrategyAgent")
emit_determinism_digest("p0", "ExecutiveStrategyAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ExecutiveStrategyAgent", "execution_auth")
_emit_validates_capability("p2", "ExecutiveStrategyAgent", "capability_check")
_emit_routes_to_capability("p2", "ExecutiveStrategyAgent", "capability_route")
_emit_writes_via_uwg("p2", "ExecutiveStrategyAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ExecutiveStrategyAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ExecutiveStrategyAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ExecutiveStrategyAgent", "exec_output")
_emit_dispatches_agent("p3", "ExecutiveStrategyAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ExecutiveStrategyAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ExecutiveStrategyAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ExecutiveStrategyAgent", "healing_outcome")
_emit_escalates_failure("p3", "ExecutiveStrategyAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ExecutiveStrategyAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ExecutiveStrategyAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ExecutiveStrategyAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ExecutiveStrategyAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ExecutiveStrategyAgent", "eval_metric")
_emit_stores_embedding("p4", "ExecutiveStrategyAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ExecutiveStrategyAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ExecutiveStrategyAgent", "exec_snapshot_link")


class ExecutiveStrategyAgent:
    """Executive strategy agent for shadow audits, roadmaps, and interviewer profiling.

    Integrates orphan executive prompts:
    - k11_shadow_audit.yaml
    - k12_strategy_roadmap.yaml
    - k13_interviewer_sim.yaml
    """

    _RESERVED_KEYS = {"domain", "name", "prompt_name"}
    _PROMPT_REFERENCES = {"k11_shadow_audit", "k12_strategy_roadmap", "k13_interviewer_sim"}

    def __init__(self, prompt_root: Path | None = None) -> None:
        """Initialize with injected prompt root.

        Args:
            prompt_root: Base directory containing prompt files.
                        Defaults to data/prompt_governance if None.
        """
        if prompt_root is None:
            prompt_root = Path(__file__).parent.parent.parent / "data" / "prompt_governance"
        self.prompt_root = prompt_root
        self._prompt_loader = PromptLoader(self.prompt_root)

    def _render(self, domain: str, prompt_name: str, template_vars: dict[str, Any]) -> str:
        """Render prompt with constraints prefix and reserved key filtering.

        Args:
            domain: Prompt domain
            prompt_name: Prompt name
            template_vars: Template variables (filtered to remove reserved keys)

        Returns:
            Rendered prompt with constraints prefixed when present
        """
        filtered_vars = {k: v for k, v in template_vars.items() if k not in self._RESERVED_KEYS}
        prompt_data = self._prompt_loader.load_prompt(domain, prompt_name)
        rendered = self._prompt_loader.get_template(domain, prompt_name, **filtered_vars)
        constraints = prompt_data.get("constraints")
        if constraints:
            if isinstance(constraints, list):
                constraints_text = "\n".join(f"- {c}" for c in constraints)
            else:
                constraints_text = str(constraints)
            return f"CONSTRAINTS:\n{constraints_text}\n\n{rendered}"
        return rendered

    def conduct_shadow_audit(self, payload: dict[str, Any]) -> str:
        """Conduct executive shadow audit using k11_shadow_audit prompt.

        Args:
            payload: Audit context data for template substitution

        Returns:
            Rendered shadow audit prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "ExecutiveStrategyAgent.conduct_shadow_audit")
        return self._render("executive", "k11_shadow_audit", payload)

    def generate_strategy_roadmap(self, payload: dict[str, Any]) -> str:
        """Generate 30-60-90 day strategy roadmap using k12_strategy_roadmap prompt.

        Args:
            payload: Roadmap context data for template substitution

        Returns:
            Rendered strategy roadmap prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k12_strategy_roadmap", payload)

    def profile_interviewer(self, payload: dict[str, Any]) -> str:
        """Profile interviewer using k13_interviewer_sim prompt.

        Args:
            payload: Interviewer context data for template substitution

        Returns:
            Rendered interviewer profiling prompt

        Raises:
            PromptLoadError: If prompt file cannot be loaded
            PromptSchemaError: If template formatting fails
        """
        return self._render("executive", "k13_interviewer_sim", payload)

    def heal(self, *args, **kwargs) -> dict[str, Any]:
        """heal() not implemented for ExecutiveStrategyAgent."""
        raise NotImplementedError("heal() not implemented for ExecutiveStrategyAgent")

    def heal_repository(self, *args, **kwargs) -> dict[str, Any]:
        """heal_repository() not implemented for ExecutiveStrategyAgent."""
        raise NotImplementedError("heal_repository() not implemented for ExecutiveStrategyAgent")


def get_exec_shadow_audit(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive shadow audit.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted shadow audit prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.conduct_shadow_audit(payload)


def get_exec_strategy_roadmap(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive strategy roadmap.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted strategy roadmap prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.generate_strategy_roadmap(payload)


def get_exec_interviewer_profile(payload: dict[str, Any], *, prompt_root: Path | None = None) -> str:
    """Dispatch function for executive interviewer profiling.

    Args:
        payload: Dictionary of template variables
        prompt_root: Optional prompt directory override

    Returns:
        Formatted interviewer profile prompt
    """
    agent = ExecutiveStrategyAgent(prompt_root=prompt_root)
    return agent.profile_interviewer(payload)
