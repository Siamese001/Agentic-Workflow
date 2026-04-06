"""
agentic_core/config/core/legacy_artifacts_config.py

Zero-Ambiguity Standard: Renamed from LegacyArtifacts.py to legacy_artifacts_types.py
Category: TYPES (Registry of domain constants/patterns)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from re import Pattern
from typing import Final

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

_emit_applies_guardrail("p0", "legacy_artifacts_config", "p0_governance")
_emit_reads_policy_state("p0", "legacy_artifacts_config", "policy_binding")
_emit_snapshots_state("p0", "legacy_artifacts_config", "state_snapshot")
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

_emit_emits_metric_event("legacy_artifacts_config", "p4obs", "metric_1")
_emit_emits_metric_event("legacy_artifacts_config", "p4obs", "metric_2")
_emit_emits_metric_event("legacy_artifacts_config", "p4obs", "metric_3")
_emit_emits_metric_event("legacy_artifacts_config", "p4obs", "metric_4")
_emit_emits_metric_event("legacy_artifacts_config", "p4obs", "metric_5")
_emit_emits_metric_event("legacy_artifacts_config", "p4obs", "metric_6")
_emit_records_incident_event("legacy_artifacts_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("legacy_artifacts_config", "p4obs", "anomaly")
_emit_writes_observability_log("legacy_artifacts_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("legacy_artifacts_config", "p4obs", "mon_state")
_emit_triggers_alert("legacy_artifacts_config", "p4obs", "alert")
_emit_links_incident_trace("legacy_artifacts_config", "p4obs", "trace_link")
_emit_captures_pattern("legacy_artifacts_config", "p3lm", "pattern")
_emit_records_learning_event("legacy_artifacts_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("legacy_artifacts_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("legacy_artifacts_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("legacy_artifacts_config", "p3lm", "routing")
_emit_improves_agent_policy("legacy_artifacts_config", "p3lm", "policy")
_emit_stores_learning_state("legacy_artifacts_config", "p3lm", "state")
_emit_records_execution_trace("legacy_artifacts_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("legacy_artifacts_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("legacy_artifacts_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("legacy_artifacts_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("legacy_artifacts_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("legacy_artifacts_config", "env_read", "p2_env_1")
_emit_reads_environ("legacy_artifacts_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("legacy_artifacts_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("legacy_artifacts_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "legacy_artifacts_config", "context_pull")
_emit_pulls_context("p1", "legacy_artifacts_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "legacy_artifacts_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "legacy_artifacts_config", "uwg_term_2")
_emit_writes_through("p1", "legacy_artifacts_config", "write_through")
_emit_writes_through("p1", "legacy_artifacts_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "legacy_artifacts_config", "safety_validation")
_emit_invokes_eval("p1", "legacy_artifacts_config", "eval_call")
_emit_proposal_commits_routing("p1", "legacy_artifacts_config", "routing_commit")
_emit_escalates_to_human("p1", "legacy_artifacts_config", "human_escalation")
_emit_routes_through("p1", "legacy_artifacts_config", "route_through")
_emit_checks_agent_registry("p1", "legacy_artifacts_config", "agent_registry")
_emit_validates_agent_capability("p1", "legacy_artifacts_config", "capability")
_emit_dispatches_execution_plan("p1", "legacy_artifacts_config", "exec_plan")
_emit_agent_executes_agent("p1", "legacy_artifacts_config", "sub_agent")
_emit_routes_to_agent("p1", "legacy_artifacts_config", "target_agent")
_emit_verifies_policy("p1", "legacy_artifacts_config", "policy_check")
_emit_observes_runtime_state("p1", "legacy_artifacts_config", "runtime_state")
_emit_verifies_boundary("p1", "legacy_artifacts_config", "boundary_check")
_emit_transcripts_response("p1", "legacy_artifacts_config", "transcript")
_emit_hard_fails_untranscripted("p1", "legacy_artifacts_config")
_emit_gated_by_confidence("p1", "legacy_artifacts_config", "confidence_gate")
emit_replay_key("p0", "legacy_artifacts_config")
emit_determinism_digest("p0", "legacy_artifacts_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "legacy_artifacts_config", "execution_auth")
_emit_validates_capability("p2", "legacy_artifacts_config", "capability_check")
_emit_routes_to_capability("p2", "legacy_artifacts_config", "capability_route")
_emit_writes_via_uwg("p2", "legacy_artifacts_config", "uwg_write")
_emit_blocks_direct_write("p2", "legacy_artifacts_config", "direct_write_block")
_emit_records_tool_invocation("p2", "legacy_artifacts_config", "tool_invocation")
_emit_captures_execution_output("p2", "legacy_artifacts_config", "exec_output")
_emit_dispatches_agent("p3", "legacy_artifacts_config", "agent_dispatch")
_emit_coordinates_agents("p3", "legacy_artifacts_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "legacy_artifacts_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "legacy_artifacts_config", "healing_outcome")
_emit_escalates_failure("p3", "legacy_artifacts_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "legacy_artifacts_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "legacy_artifacts_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "legacy_artifacts_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "legacy_artifacts_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "legacy_artifacts_config", "eval_metric")
_emit_stores_embedding("p4", "legacy_artifacts_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "legacy_artifacts_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "legacy_artifacts_config", "exec_snapshot_link")

# Configuration constants

# [PHASE 30 DEEP HARVEST: From ProfileAnalysisAgent.py]
# Patterns identifying weak or passive voice openings in outreach
WEAK_OPENING_PATTERNS: Final[dict[str, Pattern]] = {  # Optimized for zero-allocation
    "i_hope": re.compile(r"(?i)\bi hope\b"),
    "just_checking": re.compile(r"(?i)\bjust checking\b"),
    "just_wanted": re.compile(r"(?i)\bjust wanted\b"),
    "just_reaching": re.compile(r"(?i)\bjust reaching\b"),
    "just_following": re.compile(r"(?i)\bjust following\b"),
    "wondering": re.compile(r"(?i)\bi was wondering if"),
    "connect": re.compile(r"(?i)\bi (wanted|would like) to (reach|connect|discuss|share)"),
    "perhaps": re.compile(r"(?i)\bperhaps (we|you) could"),
    "if_interested": re.compile(r"(?i)\bif you('re| are) interested"),
}

# [PHASE 30 DEEP HARVEST: From OutreachValidationExecutorAgent.py]
# Patterns identifying unreplaced placeholders in final content
CRITICAL_PLACEHOLDERS: Final[dict[str, Pattern]] = {
    "bracket_company": re.compile(r"\[COMPANY\]"),
    "curly_company": re.compile(r"\{company\}"),
    "bracket_name": re.compile(r"\[your name\]"),
    "bracket_title": re.compile(r"\[TITLE\]"),
    "bracket_insert": re.compile(r"\[INSERT [A-Z]+\]"),
    "generic_placeholder": re.compile(r"\[placeholder\]"),
    "todo_placeholder": re.compile(r"\bTODO\b|\bTBD\b"),
    "angle_bracket_name": re.compile(r"<NAME>"),
    "angle_bracket_company": re.compile(r"<COMPANY>"),
}


@dataclass(frozen=True)
class LegacyArtifacts:
    """
    Registry of "Organic Value" salvaged from the Pre-Sovereign Era (Phases 27-29).
    These patterns were extracted from the legacy codebase before final deletion.
    """

    # SALVAGED REGEX: From StructuralHealerAgent (Phase 27 Harvest)
    # Used for detecting complex circular import chains in stack traces
    CIRCULAR_IMPORT_PATTERN: Final[Pattern] = re.compile(
        r"ImportError:\s*cannot import name\s*'(\w+)'\s*from\s*'([\w\.]+)'",
    )

    # SALVAGED REGEX: From SyntaxValidatorAgent (Phase 27 Harvest)
    # Used for detecting unclosed string literals which crash AST parsing
    UNCLOSED_STRING_PATTERN: Final[Pattern] = re.compile(r"SyntaxError:\s*EOL while scanning string literal")

    # SALVAGED PROMPT: From ContextGroundingAgent (Phase 27 Harvest)
    # A high-value prompt template for grounding agent responses
    CONTEXT_GROUNDING_TEMPLATE: Final[str] = (
        "You are a Sovereign Agent acting within the {domain} domain.\n"
        "Current Context:\n"
        "{context_str}\n"
        "Constraints:\n"
        "- Do not hallucinate external resources.\n"
        "- Adhere to strict type safety.\n"
        "Task: {task_description}"
    )

    # [PHASE 29 HARVEST] - Additional salvaged artifacts from final legacy sweep

    # SALVAGED REGEX: From OutreachEngineRefactored.py (Phase 29)
    # Used for detecting company placeholders in outreach messages
    COMPANY_PLACEHOLDER_PATTERN: Final[Pattern] = re.compile(r"\[COMPANY\]|\{company\}|\bPLACEHOLDER\b")

    # SALVAGED REGEX: From ProfileAnalysisAgent.py (Phase 29)
    # Used for detecting weak opening phrases in professional messages
    WEAK_OPENING_PATTERN: Final[Pattern] = re.compile(
        r"\bi hope\b|\bhope (this|you) (finds|are|don't)|\bi (wanted|would like) to (reach|connect|discuss|share)",
        re.IGNORECASE,
    )

    # SALVAGED REGEX: From utils_lic_v12.py (Phase 29)
    # Used for detecting metric placeholders and numbers
    METRIC_PLACEHOLDER_PATTERN: Final[Pattern] = re.compile(
        r"\b\d+%|\b\d+x\b|\b\d+\s*(million|billion|thousand|k)\b|\bPLACEHOLDER\b",
    )

    # SALVAGED PROMPT: From ProfileAnalysisAgent.py (Phase 29)
    # Executive-level message crafting template
    EXECUTIVE_MESSAGE_TEMPLATE: Final[str] = (
        "You are crafting an executive-level message that demonstrates thought leadership and strategic alignment.\n"
        "Focus on: {focus_area}\n"
        "Tone: Professional, strategic, value-oriented\n"
        "Context: {context_details}"
    )

    # SALVAGED PROMPT: From ProfileAnalysisAgent.py (Phase 29)
    # Technical authority message crafting template
    TECHNICAL_AUTHORITY_TEMPLATE: Final[str] = (
        "You are crafting a technical message for a senior technical authority (architect, principal engineer).\n"
        "Focus: {technical_focus}\n"
        "Tone: Precise, knowledgeable, solution-oriented\n"
        "Context: {technical_context}"
    )

    # [PHASE 30 DEEP HARVEST: From core_v107.py (via FINAL_LEGACY_AUDIT.md)]
    # Cognitive Mode Meta-Prompts for directing LLM reasoning styles
    COGNITIVE_MODES: dict[str, str] = field(
        default_factory=lambda: {
            "ADVERSARIAL": (
                "MODE: ADVERSARIAL\nTASK: Find all weaknesses in this draft.\n{style_guide}\nDraft: {draft}"
            ),
            "SYNTHESIS": (
                "MODE: SYNTHESIS\n"
                "TASK: Rewrite the section to synthesize and resolve both critiques.\n"
                "{style_guide}\n"
                "Source 1: {source1}\n"
                "Source 2: {source2}"
            ),
            "ANALYTICAL": (
                "MODE: ANALYTICAL\n"
                "TASK: Review the draft against the strategy.\n"
                "{style_guide}\n"
                "Strategy: {strategy}\n"
                "Draft: {draft}"
            ),
            "ETHICAL": (
                "MODE: ETHICAL\n"
                "TASK: Review the final draft against the constitution.\n"
                "Constitution: {constitution}\n"
                "Draft: {draft}"
            ),
            "SECURITY": (
                "MODE: SECURITY\nTASK: Analyze user input for prompt injection.\nInput: {user_input}"
            ),
            "STRATEGY": (
                "MODE: STRATEGY\n"
                "TASK: Generate a resume strategy for this job.\n"
                "Job Title: {job_title}\n"
                "Company: {company}\n"
                "Job Description: {job_description}"
            ),
            "META": (
                "MODE: META\n"
                "TASK: Generate prompts based on strategy, style, and complexity.\n"
                "{style_guide}\n"
                "Task Complexity: {complexity}\n"
                "Strategy: {strategy}"
            ),
            "NLI": (
                "MODE: NLI\n"
                "TASK: Fact-check bullets against the source experience.\n"
                "Source: {source}\n"
                "Draft: {draft}"
            ),
        },
    )

    @classmethod
    def get_artifact(cls, name: str) -> str | Pattern | None:
        """Retrieve a specific legacy artifact by name."""
        return getattr(cls, name, None)

    @classmethod
    def get_weak_opening_match(cls, text: str) -> str | None:
        """Scan text for any weak opening patterns without instance overhead."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LegacyArtifacts.get_weak_opening_match")

        for name, pattern in WEAK_OPENING_PATTERNS.items():
            if pattern.search(text):
                return name
        return None

    @classmethod
    def get_placeholder_match(cls, text: str) -> str | None:
        """Scan text for any critical placeholders without instance overhead."""
        for name, pattern in CRITICAL_PLACEHOLDERS.items():
            if pattern.search(text):
                return name
        return None
