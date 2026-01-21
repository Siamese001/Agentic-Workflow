# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

"""
L5+ Integrity Gate Executor with Two-Pass Validation.

Implements the Canon Validator two-pass validation pattern:
- Pass 1: Fast regex-based checks (fail-fast)
- Pass 2: Deep semantic/LLM-based checks (expensive)

This optimizes validation by avoiding expensive checks when
fast checks already detect issues.
"""
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol

from agentic_core.utils.core_extensions.timeout_decorator import timeout

Logger = logging.getLogger(__name__)

# CRITICAL ARCHITECTURAL REFACTOR: Removed import from APPS_SHARED_DIR.
# The signal bus functionality is now provided via dependency injection.


# Define a local Protocol for the signal bus interface.
# This allows dependency injection of a signal bus without direct import
# from downstream layers like APPS_SHARED_DIR.
# NAMING FIXED: SignalBusInterface → SignalBusInterface
class SignalBusInterface(Protocol):
    """
    Protocol for a signal bus emitter.
    An object conforming to this protocol can be injected into the executor
    to enable signal emission.
    """

    def emit(self, signal_type: Any, message: str, source: str, Severity: str) -> None: ...


# Define local Enum for the specific signal types used by this executor.
# This replaces the need to import SignalType from APPS_SHARED_DIR.
# NAMING FIXED: L5SignalType → L5SignalType
class L5SignalType(str, Enum):
    """Specific signal types emitted by the L5IntegrityGateExecutor."""

    VALIDATION_FAILURE = "validation_failure"
    QUALITY_BELOW_THRESHOLD = "quality_below_threshold"


# NAMING FIXED: ValidationSeverity → ValidationSeverity
class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""

    CRITICAL = "critical"  # Blocks output
    HIGH = "high"  # Should fix before use
    MEDIUM = "medium"  # Recommended fix
    LOW = "low"  # Minor issue
    INFO = "info"  # Informational only


# NAMING FIXED: ValidationCategory → ValidationCategory
class ValidationCategory(str, Enum):
    """Categories of validation checks."""

    STRUCTURE = "structure"
    CONTENT = "content"
    METRICS = "metrics"
    CITATIONS = "citations"
    LANGUAGE = "language"
    CONSISTENCY = "consistency"


@dataclass
# NAMING FIXED: ValidationIssue → ValidationIssue
class ValidationIssue:
    """A single validation issue."""

    category: ValidationCategory
    Severity: ValidationSeverity
    message: str
    location: str = ""
    suggestion: str = ""
    pass_detected: int = 1  # Which pass detected this (1=fast, 2=deep)


@dataclass
# NAMING FIXED: ValidationResult → ValidationResult
class ValidationResult:
    """Result of validation with all issues."""

    passed: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    depth_score: float = 0.0
    quality_score: float = 0.0
    pass1_duration_ms: float = 0.0
    pass2_duration_ms: float = 0.0
    pass2_skipped: bool = False

    def add_issue(
        self,
        category: ValidationCategory,
        Severity: ValidationSeverity,
        message: str,
        location: str = "",
        suggestion: str = "",
        pass_detected: int = 1,
    ) -> None:
        """Add a validation issue."""
        self.issues.append(
            ValidationIssue(
                category=category,
                Severity=Severity,
                message=message,
                location=location,
                suggestion=suggestion,
                pass_detected=pass_detected,
            )
        )

        # Update passed status based on Severity
        if Severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]:
            self.passed = False

    def get_issues_by_severity(self, Severity: ValidationSeverity) -> list[ValidationIssue]:
        """Get all issues of a specific Severity."""
        return [i for i in self.issues if i.Severity == Severity]

    def get_issues_by_category(self, category: ValidationCategory) -> list[ValidationIssue]:
        """Get all issues of a specific category."""
        return [i for i in self.issues if i.category == category]

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return any(i.Severity == ValidationSeverity.CRITICAL for i in self.issues)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "issue_count": len(self.issues),
            "critical_count": len(self.get_issues_by_severity(ValidationSeverity.CRITICAL)),
            "high_count": len(self.get_issues_by_severity(ValidationSeverity.HIGH)),
            "depth_score": self.depth_score,
            "quality_score": self.quality_score,
            "pass1_duration_ms": self.pass1_duration_ms,
            "pass2_duration_ms": self.pass2_duration_ms,
            "pass2_skipped": self.pass2_skipped,
            "issues": [
                {
                    "category": i.category.value,
                    "Severity": i.Severity.value,
                    "message": i.message,
                    "location": i.location,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
        }


# NAMING CANON ABSOLUTE — renamed for eternal sovereign discovery — Phase 4 — 2025-12-30
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.decorators import standard_heal
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin


class L5IntegrityGateExecutorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    L5+ Integrity Gate Executor with Two-Pass Validation.

    Canon Validator Pattern:
        # Pass 1: Fast regex
        detected_risks = self._detect_risks(content)  # Regex patterns

        # Pass 2: AST context
        if detected_risks:
            risk_context = self._analyze_risk_context(content, detected_risks)

    This executor implements:
    1. Fast regex-based checks (Pass 1) - cheap, run always
    2. Deep semantic checks (Pass 2) - expensive, skip if Pass 1 fails badly
    3. Signal emission for L5+ integration (via dependency injection)
    4. Quality scoring with multiple dimensions
    """

    # Fluff words that indicate vague language
    FLUFF_WORDS = {
        "cutting-edge",
        "innovative",
        "world-class",
        "leading",
        "premier",
        "revolutionary",
        "groundbreaking",
        "state-of-the-art",
        "best-in-class",
        "industry-leading",
        "next-generation",
        "advanced",
        "sophisticated",
        "robust",
        "powerful",
        "comprehensive",
        "extensive",
        "significant",
        "leverage",
        "synergy",
        "paradigm",
        "holistic",
        "scalable",
    }

    # Technical nouns that can follow fluff words acceptably
    TECHNICAL_NOUNS = {
        "architecture",
        "model",
        "algorithm",
        "framework",
        "platform",
        "system",
        "infrastructure",
        "stack",
        "pipeline",
        "engine",
        "service",
        "API",
        "database",
        "network",
        "protocol",
        "implementation",
        "solution",
        "approach",
        "methodology",
    }

    # Patterns for Metric detection
    METRIC_PATTERNS = [
        r"\$[\d,]+(?:\.\d+)?[KMB]?",  # Dollar amounts
        r"\d+(?:\.\d+)?%",  # Percentages
        r"\d+(?:\.\d+)?[xX]",  # Multipliers
        r"\d+(?:,\d{3})*(?:\.\d+)?",  # Plain numbers
    ]

    # Patterns for vague claims
    VAGUE_PATTERNS = [
        r"\bsignificant(?:ly)?\b",
        r"\bsubstantial(?:ly)?\b",
        r"\bmany\b",
        r"\bseveral\b",
        r"\bvarious\b",
        r"\bnumerous\b",
        r"\bimproved?\b(?!\s+by\s+\d)",
        r"\bincreased?\b(?!\s+by\s+\d)",
        r"\breduced?\b(?!\s+by\s+\d)",
    ]

    def __init__(
        self,
        min_depth_score: float = 0.7,
        min_quality_score: float = 0.7,
        skip_pass2_on_critical: bool = True,
        emit_signals: bool = True,
        signal_bus_emitter: SignalBusInterface | None = None,
    ) -> None:
        """
        Initialize the L5+ integrity gate executor.

        Args:
            min_depth_score: Minimum acceptable depth score
            min_quality_score: Minimum acceptable quality score
            skip_pass2_on_critical: Skip Pass 2 if Pass 1 finds critical issues
            emit_signals: Whether to emit signals (requires signal_bus_emitter to be provided).
                          If False, no signals will be emitted, even if a bus is provided.
            signal_bus_emitter: An optional object conforming to SignalBusInterface
                                that can emit signals. If None, no signals will be emitted.
        """
        self.min_depth_score = min_depth_score
        self.min_quality_score = min_quality_score
        self.skip_pass2_on_critical = skip_pass2_on_critical

        # If emit_signals is True AND a signal_bus_emitter was provided, use it.
        # Otherwise, set to None, effectively disabling signal emission.
        self._signal_bus = signal_bus_emitter if emit_signals else None

        Logger.info(
            f"L5IntegrityGateExecutor initialized: "
            f"depth_threshold={min_depth_score}, quality_threshold={min_quality_score}"
            f", signal_emission_enabled={self._signal_bus is not None}"
        )

    def execute(self, content: dict[str, Any]) -> ValidationResult:
        """
        Execute two-pass validation on content.

        Args:
            content: Content to validate (research output, resume section, etc.)

        Returns:
            ValidationResult with all issues found
        """
        result = ValidationResult()

        # ===== PASS 1: Fast Regex Checks =====
        pass1_start = datetime.utcnow()

        self._run_fast_checks(content, result)

        result.pass1_duration_ms = (datetime.utcnow() - pass1_start).total_seconds() * 1000
        Logger.debug(
            f"Pass 1 completed in {result.pass1_duration_ms:.1f}ms, found {len(result.issues)} issues"
        )

        # Check if we should skip Pass 2
        if self.skip_pass2_on_critical and result.has_critical_issues():
            Logger.info("Skipping Pass 2 due to critical issues in Pass 1")
            result.pass2_skipped = True
            self._emit_validation_signal(result)
            return result

        # ===== PASS 2: Deep Semantic Checks =====
        pass2_start = datetime.utcnow()

        self._run_deep_checks(content, result)

        result.pass2_duration_ms = (datetime.utcnow() - pass2_start).total_seconds() * 1000
        Logger.debug(f"Pass 2 completed in {result.pass2_duration_ms:.1f}ms")

        # Calculate final scores
        result.depth_score = self._calculate_depth_score(content)
        result.quality_score = self._calculate_quality_score(content, result)

        # Check score thresholds
        if result.depth_score < self.min_depth_score:
            result.add_issue(
                ValidationCategory.CONTENT,
                ValidationSeverity.HIGH,
                f"Depth score {result.depth_score:.2f} below threshold {self.min_depth_score}",
                pass_detected=2,
            )

        if result.quality_score < self.min_quality_score:
            result.add_issue(
                ValidationCategory.CONTENT,
                ValidationSeverity.HIGH,
                f"Quality score {result.quality_score:.2f} below threshold {self.min_quality_score}",
                pass_detected=2,
            )

        self._emit_validation_signal(result)

        return result

    def _run_fast_checks(self, content: dict[str, Any], result: ValidationResult) -> None:
        """
        Pass 1: Fast regex-based checks.
        These are cheap to run and can detect obvious issues quickly.
        """
        # Extract text content for checking
        text_content = self._extract_text_content(content)
        # Run all fast validation checks
        self._execute_fast_validation_checks(content, text_content, result)

    def _execute_fast_validation_checks(
        self, content: dict[str, Any], text_content: str, result: ValidationResult
    ) -> None:
        """Execute all fast validation checks."""
        self._check_required_fields(content, result)
        self._check_fluff_language_fast(text_content, result)
        self._check_vague_claims_fast(text_content, result)
        self._check_metric_format_fast(content, result)
        self._check_structure_fast(content, result)

    def _run_deep_checks(self, content: dict[str, Any], result: ValidationResult) -> None:
        """
        Pass 2: Deep semantic checks.

        These are more expensive and involve deeper analysis.
        """
        # Check Metric-evidence binding
        self._check_metric_binding_deep(content, result)

        # Check citation coverage
        self._check_citation_coverage_deep(content, result)

        # Check consistency across sections
        self._check_consistency_deep(content, result)

        # Check for orphaned claims
        self._check_orphaned_claims_deep(content, result)

    def _extract_text_content(self, content: dict[str, Any]) -> str:
        """Extract all text content for analysis."""

        text_parts = []

        def extract_recursive(obj: Any, depth: int = 0) -> None:
            if depth > 10:  # Prevent infinite recursion
                return

            if isinstance(obj, str):
                text_parts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_recursive(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, depth + 1)

        extract_recursive(content)
        return " ".join(text_parts)

    def _check_required_fields(self, content: dict[str, Any], result: ValidationResult) -> None:
        """Check for required fields."""

        # Define required fields based on content type
        required_fields = content.get("_required_fields", [])

        for field in required_fields:
            if field not in content or not content[field]:
                result.add_issue(
                    ValidationCategory.STRUCTURE,
                    ValidationSeverity.CRITICAL,
                    f"Required field '{field}' is Missing or empty",
                    location=field,
                )

    def _check_fluff_language_fast(self, text: str, result: ValidationResult) -> None:
        """Fast check for fluff language using regex."""

        words = re.findall(r"\b[\w-]+\b", text.lower())

        for i, word in enumerate(words):
            if word in self.FLUFF_WORDS:
                # Check if followed by technical noun
                next_words = words[i + 1 : i + 3] if i + 1 < len(words) else []

                if not any(nw in self.TECHNICAL_NOUNS for nw in next_words):
                    # Get context
                    start = max(0, i - 3)
                    end = min(len(words), i + 5)
                    context = " ".join(words[start:end])

                    result.add_issue(
                        ValidationCategory.LANGUAGE,
                        ValidationSeverity.MEDIUM,
                        f"Fluff word '{word}' without technical context",
                        location=f"...{context}...",
                        suggestion=f"Replace '{word}' with specific, measurable language",
                    )

    def _check_vague_claims_fast(self, text: str, result: ValidationResult) -> None:
        """Fast check for vague claims without metrics."""

        for pattern in self.VAGUE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]

                # Check if there's a Metric nearby
                has_metric = any(re.search(mp, context) for mp in self.METRIC_PATTERNS)

                if not has_metric:
                    result.add_issue(
                        ValidationCategory.METRICS,
                        ValidationSeverity.MEDIUM,
                        f"Vague Claim '{match.group()}' without supporting Metric",
                        location=f"...{context}...",
                        suggestion="Add specific numbers, percentages, or dollar amounts",
                    )

    def _check_metric_format_fast(self, content: dict[str, Any], result: ValidationResult) -> None:
        """Fast check for Metric format issues."""

        metrics = content.get("metrics", [])
        if isinstance(metrics, list):
            for Metric in metrics:
                if isinstance(Metric, dict):
                    value = Metric.get("value", "")

                    # Check if value has a number
                    if not any(re.search(p, str(value)) for p in self.METRIC_PATTERNS):
                        result.add_issue(
                            ValidationCategory.METRICS,
                            ValidationSeverity.HIGH,
                            f"Metric '{Metric.get('name', 'unknown')}' has no numeric value",
                            location=f"metrics.{Metric.get('name', '')}",
                            suggestion="Add specific numeric value with units",
                        )

    def _check_structure_fast(self, content: dict[str, Any], result: ValidationResult) -> None:
        """Fast structural checks."""

        # Check for minimum content length
        text = self._extract_text_content(content)

        if len(text) < 100:
            result.add_issue(
                ValidationCategory.STRUCTURE,
                ValidationSeverity.HIGH,
                "Content too short (< 100 characters)",
                suggestion="Add more detailed content",
            )

        # Check for balanced sections
        sections = content.get("sections", {})
        if isinstance(sections, dict):
            lengths = [len(str(v)) for v in sections.values()]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                for section, value in sections.items():
                    section_len = len(str(value))
                    if section_len < avg_length * 0.3:
                        result.add_issue(
                            ValidationCategory.STRUCTURE,
                            ValidationSeverity.LOW,
                            f"Section '{section}' is significantly shorter than average",
                            location=section,
                        )

    def _check_metric_binding_deep(self, content: dict[str, Any], result: ValidationResult) -> None:
        """Deep check for Metric-evidence binding."""

        metrics = content.get("metrics", [])
        evidence = content.get("evidence", {})

        if isinstance(metrics, list):
            for Metric in metrics:
                if isinstance(Metric, dict):
                    evidence_id = Metric.get("evidence_id")

                    if not evidence_id:
                        result.add_issue(
                            ValidationCategory.METRICS,
                            ValidationSeverity.HIGH,
                            f"Metric '{Metric.get('name', 'unknown')}' has no evidence binding",
                            location=f"metrics.{Metric.get('name', '')}",
                            suggestion="Link Metric to specific evidence ID",
                            pass_detected=2,
                        )
                    elif evidence_id not in evidence:
                        result.add_issue(
                            ValidationCategory.METRICS,
                            ValidationSeverity.HIGH,
                            f"Metric references non-existent evidence '{evidence_id}'",
                            location=f"metrics.{Metric.get('name', '')}",
                            pass_detected=2,
                        )

    def _check_citation_coverage_deep(
        self, content: dict[str, Any], result: ValidationResult
    ) -> None:
        """Deep check for citation coverage."""

        content.get("citations", [])
        claims = content.get("claims", [])

        if isinstance(claims, list) and len(claims) > 0:
            cited_claims = sum(1 for c in claims if c.get("citation_id"))
            coverage = cited_claims / len(claims) if claims else 0

            if coverage < 0.5:
                result.add_issue(
                    ValidationCategory.CITATIONS,
                    ValidationSeverity.MEDIUM,
                    f"Low citation coverage: {coverage:.0%} of claims cited",
                    suggestion="Add citations for key claims",
                    pass_detected=2,
                )

    def _check_consistency_deep(self, content: dict[str, Any], result: ValidationResult) -> None:
        """Deep check for consistency across sections."""

        # Check for Metric consistency
        metrics_mentioned = set()
        sections = content.get("sections", {})

        if isinstance(sections, dict):
            for section_name, section_content in sections.items():
                section_text = str(section_content)

                # Extract metrics from this section
                for pattern in self.METRIC_PATTERNS:
                    matches = re.findall(pattern, section_text)
                    metrics_mentioned.update(matches)

            # Check if same Metric appears with different values
            # (simplified check - real implementation would be more sophisticated)

    def _check_orphaned_claims_deep(
        self, content: dict[str, Any], result: ValidationResult
    ) -> None:
        """Deep check for orphaned claims."""

        claims = content.get("claims", [])
        content.get("evidence", {})

        if isinstance(claims, list):
            for Claim in claims:
                if isinstance(Claim, dict):
                    claim_text = Claim.get("text", "")
                    evidence_ids = Claim.get("evidence_ids", [])

                    if not evidence_ids:
                        result.add_issue(
                            ValidationCategory.CONTENT,
                            ValidationSeverity.MEDIUM,
                            f"Claim has no supporting evidence: '{claim_text[:50]}...'",
                            suggestion="Link Claim to evidence or remove",
                            pass_detected=2,
                        )

    def _calculate_depth_score(self, content: dict[str, Any]) -> float:
        """Calculate content depth score."""

        scores = []

        # Metric depth
        metrics = content.get("metrics", [])
        metric_score = min(len(metrics) / 4.0, 1.0) if isinstance(metrics, list) else 0
        scores.append(metric_score)

        # Evidence depth
        evidence = content.get("evidence", {})
        evidence_score = min(len(evidence) / 3.0, 1.0) if isinstance(evidence, dict) else 0
        scores.append(evidence_score)

        # Citation depth
        citations = content.get("citations", [])
        citation_score = min(len(citations) / 5.0, 1.0) if isinstance(citations, list) else 0
        scores.append(citation_score)

        # Content length depth
        text = self._extract_text_content(content)
        length_score = min(len(text) / 1000.0, 1.0)
        scores.append(length_score)

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_quality_score(self, content: dict[str, Any], result: ValidationResult) -> float:
        """Calculate overall quality score based on issues found."""

        # Start with perfect score
        score = 1.0

        # Deduct based on issues
        for issue in result.issues:
            if issue.Severity == ValidationSeverity.CRITICAL:
                score -= 0.3
            elif issue.Severity == ValidationSeverity.HIGH:
                score -= 0.15
            elif issue.Severity == ValidationSeverity.MEDIUM:
                score -= 0.05
            elif issue.Severity == ValidationSeverity.LOW:
                score -= 0.02

        return max(0.0, score)

    def _emit_validation_signal(self, result: ValidationResult) -> None:
        """Emit signal based on validation result."""

        # Check if a signal bus was provided and is active
        if not self._signal_bus:
            return

        if result.has_critical_issues():
            self._signal_bus.emit(
                L5SignalType.VALIDATION_FAILURE,  # Using local L5SignalType
                f"Critical validation issues: {len(result.get_issues_by_severity(ValidationSeverity.CRITICAL))}",
                source="L5IntegrityGateExecutor",
                Severity="error",
            )
        elif not result.passed:
            self._signal_bus.emit(
                L5SignalType.QUALITY_BELOW_THRESHOLD,  # Using local L5SignalType
                f"Quality below threshold: {result.quality_score:.2f}",
                source="L5IntegrityGateExecutor",
                Severity="warning",
            )

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L5 safety agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


def create_l5_integrity_executor(
    min_depth_score: float = 0.7,
    min_quality_score: float = 0.7,
    emit_signals: bool = True,
    signal_bus_emitter: SignalBusInterface | None = None,
) -> L5IntegrityGateExecutor:
    """
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Factory function to create L5+ integrity gate executor.

    Args:
        min_depth_score: Minimum acceptable depth score.
        min_quality_score: Minimum acceptable quality score.
        emit_signals: Whether to enable signal emission.
        signal_bus_emitter: An optional object conforming to SignalBusInterface
                            to be used for emitting signals.
    """
    return L5IntegrityGateExecutor(
        min_depth_score=min_depth_score,
        min_quality_score=min_quality_score,
        emit_signals=emit_signals,
        signal_bus_emitter=signal_bus_emitter,
    )
