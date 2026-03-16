"""
Text Processing Utilities - Phase 4 Optimization
Native Python implementations for common text operations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern

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

_emit_applies_guardrail("p0", "text_processing_validator_util", "p0_governance")
_emit_reads_policy_state("p0", "text_processing_validator_util", "policy_binding")
_emit_snapshots_state("p0", "text_processing_validator_util", "state_snapshot")
emit_replay_key("p0", "text_processing_validator_util")
emit_determinism_digest("p0", "text_processing_validator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "text_processing_validator_util", "execution_auth")
_emit_validates_capability("p2", "text_processing_validator_util", "capability_check")
_emit_routes_to_capability("p2", "text_processing_validator_util", "capability_route")
_emit_writes_via_uwg("p2", "text_processing_validator_util", "uwg_write")
_emit_blocks_direct_write("p2", "text_processing_validator_util", "direct_write_block")
_emit_records_tool_invocation("p2", "text_processing_validator_util", "tool_invocation")
_emit_captures_execution_output("p2", "text_processing_validator_util", "exec_output")
_emit_dispatches_agent("p3", "text_processing_validator_util", "agent_dispatch")
_emit_coordinates_agents("p3", "text_processing_validator_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "text_processing_validator_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "text_processing_validator_util", "healing_outcome")
_emit_escalates_failure("p3", "text_processing_validator_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "text_processing_validator_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "text_processing_validator_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "text_processing_validator_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "text_processing_validator_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "text_processing_validator_util", "eval_metric")
_emit_stores_embedding("p4", "text_processing_validator_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "text_processing_validator_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "text_processing_validator_util", "exec_snapshot_link")


@dataclass
class TextMatch:
    """Result of a text matching operation."""

    matched: bool
    matches: list[str]
    groups: list[tuple]
    positions: list[tuple]


class TextProcessor:
    """Native Python text processing utilities."""

    @staticmethod
    def extract_patterns(text: str, pattern: str | Pattern, flags: int = 0) -> TextMatch:
        """
        Extract all matches of a pattern from text.

        Args:
            text: Text to search
            pattern: Regex pattern (string or compiled)
            flags: Regex flags (e.g., re.IGNORECASE)

        Returns:
            TextMatch with all matches and positions
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TextProcessor.extract_patterns")

        if isinstance(pattern, str):
            compiled_pattern = re.compile(pattern, flags)
        else:
            compiled_pattern = pattern
        matches = compiled_pattern.finditer(text)
        match_list = []
        group_list = []
        position_list = []
        for match in matches:
            match_list.append(match.group(0))
            group_list.append(match.groups())
            position_list.append((match.start(), match.end()))
        return TextMatch(
            matched=len(match_list) > 0, matches=match_list, groups=group_list, positions=position_list
        )

    @staticmethod
    def validate_pattern(text: str, pattern: str | Pattern, flags: int = 0) -> bool:
        """
        Check if text matches a pattern.

        Args:
            text: Text to validate
            pattern: Regex pattern
            flags: Regex flags

        Returns:
            True if pattern matches, False otherwise
        """
        if isinstance(pattern, str):
            compiled_pattern = re.compile(pattern, flags)
        else:
            compiled_pattern = pattern
        return compiled_pattern.search(text) is not None

    @staticmethod
    def replace_pattern(
        text: str, pattern: str | Pattern, replacement: str, count: int = 0, flags: int = 0
    ) -> str:
        """
        Replace pattern matches in text.

        Args:
            text: Text to process
            pattern: Regex pattern
            replacement: Replacement string
            count: Maximum replacements (0 = all)
            flags: Regex flags

        Returns:
            Text with replacements applied
        """
        if isinstance(pattern, str):
            compiled_pattern = re.compile(pattern, flags)
        else:
            compiled_pattern = pattern
        return compiled_pattern.sub(replacement, text, count=count)

    @staticmethod
    def clean_whitespace(text: str, preserve_newlines: bool = False) -> str:
        """
        Clean excessive whitespace from text.

        Args:
            text: Text to clean
            preserve_newlines: Whether to preserve newline characters

        Returns:
            Cleaned text
        """
        if preserve_newlines:
            lines = text.split("\n")
            cleaned_lines = [re.sub("[ \\t]+", " ", line.strip()) for line in lines]
            return "\n".join(cleaned_lines)
        else:
            return re.sub("\\s+", " ", text).strip()

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        """
        Extract email addresses from text.

        Args:
            text: Text to search

        Returns:
            List of email addresses found
        """
        pattern = "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"
        return re.findall(pattern, text)

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """
        Extract URLs from text.

        Args:
            text: Text to search

        Returns:
            List of URLs found
        """
        pattern = "https?://(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&/=]*)"
        return re.findall(pattern, text)

    @staticmethod
    def extract_numbers(text: str, include_decimals: bool = True) -> list[float]:
        """
        Extract numbers from text.

        Args:
            text: Text to search
            include_decimals: Whether to include decimal numbers

        Returns:
            List of numbers found
        """
        if include_decimals:
            pattern = "-?\\d+\\.?\\d*"
        else:
            pattern = "-?\\d+"
        matches = re.findall(pattern, text)
        return [float(m) for m in matches if m and m != "-"]

    @staticmethod
    def tokenize(text: str, delimiter: str | None = None) -> list[str]:
        """
        Tokenize text into words or custom delimited parts.

        Args:
            text: Text to tokenize
            delimiter: Optional delimiter (None = whitespace)

        Returns:
            List of tokens
        """
        if delimiter:
            return [t.strip() for t in text.split(delimiter) if t.strip()]
        else:
            return text.split()

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length.

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - len(suffix)] + suffix

    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.

        Args:
            text: Text to count

        Returns:
            Number of words
        """
        return len(text.split())

    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count sentences in text.

        Args:
            text: Text to count

        Returns:
            Number of sentences
        """
        sentences = re.split("[.!?]+", text)
        return len([s for s in sentences if s.strip()])
