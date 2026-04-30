"""
Bullet Generation Task - Stateless bullet writer
Refactored from create_experience_bullets.py
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
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

from apps_rg.engines.base_rg_engine import BaseRGEngine

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

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle

_emit_engine_lifecycle("bullet_generation_task")


Logger = logging.getLogger(__name__)


class BulletGenerationTask(BaseRGEngine):
    """
    Stateless bullet writer for experience sections.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="GENERATION.BULLETS")

    @traces_execute(layer="L3_ORCHESTRATION")
    async def execute(self, experience_context: dict[str, Any], target_count: int = 5) -> list[str]:
        """
        Generate achievement bullets for an experience section.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "BulletGenerationTask.execute"
        )

        self._mcp_audit("bullet_generation_start", {"target_count": target_count})
        prompt_template = self.get_frozen_prompt("bullet_generation") if self.knowledge else ""
        if not prompt_template:
            prompt_template = "Generate {count} achievement bullets for {role} at {company}"
        prompt = prompt_template.format(
            count=target_count,
            role=experience_context.get("role", "Professional"),
            company=experience_context.get("company", "Company"),
        )
        raw_output = await self.call_llm(prompt)
        bullets = self._parse_bullets(raw_output)
        if len(bullets) != target_count:
            self.record_fail(f"Generated {len(bullets)} bullets, expected {target_count}")
        else:
            self.record_pass(f"Generated {len(bullets)} bullets")
        return bullets

    def _parse_bullets(self, text: str) -> list[str]:
        """Parse LLM output into bullet list."""
        if not text:
            return []
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        bullets = [line.lstrip("•-*").strip() for line in lines if line]
        return bullets
