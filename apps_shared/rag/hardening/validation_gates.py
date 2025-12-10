"""
runtime/shared/validation_gates.py
Validation Gate Registry for Agentic Workflow

Ported from historical resume gen Job_Workflow_v61.27.json
Implements 12+ validation gates for output quality assurance:
  - VG_SUMMARY_GROUNDING_CHECK
  - VG_BULLET_HALLUCINATION_CHECK
  - VG_THEMATIC_UNIQUENESS
  - VG_CREATIVE_BRIEF_ADHERENCE
  - VG_HEADER_INTEGRITY_CHECK
  - VG_BULLET_PROVENANCE_CHECK
  - VG_REDUNDANCY_CHECK
  - VG_NATURAL_HYPHEN_PRESERVATION
  - VG_COMPETENCY_WORD_COUNT_BALANCE
  - VG_BULLET_PUNCTUATION
  - VG_SUMMARY_VOICE_TENSE
  - VG_AGENTIC_OUTPUT_VALIDATION
"""


import hashlib
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Set, Tuple, Type

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class GatePolicy(Enum):
    """Policies for validation gate behavior."""
    VERIFY_ALL_CLAIMS_AGAINST_BULLET_POOL = auto()
    VALIDATE_GENERATED_BULLETS_AGAINST_SOURCE_POOL = auto()
    ENSURE_PRIMARY_THEME_APPEARS_ONCE = auto()
    ENFORCE_ALL_CREATIVE_BRIEF_CONSTRAINTS = auto()
    STRICT_COMPARE_HEADER_TO_framework = auto()
    VALIDATE_BULLET_ORIGIN_AND_METRICS = auto()
    ENFORCE_GLOBAL_DEDUPLICATION_MATRIX = auto()
    ENFORCE_HYPHENATION_RULES_JSON = auto()
    VALIDATE_WORD_COUNT_VARIANCE = auto()
    ENSURE_ALL_BULLETS_END_WITH_PERIOD = auto()
    ENFORCE_THIRD_PERSON_PAST_TENSE = auto()
    ENSURE_DETAILED_TRACE_NOT_SUMMARY = auto()
    HALT_ON_POTENTIAL_DATA_LOSS = auto()
    VALIDATE_ENUMS_AGAINST_QA_SPEC = auto()
    MAP_AND_VALIDATE_TO_SCHEMA = auto()


class GateDecision(Enum):
    """Decision outcomes for gate validation."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class GateSeverity(Enum):
    """Severity levels for gate failures."""
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()  # Halts workflow


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class GateViolation:
    """A single violation detected by a gate."""
    violation_id: str
    message: str
    severity: GateSeverity
    location: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "violation_id": self.violation_id,
            "message": self.message,
            "severity": self.severity.name,
            "location": self.location,
            "expected": self.expected,
            "actual": self.actual,
            "suggestion": self.suggestion,
        }


@dataclass
class GateResult:
    """Result from a validation gate."""
    gate_id: str
    policy: GatePolicy
    decision: GateDecision
    violations: List[GateViolation] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def passed(self) -> bool:
        """Check if gate passed."""
        return self.decision in (GateDecision.PASS, GateDecision.WARN)
    
    @property
    def has_critical_violations(self) -> bool:
        """Check for critical violations."""
        return any(v.severity == GateSeverity.CRITICAL for v in self.violations)
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "gate_id": self.gate_id,
            "policy": self.policy.name,
            "decision": self.decision.value,
            "passed": self.passed,
            "violation_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class GateContext:
    """Context passed to validation gates."""
    # Source data
    source_pool: List[Dict[str, object]] = field(default_factory=list)
    bullet_pool: List[str] = field(default_factory=list)
    framework_data: Dict[str, object] = field(default_factory=dict)
    
    # Generated content
    generated_content: Dict[str, object] = field(default_factory=dict)
    generated_bullets: List[str] = field(default_factory=list)
    
    # Thematic data
    primary_theme: Optional[str] = None
    secondary_themes: List[str] = field(default_factory=list)
    
    # Creative brief constraints
    creative_brief: Optional[Dict[str, object]] = None
    
    # Hyphenation rules
    hyphenation_rules: Dict[str, str] = field(default_factory=dict)
    
    # QA spec for enum validation
    qa_spec: Optional[Dict[str, object]] = None
    
    # Additional context
    extra: Dict[str, object] = field(default_factory=dict)


@dataclass
class ValidationGateConfig:
    """Configuration for the validation gate registry."""
    halt_on_critical: bool = True
    collect_all_violations: bool = True
    max_violations_per_gate: int = 100
    enabled_gates: Optional[Set[str]] = None  # None = all enabled
    disabled_gates: Set[str] = field(default_factory=set)


# =============================================================================
# interface foundation GATE
# =============================================================================

class ValidationGate(ABC):
    """interface foundation class for validation gates."""
    
    gate_id: str
    policy: GatePolicy
    description: str
    severity: GateSeverity = GateSeverity.MEDIUM
    
    @abstractmethod
    def validate(self, context: GateContext) -> GateResult:
        """
        Execute the validation gate.
        
        Args:
            context: The validation context
            
        Returns:
            GateResult with decision and any violations
        """
        pass
    
    def _create_result(
        self,
        decision: GateDecision,
        violations: Optional[List[GateViolation]] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> GateResult:
        """support to create a gate result."""
        return GateResult(
            gate_id=self.gate_id,
            policy=self.policy,
            decision=decision,
            violations=violations or [],
            metadata=metadata or {},
        )


# =============================================================================
# CONCRETE VALIDATION GATES
# =============================================================================

class SummaryGroundingCheckGate(ValidationGate):
    """VG_SUMMARY_GROUNDING_CHECK: Verify all claims against bullet pool."""
    
    gate_id = "VG_SUMMARY_GROUNDING_CHECK"
    policy = GatePolicy.VERIFY_ALL_CLAIMS_AGAINST_BULLET_POOL
    description = "Verifies that all claims in the summary are grounded in the bullet pool"
    severity = GateSeverity.HIGH
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        summary = context.generated_content.get("executive_summary", "")
        
        if not summary:
            return self._create_result(GateDecision.SKIP, metadata={"reason": "No summary to validate"})
            
        if not context.bullet_pool:
            violations.append(GateViolation(
                violation_id=f"{self.gate_id}_001",
                message="No bullet pool available for grounding check",
                severity=GateSeverity.HIGH,
            ))
            return self._create_result(GateDecision.FAIL, violations)
            
        # Extract claims from summary (sentences with metrics or specific assertions)
        claims = self._extract_claims(summary)
        
        for claim in claims:
            if not self._is_grounded(claim, context.bullet_pool):
                violations.append(GateViolation(
                    violation_id=f"{self.gate_id}_{len(violations)+1:03d}",
                    message=f"Ungrounded claim detected",
                    severity=GateSeverity.HIGH,
                    actual=claim[:100],
                    suggestion="Ensure claim is supported by source bullet pool",
                ))
                
        decision = GateDecision.PASS if not violations else GateDecision.FAIL
        return self._create_result(decision, violations, {"claims_checked": len(claims)})
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract verifiable claims from text."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        claims = []
        
        # Look for sentences with metrics, percentages, or specific assertions
        metric_pattern = re.compile(r'\d+%|\$[\d,]+[MBK]?|\d+\+?\s*(years?|clients?|projects?)', re.IGNORECASE)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and (metric_pattern.search(sentence) or len(sentence.split()) > 10):
                claims.append(sentence)
                
        return claims
    
    def _is_grounded(self, claim: str, bullet_pool: List[str]) -> bool:
        """Check if claim is grounded in bullet pool."""
        claim_lower = claim.lower()
        claim_terms = set(claim_lower.split())
        
        for bullet in bullet_pool:
            bullet_lower = bullet.lower()
            bullet_terms = set(bullet_lower.split())
            
            # Check for significant overlap
            overlap = claim_terms & bullet_terms
            if len(overlap) >= min(5, len(claim_terms) * 0.5):
                return True
                
        return False


class BulletHallucinationCheckGate(ValidationGate):
    """VG_BULLET_HALLUCINATION_CHECK: Validate generated bullets against source pool."""
    
    gate_id = "VG_BULLET_HALLUCINATION_CHECK"
    policy = GatePolicy.VALIDATE_GENERATED_BULLETS_AGAINST_SOURCE_POOL
    description = "Validates that generated bullets are derived from source pool"
    severity = GateSeverity.CRITICAL
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        if not context.generated_bullets:
            return self._create_result(GateDecision.SKIP, metadata={"reason": "No bullets to validate"})
            
        if not context.source_pool:
            violations.append(GateViolation(
                violation_id=f"{self.gate_id}_001",
                message="No source pool available for hallucination check",
                severity=GateSeverity.CRITICAL,
            ))
            return self._create_result(GateDecision.FAIL, violations)
            
        source_content = " ".join(str(s) for s in context.source_pool).lower()
        
        for i, bullet in enumerate(context.generated_bullets):
            # Extract key terms (nouns, metrics, proper nouns)
            key_terms = self._extract_key_terms(bullet)
            
            missing_terms = []
            for term in key_terms:
                if term.lower() not in source_content:
                    missing_terms.append(term)
                    
            if len(missing_terms) > len(key_terms) * 0.3:  # >30% missing = hallucination
                violations.append(GateViolation(
                    violation_id=f"{self.gate_id}_{i+1:03d}",
                    message=f"Potential hallucination in bullet {i+1}",
                    severity=GateSeverity.CRITICAL,
                    actual=bullet[:100],
                    expected="Content derived from source pool",
                    suggestion=f"Missing terms: {', '.join(missing_terms[:5])}",
                ))
                
        decision = GateDecision.PASS if not violations else GateDecision.FAIL
        return self._create_result(decision, violations, {"bullets_checked": len(context.generated_bullets)})
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b[A-Za-z][a-z]*(?:[A-Z][a-z]*)*\b|\b\d+%?\b', text)
        return [w for w in words if w.lower() not in stop_words and len(w) > 2]


class ThematicUniquenessGate(ValidationGate):
    """VG_THEMATIC_UNIQUENESS: Ensure primary theme appears once."""
    
    gate_id = "VG_THEMATIC_UNIQUENESS"
    policy = GatePolicy.ENSURE_PRIMARY_THEME_APPEARS_ONCE
    description = "Ensures the primary theme is used uniquely without repetition"
    severity = GateSeverity.MEDIUM
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        if not context.primary_theme:
            return self._create_result(GateDecision.SKIP, metadata={"reason": "No primary theme defined"})
            
        # Check all generated content for theme occurrences
        all_content = " ".join(str(v) for v in context.generated_content.values())
        theme_lower = context.primary_theme.lower()
        
        # Count occurrences
        occurrences = all_content.lower().count(theme_lower)
        
        if occurrences == 0:
            violations.append(GateViolation(
                violation_id=f"{self.gate_id}_001",
                message="Primary theme not found in generated content",
                severity=GateSeverity.MEDIUM,
                expected=f"Theme '{context.primary_theme}' should appear at least once",
            ))
        elif occurrences > 3:
            violations.append(GateViolation(
                violation_id=f"{self.gate_id}_002",
                message=f"Primary theme overused ({occurrences} times)",
                severity=GateSeverity.LOW,
                suggestion="Reduce theme repetition for better readability",
            ))
            
        decision = GateDecision.PASS if not violations else (
            GateDecision.WARN if violations[0].severity == GateSeverity.LOW else GateDecision.FAIL
        )
        return self._create_result(decision, violations, {"theme_occurrences": occurrences})


class CreativeBriefAdherenceGate(ValidationGate):
    """VG_CREATIVE_BRIEF_ADHERENCE: Enforce all creative brief constraints."""
    
    gate_id = "VG_CREATIVE_BRIEF_ADHERENCE"
    policy = GatePolicy.ENFORCE_ALL_CREATIVE_BRIEF_CONSTRAINTS
    description = "Enforces word counts, character limits, and forbidden patterns"
    severity = GateSeverity.HIGH
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        if not context.creative_brief:
            return self._create_result(GateDecision.SKIP, metadata={"reason": "No creative brief defined"})
            
        brief = context.creative_brief
        content = context.generated_content
        
        # Check headline constraints
        if "headline" in brief and "headline" in content:
            headline = content["headline"]
            headline_rules = brief["headline"]
            
            # Word count
            word_count = len(headline.split())
            if "word_count" in headline_rules:
                min_wc, max_wc = headline_rules["word_count"]
                if not (min_wc <= word_count <= max_wc):
                    violations.append(GateViolation(
                        violation_id=f"{self.gate_id}_HL_WC",
                        message=f"Headline word count out of range",
                        severity=GateSeverity.MEDIUM,
                        expected=f"{min_wc}-{max_wc} words",
                        actual=f"{word_count} words",
                    ))
                    
            # Character count
            if "char_count_max" in headline_rules:
                if len(headline) > headline_rules["char_count_max"]:
                    violations.append(GateViolation(
                        violation_id=f"{self.gate_id}_HL_CC",
                        message=f"Headline exceeds character limit",
                        severity=GateSeverity.MEDIUM,
                        expected=f"Max {headline_rules['char_count_max']} chars",
                        actual=f"{len(headline)} chars",
                    ))
                    
        # Check executive summary constraints
        if "executive_summary" in brief and "executive_summary" in content:
            summary = content["executive_summary"]
            summary_rules = brief["executive_summary"]
            
            # Word count
            word_count = len(summary.split())
            if "word_count" in summary_rules:
                min_wc, max_wc = summary_rules["word_count"]
                if not (min_wc <= word_count <= max_wc):
                    violations.append(GateViolation(
                        violation_id=f"{self.gate_id}_ES_WC",
                        message=f"Executive summary word count out of range",
                        severity=GateSeverity.MEDIUM,
                        expected=f"{min_wc}-{max_wc} words",
                        actual=f"{word_count} words",
                    ))
                    
            # Forbidden patterns
            if "forbidden_patterns" in summary_rules:
                for pattern in summary_rules["forbidden_patterns"]:
                    if pattern.lower() in summary.lower():
                        violations.append(GateViolation(
                            violation_id=f"{self.gate_id}_ES_FP",
                            message=f"Forbidden pattern found in summary",
                            severity=GateSeverity.HIGH,
                            actual=f"Pattern: '{pattern}'",
                            suggestion="Remove or rephrase the forbidden pattern",
                        ))
                        
        decision = GateDecision.PASS if not violations else GateDecision.FAIL
        return self._create_result(decision, violations)


class HeaderIntegrityCheckGate(ValidationGate):
    """VG_HEADER_INTEGRITY_CHECK: Strict compare header to framework."""
    
    gate_id = "VG_HEADER_INTEGRITY_CHECK"
    policy = GatePolicy.STRICT_COMPARE_HEADER_TO_framework
    description = "Ensures header data matches the factual framework exactly"
    severity = GateSeverity.CRITICAL
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        framework = context.framework_data
        content = context.generated_content
        
        # Check name
        if "name" in framework and "name" in content:
            if framework["name"] != content["name"]:
                violations.append(GateViolation(
                    violation_id=f"{self.gate_id}_NAME",
                    message="Name mismatch between framework and output",
                    severity=GateSeverity.CRITICAL,
                    expected=framework["name"],
                    actual=content["name"],
                ))
                
        # Check contact info
        for field in ["email", "phone", "location", "linkedin"]:
            if field in framework and field in content:
                if framework[field] != content[field]:
                    violations.append(GateViolation(
                        violation_id=f"{self.gate_id}_{field.upper()}",
                        message=f"{field.title()} mismatch",
                        severity=GateSeverity.CRITICAL,
                        expected=framework[field],
                        actual=content[field],
                    ))
                    
        decision = GateDecision.PASS if not violations else GateDecision.FAIL
        return self._create_result(decision, violations)


class BulletProvenanceCheckGate(ValidationGate):
    """VG_BULLET_PROVENANCE_CHECK: Validate bullet origin and metrics."""
    
    gate_id = "VG_BULLET_PROVENANCE_CHECK"
    policy = GatePolicy.VALIDATE_BULLET_ORIGIN_AND_METRICS
    description = "Validates that bullet metrics and claims have documented provenance"
    severity = GateSeverity.HIGH
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        # Check for metrics in bullets
        metric_pattern = re.compile(r'\$[\d,]+[MBK]?|\d+%|\d+x')
        
        for i, bullet in enumerate(context.generated_bullets):
            metrics = metric_pattern.findall(bullet)
            
            for metric in metrics:
                # Check if metric exists in source pool
                source_content = " ".join(str(s) for s in context.source_pool)
                if metric not in source_content:
                    violations.append(GateViolation(
                        violation_id=f"{self.gate_id}_{i+1:03d}",
                        message=f"Metric '{metric}' has no source provenance",
                        severity=GateSeverity.HIGH,
                        location=f"Bullet {i+1}",
                        actual=metric,
                        suggestion="Verify metric exists in source documents",
                    ))
                    
        decision = GateDecision.PASS if not violations else GateDecision.FAIL
        return self._create_result(decision, violations)


class RedundancyCheckGate(ValidationGate):
    """VG_REDUNDANCY_CHECK: Enforce global deduplication matrix."""
    
    gate_id = "VG_REDUNDANCY_CHECK"
    policy = GatePolicy.ENFORCE_GLOBAL_DEDUPLICATION_MATRIX
    description = "Detects and flags redundant content across all sections"
    severity = GateSeverity.MEDIUM
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        all_bullets = context.generated_bullets
        if len(all_bullets) < 2:
            return self._create_result(GateDecision.PASS)
            
        # Build similarity matrix
        for i, bullet1 in enumerate(all_bullets):
            for j, bullet2 in enumerate(all_bullets[i+1:], i+1):
                similarity = self._calculate_similarity(bullet1, bullet2)
                
                if similarity >= self.similarity_threshold:
                    violations.append(GateViolation(
                        violation_id=f"{self.gate_id}_{i+1}_{j+1}",
                        message=f"Redundant content detected ({similarity:.0%} similar)",
                        severity=GateSeverity.MEDIUM,
                        location=f"Bullets {i+1} and {j+1}",
                        suggestion="Consolidate or differentiate the bullets",
                    ))
                    
        decision = GateDecision.PASS if not violations else GateDecision.WARN
        return self._create_result(decision, violations, {"pairs_checked": len(all_bullets) * (len(all_bullets) - 1) // 2})
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


class HyphenPreservationGate(ValidationGate):
    """VG_NATURAL_HYPHEN_PRESERVATION: Enforce hyphenation rules."""
    
    gate_id = "VG_NATURAL_HYPHEN_PRESERVATION"
    policy = GatePolicy.ENFORCE_HYPHENATION_RULES_JSON
    description = "Ensures proper hyphenation according to defined rules"
    severity = GateSeverity.LOW
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        if not context.hyphenation_rules:
            return self._create_result(GateDecision.SKIP, metadata={"reason": "No hyphenation rules defined"})
            
        all_content = " ".join(str(v) for v in context.generated_content.values())
        
        for incorrect, correct in context.hyphenation_rules.items():
            if incorrect in all_content:
                violations.append(GateViolation(
                    violation_id=f"{self.gate_id}_{len(violations)+1:03d}",
                    message=f"Incorrect hyphenation",
                    severity=GateSeverity.LOW,
                    expected=correct,
                    actual=incorrect,
                ))
                
        decision = GateDecision.PASS if not violations else GateDecision.WARN
        return self._create_result(decision, violations)


class WordCountBalanceGate(ValidationGate):
    """VG_COMPETENCY_WORD_COUNT_BALANCE: Validate word count variance."""
    
    gate_id = "VG_COMPETENCY_WORD_COUNT_BALANCE"
    policy = GatePolicy.VALIDATE_WORD_COUNT_VARIANCE
    description = "Ensures consistent word counts across similar sections"
    severity = GateSeverity.LOW
    
    def __init__(self, max_variance: float = 0.3):
        self.max_variance = max_variance
        
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        # Check competency descriptions
        competencies = context.generated_content.get("competencies", [])
        if len(competencies) < 2:
            return self._create_result(GateDecision.PASS)
            
        word_counts = [len(str(c).split()) for c in competencies]
        avg_count = sum(word_counts) / len(word_counts)
        
        for i, count in enumerate(word_counts):
            variance = abs(count - avg_count) / avg_count if avg_count > 0 else 0
            if variance > self.max_variance:
                violations.append(GateViolation(
                    violation_id=f"{self.gate_id}_{i+1:03d}",
                    message=f"Competency {i+1} word count variance too high",
                    severity=GateSeverity.LOW,
                    expected=f"~{avg_count:.0f} words (±{self.max_variance:.0%})",
                    actual=f"{count} words ({variance:.0%} variance)",
                ))
                
        decision = GateDecision.PASS if not violations else GateDecision.WARN
        return self._create_result(decision, violations, {"avg_word_count": avg_count})


class BulletPunctuationGate(ValidationGate):
    """VG_BULLET_PUNCTUATION: Ensure all bullets end with period."""
    
    gate_id = "VG_BULLET_PUNCTUATION"
    policy = GatePolicy.ENSURE_ALL_BULLETS_END_WITH_PERIOD
    description = "Ensures consistent punctuation at end of bullets"
    severity = GateSeverity.LOW
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        for i, bullet in enumerate(context.generated_bullets):
            bullet = bullet.strip()
            if bullet and not bullet.endswith('.'):
                violations.append(GateViolation(
                    violation_id=f"{self.gate_id}_{i+1:03d}",
                    message=f"Bullet {i+1} missing terminal period",
                    severity=GateSeverity.LOW,
                    actual=bullet[-20:] if len(bullet) > 20 else bullet,
                    suggestion="Add period at end of bullet",
                ))
                
        decision = GateDecision.PASS if not violations else GateDecision.WARN
        return self._create_result(decision, violations)


class SummaryVoiceTenseGate(ValidationGate):
    """VG_SUMMARY_VOICE_TENSE: Enforce third person past tense."""
    
    gate_id = "VG_SUMMARY_VOICE_TENSE"
    policy = GatePolicy.ENFORCE_THIRD_PERSON_PAST_TENSE
    description = "Ensures summary uses third person implied voice"
    severity = GateSeverity.MEDIUM
    
    # First person indicators
    FIRST_PERSON = {'i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours'}
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        summary = context.generated_content.get("executive_summary", "")
        if not summary:
            return self._create_result(GateDecision.SKIP)
            
        words = summary.lower().split()
        
        for word in words:
            # Clean punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.FIRST_PERSON:
                violations.append(GateViolation(
                    violation_id=f"{self.gate_id}_{len(violations)+1:03d}",
                    message=f"First person pronoun detected: '{clean_word}'",
                    severity=GateSeverity.MEDIUM,
                    suggestion="Use third person implied voice",
                ))
                
        decision = GateDecision.PASS if not violations else GateDecision.FAIL
        return self._create_result(decision, violations)


class AgenticOutputValidationGate(ValidationGate):
    """VG_AGENTIC_OUTPUT_VALIDATION: Ensure detailed trace not summary."""
    
    gate_id = "VG_AGENTIC_OUTPUT_VALIDATION"
    policy = GatePolicy.ENSURE_DETAILED_TRACE_NOT_SUMMARY
    description = "Validates that agentic output includes detailed reasoning trace"
    severity = GateSeverity.HIGH
    
    def validate(self, context: GateContext) -> GateResult:
        """Execute validate operation."""
        violations = []
        
        # Check for reasoning trace in extra context
        trace = context.extra.get("reasoning_trace", [])
        
        if not trace:
            violations.append(GateViolation(
                violation_id=f"{self.gate_id}_001",
                message="No reasoning trace found in output",
                severity=GateSeverity.HIGH,
                suggestion="Include step-by-step reasoning trace",
            ))
        elif len(trace) < 3:
            violations.append(GateViolation(
                violation_id=f"{self.gate_id}_002",
                message=f"Reasoning trace too short ({len(trace)} steps)",
                severity=GateSeverity.MEDIUM,
                expected="At least 3 reasoning steps",
                actual=f"{len(trace)} steps",
            ))
            
        decision = GateDecision.PASS if not violations else GateDecision.FAIL
        return self._create_result(decision, violations)


# =============================================================================
# VALIDATION GATE REGISTRY
# =============================================================================

class ValidationGateRegistry:
    """
    Registry and executor for validation gates.
    
    Manages a collection of validation gates and executes them
    in sequence, collecting results and handling failures.
    """
    
    # Default gates in execution order
    DEFAULT_GATES: List[Type[ValidationGate]] = [
        SummaryGroundingCheckGate,
        BulletHallucinationCheckGate,
        ThematicUniquenessGate,
        CreativeBriefAdherenceGate,
        HeaderIntegrityCheckGate,
        BulletProvenanceCheckGate,
        RedundancyCheckGate,
        HyphenPreservationGate,
        WordCountBalanceGate,
        BulletPunctuationGate,
        SummaryVoiceTenseGate,
        AgenticOutputValidationGate,
    ]
    
    def __init__(self, config: Optional[ValidationGateConfig] = None) -> None:
        self.config = config or ValidationGateConfig()
        self._gates: Dict[str, ValidationGate] = {}
        self._execution_order: List[str] = []
        
        # Register default gates
        for gate_class in self.DEFAULT_GATES:
            self.register(gate_class())
            
    def register(self, gate: ValidationGate) -> None:
        """Register a validation gate."""
        self._gates[gate.gate_id] = gate
        if gate.gate_id not in self._execution_order:
            self._execution_order.append(gate.gate_id)
            
    def unregister(self, gate_id: str) -> None:
        """Unregister a validation gate."""
        if gate_id in self._gates:
            del self._gates[gate_id]
        if gate_id in self._execution_order:
            self._execution_order.remove(gate_id)
            
    def get_gate(self, gate_id: str) -> Optional[ValidationGate]:
        """Get a gate by ID."""
        return self._gates.get(gate_id)
    
    def list_gates(self) -> List[str]:
        """List all registered gate IDs."""
        return list(self._execution_order)
    
    def execute_all(self, context: GateContext) -> List[GateResult]:
        """
        Execute all enabled gates in order.
        
        Args:
            context: The validation context
            
        Returns:
            List of GateResults from all executed gates
        """
        import time
        results = []
        
        for gate_id in self._execution_order:
            # Check if gate is enabled
            if self.config.enabled_gates and gate_id not in self.config.enabled_gates:
                continue
            if gate_id in self.config.disabled_gates:
                continue
                
            gate = self._gates.get(gate_id)
            if not gate:
                continue
                
            # Execute gate
            start_time = time.time()
            try:
                result = gate.validate(context)
                result.duration_ms = (time.time() - start_time) * 1000
            except (ValueError, TypeError, RuntimeError, KeyError) as e:
                logger.error(f"Gate {gate_id} failed with exception: {e}")
                result = GateResult(
                    gate_id=gate_id,
                    policy=gate.policy,
                    decision=GateDecision.FAIL,
                    violations=[GateViolation(
                        violation_id=f"{gate_id}_EXCEPTION",
                        message=f"Gate execution failed: {str(e)}",
                        severity=GateSeverity.CRITICAL,
                    )],
                    duration_ms=(time.time() - start_time) * 1000,
                )
                
            results.append(result)
            
            # Check for halt condition
            if self.config.halt_on_critical and result.has_critical_violations:
                logger.warning(f"Halting validation at gate {gate_id} due to critical violations")
                break
                
        return results
    
    def execute_gate(self, gate_id: str, context: GateContext) -> Optional[GateResult]:
        """Execute a single gate by ID."""
        gate = self._gates.get(gate_id)
        if not gate:
            return None
            
        import time
        start_time = time.time()
        result = gate.validate(context)
        result.duration_ms = (time.time() - start_time) * 1000
        return result


@dataclass
class ValidationReport:
    """Summary report from validation gate execution."""
    total_gates: int
    passed_gates: int
    failed_gates: int
    warned_gates: int
    skipped_gates: int
    total_violations: int
    critical_violations: int
    results: List[GateResult]
    total_duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def success(self) -> bool:
        """Check if validation passed overall."""
        return self.failed_gates == 0 and self.critical_violations == 0
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        executed = self.total_gates - self.skipped_gates
        return self.passed_gates / executed if executed > 0 else 0.0
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "pass_rate": self.pass_rate,
            "summary": {
                "total": self.total_gates,
                "passed": self.passed_gates,
                "failed": self.failed_gates,
                "warned": self.warned_gates,
                "skipped": self.skipped_gates,
            },
            "violations": {
                "total": self.total_violations,
                "critical": self.critical_violations,
            },
            "total_duration_ms": self.total_duration_ms,
            "timestamp": self.timestamp,
            "gates": [r.to_dict() for r in self.results],
        }


def generate_validation_report(results: List[GateResult]) -> ValidationReport:
    """Generate a summary report from gate results."""
    passed = sum(1 for r in results if r.decision == GateDecision.PASS)
    failed = sum(1 for r in results if r.decision == GateDecision.FAIL)
    warned = sum(1 for r in results if r.decision == GateDecision.WARN)
    skipped = sum(1 for r in results if r.decision == GateDecision.SKIP)
    
    total_violations = sum(len(r.violations) for r in results)
    critical_violations = sum(
        1 for r in results for v in r.violations if v.severity == GateSeverity.CRITICAL
    )
    
    total_duration = sum(r.duration_ms for r in results)
    
    return ValidationReport(
        total_gates=len(results),
        passed_gates=passed,
        failed_gates=failed,
        warned_gates=warned,
        skipped_gates=skipped,
        total_violations=total_violations,
        critical_violations=critical_violations,
        results=results,
        total_duration_ms=total_duration,
    )


# =============================================================================
# builder FUNCTIONS
# =============================================================================

def create_default_registry() -> ValidationGateRegistry:
    """Create a registry with default configuration."""
    return ValidationGateRegistry()


def create_strict_registry() -> ValidationGateRegistry:
    """Create a registry with strict validation."""
    config = ValidationGateConfig(
        halt_on_critical=True,
        collect_all_violations=True,
    )
    return ValidationGateRegistry(config=config)


def create_minimal_registry() -> ValidationGateRegistry:
    """Create a registry with only critical gates."""
    config = ValidationGateConfig(
        enabled_gates={
            "VG_BULLET_HALLUCINATION_CHECK",
            "VG_HEADER_INTEGRITY_CHECK",
            "VG_SUMMARY_GROUNDING_CHECK",
        },
    )
    return ValidationGateRegistry(config=config)