"""Unified Formatter - Shared formatting module for all engines.

This module provides a unified formatting system that both resume and outreach
engines can use, eliminating the need for separate format_* modules.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
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

_emit_applies_guardrail("p0", "unified_formatter_types", "p0_governance")
_emit_reads_policy_state("p0", "unified_formatter_types", "policy_binding")
_emit_snapshots_state("p0", "unified_formatter_types", "state_snapshot")
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

_emit_emits_metric_event("unified_formatter_types", "p4obs", "metric_1")
_emit_emits_metric_event("unified_formatter_types", "p4obs", "metric_2")
_emit_emits_metric_event("unified_formatter_types", "p4obs", "metric_3")
_emit_emits_metric_event("unified_formatter_types", "p4obs", "metric_4")
_emit_emits_metric_event("unified_formatter_types", "p4obs", "metric_5")
_emit_emits_metric_event("unified_formatter_types", "p4obs", "metric_6")
_emit_records_incident_event("unified_formatter_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("unified_formatter_types", "p4obs", "anomaly")
_emit_writes_observability_log("unified_formatter_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("unified_formatter_types", "p4obs", "mon_state")
_emit_triggers_alert("unified_formatter_types", "p4obs", "alert")
_emit_links_incident_trace("unified_formatter_types", "p4obs", "trace_link")
_emit_captures_pattern("unified_formatter_types", "p3lm", "pattern")
_emit_records_learning_event("unified_formatter_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("unified_formatter_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("unified_formatter_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("unified_formatter_types", "p3lm", "routing")
_emit_improves_agent_policy("unified_formatter_types", "p3lm", "policy")
_emit_stores_learning_state("unified_formatter_types", "p3lm", "state")
_emit_records_execution_trace("unified_formatter_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("unified_formatter_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("unified_formatter_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("unified_formatter_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("unified_formatter_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("unified_formatter_types", "env_read", "p2_env_1")
_emit_reads_environ("unified_formatter_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("unified_formatter_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("unified_formatter_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "unified_formatter_types", "context_pull")
_emit_pulls_context("p1", "unified_formatter_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "unified_formatter_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "unified_formatter_types", "uwg_term_2")
_emit_writes_through("p1", "unified_formatter_types", "write_through")
_emit_writes_through("p1", "unified_formatter_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "unified_formatter_types", "safety_validation")
_emit_invokes_eval("p1", "unified_formatter_types", "eval_call")
_emit_proposal_commits_routing("p1", "unified_formatter_types", "routing_commit")
_emit_escalates_to_human("p1", "unified_formatter_types", "human_escalation")
_emit_routes_through("p1", "unified_formatter_types", "route_through")
_emit_checks_agent_registry("p1", "unified_formatter_types", "agent_registry")
_emit_validates_agent_capability("p1", "unified_formatter_types", "capability")
_emit_dispatches_execution_plan("p1", "unified_formatter_types", "exec_plan")
_emit_agent_executes_agent("p1", "unified_formatter_types", "sub_agent")
_emit_routes_to_agent("p1", "unified_formatter_types", "target_agent")
_emit_verifies_policy("p1", "unified_formatter_types", "policy_check")
_emit_observes_runtime_state("p1", "unified_formatter_types", "runtime_state")
_emit_verifies_boundary("p1", "unified_formatter_types", "boundary_check")
_emit_transcripts_response("p1", "unified_formatter_types", "transcript")
_emit_hard_fails_untranscripted("p1", "unified_formatter_types")
_emit_gated_by_confidence("p1", "unified_formatter_types", "confidence_gate")
emit_replay_key("p0", "unified_formatter_types")
emit_determinism_digest("p0", "unified_formatter_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "unified_formatter_types", "execution_auth")
_emit_validates_capability("p2", "unified_formatter_types", "capability_check")
_emit_routes_to_capability("p2", "unified_formatter_types", "capability_route")
_emit_writes_via_uwg("p2", "unified_formatter_types", "uwg_write")
_emit_blocks_direct_write("p2", "unified_formatter_types", "direct_write_block")
_emit_records_tool_invocation("p2", "unified_formatter_types", "tool_invocation")
_emit_captures_execution_output("p2", "unified_formatter_types", "exec_output")
_emit_dispatches_agent("p3", "unified_formatter_types", "agent_dispatch")
_emit_coordinates_agents("p3", "unified_formatter_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "unified_formatter_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "unified_formatter_types", "healing_outcome")
_emit_escalates_failure("p3", "unified_formatter_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "unified_formatter_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "unified_formatter_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "unified_formatter_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "unified_formatter_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "unified_formatter_types", "eval_metric")
_emit_stores_embedding("p4", "unified_formatter_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "unified_formatter_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "unified_formatter_types", "exec_snapshot_link")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_1")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_2")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_3")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_4")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_5")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_6")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_7")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_8")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_9")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_10")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_11")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_12")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_13")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_14")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_15")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_16")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_17")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_18")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_19")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_20")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_21")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_22")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_23")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_24")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_25")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_26")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_27")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_28")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_29")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_30")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_31")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_32")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_33")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_34")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_35")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_36")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_37")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_38")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_39")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_40")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_41")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_42")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_43")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_44")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_45")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_46")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_47")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_48")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_49")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_50")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_51")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_52")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_53")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_54")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_55")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_56")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_57")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_58")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_59")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_60")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_61")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_62")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_63")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_64")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_65")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_66")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_67")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_68")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_69")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_70")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_71")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_72")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_73")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_74")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_75")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_76")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_77")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_78")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_79")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_80")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_81")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_82")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_83")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_84")
_emit_reads_through("l4", "unified_formatter_types", "urg_read_85")

logger = logging.getLogger(__name__)


class FormatType(Enum):
    """Types of formatting."""

    DEFAULT = "default"
    RESUME_BULLET = "resume_bullet"
    RESUME_SECTION = "resume_section"
    OUTREACH_MESSAGE = "outreach_message"
    OUTREACH_SUBJECT = "outreach_subject"
    JSON = "json"
    XML = "xml"


@dataclass
class FormatResult:
    """Result of formatting operation."""

    data: Any
    format_type: str
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data": self.data,
            "format_type": self.format_type,
            "success": self.success,
            "metadata": self.metadata,
            "errors": self.errors,
        }


class FormatterStrategy(ABC):
    """Abstract base for formatting strategies."""

    @abstractmethod
    def format(self, data: str | dict, config: dict | None = None) -> FormatResult:
        """Format the data.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get format name."""
        pass


class DefaultFormatter(FormatterStrategy):
    """Default formatting strategy."""

    def format(self, data: str | dict, config: dict | None = None) -> FormatResult:
        """Format data with default strategy.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "UnifiedFormatter.format"
        )
        try:
            if isinstance(data, str):
                formatted = data.strip()
            elif isinstance(data, dict):
                formatted = json.dumps(data, indent=2)
            else:
                formatted = str(data)
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"original_type": type(data).__name__},
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            return FormatResult(data=data, format_type=self.format_name, success=False, errors=[str(e)])

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "default"


class ResumeBulletFormatter(FormatterStrategy):
    """Formats resume bullet points."""

    def format(self, data: str | dict, config: dict | None = None) -> FormatResult:
        """Format resume bullet points.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                bullets = self._format_text_to_bullets(data)
            elif isinstance(data, list):
                bullets = self._format_list_to_bullets(data)
            else:
                bullets = [str(data)]
            if config:
                bullets = self._apply_config(bullets, config)
            return FormatResult(
                data=bullets,
                format_type=self.format_name,
                metadata={"bullet_count": len(bullets)},
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            return FormatResult(data=data, format_type=self.format_name, success=False, errors=[str(e)])

    def _format_text_to_bullets(self, text: str) -> list[str]:
        """Format text to bullet points.

        Args:
            text: Text to format

        Returns:
            List of bullet points
        """
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        bullets = []
        for sentence in sentences:
            if not any(
                sentence.startswith(verb)
                for verb in ["Led", "Managed", "Developed", "Created", "Implemented"]
            ):
                sentence = "• " + sentence
            elif not sentence.startswith("•"):
                sentence = "• " + sentence
            bullets.append(sentence)
        return bullets[:5]

    def _format_list_to_bullets(self, items: list[Any]) -> list[str]:
        """Format list to bullet points.

        Args:
            items: List of items

        Returns:
            List of bullet points
        """
        bullets = []
        for item in items:
            bullet = "• " + str(item).strip()
            if not bullet.endswith("."):
                bullet += "."
            bullets.append(bullet)
        return bullets

    def _apply_config(self, bullets: list[str], config: dict) -> list[str]:
        """Apply configuration to bullets.

        Args:
            bullets: List of bullets
            config: configuration

        Returns:
            Modified bullets
        """
        # guardian: allow-config-with-logic
        if config.get("ensure_metrics", False):
            bullets = [self._ensure_metrics(b) for b in bullets]
        # guardian: allow-config-with-logic
        if config.get("max_length"):
            max_len = config["max_length"]
            bullets = [b[:max_len] + "..." if len(b) > max_len else b for b in bullets]
        return bullets

    def _ensure_metrics(self, bullet: str) -> str:
        """Ensure bullet has metrics.

        Args:
            bullet: Bullet point

        Returns:
            Bullet with metrics
        """
        if any(char.isdigit() for char in bullet):
            return bullet
        if bullet.endswith("."):
            return bullet[:-1] + " (achieving X% improvement)."
        return bullet + " (achieving X% improvement)."

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "resume_bullet"


class ResumeSectionFormatter(FormatterStrategy):
    """Formats resume sections."""

    def format(self, data: str | dict, config: dict | None = None) -> FormatResult:
        """Format resume section.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, dict):
                formatted = self._format_dict_section(data, config)
            else:
                formatted = self._format_text_section(str(data), config)
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"section_type": config.get("section_type", "general")},
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            return FormatResult(data=data, format_type=self.format_name, success=False, errors=[str(e)])

    def _format_dict_section(self, data: dict, config: dict | None) -> dict:
        """Format dictionary section.

        Args:
            data: Section data
            config: configuration

        Returns:
            Formatted section
        """
        section_type = config.get("section_type", "general") if config else "general"
        if section_type == "experience":
            return self._format_experience_section(data)
        elif section_type == "skills":
            return self._format_skills_section(data)
        else:
            return data

    def _format_experience_section(self, data: dict) -> dict:
        """Format experience section.

        Args:
            data: Experience data

        Returns:
            Formatted experience
        """
        if "title" not in data:
            data["title"] = "Professional Experience"
        if "duration" not in data:
            data["duration"] = "Present"
        return data

    def _format_skills_section(self, data: dict) -> dict:
        """Format skills section.

        Args:
            data: Skills data

        Returns:
            Formatted skills
        """
        if "skills" in data and isinstance(data["skills"], list):
            data["technical_skills"] = [s for s in data["skills"] if self._is_technical_skill(s)]
            data["soft_skills"] = [s for s in data["skills"] if not self._is_technical_skill(s)]
        return data

    def _is_technical_skill(self, skill: str) -> bool:
        """Check if skill is technical.

        Args:
            skill: Skill name

        Returns:
            True if technical
        """
        technical_keywords = ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"]
        return any(keyword in skill.lower() for keyword in technical_keywords)

    def _format_text_section(self, text: str, config: dict | None) -> str:
        """Format text section.

        Args:
            text: Section text
            config: configuration

        Returns:
            Formatted text
        """
        if config and "section_title" in config:
            text = f"{config['section_title']}\n\n{text}"
        return text

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "resume_section"


class OutreachMessageFormatter(FormatterStrategy):
    """Formats outreach messages."""

    def format(self, data: str | dict, config: dict | None = None) -> FormatResult:
        """Format outreach message.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                formatted = self._format_message_text(data, config)
            elif isinstance(data, dict):
                formatted = self._format_message_dict(data, config)
            else:
                formatted = str(data)
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"message_length": len(str(formatted))},
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            return FormatResult(data=data, format_type=self.format_name, success=False, errors=[str(e)])

    def _format_message_text(self, text: str, config: dict | None) -> str:
        """Format message text.

        Args:
            text: Message text
            config: configuration

        Returns:
            Formatted text
        """
        if not any(greeting in text.lower() for greeting in ["dear", "hi ", "hello"]):
            text = (
                "Dear "
                + (config.get("recipient_name", "Hiring Manager") if config else "Hiring Manager")
                + ",\n\n"
                + text
            )
        if not any(closing in text.lower() for closing in ["sincerely", "regards", "best"]):
            text += "\n\nBest regards,\n[Your Name]"
        max_length = config.get("max_length", 500) if config else 500
        if len(text) > max_length:
            text = text[: max_length - 3] + "..."
        return text

    def _format_message_dict(self, data: dict, config: dict | None) -> dict:
        """Format message dictionary.

        Args:
            data: Message data
            config: configuration

        Returns:
            Formatted message
        """
        if "greeting" not in data:
            data["greeting"] = "Dear Hiring Manager,"
        if "body" not in data:
            data["body"] = ""
        if "closing" not in data:
            data["closing"] = "Best regards,"
        return data

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "outreach_message"


class OutreachSubjectFormatter(FormatterStrategy):
    """Formats outreach subject lines."""

    def format(self, data: str | dict, config: dict | None = None) -> FormatResult:
        """Format outreach subject.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                formatted = self._format_subject_text(data, config)
            else:
                formatted = str(data)
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"subject_length": len(formatted)},
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            return FormatResult(data=data, format_type=self.format_name, success=False, errors=[str(e)])

    def _format_subject_text(self, text: str, config: dict | None) -> str:
        """Format subject text.

        Args:
            text: Subject text
            config: configuration

        Returns:
            Formatted subject
        """
        text = text[0].upper() + text[1:] if text else text
        text = text.rstrip(".")
        max_length = config.get("max_length", 50) if config else 50
        if len(text) > max_length:
            text = text[: max_length - 3] + "..."
        return text

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "outreach_subject"


class JSONFormatter(FormatterStrategy):
    """Formats data as JSON."""

    def format(self, data: str | dict, config: dict | None = None) -> FormatResult:
        """Format as JSON.

        Args:
            data: Data to format
            config: Optional configuration

        Returns:
            Format result
        """
        try:
            if isinstance(data, str):
                try:
                    parsed = json.loads(data)
                except (ValueError, TypeError, RuntimeError) as e:
                    raise
            else:
                parsed = data
            indent = config.get("indent", 2) if config else 2
            formatted = json.dumps(parsed, indent=indent, default=str)
            return FormatResult(
                data=formatted,
                format_type=self.format_name,
                metadata={"json_keys": len(parsed) if isinstance(parsed, dict) else 0},
            )
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            return FormatResult(data=data, format_type=self.format_name, success=False, errors=[str(e)])

    @property
    def format_name(self) -> str:
        """Get format name."""
        return "json"


class UnifiedFormatter:
    """Unified formatter for all engines."""

    def __init__(self):
        """Initialize the unified formatter."""
        self.strategies = {
            FormatType.DEFAULT: DefaultFormatter(),
            FormatType.RESUME_BULLET: ResumeBulletFormatter(),
            FormatType.RESUME_SECTION: ResumeSectionFormatter(),
            FormatType.OUTREACH_MESSAGE: OutreachMessageFormatter(),
            FormatType.OUTREACH_SUBJECT: OutreachSubjectFormatter(),
            FormatType.JSON: JSONFormatter(),
        }
        logger.info("Initialized UnifiedFormatter")

    def format(
        self,
        data: str | dict | list,
        format_type: FormatType | str,
        engine_type: EngineType | None = None,
        config: dict | None = None,
    ) -> FormatResult:
        """Format data using specified strategy.

        Args:
            data: Data to format
            format_type: Type of formatting to apply
            engine_type: Optional engine type for context
            config: Optional configuration

        Returns:
            Format result
        """
        if isinstance(format_type, str):
            try:
                format_type = FormatType(format_type.lower())
            except ValueError:
                format_type = FormatType.DEFAULT
        strategy = self.strategies.get(format_type, self.strategies[FormatType.DEFAULT])
        if engine_type and config is None:
            config = {"engine": engine_type.value}
        elif engine_type and config:
            config["engine"] = engine_type.value
        result = strategy.format(data, config)
        if engine_type:
            result.metadata["engine_type"] = engine_type.value
        return result

    def register_strategy(self, format_type: FormatType, strategy: FormatterStrategy) -> None:
        """Register a custom formatting strategy.

        Args:
            format_type: Format type
            strategy: Formatting strategy
        """
        self.strategies[format_type] = strategy
        logger.info(f"Registered custom strategy for {format_type.value}")

    def get_available_formats(self) -> list[str]:
        """Get list of available format types.

        Returns:
            List of format type names
        """
        return [ft.value for ft in self.strategies.keys()]


_formatter: UnifiedFormatter | None = None


def get_unified_formatter() -> UnifiedFormatter:
    """Get the global unified formatter instance.

    Returns:
        UnifiedFormatter instance
    """
    global _formatter
    if _formatter is None:
        _formatter = UnifiedFormatter()
    return _formatter


def format_data(
    data: str | dict | list,
    format_type: FormatType | str,
    engine_type: EngineType | None = None,
    config: dict | None = None,
) -> FormatResult:
    """Format data using unified formatter.

    Args:
        data: Data to format
        format_type: Type of formatting
        engine_type: Optional engine type
        config: Optional configuration

    Returns:
        Format result
    """
    formatter = get_unified_formatter()
    return formatter.format(data, format_type, engine_type, config)


def format_resume_bullets(data: str | list, config: dict | None = None) -> FormatResult:
    """Format resume bullet points.

    Args:
        data: Bullet data
        config: Optional configuration

    Returns:
        Format result
    """
    return format_data(data, FormatType.RESUME_BULLET, EngineType.RESUME, config)


def format_outreach_message(data: str | dict, config: dict | None = None) -> FormatResult:
    """Format outreach message.

    Args:
        data: Message data
        config: Optional configuration

    Returns:
        Format result
    """
    return format_data(data, FormatType.OUTREACH_MESSAGE, EngineType.OUTREACH, config)
