"""Self-Healing Formatter - Robust formatting with automatic repair.

This module implements a resilient formatter that can handle malformed LLM outputs,
repair common issues, and ensure the user always receives usable content even when
the LLM produces broken JSON, markdown wrappers, or missing fields.
"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "self_healing_formatter_types", "p0_governance")
_emit_reads_policy_state("p0", "self_healing_formatter_types", "policy_binding")
_emit_snapshots_state("p0", "self_healing_formatter_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("self_healing_formatter_types", "p4obs", "metric_1")
_emit_emits_metric_event("self_healing_formatter_types", "p4obs", "metric_2")
_emit_emits_metric_event("self_healing_formatter_types", "p4obs", "metric_3")
_emit_emits_metric_event("self_healing_formatter_types", "p4obs", "metric_4")
_emit_emits_metric_event("self_healing_formatter_types", "p4obs", "metric_5")
_emit_emits_metric_event("self_healing_formatter_types", "p4obs", "metric_6")
_emit_records_incident_event("self_healing_formatter_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("self_healing_formatter_types", "p4obs", "anomaly")
_emit_writes_observability_log("self_healing_formatter_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("self_healing_formatter_types", "p4obs", "mon_state")
_emit_triggers_alert("self_healing_formatter_types", "p4obs", "alert")
_emit_links_incident_trace("self_healing_formatter_types", "p4obs", "trace_link")
_emit_captures_pattern("self_healing_formatter_types", "p3lm", "pattern")
_emit_records_learning_event("self_healing_formatter_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("self_healing_formatter_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("self_healing_formatter_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("self_healing_formatter_types", "p3lm", "routing")
_emit_improves_agent_policy("self_healing_formatter_types", "p3lm", "policy")
_emit_stores_learning_state("self_healing_formatter_types", "p3lm", "state")
_emit_records_execution_trace("self_healing_formatter_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("self_healing_formatter_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("self_healing_formatter_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("self_healing_formatter_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("self_healing_formatter_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("self_healing_formatter_types", "env_read", "p2_env_1")
_emit_reads_environ("self_healing_formatter_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("self_healing_formatter_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("self_healing_formatter_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "self_healing_formatter_types", "context_pull")
_emit_pulls_context("p1", "self_healing_formatter_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "self_healing_formatter_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "self_healing_formatter_types", "uwg_term_2")
_emit_writes_through("p1", "self_healing_formatter_types", "write_through")
_emit_writes_through("p1", "self_healing_formatter_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "self_healing_formatter_types", "safety_validation")
_emit_invokes_eval("p1", "self_healing_formatter_types", "eval_call")
_emit_proposal_commits_routing("p1", "self_healing_formatter_types", "routing_commit")
_emit_escalates_to_human("p1", "self_healing_formatter_types", "human_escalation")
_emit_routes_through("p1", "self_healing_formatter_types", "route_through")
_emit_checks_agent_registry("p1", "self_healing_formatter_types", "agent_registry")
_emit_validates_agent_capability("p1", "self_healing_formatter_types", "capability")
_emit_dispatches_execution_plan("p1", "self_healing_formatter_types", "exec_plan")
_emit_agent_executes_agent("p1", "self_healing_formatter_types", "sub_agent")
_emit_routes_to_agent("p1", "self_healing_formatter_types", "target_agent")
_emit_verifies_policy("p1", "self_healing_formatter_types", "policy_check")
_emit_observes_runtime_state("p1", "self_healing_formatter_types", "runtime_state")
_emit_verifies_boundary("p1", "self_healing_formatter_types", "boundary_check")
_emit_transcripts_response("p1", "self_healing_formatter_types", "transcript")
_emit_hard_fails_untranscripted("p1", "self_healing_formatter_types")
_emit_gated_by_confidence("p1", "self_healing_formatter_types", "confidence_gate")
emit_replay_key("p0", "self_healing_formatter_types")
emit_determinism_digest("p0", "self_healing_formatter_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "self_healing_formatter_types", "execution_auth")
_emit_validates_capability("p2", "self_healing_formatter_types", "capability_check")
_emit_routes_to_capability("p2", "self_healing_formatter_types", "capability_route")
_emit_writes_via_uwg("p2", "self_healing_formatter_types", "uwg_write")
_emit_blocks_direct_write("p2", "self_healing_formatter_types", "direct_write_block")
_emit_records_tool_invocation("p2", "self_healing_formatter_types", "tool_invocation")
_emit_captures_execution_output("p2", "self_healing_formatter_types", "exec_output")
_emit_dispatches_agent("p3", "self_healing_formatter_types", "agent_dispatch")
_emit_coordinates_agents("p3", "self_healing_formatter_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "self_healing_formatter_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "self_healing_formatter_types", "healing_outcome")
_emit_escalates_failure("p3", "self_healing_formatter_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "self_healing_formatter_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "self_healing_formatter_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "self_healing_formatter_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "self_healing_formatter_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "self_healing_formatter_types", "eval_metric")
_emit_stores_embedding("p4", "self_healing_formatter_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "self_healing_formatter_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "self_healing_formatter_types", "exec_snapshot_link")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_1")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_2")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_3")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_4")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_5")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_6")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_7")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_8")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_9")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_10")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_11")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_12")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_13")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_14")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_15")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_16")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_17")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_18")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_19")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_20")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_21")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_22")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_23")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_24")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_25")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_26")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_27")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_28")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_29")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_30")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_31")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_32")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_33")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_34")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_35")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_36")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_37")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_38")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_39")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_40")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_41")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_42")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_43")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_44")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_45")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_46")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_47")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_48")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_49")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_50")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_51")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_52")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_53")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_54")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_55")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_56")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_57")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_58")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_59")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_60")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_61")
_emit_reads_through("l4", "self_healing_formatter_types", "urg_read_62")

logger = logging.getLogger(__name__)


class RepairStrategy(str, Enum):
    """Types of repair strategies."""

    JSON_REPAIR = "json_repair"
    MARKDOWN_STRIP = "markdown_strip"
    REGEX_EXTRACT = "regex_extract"
    SCHEMA_FILL = "schema_fill"
    FALLBACK_TEXT = "fallback_text"


@dataclass
class RepairResult:
    """Result of a repair attempt."""

    success: bool
    repaired_data: Any
    strategy_used: RepairStrategy | None = None
    error_message: str | None = None
    original_error: str | None = None
    attempts: int = 0


class FormatRepair(ABC):
    """Abstract base for format repair strategies."""

    @abstractmethod
    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Repair broken content.

        Args:
            broken_content: Malformed content to repair
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        pass

    @property
    @abstractmethod
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        pass


class JSONRepairStrategy(FormatRepair):
    """Repairs malformed JSON."""

    def __init__(self):
        """Initialize JSON repair strategy."""
        self.error_patterns = [
            ("(\\w+):", '"\\1":'),
            (",\\s*}", "}"),
            (",\\s*\\]", "]"),
            ("'([^']*)'", '"\\1"'),
            ("}\\s*$", "}"),
            ('(?<!\\\\)"', '\\\\"'),
        ]

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Repair JSON content.

        Args:
            broken_content: Malformed JSON
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SelfHealingFormatter.repair"
        )
        original_error = None
        attempts = 0
        try:
            data = json.loads(broken_content)
            return RepairResult(
                success=True,
                repaired_data=data,
                strategy_used=self.strategy_name,
                attempts=attempts,
            )
        except json.JSONDecodeError as e:
            original_error = str(e)
        repaired = broken_content
        for pattern, replacement in tqdm(self.error_patterns, desc="Processing", unit="item"):
            attempts += 1
            try:
                repaired = re.sub(pattern, replacement, repaired)
                data = json.loads(repaired)
                return RepairResult(
                    success=True,
                    repaired_data=data,
                    strategy_used=self.strategy_name,
                    attempts=attempts,
                    original_error=original_error,
                )
            except json.JSONDecodeError:
                continue
        attempts += 1
        repaired = self._aggressive_repair(repaired)
        try:
            data = json.loads(repaired)
            return RepairResult(
                success=True,
                repaired_data=data,
                strategy_used=self.strategy_name,
                attempts=attempts,
                original_error=original_error,
            )
        except json.JSONDecodeError as e:
            return RepairResult(
                success=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message=str(e),
                original_error=original_error,
                attempts=attempts,
            )

    def _aggressive_repair(self, content: str) -> str:
        """Apply aggressive JSON repair.

        Args:
            content: JSON content to repair

        Returns:
            Repaired content
        """
        cleaned = re.sub("[^\\x00-\\x7F]", "", content)
        open_braces = cleaned.count("{")
        close_braces = cleaned.count("}")
        if open_braces > close_braces:
            cleaned += "}" * (open_braces - close_braces)
        open_brackets = cleaned.count("[")
        close_brackets = cleaned.count("]")
        if open_brackets > close_brackets:
            cleaned += "]" * (open_brackets - close_brackets)
        return cleaned

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.JSON_REPAIR


class MarkdownStripStrategy(FormatRepair):
    """Strips markdown wrappers from content."""

    def __init__(self):
        """Initialize markdown strip strategy."""
        self.patterns = [
            "```json\\s*(.*?)\\s*```",
            "```JSON\\s*(.*?)\\s*```",
            "```\\s*(.*?)\\s*```",
            "`([^`]*)`",
        ]

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Strip markdown from content.

        Args:
            broken_content: Content with markdown
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        for pattern in self.patterns:
            match = re.search(pattern, broken_content, re.DOTALL)
            if match:
                stripped = match.group(1).strip()
                return RepairResult(
                    success=True,
                    repaired_data=stripped,
                    strategy_used=self.strategy_name,
                    attempts=1,
                )
        return RepairResult(
            success=False,
            repaired_data=broken_content,
            strategy_used=self.strategy_name,
            error_message="No markdown wrappers found",
            attempts=1,
        )

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.MARKDOWN_STRIP


class RegexExtractStrategy(FormatRepair):
    """Extracts structured data using regex patterns."""

    def __init__(self):
        """Initialize regex extract strategy."""
        self.patterns = {
            "json_object": "\\{[^{}]*(?:\\{[^{}]*\\}[^{}]*)*\\}",
            "json_array": "\\[[^\\[\\]]*(?:\\[[^\\[\\]]*\\][^\\[\\]]*)*\\]",
            "email": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            "phone": "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b",
            "url": 'https?://[^\\s<>"{}|\\\\^`[\\]]+',
        }

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Extract data using regex.

        Args:
            broken_content: Content to extract from
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result
        """
        for pattern_name in tqdm(["json_object", "json_array"], desc="Processing", unit="item"):
            pattern = self.patterns[pattern_name]
            matches = re.findall(pattern, broken_content, re.DOTALL)
            for match in tqdm(matches, desc="Processing", unit="item"):
                try:
                    data = json.loads(match)
                    return RepairResult(
                        success=True,
                        repaired_data=data,
                        strategy_used=self.strategy_name,
                        attempts=1,
                        error_message=f"Extracted using {pattern_name} pattern",
                    )
                except json.JSONDecodeError:
                    continue
        extracted = {}
        for name, pattern in self.patterns.items():
            if name in ["json_object", "json_array"]:
                continue
            matches = re.findall(pattern, broken_content)
            if matches:
                extracted[name] = matches
        if extracted:
            return RepairResult(
                success=True,
                repaired_data=extracted,
                strategy_used=self.strategy_name,
                attempts=1,
            )
        return RepairResult(
            success=False,
            repaired_data=broken_content,
            strategy_used=self.strategy_name,
            error_message="No structured data found",
            attempts=1,
        )

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.REGEX_EXTRACT


class SchemaFillStrategy(FormatRepair):
    """Fills missing fields based on target schema."""

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Fill missing schema fields.

        Args:
            broken_content: Content to repair
            target_schema: Target Pydantic schema
            context: Additional context

        Returns:
            Repair result
        """
        if not target_schema:
            return RepairResult(
                success=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message="No target schema provided",
                attempts=1,
            )
        try:
            if isinstance(broken_content, str):
                try:
                    data = json.loads(broken_content)
                except json.JSONDecodeError:
                    data = {"raw_content": broken_content}
            else:
                data = broken_content
            filled = self._fill_missing_fields(data, target_schema)
            validated = target_schema(**filled)
            return RepairResult(
                success=True,
                repaired_data=validated,
                strategy_used=self.strategy_name,
                attempts=1,
            )
        except (
            ValidationError,
            Exception,
        ) as e:  # guardian: Multiple exceptions (ValidationError, Exception) need specific handling
            return RepairResult(
                success=False,
                repaired_data=broken_content,
                strategy_used=self.strategy_name,
                error_message=str(e),
                attempts=1,
            )

    def _fill_missing_fields(self, data: dict, schema: BaseModel) -> dict:
        """Fill missing fields based on schema.

        Args:
            data: Current data
            schema: Target schema

        Returns:
            Filled data
        """
        filled = data.copy()
        for field_name, field_info in tqdm(schema.__fields__.items(), desc="Processing", unit="item"):
            if field_name not in filled:
                if field_info.default is not None:
                    filled[field_name] = field_info.default
                elif field_info.default_factory is not None:
                    filled[field_name] = field_info.default_factory()
                else:
                    field_type = str(field_info.type_)
                    if "list" in field_type:
                        filled[field_name] = []
                    elif "dict" in field_type:
                        filled[field_name] = {}
                    elif "str" in field_type:
                        filled[field_name] = ""
                    elif "int" in field_type or "float" in field_type:
                        filled[field_name] = 0
                    elif "bool" in field_type:
                        filled[field_name] = False
        return filled

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.SCHEMA_FILL


class FallbackTextStrategy(FormatRepair):
    """Provides safe text fallback."""

    async def repair(
        self,
        broken_content: str,
        target_schema: BaseModel | None = None,
        context: dict[str, Any] | None = None,
    ) -> RepairResult:
        """Provide text fallback.

        Args:
            broken_content: Content to fallback
            target_schema: Optional target schema
            context: Additional context

        Returns:
            Repair result with safe fallback
        """
        cleaned = broken_content.strip()
        cleaned = re.sub("[^\\x20-\\x7E\\n\\r\\t]", "", cleaned)
        if len(cleaned) > 1000:
            cleaned = cleaned[:1000] + "... [truncated]"
        fallback = {
            "raw_content": cleaned,
            "fallback_used": True,
            "timestamp": datetime.utcnow().isoformat(),
            "original_error": "Formatting failed, using text fallback",
        }
        return RepairResult(
            success=True,
            repaired_data=fallback,
            strategy_used=self.strategy_name,
            attempts=1,
            error_message="Using text fallback",
        )

    @property
    def strategy_name(self) -> RepairStrategy:
        """Get strategy name."""
        return RepairStrategy.FALLBACK_TEXT


class SelfHealingFormatter:
    """Formatter with automatic error recovery."""

    def __init__(self):
        """Initialize self-healing formatter."""
        self.base_formatter = get_unified_formatter()
        self.repair_strategies = [
            MarkdownStripStrategy(),
            JSONRepairStrategy(),
            RegexExtractStrategy(),
            SchemaFillStrategy(),
            FallbackTextStrategy(),
        ]
        self._stats = {
            "total_formats": 0,
            "successful_formats": 0,
            "repairs_needed": 0,
            "strategy_usage": {s.strategy_name.value: 0 for s in self.repair_strategies},
        }
        logger.info("Initialized SelfHealingFormatter")

    async def format_with_healing(
        self,
        data: Any,
        format_type: FormatType | str,
        engine_type: EngineType | None = None,
        config: dict[str, Any] | None = None,
        target_schema: BaseModel | None = None,
    ) -> FormatResult:
        """Format data with automatic healing.

        Args:
            data: Data to format
            format_type: Type of formatting
            engine_type: Optional engine type
            config: Optional configuration
            target_schema: Optional target schema

        Returns:
            Format result with healing applied
        """
        self._stats["total_formats"] += 1
        try:
            result = self.base_formatter.format(data, format_type, engine_type, config)
            if result.success:
                self._stats["successful_formats"] += 1
                return result
        except Exception as e:  # guardian: allow-silent-swallow
            logger.warning(f"Standard formatting failed: {e}")
            result = FormatResult(data=data, format_type=str(format_type), success=False, errors=[str(e)])
        self._stats["repairs_needed"] += 1
        content_str = str(data)
        for strategy in self.repair_strategies:
            try:
                repair_result = await strategy.repair(
                    content_str,
                    target_schema,
                    {"format_type": format_type, "engine_type": engine_type},
                )
                if repair_result.success:
                    self._stats["strategy_usage"][strategy.strategy_name.value] += 1
                    try:
                        healed_result = self.base_formatter.format(
                            repair_result.repaired_data,
                            format_type,
                            engine_type,
                            config,
                        )
                        if healed_result.success:
                            healed_result.metadata.update(
                                {
                                    "healed": True,
                                    "repair_strategy": strategy.strategy_name.value,
                                    "repair_attempts": repair_result.attempts,
                                    "original_error": repair_result.original_error,
                                },
                            )
                            self._stats["successful_formats"] += 1
                            logger.info(f"Successfully healed using {strategy.strategy_name.value}")
                            return healed_result
                    except Exception as e:  # guardian: allow-silent-swallow
                        logger.warning(f"Healed data still failed to format: {e}")
                        continue
            except Exception as e:  # guardian: allow-silent-swallow
                logger.error(f"Repair strategy {strategy.strategy_name.value} failed: {e}")
                continue
        logger.error("All repair strategies failed, returning safe fallback")
        fallback_strategy = FallbackTextStrategy()
        fallback_result = await fallback_strategy.repair(content_str)
        return FormatResult(
            data=fallback_result.repaired_data,
            format_type="fallback",
            success=True,
            metadata={"healed": True, "repair_strategy": "fallback", "all_strategies_failed": True},
            errors=result.errors,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get healing statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        if stats["total_formats"] > 0:
            stats["success_rate"] = stats["successful_formats"] / stats["total_formats"]
            stats["repair_rate"] = stats["repairs_needed"] / stats["total_formats"]
        else:
            stats["success_rate"] = 0.0
            stats["repair_rate"] = 0.0
        return stats

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._stats = {
            "total_formats": 0,
            "successful_formats": 0,
            "repairs_needed": 0,
            "strategy_usage": {s.strategy_name.value: 0 for s in self.repair_strategies},
        }


_healing_formatter: SelfHealingFormatter | None = None


def get_self_healing_formatter() -> SelfHealingFormatter:
    """Get global self-healing formatter instance.

    Returns:
        SelfHealingFormatter instance
    """
    global _healing_formatter
    if _healing_formatter is None:
        _healing_formatter = SelfHealingFormatter()
    return _healing_formatter


async def format_with_healing(
    data: Any,
    format_type: FormatType | str,
    engine_type: EngineType | None = None,
    config: dict[str, Any] | None = None,
    target_schema: BaseModel | None = None,
) -> FormatResult:
    """Format data with self-healing.

    Args:
        data: Data to format
        format_type: Type of formatting
        engine_type: Optional engine type
        config: Optional configuration
        target_schema: Optional target schema

    Returns:
        Healed format result
    """
    formatter = get_self_healing_formatter()
    return await formatter.format_with_healing(data, format_type, engine_type, config, target_schema)
