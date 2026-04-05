"""Content Filter.

Implements content filtering for various types of sensitive content
including PII, toxicity, and other policy violations.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.types.guardrail_types import (
    ContentFilter,
    ContentType,
    GuardrailAction,
    GuardrailCheck,
    GuardrailConfig,
    GuardrailReport,
    GuardrailSeverity,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

class ContentFilterEngine:
    """Engine for filtering sensitive content."""

    def __init__(self, config: GuardrailConfig | None = None) -> None:
        """Initialize the content filter engine.

        Args:
            config: Guardrail configuration
        """
        self.config = config or GuardrailConfig()
        self.graphrag_config = get_config()

        # Filter storage
        self.filters: dict[str, ContentFilter] = {}

        # Initialize default filters
        self._initialize_default_filters()

        # Statistics
        self._filter_stats: dict[str, list[float]] = {
            "filter_time": [],
            "filter_matches": {},
            "content_type_matches": {}
        }

    def _initialize_default_filters(self) -> None:
        """Initialize default content filters."""

        # PII Filter
        pii_filter = ContentFilter(
            filter_id="pii_001",
            name="PII Detection",
            description="Detects personally identifiable information",
            content_type=ContentType.PII,
            pattern=r'\b(?:\d{3}[-.]?\d{3}[-.]?\d{4}|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)',
            keywords=["social security", "credit card", "driver's license", "passport"],
            action=GuardrailAction.BLOCK,
            severity=GuardrailSeverity.HIGH,
            confidence_threshold=0.7,
            category="privacy"
        )
        self.filters[pii_filter.filter_id] = pii_filter

        # Email Filter
        email_filter = ContentFilter(
            filter_id="email_001",
            name="Email Detection",
            description="Detects email addresses",
            content_type=ContentType.EMAIL,
            pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            action=GuardrailAction.MODIFY,
            severity=GuardrailSeverity.MEDIUM,
            confidence_threshold=0.8,
            category="contact"
        )
        self.filters[email_filter.filter_id] = email_filter

        # Phone Filter
        phone_filter = ContentFilter(
            filter_id="phone_001",
            name="Phone Detection",
            description="Detects phone numbers",
            content_type=ContentType.PHONE,
            pattern=r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            action=GuardrailAction.MODIFY,
            severity=GuardrailSeverity.MEDIUM,
            confidence_threshold=0.7,
            category="contact"
        )
        self.filters[phone_filter.filter_id] = phone_filter

        # URL Filter
        url_filter = ContentFilter(
            filter_id="url_001",
            name="URL Detection",
            description="Detects URLs",
            content_type=ContentType.URL,
            pattern=r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?',
            action=GuardrailAction.WARN,
            severity=GuardrailSeverity.LOW,
            confidence_threshold=0.8,
            category="web"
        )
        self.filters[url_filter.filter_id] = url_filter

        # Toxicity Filter
        toxicity_filter = ContentFilter(
            filter_id="toxicity_001",
            name="Toxicity Detection",
            description="Detects toxic content",
            content_type=ContentType.TOXICITY,
            keywords=["hate", "toxic", "abuse", "harassment", "bully", "threat"],
            action=GuardrailAction.BLOCK,
            severity=GuardrailSeverity.HIGH,
            confidence_threshold=0.6,
            category="safety"
        )
        self.filters[toxicity_filter.filter_id] = toxicity_filter

        # Violence Filter
        violence_filter = ContentFilter(
            filter_id="violence_001",
            name="Violence Detection",
            description="Detects violent content",
            content_type=ContentType.VIOLENCE,
            keywords=["kill", "murder", "violence", "attack", "harm", "weapon", "gun"],
            action=GuardrailAction.BLOCK,
            severity=GuardrailSeverity.CRITICAL,
            confidence_threshold=0.7,
            category="safety"
        )
        self.filters[violence_filter.filter_id] = violence_filter

        # Hate Speech Filter
        hate_speech_filter = ContentFilter(
            filter_id="hate_speech_001",
            name="Hate Speech Detection",
            description="Detects hate speech",
            content_type=ContentType.HATE_SPEECH,
            keywords=["racist", "sexist", "homophobic", "discrimination", "slur"],
            action=GuardrailAction.BLOCK,
            severity=GuardrailSeverity.CRITICAL,
            confidence_threshold=0.7,
            category="safety"
        )
        self.filters[hate_speech_filter.filter_id] = hate_speech_filter

        # Self Harm Filter
        self_harm_filter = ContentFilter(
            filter_id="self_harm_001",
            name="Self Harm Detection",
            description="Detects self-harm content",
            content_type=ContentType.SELF_HARM,
            keywords=["suicide", "self harm", "kill myself", "end my life", "depressed"],
            action=GuardrailAction.ESCALATE,
            severity=GuardrailSeverity.CRITICAL,
            confidence_threshold=0.6,
            category="safety"
        )
        self.filters[self_harm_filter.filter_id] = self_harm_filter

        # Illegal Content Filter
        illegal_filter = ContentFilter(
            filter_id="illegal_001",
            name="Illegal Content Detection",
            description="Detects illegal content",
            content_type=ContentType.ILLEGAL_CONTENT,
            keywords=["illegal", "crime", "fraud", "scam", "theft", "drugs"],
            action=GuardrailAction.BLOCK,
            severity=GuardrailSeverity.HIGH,
            confidence_threshold=0.7,
            category="legal"
        )
        self.filters[illegal_filter.filter_id] = illegal_filter

    def add_filter(self, filter: ContentFilter) -> None:
        """Add a content filter."""
        self.filters[filter.filter_id] = filter

        _emit_records_telemetry_event(
            "content_filter",
            f"filter_added_{filter.filter_id}"
        )

    def remove_filter(self, filter_id: str) -> bool:
        """Remove a content filter."""
        if filter_id in self.filters:
            del self.filters[filter_id]

            _emit_records_telemetry_event(
                "content_filter",
                f"filter_removed_{filter_id}"
            )
            return True
        return False

    def filter_content(
        self,
        content: str,
        content_id: str,
        content_type: str,
        context: str | None = None
    ) -> GuardrailReport:
        """Filter content for policy violations.

        Args:
            content: Content to filter
            content_id: Unique identifier for the content
            content_type: Type of content ("query", "context", "response", "generation")
            context: Additional context for filtering

        Returns:
            Comprehensive guardrail report
        """
        start_time = datetime.utcnow()

        try:
            # Apply all enabled filters
            checks = []
            modified_content = content

            for filter in self.filters.values():
                if not filter.enabled:
                    continue

                check = self._apply_filter(filter, content, content_id)
                checks.append(check)

                # Update filter statistics
                if not check.passed:
                    filter.match_count += 1
                    filter.last_matched = datetime.utcnow()

                    # Apply modification if needed
                    if check.action == GuardrailAction.MODIFY and check.modified_content:
                        modified_content = check.modified_content

            # Create report
            report = self._create_report(
                content_id, content_type, checks, start_time
            )

            # Update statistics
            filter_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._filter_stats["filter_time"].append(filter_time)

            _emit_records_telemetry_event(
                "content_filter",
                f"filtering_completed_{len(checks)}_checks_{report.passed}",
                "filtering_completed"
            )

            return report

        except Exception as e:
            # Return error report
            return GuardrailReport(
                report_id=f"error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                content_id=content_id,
                content_type=content_type,
                passed=False,
                overall_score=0.0,
                highest_severity=GuardrailSeverity.CRITICAL,
                checks=[],
                total_checks=0,
                passed_checks=0,
                failed_checks=0,
                warnings=0,
                actions_taken=[GuardrailAction.ESCALATE],
                content_modified=False,
                escalation_required=True,
                check_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={"error": str(e)}
            )

    def _apply_filter(
        self,
        filter: ContentFilter,
        content: str,
        content_id: str
    ) -> GuardrailCheck:
        """Apply a single content filter."""
        check_id = f"filter_{filter.filter_id}_{content_id}"

        # Check if content matches filter
        matches, confidence = filter.matches(content)

        if not matches:
            # Content passes filter
            return GuardrailCheck(
                check_id=check_id,
                rule_id=None,
                filter_id=filter.filter_id,
                passed=True,
                confidence=1.0 - confidence,  # Inverse confidence for pass
                severity=filter.severity,
                reason=f"No {filter.name} detected",
                evidence="No matching patterns found",
                action=GuardrailAction.ALLOW,
                check_type="content_filter",
                metadata={
                    "filter_name": filter.name,
                    "filter_category": filter.category
                }
            )

        # Content violates filter
        modified_content = None
        if filter.action == GuardrailAction.MODIFY:
            modified_content = self._modify_content(content, filter)

        return GuardrailCheck(
            check_id=check_id,
            rule_id=None,
            filter_id=filter.filter_id,
            passed=False,
            confidence=confidence,
            severity=filter.severity,
            reason=f"{filter.name} detected",
            evidence=self._get_evidence(content, filter),
            matched_content=self._extract_matched_content(content, filter),
            action=filter.action,
            modified_content=modified_content,
            check_type="content_filter",
            metadata={
                "filter_name": filter.name,
                "filter_category": filter.category
            }
        )

    def _modify_content(self, content: str, filter: ContentFilter) -> str:
        """Modify content to remove/filter sensitive information."""
        if filter.content_type == ContentType.EMAIL:
            # Replace emails with [EMAIL_REDACTED]
            return re.sub(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                '[EMAIL_REDACTED]',
                content
            )
        elif filter.content_type == ContentType.PHONE:
            # Replace phone numbers with [PHONE_REDACTED]
            return re.sub(
                r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
                '[PHONE_REDACTED]',
                content
            )
        elif filter.content_type == ContentType.PII:
            # Replace PII patterns with [PII_REDACTED]
            return re.sub(
                r'\b(?:\d{3}[-.]?\d{3}[-.]?\d{4}|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)',
                '[PII_REDACTED]',
                content
            )
        else:
            # For other content types, return original (or could block entirely)
            return content

    def _get_evidence(self, content: str, filter: ContentFilter) -> str:
        """Get evidence for why content matched the filter."""
        evidence_parts = []

        # Check keywords
        if filter.keywords:
            matched_keywords = []
            for keyword in filter.keywords:
                if keyword.lower() in content.lower():
                    matched_keywords.append(keyword)

            if matched_keywords:
                evidence_parts.append(f"Keywords: {', '.join(matched_keywords)}")

        # Check pattern
        if filter.pattern:
            if re.search(filter.pattern, content, re.IGNORECASE):
                evidence_parts.append("Pattern matched")

        return "; ".join(evidence_parts) if evidence_parts else "Content matched filter criteria"

    def _extract_matched_content(self, content: str, filter: ContentFilter) -> str | None:
        """Extract the specific content that matched the filter."""
        if filter.pattern:
            matches = re.findall(filter.pattern, content, re.IGNORECASE)
            if matches:
                return str(matches[0]) if matches else None

        if filter.keywords:
            for keyword in filter.keywords:
                if keyword.lower() in content.lower():
                    # Extract surrounding context
                    start = content.lower().find(keyword.lower())
                    if start != -1:
                        context_start = max(0, start - 20)
                        context_end = min(len(content), start + len(keyword) + 20)
                        return content[context_start:context_end]

        return None

    def _create_report(
        self,
        content_id: str,
        content_type: str,
        checks: list[GuardrailCheck],
        start_time: datetime
    ) -> GuardrailReport:
        """Create a comprehensive guardrail report."""
        # Calculate overall statistics
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks if check.passed)
        failed_checks = total_checks - passed_checks

        # Determine overall pass/fail
        if self.config.strict_mode:
            passed = failed_checks == 0
        else:
            # In non-strict mode, allow warnings
            critical_failures = sum(1 for check in checks
                                 if not check.passed and check.severity == GuardrailSeverity.CRITICAL)
            passed = critical_failures == 0

        # Calculate overall score
        if checks:
            overall_score = sum(check.confidence for check in checks if check.passed) / total_checks
        else:
            overall_score = 1.0

        # Find highest severity
        highest_severity = None
        for check in checks:
            if not check.passed:
                if highest_severity is None or check.severity.value > highest_severity.value:
                    highest_severity = check.severity

        # Count actions and warnings
        actions_taken = list(set(check.action for check in checks if not check.passed))
        warnings = sum(1 for check in checks if not check.passed and check.action == GuardrailAction.WARN)
        content_modified = any(check.modified_content is not None for check in checks)
        escalation_required = any(check.action == GuardrailAction.ESCALATE for check in checks)

        # Create report
        report = GuardrailReport(
            report_id=f"report_{content_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            content_id=content_id,
            content_type=content_type,
            passed=passed,
            overall_score=overall_score,
            highest_severity=highest_severity,
            checks=checks,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            actions_taken=actions_taken,
            content_modified=content_modified,
            escalation_required=escalation_required,
            check_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
        )

        return report

    def get_filters(self) -> list[ContentFilter]:
        """Get all content filters."""
        return list(self.filters.values())

    def get_filters_by_category(self, category: str) -> list[ContentFilter]:
        """Get filters by category."""
        return [f for f in self.filters.values() if f.category == category]

    def get_filter(self, filter_id: str) -> ContentFilter | None:
        """Get a specific filter."""
        return self.filters.get(filter_id)

    def update_filter(self, filter: ContentFilter) -> bool:
        """Update an existing filter."""
        if filter.filter_id in self.filters:
            self.filters[filter.filter_id] = filter
            return True
        return False

    def get_filter_stats(self) -> dict[str, Any]:
        """Get filter statistics."""
        stats = {}

        # Filter time stats
        if self._filter_stats["filter_time"]:
            times = self._filter_stats["filter_time"]
            stats["avg_filter_time_ms"] = sum(times) / len(times)
            stats["min_filter_time_ms"] = min(times)
            stats["max_filter_time_ms"] = max(times)
            stats["total_filters"] = len(times)
        else:
            stats["avg_filter_time_ms"] = 0.0
            stats["min_filter_time_ms"] = 0.0
            stats["max_filter_time_ms"] = 0.0
            stats["total_filters"] = 0

        # Filter match stats
        stats["filter_matches"] = {}
        for filter_id, filter in self.filters.items():
            stats["filter_matches"][filter_id] = {
                "match_count": filter.match_count,
                "last_matched": filter.last_matched.isoformat() if filter.last_matched else None
            }

        return stats


# Factory function
def create_content_filter_engine(
    config: GuardrailConfig | None = None
) -> ContentFilterEngine:
    """Create a content filter engine."""
    return ContentFilterEngine(config)


__all__ = [
    "ContentFilterEngine",
    "create_content_filter_engine",
]
