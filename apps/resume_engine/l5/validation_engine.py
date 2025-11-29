#!/usr/bin/env python3
"""
Resume Engine Validation Layer (L5)
Comprehensive validation infrastructure for resume generation
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional, Set

from ..utils.rg_models import (
    ValidationResult, 
    ValidationSeverity, 
    ResumeSection,
    JDEnforcementRule,
    JDEnforcementResult
)
from ..config.rg_config import (
    ValidatorConfig,
    ContentConstraintsConfig,
    SignalControlConfig
)


# Mock data indicators for JD enforcement validation
mock_indicators = [
    "example", "sample", "placeholder", "test", "demo",
    "mock", "fake", "dummy", "template", "generic"
]


class ValidationRule:
    """Individual validation rule with configurable validator"""

    def __init__(self, rule_id: str, severity: ValidationSeverity, validator: Any, error_message: str, category: str = "general"):
        self.rule_id = rule_id
        self.severity = severity
        self.validator = validator
        self.error_message = error_message
        self.category = category

    def execute(self, data: Dict) -> ValidationResult:
        """Execute validation rule against provided data"""
        try:
            passed = self.validator(data)
            
            error_msg = self.error_message if not passed else ""
            
            return ValidationResult(
                rule_id=self.rule_id,
                passed=passed,
                severity=self.severity,
                message=error_msg,
                details=data.get('error_details', {})
            )
        except Exception as e:
            return ValidationResult(
                rule_id=self.rule_id,
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation logic failed for {self.rule_id}: {str(e)}",
                details={'exception': str(e)}
            )


class ValidationEngine:
    """Core validation engine for managing and executing validation rules"""

    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.rules_by_category: Dict[str, List[ValidationRule]] = {}

    def register_rule(self, rule: ValidationRule) -> None:
        """Register a single validation rule"""
        self.rules.append(rule)
        if rule.category not in self.rules_by_category:
            self.rules_by_category[rule.category] = []
        self.rules_by_category[rule.category].append(rule)

    def register_rules(self, rules: List[ValidationRule]) -> None:
        """Register multiple validation rules"""
        for rule in rules:
            self.register_rule(rule)

    def validate(self, data: Dict, categories: Optional[List[str]] = None) -> List[ValidationResult]:
        """Execute validation against data, optionally filtered by categories"""
        results = []
        
        rules_to_run = self.rules
        if categories:
            rules_to_run = []
            for category in categories:
                rules_to_run.extend(self.rules_by_category.get(category, []))

        for rule in rules_to_run:
            result = rule.execute(data)
            results.append(result)

        return results

    def has_high_or_critical_failures(self, results: List[ValidationResult]) -> bool:
        """Check if any validation results have high or critical failures"""
        return any(
            not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]
            for r in results
        )


class JDEnforcementValidator:
    """Job Description enforcement validator ensuring JD data flows through pipeline"""

    def __init__(self):
        self.enforcement_results: List[JDEnforcementResult] = []
        self.jd_hash: Optional[str] = None
        self.jd_keywords: List[str] = []

    def _check_mock_data(self, data: Any, gate_id: str, rule: JDEnforcementRule) -> JDEnforcementResult:
        """Check for mock/fake data indicators"""
        data_str = str(data).lower()
        has_mock = any(indicator in data_str for indicator in mock_indicators)
        return JDEnforcementResult(
            rule,
            not has_mock,
            f"No mock data indicators found in {rule.name}" if not has_mock else f"Mock data indicators found in {rule.name}",
            gate_id
        )

    def _check_jd_keywords(self, data: Any, gate_id: str, rule: JDEnforcementRule, min_count: int) -> JDEnforcementResult:
        """Check for minimum JD keyword presence"""
        if not self.jd_keywords:
            return JDEnforcementResult(rule, False, "JD keywords list is empty, cannot check", gate_id)
        
        data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        data_str = data_str.lower()
        keywords_found = [kw for kw in self.jd_keywords[:15] if kw.lower() in data_str]
        
        passed = len(keywords_found) >= min_count
        return JDEnforcementResult(
            rule,
            passed,
            f"Found {len(keywords_found)} JD keywords in {rule.name} (>= {min_count})" if passed else f"Found only {len(keywords_found)} JD keywords in {rule.name} (< {min_count})",
            gate_id
        )

    def validate_jd_input(self, job_description: str, gate_id: str) -> List[JDEnforcementResult]:
        """Validate initial job description input"""
        results = []

        # Check minimum length
        if len(job_description) >= 100:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E1_JD_MIN_LENGTH,
                True,
                f"JD length: {len(job_description)} chars",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E1_JD_MIN_LENGTH,
                False,
                f"JD too short: {len(job_description)} chars < 100 minimum",
                gate_id
            ))

        # Check for non-null
        if job_description and job_description.strip():
            results.append(JDEnforcementResult(
                JDEnforcementRule.E2_JD_NON_NULL,
                True,
                "JD is non-null and non-empty",
                gate_id
            ))
        else:
            results.append(JDEnforcementResult(
                JDEnforcementRule.E2_JD_NON_NULL,
                False,
                "JD is null or empty",
                gate_id
            ))

        # Extract keywords for later validation
        self.jd_keywords = self._extract_keywords(job_description)
        
        return results

    def _extract_keywords(self, job_description: str) -> List[str]:
        """Extract keywords from job description for validation"""
        # Simple keyword extraction - in production would use more sophisticated NLP
        words = job_description.lower().split()
        # Filter out common words and keep technical/business terms
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'a', 'an'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:20]  # Limit to top 20 keywords


class PreFlightValidator:
    """Pre-flight validation for resume generation constraints and requirements"""

    def __init__(self, master_resume: Dict, validator_config: ValidatorConfig, 
                 content_constraints: ContentConstraintsConfig, signal_config: SignalControlConfig):
        self.master_resume = master_resume
        self.engine = ValidationEngine()
        self.constraints = content_constraints
        self.signal_constraints = signal_config
        self.validator_config = validator_config
        
        self.FORBIDDEN_VERBS = self.validator_config.forbidden_verbs
        self.PIPELINE_STATUS_ENUM = self.validator_config.pipeline_status_enum
        
        self.REQUIRED_SECTIONS = self._convert_section_names_to_enums(
            self.validator_config.required_sections
        )
        self.BULLET_WORD_COUNT_SECTIONS_TO_CHECK = self._convert_section_names_to_enums(
            self.validator_config.bullet_word_count_sections_to_check
        )
        self.PROVENANCE_SPLIT_TARGETS = self._convert_config_keys_to_enums(
            self.validator_config.provenance_split_targets
        )
        
        # Section signal targets configuration
        self.SECTION_SIGNAL_TARGETS_CONFIG = {
            "K1_Exec_Summary": (ResumeSection.K1_HEADLINE, 0.85, 1.20, None, None),
            "K2_Unify": (ResumeSection.K2_SUMMARY, 0.70, 1.00, None, None),
            "K3_IBM": (ResumeSection.K3_EXPERIENCE, 0.70, 1.00, None, None),
            "K4_TraderSense": (ResumeSection.K4_EDUCATION, 0.60, 0.90, None, None),
            "K6_Narrative": (ResumeSection.K6_PROJECTS, 0.70, 1.00, None, None),
        }

        self.RULE_TO_SECTION_MAP = self._initialize_rule_map()
        self._register_rules()
        self.logger = logging.getLogger(__name__)
    
    def _convert_section_names_to_enums(self, section_names: Set[str]) -> Set:
        """Convert string section names to ResumeSection enums"""
        result = set()
        for name in section_names:
            if isinstance(name, str):
                try:
                    enum_val = ResumeSection[name]
                    result.add(enum_val)
                except KeyError:
                    logging.warning(f"Unknown ResumeSection '{name}' in validator config, skipping")
            else:
                result.add(name)
        return result
    
    def _convert_config_keys_to_enums(self, config_dict: Dict) -> Dict:
        """Convert config dictionary keys to enums where applicable"""
        result = {}
        for key, value in config_dict.items():
            try:
                if isinstance(key, str) and hasattr(ResumeSection, key):
                    enum_key = ResumeSection[key]
                    result[enum_key] = value
                else:
                    result[key] = value
            except KeyError:
                result[key] = value
        return result

    def _initialize_rule_map(self) -> Dict[str, str]:
        """Initialize mapping of validation rules to sections"""
        return {
            "forbidden_verbs": "content_quality",
            "word_count_limits": "content_constraints",
            "required_sections": "structure_validation",
            "jd_keyword_presence": "content_relevance"
        }

    def _register_rules(self) -> None:
        """Register all validation rules"""
        # Forbidden verbs rule
        self.engine.register_rule(ValidationRule(
            rule_id="forbidden_verbs_check",
            severity=ValidationSeverity.MEDIUM,
            validator=lambda data: self._check_forbidden_verbs(data),
            error_message="Content contains forbidden verbs",
            category="content_quality"
        ))

        # Word count constraints rule
        self.engine.register_rule(ValidationRule(
            rule_id="word_count_constraints",
            severity=ValidationSeverity.HIGH,
            validator=lambda data: self._check_word_count_constraints(data),
            error_message="Content violates word count constraints",
            category="content_constraints"
        ))

        # Required sections rule
        self.engine.register_rule(ValidationRule(
            rule_id="required_sections_check",
            severity=ValidationSeverity.HIGH,
            validator=lambda data: self._check_required_sections(data),
            error_message="Missing required sections",
            category="structure_validation"
        ))

    def _check_forbidden_verbs(self, data: Dict) -> bool:
        """Check for presence of forbidden verbs in content"""
        content = data.get('content', '').lower()
        for verb in self.FORBIDDEN_VERBS:
            if verb in content:
                return False
        return True

    def _check_word_count_constraints(self, data: Dict) -> bool:
        """Check word count constraints against configuration"""
        word_count = data.get('word_count', 0)
        section = data.get('section')
        
        if not section:
            return True
        
        # Check against total constraints
        if section == 'total':
            return self.constraints.TOTAL_WORD_COUNT_MIN <= word_count <= self.constraints.TOTAL_WORD_COUNT_MAX
        
        # Section-specific constraints would be checked here
        return True

    def _check_required_sections(self, data: Dict) -> bool:
        """Check that all required sections are present"""
        sections = data.get('sections', [])
        for required_section in self.REQUIRED_SECTIONS:
            if required_section not in sections:
                return False
        return True

    def validate_content(self, content_data: Dict, categories: Optional[List[str]] = None) -> List[ValidationResult]:
        """Validate content against all registered rules"""
        return self.engine.validate(content_data, categories)

    def has_critical_failures(self, validation_results: List[ValidationResult]) -> bool:
        """Check if validation results contain critical failures"""
        return self.engine.has_high_or_critical_failures(validation_results)
