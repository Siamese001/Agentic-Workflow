"""RG K8 Validate - Resume Quality and Compliance Validation

Incorporated from historical agentic_workflow/l2/rg_k8_validate.py to execute
comprehensive resume quality and compliance validation.

This is the eighth and final execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Individual validation rule applied to content."""
    rule_id: str
    rule_category: str  # "quality", "compliance", "content", "format"
    description: str
    severity: str  # "critical", "warning", "info"
    status: str  # "pass", "fail", "warning"
    details: str
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Complete validation result for resume content."""
    validation_id: str
    overall_status: str  # "pass", "fail", "warning"
    quality_score: float  # 0.0 to 1.0
    compliance_score: float  # 0.0 to 1.0
    content_score: float  # 0.0 to 1.0
    format_score: float  # 0.0 to 1.0
    validation_rules: List[ValidationRule]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationMetrics:
    """Metrics from resume validation process."""
    total_rules_checked: int
    rules_passed: int
    rules_failed: int
    rules_with_warnings: int
    critical_issues: int
    validation_confidence: float
    processing_time_ms: int


@dataclass
class ValidationOutput:
    """Complete output from K8 validation phase."""
    validation_result: ValidationResult
    validated_content: str
    metrics: ValidationMetrics
    validation_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK8Validate:
    """K8 Resume Validator - Eighth hop in sequential processing pipeline.
    
    Executes comprehensive resume quality and compliance validation:
    - Content quality validation (completeness, relevance, impact)
    - Compliance validation (ATS compatibility, industry standards)
    - Format validation (structure, typography, layout)
    - Professional standards validation (tone, consistency, accuracy)
    """
    
    def __init__(self, 
                 validation_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K8 resume validator."""
        self.validation_plan = validation_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Quality validation rules
        self.quality_rules = {
            "completeness": {
                "required_sections": ["contact_info", "summary", "experience", "education", "skills"],
                "min_content_length": 200,  # words
                "max_content_length": 1000,  # words
                "contact_info_required": ["email", "phone", "linkedin"]
            },
            "relevance": {
                "action_verb_density": 0.3,  # minimum ratio
                "quantification_density": 0.2,  # minimum ratio
                "keyword_alignment": 0.6,  # minimum score
                "achievement_focus": 0.4  # minimum ratio
            },
            "impact": {
                "measurable_results": True,
                "quantified_achievements": True,
                "business_value": True,
                "specific_examples": True
            }
        }
        
        # Compliance validation rules
        self.compliance_rules = {
            "ats_compatibility": {
                "standard_format": True,
                "no_special_characters": True,
                "standard_bullets": True,
                "readable_fonts": True,
                "proper_spacing": True
            },
            "industry_standards": {
                "professional_tone": True,
                "appropriate_length": True,
                "relevant_content": True,
                "current_information": True
            },
            "legal_compliance": {
                "no_discriminatory_content": True,
                "accurate_information": True,
                "privacy_compliance": True,
                "no_misleading_claims": True
            }
        }
        
        # Format validation rules
        self.format_rules = {
            "structure": {
                "logical_section_order": True,
                "consistent_headers": True,
                "proper_hierarchy": True,
                "balanced_sections": True
            },
            "typography": {
                "consistent_capitalization": True,
                "proper_punctuation": True,
                "correct_spacing": True,
                "readable_format": True
            },
            "layout": {
                "appropriate_margins": True,
                "readable_line_spacing": True,
                "professional_appearance": True,
                "visual_clarity": True
            }
        }
        
        # Content validation rules
        self.content_rules = {
            "accuracy": {
                "no_typos": True,
                "correct_grammar": True,
                "consistent_dates": True,
                "factual_consistency": True
            },
            "professionalism": {
                "appropriate_language": True,
                "professional_tone": True,
                "no_slang": True,
                "formal_address": True
            },
            "effectiveness": {
                "clear_communication": True,
                "strong_opening": True,
                "compelling_summary": True,
                "action_oriented": True
            }
        }
    
    def validate_resume_content(
        self,
        *,
        formatting_output: Any,  # From K7 formatting
        job_requirements: Dict[str, Any],
        validation_params: Optional[Dict[str, Any]] = None
    ) -> ValidationOutput:
        """Execute comprehensive resume validation.
        
        Args:
            formatting_output: Output from K7 formatting phase
            job_requirements: Target job requirements and specifications
            validation_params: Validation strategy and parameters
            
        Returns:
            Complete validation output with quality assessment and recommendations
        """
        validation_params = validation_params or {}
        processing_trace = []
        
        try:
            # 1. Initialize validation strategy
            strategy = self._initialize_validation_strategy(validation_params, job_requirements)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Extract formatted content
            content = self._extract_formatted_content(formatting_output)
            processing_trace.append({
                "step": "content_extraction",
                "content_length": len(content),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Apply quality validation rules
            quality_rules = self._validate_quality(content, strategy)
            processing_trace.append({
                "step": "quality_validation",
                "rules_checked": len(quality_rules),
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Apply compliance validation rules
            compliance_rules = self._validate_compliance(content, strategy)
            processing_trace.append({
                "step": "compliance_validation",
                "rules_checked": len(compliance_rules),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Apply format validation rules
            format_rules = self._validate_format(content, strategy)
            processing_trace.append({
                "step": "format_validation",
                "rules_checked": len(format_rules),
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Apply content validation rules
            content_rules = self._validate_content(content, strategy)
            processing_trace.append({
                "step": "content_validation",
                "rules_checked": len(content_rules),
                "timestamp": "2024-01-01T00:00:06Z"
            })
            
            # 7. Compile all validation results
            all_rules = quality_rules + compliance_rules + format_rules + content_rules
            processing_trace.append({
                "step": "results_compilation",
                "total_rules": len(all_rules),
                "timestamp": "2024-01-01T00:00:07Z"
            })
            
            # 8. Calculate overall scores and status
            validation_result = self._calculate_validation_result(all_rules, strategy)
            processing_trace.append({
                "step": "score_calculation",
                "overall_status": validation_result.overall_status,
                "quality_score": validation_result.quality_score,
                "timestamp": "2024-01-01T00:00:08Z"
            })
            
            # 9. Generate recommendations
            recommendations = self._generate_recommendations(all_rules, validation_result)
            validation_result.recommendations = recommendations
            processing_trace.append({
                "step": "recommendation_generation",
                "recommendations_count": len(recommendations),
                "timestamp": "2024-01-01T00:00:09Z"
            })
            
            # 10. Calculate validation metrics
            metrics = self._calculate_validation_metrics(all_rules)
            processing_trace.append({
                "step": "metrics_calculation",
                "validation_confidence": metrics.validation_confidence,
                "timestamp": "2024-01-01T00:00:10Z"
            })
            
            # 11. Build validation output
            validation_output = ValidationOutput(
                validation_result=validation_result,
                validated_content=content,
                metrics=metrics,
                validation_plan={
                    "strategy": strategy,
                    "parameters": validation_params,
                    "job_requirements": job_requirements
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 12. Record telemetry (best-effort)
            self._safe_record_telemetry(validation_output)
            
            return validation_output
            
        except Exception as e:
            logger.error(f"Resume validation failed: {e}")
            
            error_validation_result = ValidationResult(
                validation_id="error_validation",
                overall_status="fail",
                quality_score=0.0,
                compliance_score=0.0,
                content_score=0.0,
                format_score=0.0,
                validation_rules=[],
                recommendations=[],
                metadata={"error": str(e)}
            )
            
            error_output = ValidationOutput(
                validation_result=error_validation_result,
                validated_content="",
                metrics=ValidationMetrics(0, 0, 0, 0, 0, 0.0, 0),
                validation_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:11Z"
                }]
            )
            
            return error_output
    
    def _initialize_validation_strategy(self, params: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize validation strategy based on parameters and job requirements."""
        return {
            "level": params.get("level", "comprehensive"),
            "quality_check": params.get("quality_check", True),
            "compliance_check": params.get("compliance_check", True),
            "format_check": params.get("format_check", True),
            "content_check": params.get("content_check", True),
            "target_role": job_requirements.get("title", ""),
            "target_industry": job_requirements.get("industry", "general"),
            "strict_mode": params.get("strict_mode", False),
            "thresholds": {
                "quality": params.get("quality_threshold", 0.7),
                "compliance": params.get("compliance_threshold", 0.8),
                "content": params.get("content_threshold", 0.6),
                "format": params.get("format_threshold", 0.8)
            }
        }
    
    def _extract_formatted_content(self, formatting_output: Any) -> str:
        """Extract formatted content from K7 output."""
        if hasattr(formatting_output, 'formatted_content'):
            return formatting_output.formatted_content
        elif isinstance(formatting_output, dict):
            return formatting_output.get("formatted_content", "")
        else:
            return ""
    
    def _validate_quality(self, content: str, strategy: Dict[str, Any]) -> List[ValidationRule]:
        """Apply quality validation rules."""
        rules = []
        
        if not strategy["quality_check"]:
            return rules
        
        # Completeness validation
        completeness_rules = self._validate_completeness(content)
        rules.extend(completeness_rules)
        
        # Relevance validation
        relevance_rules = self._validate_relevance(content, strategy)
        rules.extend(relevance_rules)
        
        # Impact validation
        impact_rules = self._validate_impact(content)
        rules.extend(impact_rules)
        
        return rules
    
    def _validate_compliance(self, content: str, strategy: Dict[str, Any]) -> List[ValidationRule]:
        """Apply compliance validation rules."""
        rules = []
        
        if not strategy["compliance_check"]:
            return rules
        
        # ATS compatibility validation
        ats_rules = self._validate_ats_compatibility(content)
        rules.extend(ats_rules)
        
        # Industry standards validation
        industry_rules = self._validate_industry_standards(content, strategy)
        rules.extend(industry_rules)
        
        # Legal compliance validation
        legal_rules = self._validate_legal_compliance(content)
        rules.extend(legal_rules)
        
        return rules
    
    def _validate_format(self, content: str, strategy: Dict[str, Any]) -> List[ValidationRule]:
        """Apply format validation rules."""
        rules = []
        
        if not strategy["format_check"]:
            return rules
        
        # Structure validation
        structure_rules = self._validate_structure(content)
        rules.extend(structure_rules)
        
        # Typography validation
        typography_rules = self._validate_typography(content)
        rules.extend(typography_rules)
        
        # Layout validation
        layout_rules = self._validate_layout(content)
        rules.extend(layout_rules)
        
        return rules
    
    def _validate_content(self, content: str, strategy: Dict[str, Any]) -> List[ValidationRule]:
        """Apply content validation rules."""
        rules = []
        
        if not strategy["content_check"]:
            return rules
        
        # Accuracy validation
        accuracy_rules = self._validate_accuracy(content)
        rules.extend(accuracy_rules)
        
        # Professionalism validation
        professionalism_rules = self._validate_professionalism(content)
        rules.extend(professionalism_rules)
        
        # Effectiveness validation
        effectiveness_rules = self._validate_effectiveness(content)
        rules.extend(effectiveness_rules)
        
        return rules
    
    def _validate_completeness(self, content: str) -> List[ValidationRule]:
        """Validate resume completeness."""
        rules = []
        content_lower = content.lower()
        
        # Check required sections
        required_sections = self.quality_rules["completeness"]["required_sections"]
        missing_sections = [section for section in required_sections if section not in content_lower]
        
        if missing_sections:
            rules.append(ValidationRule(
                rule_id="completeness_missing_sections",
                rule_category="quality",
                description="Missing required sections",
                severity="critical" if len(missing_sections) > 2 else "warning",
                status="fail",
                details=f"Missing sections: {', '.join(missing_sections)}",
                confidence_score=0.9
            ))
        
        # Check content length
        word_count = len(content.split())
        min_length = self.quality_rules["completeness"]["min_content_length"]
        max_length = self.quality_rules["completeness"]["max_content_length"]
        
        if word_count < min_length:
            rules.append(ValidationRule(
                rule_id="completeness_too_short",
                rule_category="quality",
                description="Resume content too short",
                severity="warning",
                status="fail",
                details=f"Current: {word_count} words, Minimum: {min_length} words",
                confidence_score=0.8
            ))
        elif word_count > max_length:
            rules.append(ValidationRule(
                rule_id="completeness_too_long",
                rule_category="quality",
                description="Resume content too long",
                severity="warning",
                status="fail",
                details=f"Current: {word_count} words, Maximum: {max_length} words",
                confidence_score=0.8
            ))
        
        # Check contact information
        required_contact = self.quality_rules["completeness"]["contact_info_required"]
        missing_contact = [item for item in required_contact if item not in content_lower]
        
        if missing_contact:
            rules.append(ValidationRule(
                rule_id="completeness_missing_contact",
                rule_category="quality",
                description="Missing required contact information",
                severity="critical",
                status="fail",
                details=f"Missing: {', '.join(missing_contact)}",
                confidence_score=0.9
            ))
        
        return rules
    
    def _validate_relevance(self, content: str, strategy: Dict[str, Any]) -> List[ValidationRule]:
        """Validate content relevance to target role."""
        rules = []
        
        # Check action verb density
        action_verbs = ["managed", "led", "developed", "implemented", "created", "optimized", "improved"]
        words = content.split()
        action_verb_count = sum(1 for word in words if word.lower() in action_verbs)
        action_verb_density = action_verb_count / len(words) if words else 0
        
        min_density = self.quality_rules["relevance"]["action_verb_density"]
        if action_verb_density < min_density:
            rules.append(ValidationRule(
                rule_id="relevance_low_action_density",
                rule_category="quality",
                description="Low action verb density",
                severity="warning",
                status="fail",
                details=f"Current: {action_verb_density:.2f}, Minimum: {min_density:.2f}",
                confidence_score=0.7
            ))
        
        # Check quantification density
        quantified_items = len(re.findall(r'\d+(?:%|\$|years?)', content))
        quantification_density = quantified_items / len(words) if words else 0
        
        min_quant_density = self.quality_rules["relevance"]["quantification_density"]
        if quantification_density < min_quant_density:
            rules.append(ValidationRule(
                rule_id="relevance_low_quantification",
                rule_category="quality",
                description="Low quantification density",
                severity="warning",
                status="fail",
                details=f"Current: {quantification_density:.2f}, Minimum: {min_quant_density:.2f}",
                confidence_score=0.7
            ))
        
        return rules
    
    def _validate_impact(self, content: str) -> List[ValidationRule]:
        """Validate impact and achievement focus."""
        rules = []
        
        # Check for measurable results
        if not re.search(r'\d+(?:%|\$|years?)', content):
            rules.append(ValidationRule(
                rule_id="impact_no_measurable_results",
                rule_category="quality",
                description="No measurable results found",
                severity="warning",
                status="fail",
                details="Include specific metrics and quantifiable achievements",
                confidence_score=0.8
            ))
        
        # Check for business value indicators
        business_value_words = ["increased", "reduced", "improved", "saved", "generated", "achieved"]
        if not any(word in content.lower() for word in business_value_words):
            rules.append(ValidationRule(
                rule_id="impact_no_business_value",
                rule_category="quality",
                description="No clear business value indicators",
                severity="warning",
                status="fail",
                details="Include statements about business impact and value",
                confidence_score=0.7
            ))
        
        return rules
    
    def _validate_ats_compatibility(self, content: str) -> List[ValidationRule]:
        """Validate ATS compatibility."""
        rules = []
        
        # Check for special characters
        if re.search(r'[^\w\s\-\.\,\;\:\!\?\n\#\•]', content):
            rules.append(ValidationRule(
                rule_id="ats_special_characters",
                rule_category="compliance",
                description="Contains special characters that may affect ATS parsing",
                severity="warning",
                status="fail",
                details="Remove special characters and symbols",
                confidence_score=0.8
            ))
        
        # Check for standard formatting
        if not re.search(r'##', content):
            rules.append(ValidationRule(
                rule_id="ats_no_standard_headers",
                rule_category="compliance",
                description="No standard section headers found",
                severity="warning",
                status="fail",
                details="Use standard section headers (## Header Name)",
                confidence_score=0.7
            ))
        
        return rules
    
    def _validate_industry_standards(self, content: str, strategy: Dict[str, Any]) -> List[ValidationRule]:
        """Validate industry standards compliance."""
        rules = []
        
        # Check for professional tone
        informal_words = ["awesome", "cool", "stuff", "things", "guys", "hey"]
        informal_found = [word for word in informal_words if word in content.lower()]
        
        if informal_found:
            rules.append(ValidationRule(
                rule_id="industry_informal_language",
                rule_category="compliance",
                description="Contains informal language",
                severity="warning",
                status="fail",
                details=f"Informal words found: {', '.join(informal_found)}",
                confidence_score=0.6
            ))
        
        return rules
    
    def _validate_legal_compliance(self, content: str) -> List[ValidationRule]:
        """Validate legal compliance."""
        rules = []
        
        # Check for potentially discriminatory content
        discriminatory_terms = ["age", "gender", "race", "religion", "marital status"]
        found_terms = [term for term in discriminatory_terms if term in content.lower()]
        
        if found_terms:
            rules.append(ValidationRule(
                rule_id="legal_potential_discrimination",
                rule_category="compliance",
                description="Potentially discriminatory content detected",
                severity="critical",
                status="fail",
                details=f"Review terms: {', '.join(found_terms)}",
                confidence_score=0.5
            ))
        
        return rules
    
    def _validate_structure(self, content: str) -> List[ValidationRule]:
        """Validate document structure."""
        rules = []
        
        # Check for logical section order
        sections = re.findall(r'##\s*(.+)', content)
        section_names = [section.lower() for section in sections]
        
        if "contact_info" in section_names:
            contact_pos = section_names.index("contact_info")
            if contact_pos > 0:
                rules.append(ValidationRule(
                    rule_id="structure_contact_not_first",
                    rule_category="format",
                    description="Contact information should be first section",
                    severity="warning",
                    status="fail",
                    details="Move contact information to the beginning",
                    confidence_score=0.8
                ))
        
        return rules
    
    def _validate_typography(self, content: str) -> List[ValidationRule]:
        """Validate typography and formatting."""
        rules = []
        
        # Check for excessive spacing
        if re.search(r'\s{3,}', content):
            rules.append(ValidationRule(
                rule_id="typography_excessive_spacing",
                rule_category="format",
                description="Contains excessive spacing",
                severity="info",
                status="warning",
                details="Normalize spacing throughout document",
                confidence_score=0.6
            ))
        
        # Check for consistent capitalization
        sentences = re.split(r'[.!?]+', content)
        inconsistent_capitalization = sum(1 for sentence in sentences if sentence.strip() and not sentence.strip()[0].isupper())
        
        if inconsistent_capitalization > len(sentences) * 0.1:  # More than 10% inconsistent
            rules.append(ValidationRule(
                rule_id="typography_inconsistent_capitalization",
                rule_category="format",
                description="Inconsistent sentence capitalization",
                severity="info",
                status="warning",
                details="Ensure consistent capitalization at sentence start",
                confidence_score=0.7
            ))
        
        return rules
    
    def _validate_layout(self, content: str) -> List[ValidationRule]:
        """Validate layout and visual structure."""
        rules = []
        
        # Check for consistent bullet points
        bullet_types = set(re.findall(r'([•·\*→])', content))
        if len(bullet_types) > 1:
            rules.append(ValidationRule(
                rule_id="layout_inconsistent_bullets",
                rule_category="format",
                description="Inconsistent bullet point styles",
                severity="info",
                status="warning",
                details="Use consistent bullet point style throughout",
                confidence_score=0.6
            ))
        
        return rules
    
    def _validate_accuracy(self, content: str) -> List[ValidationRule]:
        """Validate content accuracy."""
        rules = []
        
        # Check for common typos
        common_typos = ["teh", "adn", "recieve", "seperate", "occured"]
        found_typos = [typo for typo in common_typos if typo in content.lower()]
        
        if found_typos:
            rules.append(ValidationRule(
                rule_id="accuracy_common_typos",
                rule_category="content",
                description="Common typos detected",
                severity="warning",
                status="fail",
                details=f"Typos found: {', '.join(found_typos)}",
                confidence_score=0.8
            ))
        
        return rules
    
    def _validate_professionalism(self, content: str) -> List[ValidationRule]:
        """Validate professional tone."""
        rules = []
        
        # Check for slang or overly casual language
        slang_terms = ["gonna", "wanna", "kinda", "sorta", "yeah", "nah"]
        found_slang = [term for term in slang_terms if term in content.lower()]
        
        if found_slang:
            rules.append(ValidationRule(
                rule_id="professionalism_slang_detected",
                rule_category="content",
                description="Slang or casual language detected",
                severity="warning",
                status="fail",
                details=f"Slang terms: {', '.join(found_slang)}",
                confidence_score=0.7
            ))
        
        return rules
    
    def _validate_effectiveness(self, content: str) -> List[ValidationRule]:
        """Validate communication effectiveness."""
        rules = []
        
        # Check for clear opening statement
        if "summary" in content.lower():
            summary_section = re.search(r'##\s*summary\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
            if summary_section:
                summary_text = summary_section.group(1).strip()
                if len(summary_text.split()) < 30:  # Less than 30 words
                    rules.append(ValidationRule(
                        rule_id="effectiveness_weak_summary",
                        rule_category="content",
                        description="Summary section too brief",
                        severity="info",
                        status="warning",
                        details="Expand summary to better highlight qualifications",
                        confidence_score=0.6
                    ))
        
        return rules
    
    def _calculate_validation_result(self, rules: List[ValidationRule], strategy: Dict[str, Any]) -> ValidationResult:
        """Calculate overall validation result."""
        # Count rule statuses
        passed = sum(1 for rule in rules if rule.status == "pass")
        failed = sum(1 for rule in rules if rule.status == "fail")
        warnings = sum(1 for rule in rules if rule.status == "warning")
        
        # Calculate scores by category
        quality_rules = [rule for rule in rules if rule.rule_category == "quality"]
        compliance_rules = [rule for rule in rules if rule.rule_category == "compliance"]
        format_rules = [rule for rule in rules if rule.rule_category == "format"]
        content_rules = [rule for rule in rules if rule.rule_category == "content"]
        
        quality_score = self._calculate_category_score(quality_rules, strategy["thresholds"]["quality"])
        compliance_score = self._calculate_category_score(compliance_rules, strategy["thresholds"]["compliance"])
        format_score = self._calculate_category_score(format_rules, strategy["thresholds"]["format"])
        content_score = self._calculate_category_score(content_rules, strategy["thresholds"]["content"])
        
        # Determine overall status
        critical_issues = sum(1 for rule in rules if rule.severity == "critical" and rule.status == "fail")
        
        if critical_issues > 0:
            overall_status = "fail"
        elif failed > 0 and strategy["strict_mode"]:
            overall_status = "fail"
        elif failed > 3:
            overall_status = "fail"
        elif failed > 0 or warnings > 5:
            overall_status = "warning"
        else:
            overall_status = "pass"
        
        return ValidationResult(
            validation_id=f"validation_{len(rules)}",
            overall_status=overall_status,
            quality_score=quality_score,
            compliance_score=compliance_score,
            format_score=format_score,
            content_score=content_score,
            validation_rules=rules,
            recommendations=[],  # Will be filled separately
            metadata={
                "rules_checked": len(rules),
                "critical_issues": critical_issues,
                "strict_mode": strategy["strict_mode"]
            }
        )
    
    def _calculate_category_score(self, rules: List[ValidationRule], threshold: float) -> float:
        """Calculate score for a validation category."""
        if not rules:
            return 1.0
        
        passed = sum(1 for rule in rules if rule.status == "pass")
        total = len(rules)
        
        base_score = passed / total
        
        # Weight by confidence
        weighted_score = sum(rule.confidence_score for rule in rules if rule.status == "pass") / sum(rule.confidence_score for rule in rules) if rules else 0.0
        
        return (base_score + weighted_score) / 2
    
    def _generate_recommendations(self, rules: List[ValidationRule], result: ValidationResult) -> List[str]:
        """Generate improvement recommendations based on validation results."""
        recommendations = []
        
        # Group failed rules by category
        failed_rules = [rule for rule in rules if rule.status == "fail"]
        by_category = {}
        for rule in failed_rules:
            category = rule.rule_category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rule)
        
        # Generate recommendations for each category
        for category, category_rules in by_category.items():
            if category == "quality":
                recommendations.extend([
                    "Enhance content with more specific achievements and quantifiable results",
                    "Add missing required sections to improve completeness",
                    "Increase action verb usage to demonstrate impact"
                ])
            elif category == "compliance":
                recommendations.extend([
                    "Remove special characters to improve ATS compatibility",
                    "Review content for industry-standard terminology",
                    "Ensure all information is accurate and professional"
                ])
            elif category == "format":
                recommendations.extend([
                    "Standardize formatting elements for consistency",
                    "Improve document structure and organization",
                    "Optimize typography for better readability"
                ])
            elif category == "content":
                recommendations.extend([
                    "Proofread carefully to eliminate typos and grammatical errors",
                    "Enhance professional tone and language",
                    "Strengthen opening summary and key messages"
                ])
        
        # Add specific recommendations based on critical issues
        critical_rules = [rule for rule in failed_rules if rule.severity == "critical"]
        if critical_rules:
            recommendations.append("Address critical issues immediately before submission")
        
        return list(set(recommendations))[:10]  # Return top 10 unique recommendations
    
    def _calculate_validation_metrics(self, rules: List[ValidationRule]) -> ValidationMetrics:
        """Calculate validation performance metrics."""
        total_rules = len(rules)
        passed = sum(1 for rule in rules if rule.status == "pass")
        failed = sum(1 for rule in rules if rule.status == "fail")
        warnings = sum(1 for rule in rules if rule.status == "warning")
        critical = sum(1 for rule in rules if rule.severity == "critical" and rule.status == "fail")
        
        # Calculate overall confidence
        if rules:
            avg_confidence = sum(rule.confidence_score for rule in rules) / len(rules)
        else:
            avg_confidence = 0.0
        
        return ValidationMetrics(
            total_rules_checked=total_rules,
            rules_passed=passed,
            rules_failed=failed,
            rules_with_warnings=warnings,
            critical_issues=critical,
            validation_confidence=avg_confidence,
            processing_time_ms=500  # Placeholder
        )
    
    def _safe_record_telemetry(self, validation_output: ValidationOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k8_validate_executed", {
                    "rules_checked": validation_output.metrics.total_rules_checked,
                    "critical_issues": validation_output.metrics.critical_issues,
                    "overall_status": validation_output.validation_result.overall_status,
                    "success": validation_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_validation_summary(self, validation_output: ValidationOutput) -> Dict[str, Any]:
        """Get a summary of the validation execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k8_validate",
            "rules_checked": validation_output.metrics.total_rules_checked,
            "critical_issues": validation_output.metrics.critical_issues,
            "overall_status": validation_output.validation_result.overall_status,
            "quality_score": validation_output.validation_result.quality_score,
            "success": validation_output.success
        }





