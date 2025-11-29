"""
Resume Engine Validation Toolkit Module

Corollary to outreach_engine/l5/lic_validation_toolkit.py
Comprehensive validation utilities for resume processing and quality assurance.
"""

import re
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation checks."""
    CONTENT_QUALITY = "content_quality"
    FORMAT_COMPLIANCE = "format_compliance"
    DATA_INTEGRITY = "data_integrity"
    BUSINESS_RULES = "business_rules"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"


@dataclass
class ValidationIssue:
    """Individual validation issue found."""
    category: ValidationCategory
    level: ValidationLevel
    message: str
    field_name: Optional[str]
    line_number: Optional[int]
    suggestion: Optional[str]
    auto_fixable: bool = False


@dataclass
class ValidationReport:
    """Complete validation report for resume content."""
    is_valid: bool
    total_issues: int
    issues_by_level: Dict[ValidationLevel, int]
    issues_by_category: Dict[ValidationCategory, int]
    detailed_issues: List[ValidationIssue]
    validation_timestamp: datetime
    overall_score: float  # 0.0 to 1.0


class ResumeValidationToolkit:
    """Comprehensive validation toolkit for resume processing."""
    
    def __init__(self):
        self.content_validators = self._init_content_validators()
        self.format_validators = self._init_format_validators()
        self.integrity_validators = self._init_integrity_validators()
        self.business_validators = self._init_business_validators()
        self.security_validators = self._init_security_validators()
        self.accessibility_validators = self._init_accessibility_validators()
    
    def _init_content_validators(self) -> Dict[str, callable]:
        """Initialize content quality validators."""
        return {
            "spell_check": self._validate_spelling,
            "grammar_check": self._validate_grammar,
            "readability": self._validate_readability,
            "content_completeness": self._validate_content_completeness,
            "section_relevance": self._validate_section_relevance,
            "keyword_density": self._validate_keyword_density,
            "tone_consistency": self._validate_tone_consistency
        }
    
    def _init_format_validators(self) -> Dict[str, callable]:
        """Initialize format compliance validators."""
        return {
            "section_structure": self._validate_section_structure,
            "font_consistency": self._validate_font_consistency,
            "spacing": self._validate_spacing,
            "length_limits": self._validate_length_limits,
            "date_format": self._validate_date_format,
            "contact_format": self._validate_contact_format
        }
    
    def _init_integrity_validators(self) -> Dict[str, callable]:
        """Initialize data integrity validators."""
        return {
            "date_consistency": self._validate_date_consistency,
            "experience_timeline": self._validate_experience_timeline,
            "education_timeline": self._validate_education_timeline,
            "skill_experience_match": self._validate_skill_experience_match,
            "duplicate_content": self._validate_duplicate_content
        }
    
    def _init_business_validators(self) -> Dict[str, callable]:
        """Initialize business rule validators."""
        return {
            "experience_requirements": self._validate_experience_requirements,
            "education_requirements": self._validate_education_requirements,
            "skill_relevance": self._validate_skill_relevance,
            "achievement_quantification": self._validate_achievement_quantification,
            "industry_standards": self._validate_industry_standards
        }
    
    def _init_security_validators(self) -> Dict[str, callable]:
        """Initialize security validators."""
        return {
            "pii_detection": self._validate_pii_detection,
            "malicious_content": self._validate_malicious_content,
            "injection_attempts": self._validate_injection_attempts,
            "data_sanitization": self._validate_data_sanitization
        }
    
    def _init_accessibility_validators(self) -> Dict[str, callable]:
        """Initialize accessibility validators."""
        return {
            "screen_reader_friendly": self._validate_screen_reader_friendly,
            "color_contrast": self._validate_color_contrast,
            "font_size": self._validate_font_size,
            "alt_text": self._validate_alt_text
        }
    
    def validate_resume(self, resume_content: str, 
                       validation_categories: Optional[List[ValidationCategory]] = None) -> ValidationReport:
        """
        Perform comprehensive validation of resume content.
        
        Args:
            resume_content: Resume content to validate
            validation_categories: Specific categories to validate (all if None)
            
        Returns:
            Complete validation report
        """
        if validation_categories is None:
            validation_categories = list(ValidationCategory)
        
        all_issues = []
        
        # Content quality validation
        if ValidationCategory.CONTENT_QUALITY in validation_categories:
            content_issues = self._validate_content_quality(resume_content)
            all_issues.extend(content_issues)
        
        # Format compliance validation
        if ValidationCategory.FORMAT_COMPLIANCE in validation_categories:
            format_issues = self._validate_format_compliance(resume_content)
            all_issues.extend(format_issues)
        
        # Data integrity validation
        if ValidationCategory.DATA_INTEGRITY in validation_categories:
            integrity_issues = self._validate_data_integrity(resume_content)
            all_issues.extend(integrity_issues)
        
        # Business rules validation
        if ValidationCategory.BUSINESS_RULES in validation_categories:
            business_issues = self._validate_business_rules(resume_content)
            all_issues.extend(business_issues)
        
        # Security validation
        if ValidationCategory.SECURITY in validation_categories:
            security_issues = self._validate_security(resume_content)
            all_issues.extend(security_issues)
        
        # Accessibility validation
        if ValidationCategory.ACCESSIBILITY in validation_categories:
            accessibility_issues = self._validate_accessibility(resume_content)
            all_issues.extend(accessibility_issues)
        
        # Generate report
        return self._generate_validation_report(all_issues)
    
    def _validate_content_quality(self, content: str) -> List[ValidationIssue]:
        """Validate content quality aspects."""
        issues = []
        
        for validator_name, validator_func in self.content_validators.items():
            try:
                validator_issues = validator_func(content)
                issues.extend(validator_issues)
            except Exception as e:
                logger.error(f"Content validator {validator_name} failed: {e}")
        
        return issues
    
    def _validate_format_compliance(self, content: str) -> List[ValidationIssue]:
        """Validate format compliance."""
        issues = []
        
        for validator_name, validator_func in self.format_validators.items():
            try:
                validator_issues = validator_func(content)
                issues.extend(validator_issues)
            except Exception as e:
                logger.error(f"Format validator {validator_name} failed: {e}")
        
        return issues
    
    def _validate_data_integrity(self, content: str) -> List[ValidationIssue]:
        """Validate data integrity."""
        issues = []
        
        for validator_name, validator_func in self.integrity_validators.items():
            try:
                validator_issues = validator_func(content)
                issues.extend(validator_issues)
            except Exception as e:
                logger.error(f"Integrity validator {validator_name} failed: {e}")
        
        return issues
    
    def _validate_business_rules(self, content: str) -> List[ValidationIssue]:
        """Validate business rules."""
        issues = []
        
        for validator_name, validator_func in self.business_validators.items():
            try:
                validator_issues = validator_func(content)
                issues.extend(validator_issues)
            except Exception as e:
                logger.error(f"Business validator {validator_name} failed: {e}")
        
        return issues
    
    def _validate_security(self, content: str) -> List[ValidationIssue]:
        """Validate security aspects."""
        issues = []
        
        for validator_name, validator_func in self.security_validators.items():
            try:
                validator_issues = validator_func(content)
                issues.extend(validator_issues)
            except Exception as e:
                logger.error(f"Security validator {validator_name} failed: {e}")
        
        return issues
    
    def _validate_accessibility(self, content: str) -> List[ValidationIssue]:
        """Validate accessibility."""
        issues = []
        
        for validator_name, validator_func in self.accessibility_validators.items():
            try:
                validator_issues = validator_func(content)
                issues.extend(validator_issues)
            except Exception as e:
                logger.error(f"Accessibility validator {validator_name} failed: {e}")
        
        return issues
    
    def _validate_spelling(self, content: str) -> List[ValidationIssue]:
        """Validate spelling in resume content."""
        issues = []
        
        # Common spelling errors in resumes
        common_errors = {
            "mangement": "management",
            "resposible": "responsible",
            "acheivements": "achievements",
            "expierence": "experience",
            "sucessful": "successful",
            "proffesional": "professional",
            "deveolped": "developed",
            "anaylzed": "analyzed"
        }
        
        for wrong, correct in common_errors.items():
            if re.search(rf'\b{wrong}\b', content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_QUALITY,
                    level=ValidationLevel.WARNING,
                    message=f"Spelling error: '{wrong}' should be '{correct}'",
                    field_name=None,
                    line_number=None,
                    suggestion=f"Replace '{wrong}' with '{correct}'",
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_grammar(self, content: str) -> List[ValidationIssue]:
        """Validate grammar in resume content."""
        issues = []
        
        # Common grammar errors
        grammar_patterns = [
            (r'\bi\s+', "I should be capitalized", "Capitalize 'I'"),
            (r'\s+\.', "Space before period", "Remove space before period"),
            (r'\.\s+', "Multiple spaces after period", "Use single space after period"),
            (r'\b[a-z]\.([a-z]\.)+', "Lowercase abbreviations", "Capitalize abbreviations"),
        ]
        
        for pattern, message, suggestion in grammar_patterns:
            if re.search(pattern, content):
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_QUALITY,
                    level=ValidationLevel.WARNING,
                    message=message,
                    field_name=None,
                    line_number=None,
                    suggestion=suggestion,
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_readability(self, content: str) -> List[ValidationIssue]:
        """Validate readability of resume content."""
        issues = []
        
        # Check for very long sentences
        sentences = re.split(r'[.!?]+', content)
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 30:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_QUALITY,
                    level=ValidationLevel.WARNING,
                    message=f"Very long sentence detected ({len(sentence.split())} words)",
                    field_name=None,
                    line_number=i + 1,
                    suggestion="Consider breaking this into shorter sentences",
                    auto_fixable=False
                ))
        
        # Check for very short paragraphs
        paragraphs = content.split('\n\n')
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 0 and len(paragraph.strip()) < 50:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_QUALITY,
                    level=ValidationLevel.INFO,
                    message="Very short paragraph",
                    field_name=None,
                    line_number=i + 1,
                    suggestion="Consider expanding or combining with other paragraphs",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_content_completeness(self, content: str) -> List[ValidationIssue]:
        """Validate content completeness."""
        issues = []
        
        # Required sections
        required_sections = [
            "contact information",
            "summary",
            "experience",
            "education",
            "skills"
        ]
        
        content_lower = content.lower()
        
        for section in required_sections:
            if section not in content_lower:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_QUALITY,
                    level=ValidationLevel.ERROR,
                    message=f"Missing required section: {section}",
                    field_name=None,
                    line_number=None,
                    suggestion=f"Add a {section} section",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_section_relevance(self, content: str) -> List[ValidationIssue]:
        """Validate section relevance."""
        issues = []
        
        # Check for irrelevant sections
        irrelevant_patterns = [
            r"references available upon request",
            r"objective.*seeking.*position",
            r"hobbies.*interests",
            r"personal.*information"
        ]
        
        for pattern in irrelevant_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_QUALITY,
                    level=ValidationLevel.WARNING,
                    message="Potentially irrelevant content detected",
                    field_name=None,
                    line_number=None,
                    suggestion="Consider removing or updating this content",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_keyword_density(self, content: str) -> List[ValidationIssue]:
        """Validate keyword density."""
        issues = []
        
        # Check for keyword stuffing
        words = content.lower().split()
        word_count = len(words)
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Check for overused keywords
        for word, freq in word_freq.items():
            density = (freq / word_count) * 100
            if density > 5:  # More than 5% keyword density
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_QUALITY,
                    level=ValidationLevel.WARNING,
                    message=f"Keyword '{word}' appears too frequently ({density:.1f}% density)",
                    field_name=None,
                    line_number=None,
                    suggestion=f"Consider reducing usage of '{word}'",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_tone_consistency(self, content: str) -> List[ValidationIssue]:
        """Validate tone consistency."""
        issues = []
        
        # Check for inconsistent pronoun usage
        first_person = len(re.findall(r'\b(I|me|my|we|our)\b', content, re.IGNORECASE))
        third_person = len(re.findall(r'\b(he|she|they|his|her|their)\b', content, re.IGNORECASE))
        
        if first_person > 0 and third_person > 0:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_QUALITY,
                level=ValidationLevel.WARNING,
                message="Inconsistent pronoun usage (mix of first and third person)",
                field_name=None,
                line_number=None,
                suggestion="Use consistent first-person perspective throughout",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_section_structure(self, content: str) -> List[ValidationIssue]:
        """Validate section structure."""
        issues = []
        
        # Check for proper section headers
        section_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS headers
            r'^[A-Z][a-z\s]+:$',  # Title case with colon
            r'^\d+\.\s*[A-Z]'    # Numbered sections
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line and len(line) < 50:  # Potential header
                is_valid_header = any(re.match(pattern, line) for pattern in section_patterns)
                if not is_valid_header and not line.endswith('.'):
                    issues.append(ValidationIssue(
                        category=ValidationCategory.FORMAT_COMPLIANCE,
                        level=ValidationLevel.INFO,
                        message=f"Potential section header with non-standard format: '{line}'",
                        field_name=None,
                        line_number=i + 1,
                        suggestion="Use standard section header format (ALL CAPS or Title Case:)",
                        auto_fixable=False
                    ))
        
        return issues
    
    def _validate_font_consistency(self, content: str) -> List[ValidationIssue]:
        """Validate font consistency (for formatted resumes)."""
        issues = []
        
        # This would be more relevant for formatted documents
        # For text content, we check for inconsistent formatting markers
        
        # Check for mixed formatting styles
        has_bold = '**' in content or '__' in content
        has_italic = '*' in content or '_' in content
        has_caps = re.search(r'[A-Z]{4,}', content)
        
        formatting_count = sum([has_bold, has_italic, has_caps])
        
        if formatting_count > 2:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.WARNING,
                message="Multiple formatting styles detected - consider consistency",
                field_name=None,
                line_number=None,
                suggestion="Use consistent formatting throughout the resume",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_spacing(self, content: str) -> List[ValidationIssue]:
        """Validate spacing."""
        issues = []
        
        # Check for multiple consecutive spaces
        if re.search(r' {3,}', content):
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.WARNING,
                message="Multiple consecutive spaces detected",
                field_name=None,
                line_number=None,
                suggestion="Use single spaces between words",
                auto_fixable=True
            ))
        
        # Check for inconsistent line spacing
        lines = content.split('\n')
        empty_line_counts = []
        current_empty = 0
        
        for line in lines:
            if line.strip() == '':
                current_empty += 1
            else:
                if current_empty > 0:
                    empty_line_counts.append(current_empty)
                current_empty = 0
        
        if len(set(empty_line_counts)) > 1:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.INFO,
                message="Inconsistent line spacing detected",
                field_name=None,
                line_number=None,
                suggestion="Use consistent spacing between sections",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_length_limits(self, content: str) -> List[ValidationIssue]:
        """Validate length limits."""
        issues = []
        
        word_count = len(content.split())
        
        if word_count < 200:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.WARNING,
                message=f"Resume appears too short ({word_count} words)",
                field_name=None,
                line_number=None,
                suggestion="Consider adding more detail to your experience and achievements",
                auto_fixable=False
            ))
        elif word_count > 1000:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.WARNING,
                message=f"Resume appears too long ({word_count} words)",
                field_name=None,
                line_number=None,
                suggestion="Consider condensing content to focus on most relevant information",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_date_format(self, content: str) -> List[ValidationIssue]:
        """Validate date format consistency."""
        issues = []
        
        # Common date formats
        date_patterns = [
            (r'\b\d{1,2}/\d{1,2}/\d{4}\b', 'MM/DD/YYYY'),
            (r'\b\d{1,2}-\d{1,2}-\d{4}\b', 'MM-DD-YYYY'),
            (r'\b\w{3,9}\s\d{4}\b', 'Month YYYY'),
            (r'\b\w{3,9}\s\d{1,2},\s\d{4}\b', 'Month DD, YYYY')
        ]
        
        found_formats = []
        for pattern, format_name in date_patterns:
            if re.search(pattern, content):
                found_formats.append(format_name)
        
        if len(set(found_formats)) > 1:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.WARNING,
                message=f"Inconsistent date formats: {', '.join(found_formats)}",
                field_name=None,
                line_number=None,
                suggestion="Use consistent date format throughout the resume",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_contact_format(self, content: str) -> List[ValidationIssue]:
        """Validate contact information format."""
        issues = []
        
        # Email validation
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        
        if not emails:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.ERROR,
                message="No email address found",
                field_name="contact",
                line_number=None,
                suggestion="Add a professional email address",
                auto_fixable=False
            ))
        
        # Phone validation
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, content)
        
        if not phones:
            issues.append(ValidationIssue(
                category=ValidationCategory.FORMAT_COMPLIANCE,
                level=ValidationLevel.WARNING,
                message="No phone number found",
                field_name="contact",
                line_number=None,
                suggestion="Add a phone number",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_date_consistency(self, content: str) -> List[ValidationIssue]:
        """Validate date consistency."""
        issues = []
        
        # Extract dates and check for logical consistency
        # This is a simplified version - full implementation would parse dates
        
        # Check for future dates
        current_year = datetime.now().year
        future_dates = re.findall(r'\b(\d{4})\b', content)
        
        for year_str in future_dates:
            year = int(year_str)
            if year > current_year:
                issues.append(ValidationIssue(
                    category=ValidationCategory.DATA_INTEGRITY,
                    level=ValidationLevel.ERROR,
                    message=f"Future date detected: {year}",
                    field_name=None,
                    line_number=None,
                    suggestion="Verify date accuracy",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_experience_timeline(self, content: str) -> List[ValidationIssue]:
        """Validate experience timeline consistency."""
        issues = []
        
        # This would be more sophisticated in a full implementation
        # For now, check for obvious timeline issues
        
        # Look for overlapping dates or gaps
        # Simplified check for date patterns in experience sections
        
        return issues
    
    def _validate_education_timeline(self, content: str) -> List[ValidationIssue]:
        """Validate education timeline consistency."""
        issues = []
        
        # Check for logical education timeline
        # Education should typically precede work experience
        
        return issues
    
    def _validate_skill_experience_match(self, content: str) -> List[ValidationIssue]:
        """Validate that skills mentioned are supported by experience."""
        issues = []
        
        # Extract skills and experience
        # Check if skills are mentioned in experience sections
        
        return issues
    
    def _validate_duplicate_content(self, content: str) -> List[ValidationIssue]:
        """Validate for duplicate content."""
        issues = []
        
        # Check for duplicate sentences or phrases
        sentences = re.split(r'[.!?]+', content)
        sentence_counts = {}
        
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if len(sentence) > 20:  # Ignore short sentences
                sentence_counts[sentence] = sentence_counts.get(sentence, 0) + 1
        
        for sentence, count in sentence_counts.items():
            if count > 1:
                issues.append(ValidationIssue(
                    category=ValidationCategory.DATA_INTEGRITY,
                    level=ValidationLevel.WARNING,
                    message="Duplicate content detected",
                    field_name=None,
                    line_number=None,
                    suggestion="Remove duplicate sentences or phrases",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_experience_requirements(self, content: str) -> List[ValidationIssue]:
        """Validate experience meets typical requirements."""
        issues = []
        
        # Check for minimum experience details
        if "experience" in content.lower():
            # Look for quantified achievements
            if not re.search(r'\d+%|\$\d+|\d+\s*(years?|months?)', content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    category=ValidationCategory.BUSINESS_RULES,
                    level=ValidationLevel.WARNING,
                    message="Experience section lacks quantified achievements",
                    field_name="experience",
                    line_number=None,
                    suggestion="Add metrics and quantified results to experience descriptions",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_education_requirements(self, content: str) -> List[ValidationIssue]:
        """Validate education meets typical requirements."""
        issues = []
        
        # Check for education details
        if "education" in content.lower():
            # Look for degree information
            if not re.search(r'\b(bachelor|master|phd|degree|diploma|certificate)\b', content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    category=ValidationCategory.BUSINESS_RULES,
                    level=ValidationLevel.WARNING,
                    message="Education section lacks degree information",
                    field_name="education",
                    line_number=None,
                    suggestion="Add degree type and major information",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_skill_relevance(self, content: str) -> List[ValidationIssue]:
        """Validate skill relevance."""
        issues = []
        
        # Check for outdated or irrelevant skills
        outdated_skills = [
            "Windows XP",
            "Internet Explorer",
            "Flash",
            "FrontPage",
            "Netscape"
        ]
        
        for skill in outdated_skills:
            if skill.lower() in content.lower():
                issues.append(ValidationIssue(
                    category=ValidationCategory.BUSINESS_RULES,
                    level=ValidationLevel.INFO,
                    message=f"Potentially outdated skill: {skill}",
                    field_name="skills",
                    line_number=None,
                    suggestion="Consider removing or updating this skill",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_achievement_quantification(self, content: str) -> List[ValidationIssue]:
        """Validate achievement quantification."""
        issues = []
        
        # Check for unquantified achievements
        experience_section = re.search(r'experience[:\s]*(.*?)(?=\n\n|\n[A-Z]|\Z)', content, re.DOTALL | re.IGNORECASE)
        
        if experience_section:
            exp_content = experience_section.group(1)
            bullet_points = re.split(r'[-*•]\s*', exp_content)
            
            unquantified_count = 0
            for bullet in bullet_points:
                bullet = bullet.strip()
                if len(bullet) > 20 and not re.search(r'\d+|\$|%|times?|x', bullet, re.IGNORECASE):
                    unquantified_count += 1
            
            if unquantified_count > 3:
                issues.append(ValidationIssue(
                    category=ValidationCategory.BUSINESS_RULES,
                    level=ValidationLevel.WARNING,
                    message=f"Multiple unquantified achievements ({unquantified_count} bullet points)",
                    field_name="experience",
                    line_number=None,
                    suggestion="Add metrics, numbers, or specific results to achievements",
                    auto_fixable=False
                ))
        
        return issues
    
    def _validate_industry_standards(self, content: str) -> List[ValidationIssue]:
        """Validate industry standards compliance."""
        issues = []
        
        # Check for industry-specific requirements
        # This would be customized based on target industry
        
        return issues
    
    def _validate_pii_detection(self, content: str) -> List[ValidationIssue]:
        """Validate for PII that should be removed."""
        issues = []
        
        # PII patterns that should not be in resumes
        pii_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', "Social Security Number"),
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', "Credit Card Number"),
            (r'\b\d{3}-\d{3}-\d{4}\b', "Driver's License Number"),
            (r'\b[A-Z]{2}\d{7}\b', "Passport Number")
        ]
        
        for pattern, pii_type in pii_patterns:
            if re.search(pattern, content):
                issues.append(ValidationIssue(
                    category=ValidationCategory.SECURITY,
                    level=ValidationLevel.CRITICAL,
                    message=f"PII detected: {pii_type}",
                    field_name=None,
                    line_number=None,
                    suggestion="Remove sensitive personal information",
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_malicious_content(self, content: str) -> List[ValidationIssue]:
        """Validate for malicious content."""
        issues = []
        
        # Malicious patterns
        malicious_patterns = [
            (r'<script.*?>.*?</script>', "Script injection"),
            (r'javascript:', "JavaScript injection"),
            (r'data:text/html', "Data URI injection"),
            (r'eval\(', "Code evaluation")
        ]
        
        for pattern, threat_type in malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    category=ValidationCategory.SECURITY,
                    level=ValidationLevel.CRITICAL,
                    message=f"Malicious content detected: {threat_type}",
                    field_name=None,
                    line_number=None,
                    suggestion="Remove malicious content immediately",
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_injection_attempts(self, content: str) -> List[ValidationIssue]:
        """Validate for injection attempts."""
        issues = []
        
        # Injection patterns
        injection_patterns = [
            (r'\{\{.*\}\}', "Template injection"),
            (r'\$\{.*\}', "Expression injection"),
            (r';\s*(rm|del|format)', "Command injection"),
            (r'union\s+select', "SQL injection")
        ]
        
        for pattern, injection_type in injection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    category=ValidationCategory.SECURITY,
                    level=ValidationLevel.CRITICAL,
                    message=f"Injection attempt detected: {injection_type}",
                    field_name=None,
                    line_number=None,
                    suggestion="Remove injection attempts",
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_data_sanitization(self, content: str) -> List[ValidationIssue]:
        """Validate data sanitization."""
        issues = []
        
        # Check for unsanitized special characters
        special_chars = r'[<>&"\'()]'
        if re.search(special_chars, content):
            issues.append(ValidationIssue(
                category=ValidationCategory.SECURITY,
                level=ValidationLevel.WARNING,
                message="Unsanitized special characters detected",
                field_name=None,
                line_number=None,
                suggestion="Consider sanitizing special characters",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_screen_reader_friendly(self, content: str) -> List[ValidationIssue]:
        """Validate screen reader compatibility."""
        issues = []
        
        # Check for content that might not be screen reader friendly
        # This is more relevant for formatted documents
        
        return issues
    
    def _validate_color_contrast(self, content: str) -> List[ValidationIssue]:
        """Validate color contrast (for formatted resumes)."""
        issues = []
        
        # This would be more relevant for formatted documents
        # For text content, we check for color references
        
        return issues
    
    def _validate_font_size(self, content: str) -> List[ValidationIssue]:
        """Validate font size (for formatted resumes)."""
        issues = []
        
        # This would be more relevant for formatted documents
        
        return issues
    
    def _validate_alt_text(self, content: str) -> List[ValidationIssue]:
        """Validate alt text for images (for formatted resumes)."""
        issues = []
        
        # This would be more relevant for formatted documents
        
        return issues
    
    def _generate_validation_report(self, issues: List[ValidationIssue]) -> ValidationReport:
        """Generate comprehensive validation report."""
        # Count issues by level
        issues_by_level = {}
        for level in ValidationLevel:
            issues_by_level[level] = sum(1 for issue in issues if issue.level == level)
        
        # Count issues by category
        issues_by_category = {}
        for category in ValidationCategory:
            issues_by_category[category] = sum(1 for issue in issues if issue.category == category)
        
        # Calculate overall score
        total_issues = len(issues)
        critical_issues = issues_by_level.get(ValidationLevel.CRITICAL, 0)
        error_issues = issues_by_level.get(ValidationLevel.ERROR, 0)
        
        # Score calculation: 1.0 minus penalty for issues
        score = 1.0
        score -= (critical_issues * 0.2)  # Critical issues have high penalty
        score -= (error_issues * 0.1)     # Error issues have medium penalty
        score -= (total_issues * 0.01)    # General penalty for any issues
        score = max(0.0, score)  # Ensure score doesn't go negative
        
        is_valid = critical_issues == 0 and error_issues == 0
        
        return ValidationReport(
            is_valid=is_valid,
            total_issues=total_issues,
            issues_by_level=issues_by_level,
            issues_by_category=issues_by_category,
            detailed_issues=issues,
            validation_timestamp=datetime.now(),
            overall_score=score
        )


# Convenience functions for backward compatibility
def validate_resume_content(content: str, 
                           categories: Optional[List[ValidationCategory]] = None) -> ValidationReport:
    """Convenience function to validate resume content."""
    toolkit = ResumeValidationToolkit()
    return toolkit.validate_resume(content, categories)


def get_validation_summary(report: ValidationReport) -> str:
    """Get a human-readable summary of validation results."""
    if report.is_valid:
        return f"✅ Resume validation passed (Score: {report.overall_score:.2f})"
    else:
        critical = report.issues_by_level.get(ValidationLevel.CRITICAL, 0)
        errors = report.issues_by_level.get(ValidationLevel.ERROR, 0)
        warnings = report.issues_by_level.get(ValidationLevel.WARNING, 0)
        return f"❌ Resume validation failed (Score: {report.overall_score:.2f}): {critical} critical, {errors} errors, {warnings} warnings"
