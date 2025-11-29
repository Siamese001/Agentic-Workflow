#!/usr/bin/env python3
"""
Outreach Engine Constraints - Lift & Shift + Enhanced from LIC
Content validation, Unicode hygiene, and structural constraints
"""

from typing import Dict, List, Optional, Any, Tuple
import re
import unicodedata

from ..models import (
    ValidationResult, ValidationSeverity, RouteConstraints, Route
)


class ContentValidator:
    """Content cleanliness validator - Lift & Shift from LIC"""
    
    def __init__(self, constraints_config: Dict[str, Any]):
        self.content_cleanliness = constraints_config.get("content_cleanliness", {})
        self.forbidden_verbs = self.content_cleanliness.get("forbidden_verbs", [])
        self.filler_patterns = [re.compile(pattern) for pattern in self.content_cleanliness.get("filler_patterns", [])]
        self.placeholder_patterns = [re.compile(pattern) for pattern in self.content_cleanliness.get("placeholder_patterns", [])]
        self.max_violations = self.content_cleanliness.get("max_violations", 1)
    
    def validate_forbidden_verbs(self, content: str) -> List[ValidationResult]:
        """Check for forbidden corporate clichés"""
        validation_results = []
        content_lower = content.lower()
        
        violations = []
        for verb in self.forbidden_verbs:
            if verb in content_lower:
                violations.append(verb)
        
        if violations:
            validation_results.append(ValidationResult(
                rule_id="FORBIDDEN_VERB_USAGE",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Found forbidden verbs: {', '.join(violations)}",
                details={"forbidden_verbs": violations, "content_snippet": content_lower[:200]}
            ))
        
        return validation_results
    
    def validate_filler_patterns(self, content: str) -> List[ValidationResult]:
        """Check for weak filler phrases"""
        validation_results = []
        
        violations = []
        for pattern in self.filler_patterns:
            matches = pattern.findall(content)
            if matches:
                violations.extend(matches)
        
        if violations:
            validation_results.append(ValidationResult(
                rule_id="FILLER_PHRASE_USAGE",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Found filler phrases: {', '.join(violations[:3])}",
                details={"filler_phrases": violations[:5]}  # Limit to first 5
            ))
        
        return validation_results
    
    def validate_placeholder_patterns(self, content: str) -> List[ValidationResult]:
        """Check for placeholder text"""
        validation_results = []
        
        violations = []
        for pattern in self.placeholder_patterns:
            matches = pattern.findall(content)
            if matches:
                violations.extend(matches)
        
        if violations:
            validation_results.append(ValidationResult(
                rule_id="PLACEHOLDER_TEXT_DETECTED",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Placeholder text detected - message not ready for delivery",
                details={"placeholders": violations}
            ))
        
        return validation_results
    
    def validate_content_cleanliness(self, content: str) -> List[ValidationResult]:
        """Comprehensive content cleanliness validation"""
        all_results = []
        
        all_results.extend(self.validate_forbidden_verbs(content))
        all_results.extend(self.validate_filler_patterns(content))
        all_results.extend(self.validate_placeholder_patterns(content))
        
        # Check total violation count
        failed_validations = [r for r in all_results if not r.passed]
        if len(failed_validations) > self.max_violations:
            all_results.append(ValidationResult(
                rule_id="EXCESSIVE_VIOLATIONS",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Too many content violations: {len(failed_validations)} > {self.max_violations}",
                details={"violation_count": len(failed_validations), "max_allowed": self.max_violations}
            ))
        
        return all_results


class UnicodeHygiene:
    """Unicode normalization for LinkedIn compatibility - Enhanced from LIC"""
    
    def __init__(self, constraints_config: Dict[str, Any]):
        self.ascii_hygiene = constraints_config.get("ascii_hygiene", {})
        self.replacements = self.ascii_hygiene.get("replacements", {})
        self.rules = self.ascii_hygiene.get("rules", {})
    
    def normalize_unicode(self, content: str) -> str:
        """Normalize Unicode characters to LinkedIn-safe ASCII"""
        normalized = content
        
        # Apply Unicode to ASCII replacements
        for unicode_char, ascii_replacement in self.replacements.items():
            normalized = normalized.replace(unicode_char, ascii_replacement)
        
        # Additional normalization using unicodedata
        normalized = unicodedata.normalize('NFKD', normalized)
        
        # Remove any remaining non-ASCII characters except basic punctuation
        normalized = re.sub(r'[^\x00-\x7F]+', '', normalized)
        
        return normalized
    
    def validate_unicode_compliance(self, content: str) -> List[ValidationResult]:
        """Check for Unicode characters that need normalization"""
        validation_results = []
        
        # Check for smart quotes
        if self.rules.get("no_smart_quotes", True):
            smart_quotes = ['\u2018', '\u2019', '\u201C', '\u201D']
            found_quotes = [q for q in smart_quotes if q in content]
            if found_quotes:
                validation_results.append(ValidationResult(
                    rule_id="SMART_QUOTES_DETECTED",
                    passed=False,
                    severity=ValidationSeverity.LOW,
                    message="Smart quotes detected - will be normalized to ASCII",
                    details={"smart_quotes": found_quotes}
                ))
        
        # Check for em/en dashes
        if self.rules.get("no_em_dashes", True):
            em_dash = '\u2014'
            en_dash = '\u2013'
            if em_dash in content or en_dash in content:
                validation_results.append(ValidationResult(
                    rule_id="UNICODE_DASHES_DETECTED",
                    passed=False,
                    severity=ValidationSeverity.LOW,
                    message="Unicode dashes detected - will be normalized to ASCII",
                    details={"has_em_dash": em_dash in content, "has_en_dash": en_dash in content}
                ))
        
        # Check for other Unicode characters
        if self.rules.get("no_unicode_bullets", True):
            unicode_bullets = ['\u2022', '\u2023', '\u2043', '\u204C', '\u204D']
            found_bullets = [b for b in unicode_bullets if b in content]
            if found_bullets:
                validation_results.append(ValidationResult(
                    rule_id="UNICODE_BULLETS_DETECTED",
                    passed=False,
                    severity=ValidationSeverity.LOW,
                    message="Unicode bullets detected - will be normalized to ASCII",
                    details={"unicode_bullets": found_bullets}
                ))
        
        return validation_results


class StructuralValidator:
    """Structural validation for message format - Lift & Shift from LIC"""
    
    def __init__(self, constraints_config: Dict[str, Any]):
        self.structural_validation = constraints_config.get("structural_validation", {})
        self.word_count_tolerance = self.structural_validation.get("word_count_tolerance", 0.1)
        self.char_limit_enforcement = self.structural_validation.get("char_limit_enforcement", "strict")
        self.subject_requirements = self.structural_validation.get("subject_line_requirements", {})
    
    def validate_word_count(self, content: str, target_range: Optional[List[int]]) -> List[ValidationResult]:
        """Validate word count against target range"""
        validation_results = []
        
        if target_range is None:
            return validation_results
        
        word_count = len(content.split())
        min_words, max_words = target_range
        
        # Apply tolerance
        tolerance_buffer = int(max_words * self.word_count_tolerance)
        effective_max = max_words + tolerance_buffer
        
        if word_count < min_words:
            validation_results.append(ValidationResult(
                rule_id="WORD_COUNT_TOO_LOW",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Word count {word_count} below minimum {min_words}",
                details={"word_count": word_count, "target_range": target_range}
            ))
        elif word_count > effective_max:
            validation_results.append(ValidationResult(
                rule_id="WORD_COUNT_TOO_HIGH",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Word count {word_count} above maximum {max_words} (with tolerance)",
                details={"word_count": word_count, "target_range": target_range, "effective_max": effective_max}
            ))
        
        return validation_results
    
    def validate_character_limit(self, content: str, char_limit: Optional[int]) -> List[ValidationResult]:
        """Validate character limit"""
        validation_results = []
        
        if char_limit is None:
            return validation_results
        
        char_count = len(content)
        
        if char_count > char_limit:
            severity = ValidationSeverity.CRITICAL if self.char_limit_enforcement == "strict" else ValidationSeverity.HIGH
            validation_results.append(ValidationResult(
                rule_id="CHARACTER_LIMIT_EXCEEDED",
                passed=False,
                severity=severity,
                message=f"Character count {char_count} exceeds limit {char_limit}",
                details={"char_count": char_count, "limit": char_limit}
            ))
        
        return validation_results
    
    def validate_subject_line(self, subject: str) -> List[ValidationResult]:
        """Validate subject line requirements"""
        validation_results = []
        
        if not subject:
            return validation_results
        
        subject_words = len(subject.split())
        subject_chars = len(subject)
        
        # Word count requirements
        min_words = self.subject_requirements.get("min_words", 4)
        max_words = self.subject_requirements.get("max_words", 10)
        
        if subject_words < min_words or subject_words > max_words:
            validation_results.append(ValidationResult(
                rule_id="SUBJECT_WORD_COUNT_INVALID",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Subject word count {subject_words} outside range {min_words}-{max_words}",
                details={"subject_words": subject_words, "subject": subject}
            ))
        
        # Character limit
        char_limit = self.subject_requirements.get("char_limit", 60)
        if subject_chars > char_limit:
            validation_results.append(ValidationResult(
                rule_id="SUBJECT_CHAR_LIMIT_EXCEEDED",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Subject character count {subject_chars} exceeds limit {char_limit}",
                details={"subject_chars": subject_chars, "subject": subject}
            ))
        
        # Format requirements
        format_rules = self.subject_requirements.get("format_requirements", {})
        
        if format_rules.get("no_clickbait", True):
            clickbait_patterns = [r'!', r'\?\?', r'YOU.*MUST', r'CLICK.*NOW', r'FREE.*DOWNLOAD']
            for pattern in clickbait_patterns:
                if re.search(pattern, subject, re.IGNORECASE):
                    validation_results.append(ValidationResult(
                        rule_id="SUBJECT_CLICKBAIT_DETECTED",
                        passed=False,
                        severity=ValidationSeverity.MEDIUM,
                        message="Subject line appears to be clickbait",
                        details={"subject": subject, "pattern": pattern}
                    ))
        
        if format_rules.get("no_all_caps", True) and subject.isupper():
            validation_results.append(ValidationResult(
                rule_id="SUBJECT_ALL_CAPS",
                passed=False,
                severity=ValidationSeverity.LOW,
                message="Subject line should not be all caps",
                details={"subject": subject}
            ))
        
        return validation_results


class ConstraintEngine:
    """Main constraint engine - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.constraints_config = lic_capabilities.get("constraints", {})
        self.content_validator = ContentValidator(self.constraints_config)
        self.unicode_hygiene = UnicodeHygiene(self.constraints_config)
        self.structural_validator = StructuralValidator(self.constraints_config)
    
    def validate_message(
        self, 
        content: str, 
        route_constraints: RouteConstraints,
        subject_line: Optional[str] = None
    ) -> List[ValidationResult]:
        """Comprehensive message validation"""
        all_results = []
        
        # Content cleanliness validation
        all_results.extend(self.content_validator.validate_content_cleanliness(content))
        
        # Unicode compliance validation
        all_results.extend(self.unicode_hygiene.validate_unicode_compliance(content))
        
        # Structural validation
        all_results.extend(self.structural_validator.validate_word_count(content, route_constraints.word_range))
        all_results.extend(self.structural_validator.validate_character_limit(content, route_constraints.char_limit))
        
        # Subject line validation if provided
        if subject_line and route_constraints.subject_line_enabled:
            all_results.extend(self.structural_validator.validate_subject_line(subject_line))
        
        return all_results
    
    def apply_hygiene(self, content: str) -> str:
        """Apply Unicode hygiene normalization"""
        return self.unicode_hygiene.normalize_unicode(content)
    
    def get_constraint_summary(self, route: Route) -> Dict[str, Any]:
        """Get constraint summary for a route"""
        # This would integrate with routing constraints
        return {
            "content_cleanliness": {
                "forbidden_verbs_count": len(self.content_validator.forbidden_verbs),
                "max_violations": self.content_validator.max_violations
            },
            "unicode_hygiene": {
                "normalization_enabled": True,
                "ascii_only": True
            },
            "structural_validation": {
                "word_count_tolerance": self.structural_validator.word_count_tolerance,
                "char_enforcement": self.structural_validator.char_limit_enforcement
            }
        }
