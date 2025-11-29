"""K5 Validation Executor - Fifth hop in the sequential K1-K7 execution pipeline.

Incorporated from L2 lic_k5_validation.py to perform final quality validation
and compliance checking on regenerated drafts before passing to K6 CTA optimization.

This is the fifth execution phase in the hop-based architecture that follows:
L1 Planning → K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ValidationViolation:
    """Individual validation violation with severity and impact."""
    error_code: str                      # "LIC-E001", "LIC-W001", etc.
    violation_type: str                  # "ascii_hygiene", "content_cleanliness", "compliance", "quality"
    description: str
    severity: str                        # "blocker", "warning", "info"
    section_affected: Optional[str] = None
    fix_suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationOutput:
    """Output from K5 validation execution phase."""
    is_valid: bool
    error_codes: List[str]
    validation_results: Dict[str, Any]
    blocked_violations: List[str]
    warning_violations: List[str]
    info_violations: List[str]
    all_violations: List[ValidationViolation]
    quality_score: float
    compliance_score: float
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


class K5ValidationExecutor:
    """K5 validation executor - fifth hop in sequential execution pipeline.
    
    Performs final quality validation and compliance checking on regenerated
    drafts before passing to K6 CTA optimization.
    """
    
    def __init__(self, 
                 validator_plan: Optional[Dict[str, Any]] = None,
                 constraint_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K5 validation executor."""
        self.validator_plan = validator_plan or {}
        self.constraint_plan = constraint_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Default validation configurations
        self.default_constraints = {
            "ascii_rules": {
                "no_smart_quotes": True,
                "no_em_dashes": True,
                "no_unicode_bullets": True,
                "no_special_characters": True
            },
            "forbidden_verbs": ["think", "feel", "believe", "guess", "suppose", "wonder"],
            "filler_patterns": [
                r"\bas far as I know\b",
                r"\bI think that\b",
                r"\bit seems like\b",
                r"\bkind of\b",
                r"\bsort of\b",
                r"\bas you may know\b",
                r"\bbasically\b",
                r"\bactually\b"
            ],
            "content_rules": {
                "max_sentence_length": 25,
                "min_word_count": 50,
                "max_word_count": 200,
                "required_sections": ["greeting", "value", "cta", "signature"]
            },
            "compliance_rules": {
                "no_personal_data": True,
                "no_misleading_claims": True,
                "no_spam_indicators": True,
                "professional_tone_required": True
            }
        }
        
        # Error code mappings
        self.error_codes = {
            "ascii_hygiene": "LIC-E007",
            "content_cleanliness": "LIC-E008",
            "filler_content": "LIC-E009",
            "length_violation": "LIC-E010",
            "missing_section": "LIC-E011",
            "compliance_violation": "LIC-E012",
            "quality_issue": "LIC-W001"
        }
    
    def execute(
        self,
        *,
        regen_output: Any,
        persona_plan: Optional[Any] = None,
        message_plan: Optional[Any] = None,
        outreach_context: Dict[str, Any] = None,
    ) -> ValidationOutput:
        """Execute K5 validation phase.
        
        Args:
            regen_output: Output from K4 regeneration execution
            persona_plan: Optional persona plan for validation context
            message_plan: Optional message plan for constraint validation
            outreach_context: Additional context for validation
            
        Returns:
            Complete validation results with violations and scores
        """
        outreach_context = outreach_context or {}
        
        # 1. Extract draft content from regeneration output
        draft_content = self._extract_draft_content(regen_output)
        
        # 2. Perform ASCII hygiene validation
        ascii_violations = self._validate_ascii_hygiene(draft_content)
        
        # 3. Perform content cleanliness validation
        content_violations = self._validate_content_cleanliness(draft_content)
        
        # 4. Perform structural validation
        structural_violations = self._validate_structure(draft_content, message_plan)
        
        # 5. Perform compliance validation
        compliance_violations = self._validate_compliance(draft_content, persona_plan)
        
        # 6. Perform quality validation
        quality_violations = self._validate_quality(draft_content, regen_output)
        
        # 7. Aggregate all violations
        all_violations = ascii_violations + content_violations + structural_violations + compliance_violations + quality_violations
        
        # 8. Categorize violations by severity
        blocked_violations = [v.description for v in all_violations if v.severity == "blocker"]
        warning_violations = [v.description for v in all_violations if v.severity == "warning"]
        info_violations = [v.description for v in all_violations if v.severity == "info"]
        
        # 9. Determine overall validity
        is_valid = len(blocked_violations) == 0
        
        # 10. Calculate scores
        quality_score = self._calculate_quality_score(all_violations, draft_content)
        compliance_score = self._calculate_compliance_score(all_violations)
        
        # 11. Build validation results
        validation_results = {
            "total_violations": len(all_violations),
            "blocker_count": len(blocked_violations),
            "warning_count": len(warning_violations),
            "info_count": len(info_violations),
            "quality_score": quality_score,
            "compliance_score": compliance_score,
            "validation_timestamp": "2024-01-01T00:00:00Z"
        }
        
        # 12. Build execution metadata
        execution_metadata = {
            "draft_sections_validated": len(draft_content.get("sections", {})),
            "validation_categories": list(set(v.violation_type for v in all_violations)),
            "persona_plan_used": persona_plan is not None,
            "message_plan_used": message_plan is not None
        }
        
        # 13. Create validation output
        output = ValidationOutput(
            is_valid=is_valid,
            error_codes=[v.error_code for v in all_violations],
            validation_results=validation_results,
            blocked_violations=blocked_violations,
            warning_violations=warning_violations,
            info_violations=info_violations,
            all_violations=all_violations,
            quality_score=quality_score,
            compliance_score=compliance_score,
            execution_metadata=execution_metadata
        )
        
        # 14. Record telemetry (best-effort)
        self._safe_record_telemetry(output)
        
        return output
    
    def _extract_draft_content(self, regen_output: Any) -> Dict[str, Any]:
        """Extract draft content from regeneration output."""
        if hasattr(regen_output, 'regenerated_draft'):
            return regen_output.regenerated_draft
        elif isinstance(regen_output, dict):
            return regen_output.get("regenerated_draft", {})
        else:
            return {}
    
    def _validate_ascii_hygiene(self, draft_content: Dict[str, Any]) -> List[ValidationViolation]:
        """Validate ASCII character compliance."""
        violations = []
        ascii_rules = self.constraint_plan.get("ascii_rules", self.default_constraints["ascii_rules"])
        
        # Check all sections for ASCII violations
        for section_name, section in draft_content.get("sections", {}).items():
            content = getattr(section, 'content', '') if hasattr(section, 'content') else str(section)
            
            # Check for smart quotes
            if ascii_rules.get("no_smart_quotes", True):
                if "'" in content or '"' in content:
                    violation = ValidationViolation(
                        error_code=self.error_codes["ascii_hygiene"],
                        violation_type="ascii_hygiene",
                        description="Non-ASCII characters detected - smart quotes",
                        severity="warning",
                        section_affected=section_name,
                        fix_suggestion="Replace smart quotes with standard quotes",
                        metadata={"characters_found": ["'", '"']}
                    )
                    violations.append(violation)
            
            # Check for em dashes
            if ascii_rules.get("no_em_dashes", True):
                if "—" in content:
                    violation = ValidationViolation(
                        error_code=self.error_codes["ascii_hygiene"],
                        violation_type="ascii_hygiene",
                        description="Non-ASCII characters detected - em dashes",
                        severity="warning",
                        section_affected=section_name,
                        fix_suggestion="Replace em dash with standard hyphen",
                        metadata={"characters_found": ["—"]}
                    )
                    violations.append(violation)
            
            # Check for unicode bullets
            if ascii_rules.get("no_unicode_bullets", True):
                if "•" in content or "○" in content:
                    violation = ValidationViolation(
                        error_code=self.error_codes["ascii_hygiene"],
                        violation_type="ascii_hygiene",
                        description="Non-ASCII characters detected - unicode bullets",
                        severity="warning",
                        section_affected=section_name,
                        fix_suggestion="Replace unicode bullets with standard dashes",
                        metadata={"characters_found": ["•", "○"]}
                    )
                    violations.append(violation)
        
        return violations
    
    def _validate_content_cleanliness(self, draft_content: Dict[str, Any]) -> List[ValidationViolation]:
        """Validate content for forbidden patterns and filler words."""
        violations = []
        forbidden_verbs = self.constraint_plan.get("forbidden_verbs", self.default_constraints["forbidden_verbs"])
        filler_patterns = self.constraint_plan.get("filler_patterns", self.default_constraints["filler_patterns"])
        
        # Check all sections
        for section_name, section in draft_content.get("sections", {}).items():
            content = getattr(section, 'content', '') if hasattr(section, 'content') else str(section)
            
            # Check for forbidden verbs
            for verb in forbidden_verbs:
                if verb.lower() in content.lower():
                    violation = ValidationViolation(
                        error_code=self.error_codes["content_cleanliness"],
                        violation_type="content_cleanliness",
                        description=f"Forbidden corporate verb detected - {verb}",
                        severity="warning",
                        section_affected=section_name,
                        fix_suggestion=f"Replace '{verb}' with more confident language",
                        metadata={"forbidden_verb": verb}
                    )
                    violations.append(violation)
            
            # Check for filler patterns
            for pattern in filler_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violation = ValidationViolation(
                        error_code=self.error_codes["filler_content"],
                        violation_type="content_cleanliness",
                        description=f"Weak filler phrase detected - {pattern}",
                        severity="warning",
                        section_affected=section_name,
                        fix_suggestion="Remove filler phrase for more direct communication",
                        metadata={"filler_pattern": pattern}
                    )
                    violations.append(violation)
        
        return violations
    
    def _validate_structure(self, draft_content: Dict[str, Any], message_plan: Optional[Any]) -> List[ValidationViolation]:
        """Validate message structure and required sections."""
        violations = []
        content_rules = self.constraint_plan.get("content_rules", self.default_constraints["content_rules"])
        
        sections = draft_content.get("sections", {})
        
        # Check for required sections
        required_sections = content_rules.get("required_sections", [])
        for required_section in required_sections:
            if required_section not in sections:
                violation = ValidationViolation(
                    error_code=self.error_codes["missing_section"],
                    violation_type="structural",
                    description=f"Required section missing - {required_section}",
                    severity="blocker",
                    section_affected=required_section,
                    fix_suggestion=f"Add {required_section} section to message",
                    metadata={"missing_section": required_section}
                )
                violations.append(violation)
        
        # Check word count constraints
        total_word_count = 0
        for section_name, section in sections.items():
            word_count = getattr(section, 'word_count', 0) if hasattr(section, 'word_count') else len(str(section).split())
            total_word_count += word_count
        
        min_words = content_rules.get("min_word_count", 50)
        max_words = content_rules.get("max_word_count", 200)
        
        if total_word_count < min_words:
            violation = ValidationViolation(
                error_code=self.error_codes["length_violation"],
                violation_type="structural",
                description=f"Message too short - {total_word_count} words (minimum: {min_words})",
                severity="blocker",
                fix_suggestion=f"Expand message to at least {min_words} words",
                metadata={"actual_words": total_word_count, "min_words": min_words}
            )
            violations.append(violation)
        elif total_word_count > max_words:
            violation = ValidationViolation(
                error_code=self.error_codes["length_violation"],
                violation_type="structural",
                description=f"Message too long - {total_word_count} words (maximum: {max_words})",
                severity="warning",
                fix_suggestion=f"Condense message to {max_words} words or fewer",
                metadata={"actual_words": total_word_count, "max_words": max_words}
            )
            violations.append(violation)
        
        # Check sentence length
        max_sentence_length = content_rules.get("max_sentence_length", 25)
        for section_name, section in sections.items():
            content = getattr(section, 'content', '') if hasattr(section, 'content') else str(section)
            sentences = content.split('. ')
            
            for i, sentence in enumerate(sentences):
                word_count = len(sentence.split())
                if word_count > max_sentence_length:
                    violation = ValidationViolation(
                        error_code=self.error_codes["length_violation"],
                        violation_type="structural",
                        description=f"Sentence too long in {section_name} - {word_count} words",
                        severity="info",
                        section_affected=section_name,
                        fix_suggestion="Break long sentence into shorter ones",
                        metadata={"sentence_index": i, "word_count": word_count}
                    )
                    violations.append(violation)
        
        return violations
    
    def _validate_compliance(self, draft_content: Dict[str, Any], persona_plan: Optional[Any]) -> List[ValidationViolation]:
        """Validate compliance with professional and ethical standards."""
        violations = []
        compliance_rules = self.constraint_plan.get("compliance_rules", self.default_constraints["compliance_rules"])
        
        # Combine all content for compliance checks
        all_content = ""
        for section in draft_content.get("sections", {}).values():
            content = getattr(section, 'content', '') if hasattr(section, 'content') else str(section)
            all_content += content + " "
        
        # Check for personal data indicators
        if compliance_rules.get("no_personal_data", True):
            personal_patterns = [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
                r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card pattern
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email pattern
            ]
            
            for pattern in personal_patterns:
                if re.search(pattern, all_content):
                    violation = ValidationViolation(
                        error_code=self.error_codes["compliance_violation"],
                        violation_type="compliance",
                        description="Personal data detected in message",
                        severity="blocker",
                        fix_suggestion="Remove personal data from message content",
                        metadata={"pattern_matched": pattern}
                    )
                    violations.append(violation)
        
        # Check for spam indicators
        if compliance_rules.get("no_spam_indicators", True):
            spam_indicators = [
                "click here", "free money", "guaranteed", "act now", 
                "limited time", "urgent", "congratulations", "winner"
            ]
            
            for indicator in spam_indicators:
                if indicator.lower() in all_content.lower():
                    violation = ValidationViolation(
                        error_code=self.error_codes["compliance_violation"],
                        violation_type="compliance",
                        description=f"Spam indicator detected - {indicator}",
                        severity="blocker",
                        fix_suggestion=f"Remove spam indicator '{indicator}'",
                        metadata={"spam_indicator": indicator}
                    )
                    violations.append(violation)
        
        # Check professional tone
        if compliance_rules.get("professional_tone_required", True):
            unprofessional_patterns = [
                r'\bhey\b',
                r'\byo\b',
                r'\bwhat\'s up\b',
                r'\bcya\b',
                r'\bbro\b'
            ]
            
            for pattern in unprofessional_patterns:
                if re.search(pattern, all_content, re.IGNORECASE):
                    violation = ValidationViolation(
                        error_code=self.error_codes["compliance_violation"],
                        violation_type="compliance",
                        description=f"Unprofessional language detected - {pattern}",
                        severity="warning",
                        fix_suggestion="Use more professional language",
                        metadata={"unprofessional_pattern": pattern}
                    )
                    violations.append(violation)
        
        return violations
    
    def _validate_quality(self, draft_content: Dict[str, Any], regen_output: Any) -> List[ValidationViolation]:
        """Validate overall message quality and coherence."""
        violations = []
        
        # Check confidence scores
        if hasattr(regen_output, 'final_confidence'):
            confidence = regen_output.final_confidence
            if confidence < 0.6:
                violation = ValidationViolation(
                    error_code=self.error_codes["quality_issue"],
                    violation_type="quality",
                    description=f"Low confidence score - {confidence:.3f}",
                    severity="warning",
                    fix_suggestion="Improve evidence quality and claim strength",
                    metadata={"confidence_score": confidence}
                )
                violations.append(violation)
        
        # Check for content coherence
        sections = draft_content.get("sections", {})
        if "hook" in sections and "value" in sections:
            hook_content = getattr(sections["hook"], 'content', '') if hasattr(sections["hook"], 'content') else str(sections["hook"])
            value_content = getattr(sections["value"], 'content', '') if hasattr(sections["value"], 'content') else str(sections["value"])
            
            # Simple coherence check - hook should relate to value
            hook_words = set(hook_content.lower().split())
            value_words = set(value_content.lower().split())
            overlap = len(hook_words.intersection(value_words))
            
            if overlap < 3:  # Need at least 3 overlapping words
                violation = ValidationViolation(
                    error_code=self.error_codes["quality_issue"],
                    violation_type="quality",
                    description="Poor coherence between hook and value sections",
                    severity="info",
                    fix_suggestion="Improve thematic consistency between sections",
                    metadata={"word_overlap": overlap}
                )
                violations.append(violation)
        
        return violations
    
    def _calculate_quality_score(self, violations: List[ValidationViolation], draft_content: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        base_score = 1.0
        
        # Deduct points for violations
        for violation in violations:
            if violation.severity == "blocker":
                base_score -= 0.3
            elif violation.severity == "warning":
                base_score -= 0.1
            elif violation.severity == "info":
                base_score -= 0.05
        
        # Boost for complete structure
        sections = draft_content.get("sections", {})
        if len(sections) >= 4:  # Good section coverage
            base_score += 0.1
        
        return round(max(base_score, 0.0), 3)
    
    def _calculate_compliance_score(self, violations: List[ValidationViolation]) -> float:
        """Calculate compliance score."""
        base_score = 1.0
        
        # Heavy penalties for compliance violations
        for violation in violations:
            if violation.violation_type == "compliance":
                if violation.severity == "blocker":
                    base_score -= 0.5
                elif violation.severity == "warning":
                    base_score -= 0.2
        
        return round(max(base_score, 0.0), 3)
    
    def _safe_record_telemetry(self, output: ValidationOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("k5_validation_executed", {
                    "is_valid": output.is_valid,
                    "total_violations": len(output.all_violations),
                    "blocker_count": len(output.blocked_violations),
                    "quality_score": output.quality_score,
                    "compliance_score": output.compliance_score
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_validation_summary(self, output: ValidationOutput) -> Dict[str, Any]:
        """Get a summary of the validation execution for debugging/telemetry."""
        return {
            "execution_id": "k5_validation",
            "is_valid": output.is_valid,
            "total_violations": len(output.all_violations),
            "blocker_count": len(output.blocked_violations),
            "warning_count": len(output.warning_violations),
            "info_count": len(output.info_violations),
            "quality_score": output.quality_score,
            "compliance_score": output.compliance_score,
            "violation_types": list(set(v.violation_type for v in output.all_violations)),
            "error_codes": output.error_codes
        }





