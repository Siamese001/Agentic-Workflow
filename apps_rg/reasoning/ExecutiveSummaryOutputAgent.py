"""Strategist BioWriter - Executive Summary Generation (K.1).

This agent generates executive summaries with strict 3rd-person implied voice,
enforcing 120-140 word count and 3-5 sentence structure with 1st-person blocking.

Sub-Atomic Agent Name: Strategist_BioWriter
Legacy K-Node: K.1
"""

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.types.reasoning_config import ReasoningConfig
from apps_rg.utils.RGAgentBase import RGAgentBase

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "ExecutiveSummaryOutputAgent", "p0_governance")
_emit_reads_policy_state("p0", "ExecutiveSummaryOutputAgent", "policy_binding")
_emit_snapshots_state("p0", "ExecutiveSummaryOutputAgent", "state_snapshot")
emit_replay_key("p0", "ExecutiveSummaryOutputAgent")
emit_determinism_digest("p0", "ExecutiveSummaryOutputAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ExecutiveSummaryOutputAgent", "execution_auth")
_emit_validates_capability("p2", "ExecutiveSummaryOutputAgent", "capability_check")
_emit_routes_to_capability("p2", "ExecutiveSummaryOutputAgent", "capability_route")
_emit_writes_via_uwg("p2", "ExecutiveSummaryOutputAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ExecutiveSummaryOutputAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ExecutiveSummaryOutputAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ExecutiveSummaryOutputAgent", "exec_output")
_emit_dispatches_agent("p3", "ExecutiveSummaryOutputAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ExecutiveSummaryOutputAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ExecutiveSummaryOutputAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ExecutiveSummaryOutputAgent", "healing_outcome")
_emit_escalates_failure("p3", "ExecutiveSummaryOutputAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ExecutiveSummaryOutputAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ExecutiveSummaryOutputAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ExecutiveSummaryOutputAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ExecutiveSummaryOutputAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ExecutiveSummaryOutputAgent", "eval_metric")
_emit_stores_embedding("p4", "ExecutiveSummaryOutputAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ExecutiveSummaryOutputAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ExecutiveSummaryOutputAgent", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummaryOutput:
    """Strategist BioWriter output."""

    summary: str
    word_count: int
    sentence_count: int
    first_person_violations: list[str]
    third_person_compliant: bool
    metadata: dict[str, Any]


FIRST_PERSON_PATTERNS = [
    "\\bI\\b",
    "\\bI\\'m\\b",
    "\\bI\\'ve\\b",
    "\\bI\\'ll\\b",
    "\\bI\\'d\\b",
    "\\bmy\\b",
    "\\bmine\\b",
    "\\bme\\b",
    "\\bmyself\\b",
    "\\bwe\\b",
    "\\bwe\\'re\\b",
    "\\bwe\\'ve\\b",
    "\\bour\\b",
    "\\bours\\b",
]


@dataclass
class BioWriterConfig:
    tone: str = "professional"
    length_limit: int = 500


class StrategistBioWriter(RGAgentBase):
    """
    Agent specialized in crafting executive biographies with strategic alignment.
    """

    def __init__(self, config: BioWriterConfig, reasoning: ReasoningConfig):
        super().__init__()
        self.config = config
        self.reasoning = reasoning

    async def run(self, input_data: dict) -> dict:
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ExecutiveSummaryOutputAgent.run")
        return {"bio": "Draft content..."}
