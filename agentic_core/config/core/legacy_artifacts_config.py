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

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
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
