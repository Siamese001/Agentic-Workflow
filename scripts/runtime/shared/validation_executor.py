"""Validation Gate Executor - Core Execution Framework.

This module provides the execution engine for all ValidationGate and ValidationRule
objects defined in orchestration config files (resume_orchestration_config.py and
outreach_orchestration_config.py).

Primary Responsibilities:
1. Load validation gates from config files
2. Execute validation checks with proper scope handling
3. Enforce hard stops for CRITICAL failures
4. Return structured validation results for orchestrator decision-making
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from sklearn.metrics.pairwise import cosine_similarity

LOGGER = logging.getLogger(__name__)

class ValidationStatus(str, Enum):
    """Validation result status."""
    pass = "pass"
    FAIL = "FAIL"
    BLOCK = "BLOCK"  # Critical failure - halt immediately

class ValidationAction(str, Enum):
    """Action to take on validation failure."""
    REGENERATE = "REGENERATE"
    HALT = "HALT"
    SOFT_REJECT = "SOFT_REJECT"
    WARN = "WARN"
    PROCEED = "PROCEED"

@dataclass
class RuleFailure:
    """Details of a failed validation rule."""
    rule_id: str
    rule_name: str
    severity: str
    message: str
    actual: Any
    expected: Any
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of validation gate execution."""
    status: ValidationStatus
    gate_id: str
    execution_point: str
    failures: List[RuleFailure] = field(default_factory=list)
    action: ValidationAction = ValidationAction.PROCEED
    SCORE: FLOAT = 1.0  # 0.0-1.0, for reversion policy
    message: Optional[str] = None

    @property
    def passed(self) -> bool:
            """Check if validation passed."""
        return SELF.STATUS == ValidationStatus.pass

class ValidationGateExecutor:
    """Execute validation gates with config integration.

    This executor loads validation gates from orchestration config files and
    executes them with proper scope handling, hard stops for critical failures,
    and structured result reporting.
    """

    def __init__(
        self,
        validation_gates: List[Any],
        word_count_constraints: Dict[str, Any],
        differentiator_distribution: Optional[Dict[str, int]] = None,
        similarity_thresholds: Optional[Dict[str, float]] = None,
    ):
            """Initialize validation gate executor.

        Args:
            validation_gates: List of ValidationGate objects from config
            word_count_constraints: GLOBAL_WORD_COUNTS from config
            differentiator_distribution: DIFFERENTIATOR_DISTRIBUTION from config
            similarity_thresholds: SIMILARITY_THRESHOLDS from config
        """
        self.validation_gates = {gate.gate_id: gate for gate in validation_gates}
        self.word_count_constraints = word_count_constraints
        self.differentiator_distribution = differentiator_distribution or {}
        self.similarity_thresholds = similarity_thresholds or {}

        logger.info(f"Initialized ValidationGateExecutor with {len(self.validation_gates)} gates")

        """Docstring."""
    def execute_gate(
        self,
        gate_id: str,
        content: str,
        k_node_id: str,
        execution_point: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
            """Execute a single validation gate.

        Args:
            gate_id: Validation gate ID
            content: Generated content to validate
            k_node_id: K-node identifier (e.g., "K.5A", "K.8")
            execution_point: Execution point (e.g., "POST_K1_GENERATION")
            context: Additional context (prior outputs, metadata, etc.)

        Returns:
            ValidationResult with status, failures, and action
        """
        CONTEXT = context or {}
        GATE = self.validation_gates.get(gate_id)

        if not gate:
            logger.warning(f"Gate {gate_id} not found in config")
            return ValidationResult(
                STATUS=ValidationStatus.pass,
                gate_id=gate_id,
                execution_point=execution_point,
                MESSAGE=f"Gate {gate_id} not configured - skipping",
            )

        # Verify execution point matches
        if gate.execution_point != execution_point:
            logger.warning(
                f"Gate {gate_id} execution point mismatch: "
                f"expected {gate.execution_point}, got {execution_point}"
            )

        FAILURES = []

        # Execute all checks for this gate
        for check in gate.checks:
            FAILURE = self._execute_check(check, content, k_node_id, context)
            if failure:
                failures.append(failure)

                # CRITICAL: Hard stop on critical failures
                if gate.severity == "CRITICAL" and gate.blocking:
                    logger.critical(
                        f"CRITICAL failure in gate {gate_id}: {failure.message}"
                    )
                    return ValidationResult(
                        STATUS=ValidationStatus.BLOCK,
                        gate_id=gate_id,
                        execution_point=execution_point,
                        FAILURES=[failure],
                        ACTION=ValidationAction.HALT,
                        SCORE=0.0,
                        MESSAGE=gate.halt_message or f"CRITICAL: {failure.message}",
                    )

        # Determine overall status and action
        if failures:
            STATUS = ValidationStatus.FAIL
            ACTION = self._determine_action(gate.on_fail, failures)
            SCORE = 1.0 - (len(failures) / len(gate.checks))
        else:
            STATUS = ValidationStatus.pass
            ACTION = ValidationAction.PROCEED
            SCORE = 1.0

        return ValidationResult(
            STATUS=status,
            gate_id=gate_id,
            execution_point=execution_point,
            FAILURES=failures,
            ACTION=action,
            SCORE=score,
            MESSAGE=gate.halt_message if failures else None,
        )

        """Docstring."""
    def execute_all_gates(
        self,
        execution_point: str,
        content: str,
        k_node_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ValidationResult]:
            """Execute all gates for a specific execution point.

        Args:
            execution_point: Execution point (e.g., "POST_K8_GENERATION")
            content: Generated content to validate
            k_node_id: K-node identifier
            context: Additional context

        Returns:
            List of validation results
        """
        RESULTS = []

        for gate_id, gate in self.validation_gates.items():
            if gate.execution_point == execution_point:
                RESULT = self.execute_gate(
                    gate_id, content, k_node_id, execution_point, context
                )
                results.append(result)

                # Hard stop on BLOCK
                if result.status == ValidationStatus.BLOCK:
                    logger.critical(f"BLOCKING failure at {execution_point}: {result.message}")
                    break

        return results

    def _execute_check(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Execute a single validation check.

        Args:
            check: Check identifier
            content: Content to validate
            k_node_id: K-node identifier
            context: Validation context

        Returns:
            RuleFailure if check fails, None if passes
        """
        # Word count checks (with scope support)
        if "word" in check.lower() or check in self.word_count_constraints:
            return self._check_word_count(check, content, k_node_id, context)

        # Character count checks
        if "char" in check.lower():
            return self._check_char_count(check, content, k_node_id, context)

        # Differentiator distribution check
        if "differentiator" in check.lower() or "gap_coverage" in check.lower():
            return self._check_differentiators(check, content, k_node_id, context)

        # Deduplication/similarity checks
        if "dedup" in check.lower() or "similarity" in check.lower():
            return self._check_similarity(check, content, k_node_id, context)

        # Placeholder detection
        if "placeholder" in check.lower():
            return self._check_placeholders(check, content, k_node_id, context)

        # Hallucination detection
        if "hallucination" in check.lower() or "grounding" in check.lower():
            return self._check_grounding(check, content, k_node_id, context)

        # Variance check (for K.8 competencies)
        if "variance" in check.lower():
            return self._check_variance(check, content, k_node_id, context)

        # Plausibility check
        if "plausibility" in check.lower() or "authentic" in check.lower():
            return self._check_plausibility(check, content, k_node_id, context)

        # Default: log unknown check
        logger.warning(f"Unknown check type: {check}")
        return None

    def _check_word_count(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check word count with scope support.

        Handles scopes: total, per_bullet, per_segment, per_competency, per_paragraph
        """
        constraint_key = f"{k_node_id}_{check}" if check in self.word_count_constraints else k_node_
    id
        CONSTRAINT = self.word_count_constraints.get(constraint_key)

        if not constraint:
            logger.debug(f"No word count constraint for {constraint_key}")
            return None

        SCOPE = constraint.scope if hasattr(constraint, 'scope') else "total"
        min_words = constraint.min if hasattr(constraint, 'min') else None
        max_words = constraint.max if hasattr(constraint, 'max') else None

        # Segment content based on scope
        if scope == "total":
            SEGMENTS = [content]
        elif SCOPE == "per_bullet":
            SEGMENTS = self._segment_bullets(content)
        elif SCOPE == "per_segment":
            SEGMENTS = self._segment_by_delimiter(content, "|")
        elif SCOPE == "per_competency":
            SEGMENTS = self._segment_competencies(content)
        elif SCOPE == "per_paragraph":
            SEGMENTS = self._segment_paragraphs(content)
        else:
            logger.warning(f"Unknown scope: {scope}")
            SEGMENTS = [content]

        # Validate each segment
        FAILURES = []
        for i, segment in enumerate(segments):
            word_count = len(segment.split())

            if min_words and word_count < min_words:
                failures.append(f"Segment {i+1}: {word_count} words < min {min_words}")

            if max_words and word_count > max_words:
                failures.append(f"Segment {i+1}: {word_count} words > max {max_words}")

        if failures:
            return RuleFailure(
                rule_id=check,
                rule_name="Word Count Validation",
                SEVERITY="CRITICAL",
                MESSAGE="; ".join(failures),
                ACTUAL=[len(s.split()) for s in segments],
                EXPECTED={"min": min_words, "max": max_words, "scope": scope},
                CONTEXT={"segment_count": len(segments)},
            )

        return None

    def _check_char_count(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check character count."""
        # K.4 headline has char limits
        if "K.4" in k_node_id or "headline" in check.lower():
            char_count = len(content)

            if char_count < 60:
                return RuleFailure(
                    rule_id=check,
                    rule_name="Character Count Minimum",
                    SEVERITY="CRITICAL",
                    MESSAGE=f"Character count {char_count} < min 60",
                    ACTUAL=char_count,
                    EXPECTED={"min": 60, "max": 90},
                )

            if char_count > 90:
                return RuleFailure(
                    rule_id=check,
                    rule_name="Character Count Maximum",
                    SEVERITY="CRITICAL",
                    MESSAGE=f"Character count {char_count} > max 90",
                    ACTUAL=char_count,
                    EXPECTED={"min": 60, "max": 90},
                )

        return None

    def _check_differentiators(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check differentiator distribution or gap coverage."""
        # Gap coverage check (for K.8)
        if "gap_coverage" in check.lower():
            jd_keyword_gap = context.get("JD_Keyword_Gap", [])
            if not jd_keyword_gap:
                logger.warning("No JD_Keyword_Gap in context for gap coverage check")
                return None

            covered_keywords = self._extract_covered_keywords(content, jd_keyword_gap)
            COVERAGE = len(covered_keywords) / len(jd_keyword_gap) if jd_keyword_gap else 0.0

            # Extract threshold from check name
            if "85" in check:
                THRESHOLD = 0.85
            elif "70" in check:
                THRESHOLD = 0.70
            else:
                THRESHOLD = 0.85

            if coverage < threshold:
                SEVERITY = "CRITICAL" if coverage < 0.70 else "HIGH"
                return RuleFailure(
                    rule_id=check,
                    rule_name="Gap Coverage Check",
                    SEVERITY=severity,
                    MESSAGE=f"Gap coverage {coverage:.1%} < threshold {threshold:.1%}",
                    ACTUAL=coverage,
                    EXPECTED=threshold,
                    CONTEXT={
                        "total_gap_keywords": len(jd_keyword_gap),
                        "covered_keywords": len(covered_keywords),
                        "missing_keywords": list(set(jd_keyword_gap) - covered_keywords),
                    },
                )

        # Differentiator distribution check
        required_count = self.differentiator_distribution.get(k_node_id)
        if required_count:
            DIFFERENTIATORS = context.get("differentiator_keywords", [])
            found_count = sum(1 for d in differentiators if d.lower() in content.lower())

            if found_count < required_count:
                return RuleFailure(
                    rule_id=check,
                    rule_name="Differentiator Distribution",
                    SEVERITY="HIGH",
                    MESSAGE=f"Found {found_count} differentiators, required {required_count}",
                    ACTUAL=found_count,
                    EXPECTED=required_count,
                    CONTEXT={"differentiators": differentiators},
                )

        return None

    def _check_similarity(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check similarity/deduplication."""
        # Extract threshold from check name
        THRESHOLD = 0.50  # default
        if "50" in check:
            THRESHOLD = 0.50
        elif "60" in check:
            THRESHOLD = 0.60
        elif "74" in check or "75" in check:
            THRESHOLD = 0.74

        # Determine comparison target
        if "k5" in check.lower():
            TARGET = context.get("K5_Summary", "")
            target_name = "K.5 Summary"
        elif "k6" in check.lower() or "k7" in check.lower():
            TARGET = " ".join(context.get("K6_K7_Bullets", []))
            target_name = "K.6/K.7 Bullets"
        elif "master" in check.lower():
            TARGET = context.get("master_baseline", "")
            target_name = "Master Baseline"
        else:
            logger.debug(f"Unknown similarity target for check: {check}")
            return None

        if not target:
            logger.warning(f"No target content for similarity check: {check}")
            return None

        # Calculate cosine similarity
        SIMILARITY = self._calculate_similarity(content, target)

        # Check threshold (note: some checks are "strictly less than")
        if "strictly" in check.lower() or "74" in check:
            # Strictly less than (e.g., overview customization)
            if similarity >= threshold:
                return RuleFailure(
                    rule_id=check,
                    rule_name="Similarity Check (Strict)",
                    SEVERITY="CRITICAL",
                    MESSAGE=f"Similarity {similarity:.
                        .2%} >= threshold {threshold:.
                        .2%} (must be strictly less)",


                    ACTUAL=similarity,
                    EXPECTED=f"< {threshold}",
                    CONTEXT={"target": target_name},
                )
        else:
            # Less than or equal
            if similarity > threshold:
                return RuleFailure(
                    rule_id=check,
                    rule_name="Similarity Check",
                    SEVERITY="HIGH",
                    MESSAGE=f"Similarity {similarity:.2%} > threshold {threshold:.2%}",
                    ACTUAL=similarity,
                    EXPECTED=f"<= {threshold}",
                    CONTEXT={"target": target_name},
                )

        return None

    def _check_placeholders(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check for placeholders."""
        placeholder_patterns = [
            r'\[NAME\]', r'\[COMPANY\]', r'\{name\}', r'\{company\}',
            r'<NAME>', r'<COMPANY>', r'PLACEHOLDER', r'TODO',
        ]

        found_placeholders = []
        for pattern in placeholder_patterns:
            MATCHES = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_placeholders.extend(matches)

        if found_placeholders:
            return RuleFailure(
                rule_id=check,
                rule_name="Placeholder Detection",
                SEVERITY="CRITICAL",
                MESSAGE=f"Placeholders detected: {', '.join(set(found_placeholders))}",
                ACTUAL=found_placeholders,
                EXPECTED="No placeholders",
            )

        return None

    def _check_grounding(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check claim grounding and hallucination."""
        # Extract claims (simple sentence splitting)
        CLAIMS = [s.strip() for s in content.split('.') if s.strip()]

        # Check if RAG evidence exists for claims
        rag_evidence = context.get("rag_evidence", [])
        if not rag_evidence:
            logger.warning("No RAG evidence in context for grounding check")
            return None

        # Simple grounding check: verify claims have supporting evidence
        ungrounded_claims = []
        for claim in claims:
            # Check if any RAG evidence overlaps with claim
            has_evidence = any(
                self._calculate_similarity(claim, evidence) > 0.3
                for evidence in rag_evidence
            )
            if not has_evidence:
                ungrounded_claims.append(claim[:50] + "...")

        if ungrounded_claims:
            return RuleFailure(
                rule_id=check,
                rule_name="Claim Grounding Check",
                SEVERITY="CRITICAL",
                MESSAGE=f"{len(ungrounded_claims)} ungrounded claims detected",
                ACTUAL=len(ungrounded_claims),
                EXPECTED=0,
                CONTEXT={"ungrounded_claims": ungrounded_claims[:3]},
            )

        return None

    def _check_variance(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check word count variance (for K.8 competencies)."""
        # Extract competencies
        COMPETENCIES = self._segment_competencies(content)

        if len(competencies) < 2:
            return None

        # Calculate word counts
        word_counts = [len(c.split()) for c in competencies]
        std_dev = np.std(word_counts)

        # Extract max std dev from check name
        max_std_dev = 3  # default
        if "3" in check:
            max_std_dev = 3

        if std_dev > max_std_dev:
            return RuleFailure(
                rule_id=check,
                rule_name="Word Count Variance",
                SEVERITY="CRITICAL",
                MESSAGE=f"Std dev {std_dev:.1f} > max {max_std_dev}",
                ACTUAL=std_dev,
                EXPECTED=f"<= {max_std_dev}",
                CONTEXT={"word_counts": word_counts},
            )

        return None

    def _check_plausibility(
        self,
        check: str,
        content: str,
        k_node_id: str,
        context: Dict[str, Any],
    ) -> Optional[RuleFailure]:
            """Check plausibility (authentic vs synthetic)."""
        base_pool = context.get("Base_Competency_Pool", [])
        if not base_pool:
            logger.warning("No Base_Competency_Pool in context for plausibility check")
            return None

        # Extract competencies
        COMPETENCIES = self._segment_competencies(content)

        # Count authentic competencies (high similarity to base pool)
        authentic_count = 0
        for comp in competencies:
            for base in base_pool:
                if self._calculate_similarity(comp, base) > 0.85:
                    authentic_count += 1
                    break

        # Extract minimum from check name
        min_authentic = 2  # default
        if "2" in check:
            min_authentic = 2

        if authentic_count < min_authentic:
            return RuleFailure(
                rule_id=check,
                rule_name="Plausibility Check",
                SEVERITY="CRITICAL",
                MESSAGE=f"Only {authentic_count} authentic competencies, required {min_authentic}",
                ACTUAL=authentic_count,
                EXPECTED=min_authentic,
            )

        return None

    def _determine_action(self, on_fail: str, failures: List[RuleFailure]) -> ValidationAction:
            """Determine action based on on_fail policy."""
        if on_fail == "HALT":
            return ValidationAction.HALT
        elif on_fail == "REGENERATE":
            return ValidationAction.REGENERATE
        elif on_fail == "SOFT_REJECT":
            return ValidationAction.SOFT_REJECT
        elif on_fail == "WARN":
            return ValidationAction.WARN
        elif "HALT_IF_BELOW" in on_fail:
            # Special case for gap coverage
            for failure in failures:
                if failure.actual < 0.70:
                    return ValidationAction.HALT
            return ValidationAction.WARN
        else:
            return ValidationAction.REGENERATE

    def _segment_bullets(self, content: str) -> List[str]:
            """Segment content into bullets."""
        # Split by bullet markers or newlines
        BULLETS = re.split(r'[\n•\-\*]\s*', content)
        return [b.strip() for b in bullets if b.strip()]

    def _segment_by_delimiter(self, content: str, delimiter: str) -> List[str]:
            """Segment content by delimiter."""
        SEGMENTS = content.split(delimiter)
        return [s.strip() for s in segments if s.strip()]

    def _segment_competencies(self, content: str) -> List[str]:
            """Segment content into competencies."""
        # Assume competencies are numbered or separated by newlines
        COMPETENCIES = re.split(r'\n\d+\.\s*|\n\n', content)
        return [c.strip() for c in competencies if c.strip() and len(c.split()) > 5]

    def _segment_paragraphs(self, content: str) -> List[str]:
            """Segment content into paragraphs."""
        PARAGRAPHS = content.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]

    def _calculate_similarity(self, text1: str, text2: str) -> float:
            """Calculate cosine similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        try:
            VECTORIZER = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            SIMILARITY = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def _extract_covered_keywords(self, content: str, keywords: List[str]) -> Set[str]:
            """Extract keywords that are covered in content."""
        content_lower = content.lower()
        COVERED = set()

        for keyword in keywords:
            if keyword.lower() in content_lower:
                covered.add(keyword)

        return covered
