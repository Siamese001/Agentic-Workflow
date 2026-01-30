"""Outreach Validation Executor - LIC-Specific Validation Gates.

This module extends ValidationGateExecutor with outreach-specific validation
rules including Metric source binding, redundancy guards, and forbidden content.
"""

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


# ValidationGateExecutor stub
class ValidationGateExecutor:
    pass


class RuleFailure:
    pass


if TYPE_CHECKING:
    from agentic_core.L5_safety.validators import RuleFailure

LOGGER = logging.getLogger(__name__)


# STUBS: Legacy mixins (use LICAgentBase instead)
class MCPHardenedMixin:
    """Legacy mixin - use LICAgentBase instead."""

    pass


class HealerMixin:
    """Legacy mixin - use LICAgentBase instead."""

    pass


@dataclass
class OutreachValidationExecutorAgent(SovereignBaseAgent):
    """Extended validation executor for outreach-specific rules.

    Implements LIC-specific validation gates:
    - LIC-QA-001: Placeholder detection (CRITICAL)
    - LIC-QA-008: Forbidden corporate verbs (MEDIUM)
    - LIC-QA-009: Weak filler phrases (MEDIUM)
    - LIC-QA-041: Metric source binding (HIGH)
    - LIC-QA-043: Metric context validation (HIGH)
    - Redundancy guard for EXISTING contacts (Jaccard ≤0.40)
    """

    def __init__(
        self,
        validation_gates: list[Any],
        WordCountConstraints: dict[str, Any],
        similarity_thresholds: dict[str, float],
        forbidden_verbs: list[str],
        forbidden_filler_phrases: list[str],
    ) -> None:
        """Initialize outreach validation executor.

        Args:
            validation_gates: Validation gates from config
            WordCountConstraints: Word count constraints
            similarity_thresholds: Similarity thresholds
            forbidden_verbs: Forbidden corporate verbs
            forbidden_filler_phrases: Forbidden filler phrases
        """
        super().__init__(
            validation_gates=validation_gates,
            WordCountConstraints=WordCountConstraints,
            similarity_thresholds=similarity_thresholds,
        )

        self.forbidden_verbs: list[str] = [v.lower() for v in forbidden_verbs]
        self.forbidden_filler_phrases: list[str] = [p.lower() for p in forbidden_filler_phrases]

        LOGGER.info(
            f"OutreachValidationExecutorAgent initialized: "
            f"{len(forbidden_verbs)} forbidden verbs, "
            f"{len(forbidden_filler_phrases)} forbidden phrases"
        )

    def _execute_check(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: dict[str, Any],
    ) -> RuleFailure | None:
        """Execute outreach-specific validation check.

        Args:
            check: Check identifier
            content: Content to validate
            k_node_id: K-node identifier
            context: Validation context

        Returns:
            RuleFailure if check fails, None if passes
        """
        # LIC-QA-001: Placeholder detection (CRITICAL)
        if "placeholder" in check.lower() or check == "LIC-QA-001":
            return self._check_placeholders_lic(content)

        # LIC-QA-008: Forbidden corporate verbs (MEDIUM)
        if "forbidden" in check.lower() and "verb" in check.lower() or check == "LIC-QA-008":
            return self._check_forbidden_verbs(content)

        # LIC-QA-009: Weak filler phrases (MEDIUM)
        if "filler" in check.lower() or check == "LIC-QA-009":
            return self._check_filler_phrases(content)

        # LIC-QA-041: Metric source binding (HIGH)
        if "Metric" in check.lower() and "source" in check.lower() or check == "LIC-QA-041":
            return self._check_metric_source_binding(content, context)

        # LIC-QA-043: Metric context validation (HIGH)
        if "Metric" in check.lower() and "context" in check.lower() or check == "LIC-QA-043":
            return self._check_metric_context(content, context)

        # Redundancy guard for EXISTING contacts
        if "redundancy" in check.lower() and "existing" in check.lower():
            return self._check_existing_redundancy(content, context)

        # Transition phrase validation
        if "transition" in check.lower():
            return self._check_transition_phrase(content, context)

        # Signature immutability
        if "signature" in check.lower():
            return self._check_signature_immutability(content, context)

        # Fall back to base class
        return super()._execute_check(check, content, k_node_id, context)

    def _check_placeholders_lic(self, content: str) -> RuleFailure | None:
        """Check for placeholders (LIC-QA-001 - CRITICAL).

        Args:
            content: Content to check

        Returns:
            RuleFailure if placeholders found
        """
        placeholder_patterns = [
            r"\[NAME\]",
            r"\[COMPANY\]",
            r"\[TITLE\]",
            r"\{name\}",
            r"\{company\}",
            r"\{title\}",
            r"<NAME>",
            r"<COMPANY>",
            r"<TITLE>",
            r"PLACEHOLDER",
            r"TODO",
            r"TBD",
        ]

        found_placeholders = []
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_placeholders.extend(matches)

        if found_placeholders:
            return RuleFailure(
                rule_id="LIC-QA-001",
                rule_name="Placeholder Detection",
                SEVERITY="CRITICAL",
                MESSAGE=f"Placeholders detected: {', '.join(set(found_placeholders))}",
                ACTUAL=found_placeholders,
                EXPECTED="No placeholders",
            )

        return None

    def _check_forbidden_verbs(self, content: str) -> RuleFailure | None:
        """Check for forbidden corporate verbs (LIC-QA-008 - MEDIUM).

        Args:
            content: Content to check

        Returns:
            RuleFailure if forbidden verbs found
        """
        content_lower = content.lower()
        found_verbs = []

        for verb in self.forbidden_verbs:
            if verb in content_lower:
                found_verbs.append(verb)

        if found_verbs:
            return RuleFailure(
                rule_id="LIC-QA-008",
                rule_name="Forbidden Corporate Verbs",
                SEVERITY="MEDIUM",
                MESSAGE=f"Forbidden verbs detected: {', '.join(found_verbs)}",
                ACTUAL=found_verbs,
                EXPECTED="No forbidden verbs (spearheaded, leveraged, drove, etc.)",
            )

        return None

    def _check_filler_phrases(self, content: str) -> RuleFailure | None:
        """Check for weak filler phrases (LIC-QA-009 - MEDIUM).

        Args:
            content: Content to check

        Returns:
            RuleFailure if filler phrases found
        """
        content_lower = content.lower()
        found_phrases = []

        for phrase in self.forbidden_filler_phrases:
            if phrase in content_lower:
                found_phrases.append(phrase)

        if found_phrases:
            return RuleFailure(
                rule_id="LIC-QA-009",
                rule_name="Weak Filler Phrases",
                SEVERITY="MEDIUM",
                MESSAGE=f"Filler phrases detected: {', '.join(found_phrases)}",
                ACTUAL=found_phrases,
                EXPECTED="No filler phrases ('I hope', 'I wanted to', etc.)",
            )

        return None

    def _check_metric_source_binding(
        self,
        content: str,
        context: dict[str, Any],
    ) -> RuleFailure | None:
        """Check Metric source binding (LIC-QA-041 - HIGH).

        Every Metric must map to metric_source_map entry.

        Args:
            content: Content to check
            context: Context with metric_source_map

        Returns:
            RuleFailure if unbound metrics found
        """
        metric_source_map = context.get("metric_source_map", {})
        if not metric_source_map:
            LOGGER.warning("No metric_source_map in context for LIC-QA-041")
            return None

        # Extract metrics from content (numbers with %, $, or units)
        metric_patterns = [
            r"\d+%",
            r"\$\d+[KMB]?",
            r"\d+[KMB]?\+?\s+(?:users|customers|engineers|deployments)",
        ]

        found_metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_metrics.extend(matches)

        # Check if each Metric has source binding
        unbound_metrics = []
        for Metric in found_metrics:
            # Check if Metric is in source map
            if not any(Metric in str(source) for source in metric_source_map.values()):
                unbound_metrics.append(Metric)

        if unbound_metrics:
            return RuleFailure(
                rule_id="LIC-QA-041",
                rule_name="Metric Source Binding",
                SEVERITY="HIGH",
                MESSAGE=f"Unbound metrics (no source): {', '.join(unbound_metrics)}",
                ACTUAL=unbound_metrics,
                EXPECTED="All metrics must map to metric_source_map",
            )

        return None

    def _check_metric_context(
        self,
        content: str,
        context: dict[str, Any],
    ) -> RuleFailure | None:
        """Check Metric context validation (LIC-QA-043 - HIGH).

        Metrics must have keyword context from RAG.

        Args:
            content: Content to check
            context: Context with RAG evidence

        Returns:
            RuleFailure if metrics lack context
        """
        rag_evidence = context.get("rag_evidence", [])
        if not rag_evidence:
            LOGGER.warning("No rag_evidence in context for LIC-QA-043")
            return None

        # Extract metrics
        metric_patterns = [r"\d+%", r"\$\d+[KMB]?"]
        found_metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, content)
            found_metrics.extend(matches)

        # Check if metrics have surrounding context from RAG
        metrics_without_context = []
        for Metric in found_metrics:
            # Find Metric in content with surrounding words
            metric_context = self._extract_metric_context(content, Metric)

            # Check if any RAG evidence keywords appear in context
            has_context = any(
                any(keyword.lower() in metric_context.lower() for keyword in evidence.split())
                for evidence in rag_evidence
            )

            if not has_context:
                metrics_without_context.append(Metric)

        if metrics_without_context:
            return RuleFailure(
                rule_id="LIC-QA-043",
                rule_name="Metric Context Validation",
                SEVERITY="HIGH",
                MESSAGE=f"Metrics without RAG context: {', '.join(metrics_without_context)}",
                ACTUAL=metrics_without_context,
                EXPECTED="Metrics must have keyword context from RAG",
            )

        return None

    def _check_existing_redundancy(
        self,
        content: str,
        context: dict[str, Any],
    ) -> RuleFailure | None:
        """Check redundancy guard for EXISTING contacts.

        Jaccard similarity must be ≤0.40 with previous message.

        Args:
            content: Content to check
            context: Context with previous_message

        Returns:
            RuleFailure if redundancy detected
        """
        previous_message = context.get("previous_message")
        if not previous_message:
            return None  # Not EXISTING contact

        # Calculate Jaccard similarity
        jaccard = self._calculate_jaccard_similarity(content, previous_message)

        if jaccard > 0.40:
            return RuleFailure(
                rule_id="REDUNDANCY_GUARD_EXISTING",
                rule_name="Redundancy Guard (EXISTING)",
                SEVERITY="HIGH",
                MESSAGE=f"Jaccard similarity {jaccard:.2f} > 0.40 with previous message",
                ACTUAL=jaccard,
                EXPECTED="≤0.40",
                CONTEXT={"action": "MANDATORY_DETERMINISTIC_AUTO_REWRITE"},
            )

        return None

    def _check_transition_phrase(
        self,
        content: str,
        context: dict[str, Any],
    ) -> RuleFailure | None:
        """Check transition phrase presence.

        Args:
            content: Content to check
            context: Context with expected_transition_phrase

        Returns:
            RuleFailure if transition phrase Missing
        """
        expected_phrase = context.get("expected_transition_phrase")
        if not expected_phrase:
            return None

        if expected_phrase.lower() not in content.lower():
            return RuleFailure(
                rule_id="TRANSITION_PHRASE_CHECK",
                rule_name="Transition Phrase Validation",
                SEVERITY="HIGH",
                MESSAGE=f"Missing transition phrase: '{expected_phrase}'",
                ACTUAL="Not found",
                EXPECTED=expected_phrase,
            )

        return None

    def _check_signature_immutability(
        self,
        content: str,
        context: dict[str, Any],
    ) -> RuleFailure | None:
        """Check signature immutability.

        Signature must be exact 4-line block:
        Regards,
        {first_name}

        {linkedin_url}

        Args:
            content: Content to check
            context: Context with sender info

        Returns:
            RuleFailure if signature format violated
        """
        # Extract signature block (last 4 lines before fence end)
        lines = content.split(
            "\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nfrom agentic_core.base_agents.healer_mixin import HealerMixin\n"
        )

        # Find signature (look for "Regards,")
        regards_index = -1
        for i, line in enumerate(lines):
            if line.strip() == "Regards,":
                regards_index = i
                break

        if regards_index == -1:
            return RuleFailure(
                rule_id="SIGNATURE_IMMUTABILITY",
                rule_name="Signature Immutability",
                SEVERITY="HIGH",
                MESSAGE="Signature block Missing 'Regards,' line",
                ACTUAL="Not found",
                EXPECTED="Exact 4-line signature block",
            )

        # Validate 4-line structure
        if regards_index + 3 >= len(lines):
            return RuleFailure(
                rule_id="SIGNATURE_IMMUTABILITY",
                rule_name="Signature Immutability",
                SEVERITY="HIGH",
                MESSAGE="Signature block incomplete (< 4 lines)",
                ACTUAL=f"{len(lines) - regards_index} lines",
                EXPECTED="4 lines",
            )

        return None

    def _extract_metric_context(self, content: str, Metric: str) -> str:
        """Extract surrounding context for a Metric.

        Args:
            content: Full content
            Metric: Metric to find

        Returns:
            Context string (5 words before and after)
        """
        words = content.split()

        for i, word in enumerate(words):
            if Metric in word:
                start = max(0, i - 5)
                end = min(len(words), i + 6)
                return " ".join(words[start:end])

        return ""

    def _calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Jaccard similarity (0.0-1.0)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by OutreachValidationExecutorAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {"status": "skipped", "details": f"OutreachValidationExecutorAgent heal() not yet implemented for {violation_type}", "artifacts": [], "errors": []}
        except Exception as e:
            return {"status": "failed", "details": f"OutreachValidationExecutorAgent heal() failed: {str(e)}", "artifacts": [], "errors": [str(e)]}
