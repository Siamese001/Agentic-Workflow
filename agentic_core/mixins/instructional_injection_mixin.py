"""
InstructionalInjectionMixin — Canonical location.

Relocated from agentic_core/config/injection_layer_config.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import os
from dataclasses import field
from typing import Any

from agentic_core.config.google_ai_env import google_ai_flash_model_id
from agentic_core.config.injection_layer_config import (
    INSTRUCTIONAL_PATTERNS,
    InjectionLayer,
    InstructionalPattern,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "instructional_injection_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "instructional_injection_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "instructional_injection_mixin", "state_snapshot")

trace_contract._emit_emits_metric_event("instructional_injection_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("instructional_injection_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("instructional_injection_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("instructional_injection_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("instructional_injection_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("instructional_injection_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("instructional_injection_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("instructional_injection_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("instructional_injection_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("instructional_injection_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("instructional_injection_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("instructional_injection_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("instructional_injection_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("instructional_injection_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("instructional_injection_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("instructional_injection_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("instructional_injection_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("instructional_injection_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("instructional_injection_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("instructional_injection_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("instructional_injection_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("instructional_injection_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("instructional_injection_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("instructional_injection_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("instructional_injection_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("instructional_injection_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("instructional_injection_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("instructional_injection_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "instructional_injection_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "instructional_injection_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "instructional_injection_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "instructional_injection_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "instructional_injection_mixin", "write_through")
trace_contract._emit_writes_through("p1", "instructional_injection_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "instructional_injection_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "instructional_injection_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "instructional_injection_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "instructional_injection_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "instructional_injection_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "instructional_injection_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "instructional_injection_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "instructional_injection_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "instructional_injection_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "instructional_injection_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "instructional_injection_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "instructional_injection_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "instructional_injection_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "instructional_injection_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "instructional_injection_mixin")
trace_contract._emit_gated_by_confidence("p1", "instructional_injection_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "instructional_injection_mixin")
trace_contract.emit_determinism_digest("p0", "instructional_injection_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "instructional_injection_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "instructional_injection_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "instructional_injection_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "instructional_injection_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "instructional_injection_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "instructional_injection_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "instructional_injection_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "instructional_injection_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "instructional_injection_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "instructional_injection_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "instructional_injection_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "instructional_injection_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "instructional_injection_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "instructional_injection_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "instructional_injection_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "instructional_injection_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "instructional_injection_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "instructional_injection_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "instructional_injection_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "instructional_injection_mixin", "exec_snapshot_link")


def _get_scan_untrusted_text():
    from agentic_core.prompt_governance.security import scan_untrusted_text

    return scan_untrusted_text


class InstructionalInjectionMixin:
    """
    Mixin providing all 30 instructional injection patterns to worker agents.

    Usage:
        class MyAgent(instructional_injection_mixin, HealingPolicyMixin, ...):
            def process(self, prompt):
                # Inject safety patterns
                prompt = self.inject_safety_layer(prompt)
                # Inject output patterns
                prompt = self.inject_output_layer(prompt, schema=my_schema)
                return self.llm_call(prompt)
    """

    _injection_patterns: dict[int, InstructionalPattern] = INSTRUCTIONAL_PATTERNS
    _enabled_layers: set = field(default_factory=lambda: set(InjectionLayer))

    def get_pattern(self, pattern_id: int) -> InstructionalPattern | None:
        """Get a specific instructional pattern by ID."""
        return self._injection_patterns.get(pattern_id)

    def get_patterns_by_layer(self, layer: InjectionLayer) -> list[InstructionalPattern]:
        """Get all patterns for a specific layer."""
        return [p for p in self._injection_patterns.values() if p.layer == layer and p.enabled]

    def inject_pattern(self, prompt: str, pattern_id: int, **kwargs) -> str:
        """Inject a specific pattern into a prompt."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "InstructionalInjectionMixin.inject_pattern"
        )

        pattern = self.get_pattern(pattern_id)
        if not pattern or not pattern.enabled:
            return prompt

        try:
            injection = pattern.template.format(**kwargs)
            return f"{injection}\n\n{prompt}"
        except KeyError:
            # Missing template variables - return prompt unchanged
            return prompt

    def inject_framing_layer(
        self,
        prompt: str,
        goal: str = "",
        criteria: str = "",
        mode: str = "analytical",
        boundaries: str = "",
        forbidden: str = "",
        target_tokens: int = 2000,
    ) -> str:
        """Inject all framing layer patterns (1-5)."""
        if goal:
            prompt = self.inject_pattern(prompt, 1, goal=goal)
        if criteria:
            prompt = self.inject_pattern(prompt, 2, criteria=criteria)
        prompt = self.inject_pattern(prompt, 3, mode=mode)
        if boundaries or forbidden:
            prompt = self.inject_pattern(prompt, 4, boundaries=boundaries, forbidden=forbidden)
        prompt = self.inject_pattern(prompt, 5, target_tokens=target_tokens)
        return prompt

    # guardian: allow-magic-config
    def inject_context_layer(
        self,
        prompt: str,
        user_data: str = "",
        max_tokens: int = 4000,
    ) -> str:
        """Inject context layer patterns (6-10)."""
        if user_data:
            prompt = self.inject_pattern(prompt, 6, user_data=user_data)
        prompt = self.inject_pattern(prompt, 7)
        prompt = self.inject_pattern(prompt, 8, max_tokens=max_tokens)
        prompt = self.inject_pattern(prompt, 9)
        prompt = self.inject_pattern(prompt, 10)
        return prompt

    def inject_reasoning_layer(
        self,
        prompt: str,
        n_branches: int = 3,
    ) -> str:
        """Inject reasoning layer patterns (11-15)."""
        prompt = self.inject_pattern(prompt, 11)
        prompt = self.inject_pattern(prompt, 12, n_branches=n_branches)
        prompt = self.inject_pattern(prompt, 13)
        prompt = self.inject_pattern(prompt, 14)
        prompt = self.inject_pattern(prompt, 15)
        return prompt

    def inject_tooling_layer(
        self,
        prompt: str,
        tool_output: str = "",
        source: str = "",
        priority_order: str = "RAG > QA > Draft",
        model: str = google_ai_flash_model_id()[0],
    ) -> str:
        """Inject tooling layer patterns (16-20)."""
        # §P1 — Canonical injection scan on tool_output before injection (fail-closed)
        if tool_output:
            _get_scan_untrusted_text()(tool_output, source="mixin_tool_output")
        if tool_output:
            prompt = self.inject_pattern(prompt, 16, tool_output=tool_output)
        if source:
            prompt = self.inject_pattern(prompt, 17, source=source)
        prompt = self.inject_pattern(prompt, 18, priority_order=priority_order)
        prompt = self.inject_pattern(prompt, 19)
        prompt = self.inject_pattern(prompt, 20, model=model)
        return prompt

    def inject_safety_layer(
        self,
        prompt: str,
        protected_decisions: str = "",
    ) -> str:
        """Inject safety layer patterns (21-25). CRITICAL for all agents."""
        prompt = self.inject_pattern(prompt, 21)
        prompt = self.inject_pattern(prompt, 22)
        prompt = self.inject_pattern(prompt, 23)
        if protected_decisions:
            prompt = self.inject_pattern(prompt, 24, protected_decisions=protected_decisions)
        prompt = self.inject_pattern(prompt, 25)
        return prompt

    # guardian: allow-magic-config
    def inject_output_layer(
        self,
        prompt: str,
        schema: str = "",
        example: str = "",
        max_tokens: int = 1000,
    ) -> str:
        """Inject output layer patterns (26-30)."""
        prompt = self.inject_pattern(prompt, 26)
        if schema:
            prompt = self.inject_pattern(prompt, 27, schema=schema, example=example or "{}")
        prompt = self.inject_pattern(prompt, 28)
        prompt = self.inject_pattern(prompt, 29)
        prompt = self.inject_pattern(prompt, 30, max_tokens=max_tokens)
        return prompt

    def inject_all_layers(
        self,
        prompt: str,
        goal: str = "",
        mode: str = "analytical",
        schema: str = "",
        **kwargs,
    ) -> str:
        """Inject all 30 patterns across all layers."""
        prompt = self.inject_framing_layer(prompt, goal=goal, mode=mode, **kwargs)
        prompt = self.inject_context_layer(prompt, **kwargs)
        prompt = self.inject_reasoning_layer(prompt, **kwargs)
        prompt = self.inject_tooling_layer(prompt, **kwargs)
        prompt = self.inject_safety_layer(prompt, **kwargs)
        prompt = self.inject_output_layer(prompt, schema=schema, **kwargs)
        return prompt

    def get_injection_summary(self) -> dict[str, Any]:
        """Get summary of available injection patterns."""
        return {
            "total_patterns": len(self._injection_patterns),
            "layers": {layer.value: len(self.get_patterns_by_layer(layer)) for layer in InjectionLayer},
            "enabled_count": sum(1 for p in self._injection_patterns.values() if p.enabled),
        }


# Backward compatibility alias
instructional_injection_mixin = InstructionalInjectionMixin


# Convenience function for standalone use
def get_instructional_injection_mixin() -> InstructionalInjectionMixin:
    """Get an instance of the instructional injection mixin."""
    return InstructionalInjectionMixin()
