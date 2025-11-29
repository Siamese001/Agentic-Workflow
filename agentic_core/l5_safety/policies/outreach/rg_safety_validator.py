#!/usr/bin/env python3
"""
L5 Safety Layer - Resume Generator Safety Validator
Enforces safety constraints and validation rules from ATOMIC_RG_SPEC
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import re
import uuid

# RG_capabilities is now at root level - no sys.path manipulation needed
from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC

class SafetyViolation(BaseModel):
    """Individual safety violation record"""
    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    violation_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    location: str  # Where in the resume the violation was found
    detected_at: datetime = Field(default_factory=datetime.now)
    rule_violated: str
    suggested_fix: Optional[str] = None

class SafetyReport(BaseModel):
    """Comprehensive safety validation report"""
    report_id: str = Field(default_factory=lambda: f"safety_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    overall_safety_score: float = Field(default=1.0, ge=0.0, le=1.0)
    is_safe: bool = Field(default=True)
    violations: List[SafetyViolation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    compliance_status: Dict[str, bool] = Field(default_factory=dict)
    validation_timestamp: datetime = Field(default_factory=datetime.now)
    recommendations: List[str] = Field(default_factory=list)

class ContentSafetyValidator:
    """Validates content safety and truthfulness"""
    
    def __init__(self):
        self.validators = ATOMIC_RG_SPEC.get("validators", {})
        self.constraints = ATOMIC_RG_SPEC.get("constraints", {})
    
    def validate_content_truthfulness(self, resume_content: Dict[str, Any]) -> List[SafetyViolation]:
        """Validate content truthfulness and detect potential issues"""
        violations = []
        
        # Extract text content for analysis
        content_text = self._extract_resume_text(resume_content)
        
        # Check for exaggerated claims
        violations.extend(self._check_exaggerated_claims(content_text))
        
        # Check for unverifiable metrics
        violations.extend(self._check_unverifiable_metrics(content_text))
        
        # Check for absolute claims
        violations.extend(self._check_absolute_claims(content_text))
        
        return violations
    
    def validate_ats_compliance(self, resume_content: Dict[str, Any]) -> List[SafetyViolation]:
        """Validate ATS compliance"""
        violations = []
        
        # Check for ATS-unfriendly formatting
        violations.extend(self._check_ats_formatting(resume_content))
        
        # Check for keyword stuffing
        violations.extend(self._check_keyword_stuffing(resume_content))
        
        # Check for proper structure
        violations.extend(self._check_resume_structure(resume_content))
        
        return violations
    
    def validate_constraint_adherence(self, resume_content: Dict[str, Any]) -> List[SafetyViolation]:
        """Validate adherence to constraints"""
        violations = []
        
        # Check length constraints
        violations.extend(self._check_length_constraints(resume_content))
        
        # Check content constraints
        violations.extend(self._check_content_constraints(resume_content))
        
        # Check formatting constraints
        violations.extend(self._check_formatting_constraints(resume_content))
        
        return violations
    
    def validate_personal_information_safety(self, resume_content: Dict[str, Any]) -> List[SafetyViolation]:
        """Validate personal information is handled safely"""
        violations = []
        
        # Check for excessive personal information
        violations.extend(self._check_excessive_personal_info(resume_content))
        
        # Check for sensitive data exposure
        violations.extend(self._check_sensitive_data_exposure(resume_content))
        
        return violations
    
    def _extract_resume_text(self, content: Any) -> str:
        """Extract all text content from resume"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            text_parts = []
            
            def extract_from_dict(d):
                for key, value in d.items():
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                text_parts.append(item)
                            elif isinstance(item, dict):
                                extract_from_dict(item)
                    elif isinstance(value, dict):
                        extract_from_dict(value)
            
            extract_from_dict(content)
            return " ".join(text_parts)
        
        return str(content)
    
    def _check_exaggerated_claims(self, text: str) -> List[SafetyViolation]:
        """Check for exaggerated or unrealistic claims"""
        violations = []
        
        exaggerated_patterns = [
            (r"world's best", "high", "Unverifiable superlative claim"),
            (r"revolutionized|revolutionary", "medium", "Potentially exaggerated impact claim"),
            (r"single-handedly", "medium", "Unlikely solo achievement claim"),
            (r"perfect|never failed|always successful", "high", "Absolute success claim"),
            (r"increased by \d{3,}%", "high", "Unrealistic percentage increase"),
            (r"saved \$\d{3,} million", "high", "Unverifiable large financial impact")
        ]
        
        text_lower = text.lower()
        
        for pattern, severity, description in exaggerated_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="exaggerated_claim",
                    severity=severity,
                    description=description,
                    location=f"Text position {match.start()}-{match.end()}",
                    rule_violated="truthfulness_validation",
                    suggested_fix="Use more conservative, verifiable language"
                )
                violations.append(violation)
        
        return violations
    
    def _check_unverifiable_metrics(self, text: str) -> List[SafetyViolation]:
        """Check for metrics that cannot be verified"""
        violations = []
        
        unverifiable_patterns = [
            (r"increased efficiency by \d+%", "medium", "Efficiency metric without baseline"),
            (r"reduced costs by \$\d+", "medium", "Cost reduction without context"),
            (r"improved.*by \d+x", "medium", "Multiplicative improvement without basis")
        ]
        
        text_lower = text.lower()
        
        for pattern, severity, description in unverifiable_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="unverifiable_metric",
                    severity=severity,
                    description=description,
                    location=f"Text position {match.start()}-{match.end()}",
                    rule_violated="metric_validation",
                    suggested_fix="Provide context or baseline for metrics"
                )
                violations.append(violation)
        
        return violations
    
    def _check_absolute_claims(self, text: str) -> List[SafetyViolation]:
        """Check for absolute claims that are likely false"""
        violations = []
        
        absolute_patterns = [
            (r"never.*failed", "medium", "Absolute negative claim"),
            (r"always.*succeeded", "medium", "Absolute positive claim"),
            (r"every.*project", "medium", "Universal claim"),
            (r"all.*clients", "medium", "Universal client claim")
        ]
        
        text_lower = text.lower()
        
        for pattern, severity, description in absolute_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="absolute_claim",
                    severity=severity,
                    description=description,
                    location=f"Text position {match.start()}-{match.end()}",
                    rule_violated="absolute_claim_validation",
                    suggested_fix="Use more nuanced language"
                )
                violations.append(violation)
        
        return violations
    
    def _check_ats_formatting(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check for ATS-unfriendly formatting"""
        violations = []
        
        # Check for non-standard characters
        text = self._extract_resume_text(content)
        non_standard_chars = re.findall(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\/\n\t]', text)
        
        if len(non_standard_chars) > 10:
            violation = SafetyViolation(
                violation_type="ats_formatting",
                severity="medium",
                description="Excessive non-standard characters that may confuse ATS",
                location="Throughout document",
                rule_violated="ats_formatting_rules",
                suggested_fix="Use standard ASCII characters and simple formatting"
            )
            violations.append(violation)
        
        return violations
    
    def _check_keyword_stuffing(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check for keyword stuffing"""
        violations = []
        
        text = self._extract_resume_text(content)
        words = text.lower().split()
        
        # Check for excessive repetition of keywords
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Flag words that appear too frequently
        for word, count in word_counts.items():
            if count > 10 and len(word) > 6:  # Long words repeated many times
                violation = SafetyViolation(
                    violation_type="keyword_stuffing",
                    severity="medium",
                    description=f"Potential keyword stuffing: '{word}' appears {count} times",
                    location="Throughout document",
                    rule_violated="keyword_optimization_rules",
                    suggested_fix="Reduce repetition of keywords"
                )
                violations.append(violation)
        
        return violations
    
    def _check_resume_structure(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check for proper resume structure"""
        violations = []
        
        # Check for required sections
        required_sections = ["contact_info", "experience", "education"]
        text = self._extract_resume_text(content).lower()
        
        for section in required_sections:
            if section not in text:
                violation = SafetyViolation(
                    violation_type="missing_section",
                    severity="high",
                    description=f"Missing required section: {section}",
                    location="Document structure",
                    rule_violated="structure_requirements",
                    suggested_fix=f"Add {section} section to resume"
                )
                violations.append(violation)
        
        return violations
    
    def _check_length_constraints(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check length constraints"""
        violations = []
        
        text = self._extract_resume_text(content)
        word_count = len(text.split())
        
        # Check maximum length constraint
        max_length = self.constraints.get("max_resume_length", 1000)
        if word_count > max_length:
            violation = SafetyViolation(
                violation_type="length_constraint",
                severity="medium",
                description=f"Resume exceeds maximum length: {word_count} words (max: {max_length})",
                location="Document length",
                rule_violated="length_constraints",
                suggested_fix=f"Reduce resume to {max_length} words or less"
            )
            violations.append(violation)
        
        return violations
    
    def _check_content_constraints(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check content-specific constraints"""
        violations = []
        
        # Check for prohibited content
        text = self._extract_resume_text(content)
        
        prohibited_patterns = [
            (r"social security number|ssn", "critical", "Personal identification number"),
            (r"driver's license|license number", "high", "Driver's license number"),
            (r"bank account|account number", "critical", "Financial account information"),
            (r"password|pin", "critical", "Password or PIN information")
        ]
        
        text_lower = text.lower()
        
        for pattern, severity, description in prohibited_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="prohibited_content",
                    severity=severity,
                    description=description,
                    location=f"Text position {match.start()}-{match.end()}",
                    rule_violated="content_constraints",
                    suggested_fix="Remove sensitive personal information"
                )
                violations.append(violation)
        
        return violations
    
    def _check_formatting_constraints(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check formatting constraints"""
        violations = []
        
        # Check for consistent formatting
        text = self._extract_resume_text(content)
        
        # Check for excessive use of special characters
        special_char_count = len(re.findall(r'[^\w\s]', text))
        total_chars = len(text)
        
        if total_chars > 0 and special_char_count / total_chars > 0.1:
            violation = SafetyViolation(
                violation_type="formatting_constraint",
                severity="low",
                description="Excessive use of special characters",
                location="Document formatting",
                rule_violated="formatting_constraints",
                suggested_fix="Reduce use of special characters for cleaner formatting"
            )
            violations.append(violation)
        
        return violations
    
    def _check_excessive_personal_info(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check for excessive personal information"""
        violations = []
        
        text = self._extract_resume_text(content)
        
        # Check for potentially excessive personal details
        personal_patterns = [
            (r"marital status|married|single|divorced", "medium", "Marital status information"),
            (r"date of birth|born|age \d+", "medium", "Age or birth date information"),
            (r"gender|sex|male|female", "low", "Gender information"),
            (r"religion|religious", "medium", "Religious information")
        ]
        
        text_lower = text.lower()
        
        for pattern, severity, description in personal_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="excessive_personal_info",
                    severity=severity,
                    description=description,
                    location=f"Text position {match.start()}-{match.end()}",
                    rule_violated="privacy_constraints",
                    suggested_fix="Remove unnecessary personal information"
                )
                violations.append(violation)
        
        return violations
    
    def _check_sensitive_data_exposure(self, content: Dict[str, Any]) -> List[SafetyViolation]:
        """Check for sensitive data exposure"""
        violations = []
        
        text = self._extract_resume_text(content)
        
        # Check for potential sensitive data patterns
        sensitive_patterns = [
            (r"\b\d{3}-\d{2}-\d{4}\b", "critical", "Potential SSN pattern"),
            (r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "high", "Potential credit card pattern"),
            (r"\b\d{10}\b", "medium", "Potential phone number without formatting")
        ]
        
        for pattern, severity, description in sensitive_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                violation = SafetyViolation(
                    violation_type="sensitive_data_exposure",
                    severity=severity,
                    description=description,
                    location=f"Text position {match.start()}-{match.end()}",
                    rule_violated="data_protection_rules",
                    suggested_fix="Remove or mask sensitive data"
                )
                violations.append(violation)
        
        return violations

class RGSafetyValidator:
    """Main Resume Generator Safety Validator - L5 safety layer"""
    
    def __init__(self):
        self.validators = ATOMIC_RG_SPEC.get("validators", {})
        self.constraints = ATOMIC_RG_SPEC.get("constraints", {})
        self.content_validator = ContentSafetyValidator()
        
        # Safety thresholds
        self.safety_thresholds = {
            "min_safety_score": 0.7,
            "max_critical_violations": 0,
            "max_high_violations": 2,
            "max_medium_violations": 5
        }
    
    def validate_resume_safety(self, 
                              resume_content: Dict[str, Any],
                              job_context: Optional[Dict[str, Any]] = None) -> SafetyReport:
        """
        Perform comprehensive safety validation
        
        Args:
            resume_content: Resume content to validate
            job_context: Optional job context for contextual validation
            
        Returns:
            Comprehensive safety report
        """
        
        # Initialize safety report
        safety_report = SafetyReport()
        
        # Perform all safety checks
        violations = []
        
        # Content truthfulness validation
        violations.extend(self.content_validator.validate_content_truthfulness(resume_content))
        
        # ATS compliance validation
        violations.extend(self.content_validator.validate_ats_compliance(resume_content))
        
        # Constraint adherence validation
        violations.extend(self.content_validator.validate_constraint_adherence(resume_content))
        
        # Personal information safety validation
        violations.extend(self.content_validator.validate_personal_information_safety(resume_content))
        
        # Group violations by severity
        critical_violations = [v for v in violations if v.severity == "critical"]
        high_violations = [v for v in violations if v.severity == "high"]
        medium_violations = [v for v in violations if v.severity == "medium"]
        
        # Calculate safety score
        safety_report.violations = violations
        safety_report.overall_safety_score = self._calculate_safety_score(violations)
        
        # Determine if resume is safe
        safety_report.is_safe = self._is_resume_safe(
            safety_report.overall_safety_score,
            len(critical_violations),
            len(high_violations),
            len(medium_violations)
        )
        
        # Set compliance status
        safety_report.compliance_status = {
            "ats_compliant": len([v for v in violations if v.rule_violated == "ats_formatting_rules"]) == 0,
            "constraints_satisfied": len([v for v in violations if v.rule_violated == "length_constraints"]) == 0,
            "content_safe": len([v for v in violations if v.violation_type == "prohibited_content"]) == 0,
            "truthful": len([v for v in violations if v.violation_type == "exaggerated_claim"]) == 0
        }
        
        # Generate recommendations
        safety_report.recommendations = self._generate_safety_recommendations(violations)
        
        # Add warnings for non-critical issues
        safety_report.warnings = [v.description for v in violations if v.severity in ["low", "medium"]]
        
        return safety_report
    
    def _calculate_safety_score(self, violations: List[SafetyViolation]) -> float:
        """Calculate overall safety score based on violations"""
        base_score = 1.0
        
        # Deduct points based on violation severity
        for violation in violations:
            if violation.severity == "critical":
                base_score -= 0.3
            elif violation.severity == "high":
                base_score -= 0.2
            elif violation.severity == "medium":
                base_score -= 0.1
            elif violation.severity == "low":
                base_score -= 0.05
        
        return max(0.0, base_score)
    
    def _is_resume_safe(self, 
                        safety_score: float,
                        critical_count: int,
                        high_count: int,
                        medium_count: int) -> bool:
        """Determine if resume meets safety criteria"""
        
        if safety_score < self.safety_thresholds["min_safety_score"]:
            return False
        
        if critical_count > self.safety_thresholds["max_critical_violations"]:
            return False
        
        if high_count > self.safety_thresholds["max_high_violations"]:
            return False
        
        if medium_count > self.safety_thresholds["max_medium_violations"]:
            return False
        
        return True
    
    def _generate_safety_recommendations(self, violations: List[SafetyViolation]) -> List[str]:
        """Generate safety recommendations based on violations"""
        recommendations = []
        
        # Group violations by type
        violation_types = {}
        for violation in violations:
            if violation.violation_type not in violation_types:
                violation_types[violation.violation_type] = []
            violation_types[violation.violation_type].append(violation)
        
        # Generate recommendations for each violation type
        for violation_type, type_violations in violation_types.items():
            if violation_type == "exaggerated_claim":
                recommendations.append("Review and moderate exaggerated claims with more conservative, verifiable language")
            elif violation_type == "prohibited_content":
                recommendations.append("Remove all sensitive personal information (SSN, account numbers, etc.)")
            elif violation_type == "ats_formatting":
                recommendations.append("Simplify formatting to improve ATS compatibility")
            elif violation_type == "length_constraint":
                recommendations.append("Reduce resume length to meet specified constraints")
            elif violation_type == "keyword_stuffing":
                recommendations.append("Reduce keyword repetition and focus on natural language")
            elif violation_type == "sensitive_data_exposure":
                recommendations.append("Remove or mask any sensitive data patterns")
        
        return list(set(recommendations))  # Remove duplicates
    
    def get_safety_summary(self, safety_report: SafetyReport) -> Dict[str, Any]:
        """Get summary of safety validation results"""
        
        violation_counts = {}
        for violation in safety_report.violations:
            violation_counts[violation.severity] = violation_counts.get(violation.severity, 0) + 1
        
        return {
            "report_id": safety_report.report_id,
            "overall_safety_score": safety_report.overall_safety_score,
            "is_safe": safety_report.is_safe,
            "total_violations": len(safety_report.violations),
            "violation_breakdown": violation_counts,
            "compliance_status": safety_report.compliance_status,
            "recommendations_count": len(safety_report.recommendations),
            "warnings_count": len(safety_report.warnings),
            "validation_timestamp": safety_report.validation_timestamp.isoformat()
        }





