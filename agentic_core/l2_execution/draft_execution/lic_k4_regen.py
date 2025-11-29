"""K4 Regeneration Executor - Fourth hop in the sequential K1-K7 execution pipeline.

Incorporated from L2 lic_k4_regen.py to refine and improve K3 drafts based on
quality metrics, constraint validation, and confidence thresholds before
passing to K5 validation.

This is the fourth execution phase in the hop-based architecture that follows:
L1 Planning → K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class RegenViolation:
    """Individual violation found during draft analysis."""
    violation_type: str                   # "forbidden_pattern", "filler_content", "placeholder", "confidence_threshold"
    description: str
    severity: str                         # "low", "medium", "high"
    section_affected: Optional[str] = None
    suggested_fix: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegenOutput:
    """Output from K4 regeneration execution phase."""
    regenerated_draft: Dict[str, Any]
    regeneration_count: int
    final_confidence: float
    regeneration_reasons: List[str]
    violations_found: List[RegenViolation]
    violations_fixed: List[RegenViolation]
    improvement_score: float
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


class K4RegenExecutor:
    """K4 regeneration executor - fourth hop in sequential execution pipeline.
    
    Refines and improves K3 drafts based on quality metrics, constraint validation,
    and confidence thresholds before passing to K5 validation.
    """
    
    def __init__(self, 
                 validator_plan: Optional[Dict[str, Any]] = None,
                 constraint_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K4 regeneration executor."""
        self.validator_plan = validator_plan or {}
        self.constraint_plan = constraint_plan or {}
        self.telemetry_bus = telemetry_bus
        self.max_retries = 3
        
        # Default constraint configurations
        self.default_constraints = {
            "forbidden_verbs": ["think", "feel", "believe", "guess", "suppose"],
            "filler_patterns": [
                r"\bas far as I know\b",
                r"\bI think that\b",
                r"\bit seems like\b",
                r"\bkind of\b",
                r"\bsort of\b",
                r"\bas you may know\b"
            ],
            "placeholder_patterns": [
                r"\[.*?\]",
                r"\{.*?\}",
                r"<.*?>",
                r"XXX.*XXX"
            ],
            "max_word_count": {
                "subject": 10,
                "hook": 30,
                "value": 100,
                "cta": 20,
                "signature": 10
            }
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            "per_claim_min": 0.6,
            "aggregate_min": 0.7,
            "section_min": 0.5
        }
        
        # Regeneration strategies
        self.regen_strategies = {
            "forbidden_pattern": "replace_with_alternative",
            "filler_content": "remove_filler",
            "placeholder": "fill_with_content",
            "confidence_threshold": "strengthen_claims",
            "word_count_violation": "condense_content"
        }
    
    def execute(
        self,
        *,
        draft_output: Any,
        insights_output: Any,
        persona_plan: Optional[Any] = None,
        message_plan: Optional[Any] = None,
        outreach_context: Dict[str, Any] = None,
    ) -> RegenOutput:
        """Execute K4 regeneration phase.
        
        Args:
            draft_output: Output from K3 draft execution
            insights_output: Output from K2 insights execution
            persona_plan: Optional persona plan for tone guidance
            message_plan: Optional message plan for constraints
            outreach_context: Additional context for regeneration
            
        Returns:
            Regenerated draft with improvements and validation results
        """
        outreach_context = outreach_context or {}
        
        # 1. Analyze current draft for violations
        violations = self._analyze_draft(draft_output, insights_output, message_plan)
        
        # 2. Determine if regeneration is needed
        needs_regen = self._should_regenerate(violations, draft_output)
        
        if not needs_regen:
            return self._create_no_regen_output(draft_output, violations)
        
        # 3. Apply regeneration strategies
        regenerated_draft, fixed_violations = self._regenerate_draft(
            draft_output, violations, persona_plan, message_plan
        )
        
        # 4. Calculate improvement metrics
        improvement_score = self._calculate_improvement_score(draft_output, regenerated_draft, violations, fixed_violations)
        
        # 5. Calculate final confidence
        final_confidence = self._calculate_final_confidence(regenerated_draft, insights_output)
        
        # 6. Build execution metadata
        execution_metadata = {
            "original_violations": len(violations),
            "violations_fixed": len(fixed_violations),
            "regeneration_applied": True,
            "strategies_used": list(set(v.violation_type for v in fixed_violations)),
            "improvement_score": improvement_score
        }
        
        # 7. Create regeneration output
        output = RegenOutput(
            regenerated_draft=regenerated_draft,
            regeneration_count=1,
            final_confidence=final_confidence,
            regeneration_reasons=[v.description for v in violations],
            violations_found=violations,
            violations_fixed=fixed_violations,
            improvement_score=improvement_score,
            execution_metadata=execution_metadata
        )
        
        # 8. Record telemetry (best-effort)
        self._safe_record_telemetry(output)
        
        return output
    
    def _analyze_draft(self, draft_output: Any, insights_output: Any, message_plan: Optional[Any]) -> List[RegenViolation]:
        """Analyze draft for quality violations and issues."""
        violations = []
        
        # Check forbidden patterns in all sections
        if hasattr(draft_output, 'sections'):
            for section_name, section in draft_output.sections.items():
                section_violations = self._check_forbidden_patterns(section.content, section_name)
                violations.extend(section_violations)
        
        # Check filler content
        if hasattr(draft_output, 'sections'):
            for section_name, section in draft_output.sections.items():
                filler_violations = self._check_filler_content(section.content, section_name)
                violations.extend(filler_violations)
        
        # Check placeholder patterns
        if hasattr(draft_output, 'sections'):
            for section_name, section in draft_output.sections.items():
                placeholder_violations = self._check_placeholder_patterns(section.content, section_name)
                violations.extend(placeholder_violations)
        
        # Check confidence thresholds
        confidence_violations = self._check_confidence_thresholds(insights_output)
        violations.extend(confidence_violations)
        
        # Check word count constraints
        if hasattr(draft_output, 'sections'):
            word_count_violations = self._check_word_count_constraints(draft_output.sections, message_plan)
            violations.extend(word_count_violations)
        
        # Check message plan constraints
        if message_plan and hasattr(draft_output, 'sections'):
            constraint_violations = self._check_message_constraints(draft_output.sections, message_plan)
            violations.extend(constraint_violations)
        
        return violations
    
    def _check_forbidden_patterns(self, text: str, section_name: str) -> List[RegenViolation]:
        """Check for forbidden verbs and patterns in text."""
        violations = []
        forbidden_verbs = self.constraint_plan.get("forbidden_verbs", self.default_constraints["forbidden_verbs"])
        
        for verb in forbidden_verbs:
            if verb.lower() in text.lower():
                violation = RegenViolation(
                    violation_type="forbidden_pattern",
                    description=f"Forbidden verb detected: {verb}",
                    severity="medium",
                    section_affected=section_name,
                    suggested_fix=f"Replace '{verb}' with more confident language",
                    metadata={"forbidden_verb": verb}
                )
                violations.append(violation)
        
        return violations
    
    def _check_filler_content(self, text: str, section_name: str) -> List[RegenViolation]:
        """Check for filler words and phrases."""
        violations = []
        filler_patterns = self.constraint_plan.get("filler_patterns", self.default_constraints["filler_patterns"])
        
        for pattern in filler_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violation = RegenViolation(
                    violation_type="filler_content",
                    description=f"Filler pattern detected: {pattern}",
                    severity="low",
                    section_affected=section_name,
                    suggested_fix="Remove filler phrase for more direct communication",
                    metadata={"filler_pattern": pattern}
                )
                violations.append(violation)
        
        return violations
    
    def _check_placeholder_patterns(self, text: str, section_name: str) -> List[RegenViolation]:
        """Check for placeholder content that needs to be filled."""
        violations = []
        placeholder_patterns = self.constraint_plan.get("placeholder_patterns", self.default_constraints["placeholder_patterns"])
        
        for pattern in placeholder_patterns:
            if re.search(pattern, text):
                violation = RegenViolation(
                    violation_type="placeholder",
                    description=f"Placeholder pattern detected: {pattern}",
                    severity="high",
                    section_affected=section_name,
                    suggested_fix="Replace placeholder with actual content",
                    metadata={"placeholder_pattern": pattern}
                )
                violations.append(violation)
        
        return violations
    
    def _check_confidence_thresholds(self, insights_output: Any) -> List[RegenViolation]:
        """Check if confidence scores meet minimum thresholds."""
        violations = []
        
        if not insights_output:
            return violations
        
        # Check per-claim confidence
        if hasattr(insights_output, 'per_claim_scores'):
            per_claim_min = self.confidence_thresholds["per_claim_min"]
            for claim_score in insights_output.per_claim_scores:
                if hasattr(claim_score, 'confidence_score'):
                    score = claim_score.confidence_score
                    if score < per_claim_min:
                        violation = RegenViolation(
                            violation_type="confidence_threshold",
                            description=f"Per-claim confidence below threshold: {score:.3f}",
                            severity="medium",
                            suggested_fix="Strengthen claim with more evidence",
                            metadata={"claim_score": score, "threshold": per_claim_min}
                        )
                        violations.append(violation)
        
        # Check aggregate confidence
        if hasattr(insights_output, 'aggregate_confidence'):
            aggregate_min = self.confidence_thresholds["aggregate_min"]
            aggregate_confidence = insights_output.aggregate_confidence
            if aggregate_confidence < aggregate_min:
                violation = RegenViolation(
                    violation_type="confidence_threshold",
                    description=f"Aggregate confidence below threshold: {aggregate_confidence:.3f}",
                    severity="high",
                    suggested_fix="Improve overall evidence quality",
                    metadata={"aggregate_confidence": aggregate_confidence, "threshold": aggregate_min}
                )
                violations.append(violation)
        
        return violations
    
    def _check_word_count_constraints(self, sections: Dict[str, Any], message_plan: Optional[Any]) -> List[RegenViolation]:
        """Check if sections violate word count constraints."""
        violations = []
        max_word_counts = self.default_constraints["max_word_count"]
        
        # Override with message plan constraints if available
        if message_plan and hasattr(message_plan, 'sections'):
            for section_name, section_plan in message_plan.sections.items():
                if hasattr(section_plan, 'max_length'):
                    # Convert character limit to approximate word count
                    max_word_counts[section_name] = section_plan.max_length // 6  # ~6 chars per word
        
        for section_name, section in sections.items():
            if hasattr(section, 'word_count') and section_name in max_word_counts:
                max_words = max_word_counts[section_name]
                actual_words = section.word_count
                
                if actual_words > max_words:
                    violation = RegenViolation(
                        violation_type="word_count_violation",
                        description=f"Section '{section_name}' exceeds word count: {actual_words} > {max_words}",
                        severity="medium",
                        section_affected=section_name,
                        suggested_fix=f"Condense {section_name} section to {max_words} words or fewer",
                        metadata={"actual_words": actual_words, "max_words": max_words}
                    )
                    violations.append(violation)
        
        return violations
    
    def _check_message_constraints(self, sections: Dict[str, Any], message_plan: Any) -> List[RegenViolation]:
        """Check message plan specific constraints."""
        violations = []
        
        if not hasattr(message_plan, 'constraints'):
            return violations
        
        constraints = message_plan.constraints
        
        # Check specific constraint violations
        for constraint in constraints:
            if constraint == "brevity_required":
                # Check if message is too long
                total_words = sum(section.word_count for section in sections.values())
                if total_words > 150:
                    violation = RegenViolation(
                        violation_type="constraint_violation",
                        description="Brevity constraint violated: message too long",
                        severity="medium",
                        suggested_fix="Reduce overall message length",
                        metadata={"total_words": total_words, "constraint": constraint}
                    )
                    violations.append(violation)
            
            elif constraint == "no_buzzwords":
                # Check for buzzwords in value section
                if "value" in sections:
                    buzzwords = ["synergy", "paradigm", "leverage", "optimize", "streamline"]
                    content = sections["value"].content.lower()
                    for buzzword in buzzwords:
                        if buzzword in content:
                            violation = RegenViolation(
                                violation_type="constraint_violation",
                                description=f"Buzzword detected: {buzzword}",
                                severity="low",
                                section_affected="value",
                                suggested_fix=f"Replace '{buzzword}' with specific language",
                                metadata={"buzzword": buzzword, "constraint": constraint}
                            )
                            violations.append(violation)
        
        return violations
    
    def _should_regenerate(self, violations: List[RegenViolation], draft_output: Any) -> bool:
        """Determine if draft needs regeneration based on violations."""
        if not violations:
            return False
        
        # Check for high severity violations
        high_severity = any(v.severity == "high" for v in violations)
        if high_severity:
            return True
        
        # Check for multiple medium severity violations
        medium_count = sum(1 for v in violations if v.severity == "medium")
        if medium_count >= 3:
            return True
        
        # Check if overall confidence is too low
        if hasattr(draft_output, 'confidence_score') and draft_output.confidence_score < 0.6:
            return True
        
        # Check for placeholder violations (always regenerate)
        placeholder_violations = [v for v in violations if v.violation_type == "placeholder"]
        if placeholder_violations:
            return True
        
        return False
    
    def _regenerate_draft(self, draft_output: Any, violations: List[RegenViolation], persona_plan: Optional[Any], message_plan: Optional[Any]) -> tuple[Dict[str, Any], List[RegenViolation]]:
        """Apply regeneration strategies to fix violations."""
        regenerated_sections = {}
        fixed_violations = []
        
        # Start with original sections
        if hasattr(draft_output, 'sections'):
            regenerated_sections = draft_output.sections.copy()
        
        # Apply fixes for each violation
        for violation in violations:
            if violation.section_affected and violation.section_affected in regenerated_sections:
                section = regenerated_sections[violation.section_affected]
                fixed_content = self._apply_fix_strategy(section.content, violation, persona_plan)
                
                if fixed_content != section.content:
                    # Create updated section
                    updated_section = type(section)(
                        section_type=section.section_type,
                        content=fixed_content,
                        word_count=len(fixed_content.split()),
                        tone_applied=section.tone_applied,
                        temperature_used=section.temperature_used,
                        sources_used=section.sources_used,
                        confidence_score=section.confidence_score + 0.1,  # Boost confidence after fix
                        metadata=section.metadata.copy()
                    )
                    regenerated_sections[violation.section_affected] = updated_section
                    fixed_violations.append(violation)
        
        # Create regenerated draft
        regenerated_draft = {
            "sections": regenerated_sections,
            "regeneration_applied": True,
            "original_confidence": getattr(draft_output, 'confidence_score', 0.0)
        }
        
        return regenerated_draft, fixed_violations
    
    def _apply_fix_strategy(self, content: str, violation: RegenViolation, persona_plan: Optional[Any]) -> str:
        """Apply specific fix strategy based on violation type."""
        strategy = self.regen_strategies.get(violation.violation_type, "general_improvement")
        
        if strategy == "replace_with_alternative":
            return self._replace_forbidden_patterns(content, violation)
        elif strategy == "remove_filler":
            return self._remove_filler_content(content, violation)
        elif strategy == "fill_with_content":
            return self._fill_placeholders(content, violation)
        elif strategy == "strengthen_claims":
            return self._strengthen_claims(content, violation)
        elif strategy == "condense_content":
            return self._condense_content(content, violation)
        else:
            return self._general_improvement(content, violation, persona_plan)
    
    def _replace_forbidden_patterns(self, content: str, violation: RegenViolation) -> str:
        """Replace forbidden verbs with confident alternatives."""
        forbidden_verb = violation.metadata.get("forbidden_verb", "")
        alternatives = {
            "think": "believe",
            "feel": "consider",
            "believe": "am confident",
            "guess": "estimate",
            "suppose": "expect"
        }
        
        replacement = alternatives.get(forbidden_verb, "demonstrate")
        return content.replace(forbidden_verb, replacement)
    
    def _remove_filler_content(self, content: str, violation: RegenViolation) -> str:
        """Remove filler phrases from content."""
        filler_pattern = violation.metadata.get("filler_pattern", "")
        return re.sub(filler_pattern, "", content, flags=re.IGNORECASE).strip()
    
    def _fill_placeholders(self, content: str, violation: RegenViolation) -> str:
        """Replace placeholders with generic content."""
        placeholder_pattern = violation.metadata.get("placeholder_pattern", "")
        # Replace with generic but professional content
        return re.sub(placeholder_pattern, "relevant information", content)
    
    def _strengthen_claims(self, content: str, violation: RegenViolation) -> str:
        """Strengthen claims with more confident language."""
        # Add confidence-boosting phrases
        strengthened = content.replace("might help", "will help")
        strengthened = strengthened.replace("could improve", "improves")
        strengthened = strengthened.replace("may result in", "results in")
        return strengthened
    
    def _condense_content(self, content: str, violation: RegenViolation) -> str:
        """Condense content to meet word count constraints."""
        sentences = content.split(". ")
        max_sentences = max(1, len(sentences) - 1)  # Remove at least one sentence
        return ". ".join(sentences[:max_sentences])
    
    def _general_improvement(self, content: str, violation: RegenViolation, persona_plan: Optional[Any]) -> str:
        """Apply general improvement based on persona and violation."""
        # Apply persona-aware improvements
        if persona_plan and hasattr(persona_plan, 'communication_style'):
            if persona_plan.communication_style == "formal":
                content = content.replace("Hi", "Dear")
                content = content.replace("Thanks", "Thank you")
            elif persona_plan.communication_style == "concise":
                # Remove redundant words
                content = re.sub(r'\b(very|really|quite)\s+', '', content)
        
        return content.strip()
    
    def _calculate_improvement_score(self, original_draft: Any, regenerated_draft: Dict[str, Any], violations: List[RegenViolation], fixed_violations: List[RegenViolation]) -> float:
        """Calculate improvement score from regeneration."""
        if not violations:
            return 0.0
        
        # Base improvement from fixed violations
        violations_fixed_ratio = len(fixed_violations) / len(violations)
        
        # Severity weighting
        severity_weights = {"high": 1.0, "medium": 0.7, "low": 0.3}
        weighted_improvement = sum(severity_weights.get(v.severity, 0.5) for v in fixed_violations)
        max_possible = sum(severity_weights.get(v.severity, 0.5) for v in violations)
        
        if max_possible > 0:
            severity_improvement = weighted_improvement / max_possible
        else:
            severity_improvement = 0.0
        
        # Combine metrics
        overall_improvement = (violations_fixed_ratio * 0.6) + (severity_improvement * 0.4)
        return round(overall_improvement, 3)
    
    def _calculate_final_confidence(self, regenerated_draft: Dict[str, Any], insights_output: Any) -> float:
        """Calculate final confidence score after regeneration."""
        base_confidence = 0.6
        
        # Boost from regeneration
        if regenerated_draft.get("regeneration_applied"):
            base_confidence += 0.1
        
        # Include insights confidence if available
        if insights_output and hasattr(insights_output, 'aggregate_confidence'):
            base_confidence += insights_output.aggregate_confidence * 0.3
        
        return round(min(base_confidence, 1.0), 3)
    
    def _create_no_regen_output(self, draft_output: Any, violations: List[RegenViolation]) -> RegenOutput:
        """Create output when no regeneration is needed."""
        return RegenOutput(
            regenerated_draft={"sections": getattr(draft_output, 'sections', {})},
            regeneration_count=0,
            final_confidence=getattr(draft_output, 'confidence_score', 0.0),
            regeneration_reasons=[],
            violations_found=violations,
            violations_fixed=[],
            improvement_score=0.0,
            execution_metadata={"regeneration_applied": False}
        )
    
    def _safe_record_telemetry(self, output: RegenOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("k4_regen_executed", {
                    "regeneration_count": output.regeneration_count,
                    "violations_found": len(output.violations_found),
                    "violations_fixed": len(output.violations_fixed),
                    "improvement_score": output.improvement_score,
                    "final_confidence": output.final_confidence
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_regen_summary(self, output: RegenOutput) -> Dict[str, Any]:
        """Get a summary of the regeneration execution for debugging/telemetry."""
        return {
            "execution_id": "k4_regen",
            "regeneration_count": output.regeneration_count,
            "violations_found": len(output.violations_found),
            "violations_fixed": len(output.violations_fixed),
            "improvement_score": output.improvement_score,
            "final_confidence": output.final_confidence,
            "violation_types": list(set(v.violation_type for v in output.violations_found)),
            "strategies_used": output.execution_metadata.get("strategies_used", [])
        }
