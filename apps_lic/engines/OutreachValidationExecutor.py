"""Outreach Validation Executor - LIC-Specific Validation Gates.

This module extends ValidationGateExecutor with outreach-specific validation
rules including metric source binding, redundancy guards, and forbidden content.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from runtime.shared.validation_executor import (
    ValidationGateExecutor,
    ValidationStatus,
    ValidationResult,
    RuleFailure,
)


logger = logging.getLogger(__name__)


class OutreachValidationExecutor(ValidationGateExecutor):
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
        validation_gates: List[Any],
        word_count_constraints: Dict[str, Any],
        similarity_thresholds: Dict[str, float],
        forbidden_verbs: List[str],
        forbidden_filler_phrases: List[str],
    ):
        """Initialize outreach validation executor.

        Args:
            validation_gates: Validation gates from config
            word_count_constraints: Word count constraints
            similarity_thresholds: Similarity thresholds
            forbidden_verbs: Forbidden corporate verbs
            forbidden_filler_phrases: Forbidden filler phrases
        """
        super().__init__(
            validation_gates=validation_gates,
            word_count_constraints=word_count_constraints,
            similarity_thresholds=similarity_thresholds,
        )

        self.forbidden_verbs = [v.lower() for v in forbidden_verbs]
        self.forbidden_filler_phrases = [p.lower() for p in forbidden_filler_phrases]

        logger.info(
            f"OutreachValidationExecutor initialized: "
            f"{len(forbidden_verbs)} forbidden verbs, "
            f"{len(forbidden_filler_phrases)} forbidden phrases"
        )

    def _execute_check(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
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
        if "metric" in check.lower() and "source" in check.lower() or check == "LIC-QA-041":
            return self._check_metric_source_binding(content, context)

        # LIC-QA-043: Metric context validation (HIGH)
        if "metric" in check.lower() and "context" in check.lower() or check == "LIC-QA-043":
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

    def _check_placeholders_lic(self, content: str) -> Optional[RuleFailure]:
        """Check for placeholders (LIC-QA-001 - CRITICAL).

        Args:
            content: Content to check

        Returns:
            RuleFailure if placeholders found
        """
        placeholder_patterns = [
            r'\[NAME\]', r'\[COMPANY\]', r'\[TITLE\]',
            r'\{name\}', r'\{company\}', r'\{title\}',
            r'<NAME>', r'<COMPANY>', r'<TITLE>',
            r'PLACEHOLDER', r'TODO', r'TBD',
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
                severity="CRITICAL",
                message=f"Placeholders detected: {', '.join(set(found_placeholders))}",
                actual=found_placeholders,
                expected="No placeholders",
            )

        return None

    def _check_forbidden_verbs(self, content: str) -> Optional[RuleFailure]:
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
                severity="MEDIUM",
                message=f"Forbidden verbs detected: {', '.join(found_verbs)}",
                actual=found_verbs,
                expected="No forbidden verbs (spearheaded, leveraged, drove, etc.)",
            )

        return None

    def _check_filler_phrases(self, content: str) -> Optional[RuleFailure]:
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
                severity="MEDIUM",
                message=f"Filler phrases detected: {', '.join(found_phrases)}",
                actual=found_phrases,
                expected="No filler phrases ('I hope', 'I wanted to', etc.)",
            )

        return None

    def _check_metric_source_binding(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
        """Check metric source binding (LIC-QA-041 - HIGH).

        Every metric must map to metric_source_map entry.

        Args:
            content: Content to check
            context: Context with metric_source_map

        Returns:
            RuleFailure if unbound metrics found
        """
        metric_source_map = context.get("metric_source_map", {})
        if not metric_source_map:
            logger.warning("No metric_source_map in context for LIC-QA-041")
            return None

        # Extract metrics from content (numbers with %, $, or units)
        metric_patterns = [
            r'\d+%',
            r'\$\d+[KMB]?',
            r'\d+[KMB]?\+?\s+(?:users|customers|engineers|deployments)',
        ]

        found_metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_metrics.extend(matches)

        # Check if each metric has source binding
        unbound_metrics = []
        for metric in found_metrics:
            # Check if metric is in source map
            if not any(metric in str(source) for source in metric_source_map.values()):
                unbound_metrics.append(metric)

        if unbound_metrics:
            return RuleFailure(
                rule_id="LIC-QA-041",
                rule_name="Metric Source Binding",
                severity="HIGH",
                message=f"Unbound metrics (no source): {', '.join(unbound_metrics)}",
                actual=unbound_metrics,
                expected="All metrics must map to metric_source_map",
            )

        return None

    def _check_metric_context(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
        """Check metric context validation (LIC-QA-043 - HIGH).

        Metrics must have keyword context from RAG.

        Args:
            content: Content to check
            context: Context with RAG evidence

        Returns:
            RuleFailure if metrics lack context
        """
        rag_evidence = context.get("rag_evidence", [])
        if not rag_evidence:
            logger.warning("No rag_evidence in context for LIC-QA-043")
            return None

        # Extract metrics
        metric_patterns = [r'\d+%', r'\$\d+[KMB]?']
        found_metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, content)
            found_metrics.extend(matches)

        # Check if metrics have surrounding context from RAG
        metrics_without_context = []
        for metric in found_metrics:
            # Find metric in content with surrounding words
            metric_context = self._extract_metric_context(content, metric)

            # Check if any RAG evidence keywords appear in context
            has_context = any(
                any(keyword.lower() in metric_context.lower() for keyword in evidence.split())
                for evidence in rag_evidence
            )

            if not has_context:
                metrics_without_context.append(metric)

        if metrics_without_context:
            return RuleFailure(
                rule_id="LIC-QA-043",
                rule_name="Metric Context Validation",
                severity="HIGH",
                message=f"Metrics without RAG context: {', '.join(metrics_without_context)}",
                actual=metrics_without_context,
                expected="Metrics must have keyword context from RAG",
            )

        return None

    def _check_existing_redundancy(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
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
                severity="HIGH",
                message=f"Jaccard similarity {jaccard:.2f} > 0.40 with previous message",
                actual=jaccard,
                expected="≤0.40",
                context={"action": "MANDATORY_DETERMINISTIC_AUTO_REWRITE"},
            )

        return None

    def _check_transition_phrase(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
        """Check transition phrase presence.

        Args:
            content: Content to check
            context: Context with expected_transition_phrase

        Returns:
            RuleFailure if transition phrase missing
        """
        expected_phrase = context.get("expected_transition_phrase")
        if not expected_phrase:
            return None

        if expected_phrase.lower() not in content.lower():
            return RuleFailure(
                rule_id="TRANSITION_PHRASE_CHECK",
                rule_name="Transition Phrase Validation",
                severity="HIGH",
                message=f"Missing transition phrase: '{expected_phrase}'",
                actual="Not found",
                expected=expected_phrase,
            )

        return None

    def _check_signature_immutability(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
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
        lines = content.split("\n")

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
                severity="HIGH",
                message="Signature block missing 'Regards,' line",
                actual="Not found",
                expected="Exact 4-line signature block",
            )

        # Validate 4-line structure
        if regards_index + 3 >= len(lines):
            return RuleFailure(
                rule_id="SIGNATURE_IMMUTABILITY",
                rule_name="Signature Immutability",
                severity="HIGH",
                message="Signature block incomplete (< 4 lines)",
                actual=f"{len(lines) - regards_index} lines",
                expected="4 lines",
            )

        return None

    def _extract_metric_context(self, content: str, metric: str) -> str:
        """Extract surrounding context for a metric.

        Args:
            content: Full content
            metric: Metric to find

        Returns:
            Context string (5 words before and after)
        """
        words = content.split()

        for i, word in enumerate(words):
            if metric in word:
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
