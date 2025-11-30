"""
resume_app/validators – app_resume_input_validator.py

Apps layer input validator with LIC compliance (LinkedIn character limits, formatting).
Validates resume generation requests against LinkedIn platform requirements and business rules.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class ValidationResult:
    """Validation result with detailed feedback"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    compliance_score: float = 100.0
    platform: str = "linkedin"
    validated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationRule:
    """Individual validation rule definition"""
    name: str
    description: str
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None
    required: bool = True
    severity: str = "error"  # "error", "warning", "info"


class ResumeInputValidator:
    """Apps layer resume input validator with LIC compliance

    Validates resume generation requests against LinkedIn platform requirements
    including character limits, formatting rules, and content guidelines.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.platform = "linkedin"

        # LinkedIn (LIC) compliance limits
        self.limits = {
            "summary_max_chars": 2000,
            "summary_min_chars": 50,
            "bullet_max_chars": 600,
            "bullet_min_chars": 10,
            "title_max_chars": 100,
            "title_min_chars": 5,
            "company_max_chars": 100,
            "role_max_chars": 100,
            "max_bullets_per_experience": 5,
            "max_experiences": 10,
            "max_skills_per_category": 50
        }

        # Content validation patterns
        self.patterns = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "phone": r'^[\+]?[1-9][\d]{0,15}$',
            "linkedin_url": r'^https?://(www\.)?linkedin\.com/.+$',
            "name": r'^[a-zA-Z\s\-\.\']+$',
            "bullet_format": r'^[A-Z][a-zA-Z\s\-\,\.\d\%\$\+\#\@\(\)]+$'
        }

        # Initialize validation rules
        self._initialize_validation_rules()

    def validate_resume_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """Validate complete resume generation request"""
        result = ValidationResult()

        try:
            # Validate required fields
            self._validate_required_fields(request_data, result)

            # Validate personal information
            self._validate_personal_info(request_data, result)

            # Validate professional summary
            self._validate_summary(request_data, result)

            # Validate experience section
            self._validate_experience(request_data, result)

            # Validate skills section
            self._validate_skills(request_data, result)

            # Validate contact information
            self._validate_contact_info(request_data, result)

            # Calculate compliance score
            result.compliance_score = self._calculate_compliance_score(result)

            result.is_valid = len(result.errors) == 0

        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation system error: {str(e)}")

        return result

    def validate_bullet_points(self, bullets: List[str]) -> ValidationResult:
        """Validate individual bullet points against LinkedIn limits"""
        result = ValidationResult()

        for i, bullet in enumerate(bullets):
            bullet_result = self._validate_single_bullet(bullet, f"bullet_{i+1}")
            result.errors.extend(bullet_result.errors)
            result.warnings.extend(bullet_result.warnings)

        # Check bullet count limits
        if len(bullets) > self.limits["max_bullets_per_experience"]:
            result.errors.append(
                f"Too many bullet points ({len(bullets)}). "
                f"LinkedIn requires max {self.limits['max_bullets_per_experience']} per experience."
            )

        result.is_valid = len(result.errors) == 0
        result.compliance_score = self._calculate_compliance_score(result)

        return result

    def validate_job_targeting(self, target_role: str, experience_level: str,
                             job_description: Optional[str] = None) -> ValidationResult:
        """Validate job targeting information"""
        result = ValidationResult()

        # Validate target role
        if not target_role or len(target_role.strip()) < self.limits["title_min_chars"]:
            result.errors.append("Target role is required and must be at least 5 characters")
        elif len(target_role) > self.limits["title_max_chars"]:
            result.errors.append(
                f"Target role too long ({len(target_role)} chars). "
                f"Max: {self.limits['title_max_chars']}"
            )

        # Validate experience level
        valid_levels = ["entry", "junior", "mid", "senior", "lead", "principal", "executive"]
        if experience_level.lower() not in valid_levels:
            result.warnings.append(
                f"Experience level '{experience_level}' may not be standard. "
                f"Valid levels: {', '.join(valid_levels)}"
            )

        # Validate job description if provided
        if job_description:
            if len(job_description) > 5000:  # Reasonable limit for job descriptions
                result.warnings.append("Job description is very long, may impact processing")

        result.is_valid = len(result.errors) == 0
        result.compliance_score = self._calculate_compliance_score(result)

        return result

    def _initialize_validation_rules(self):
        """Initialize validation rules for different sections"""
        self.validation_rules = {
            "personal_info": [
                ValidationRule(
                    name="name_required",
                    description="Full name is required",
                    pattern=self.patterns["name"],
                    required=True,
                    severity="error"
                ),
                ValidationRule(
                    name="name_length",
                    description="Name length validation",
                    min_length=2,
                    max_length=50,
                    required=True,
                    severity="error"
                )
            ],
            "summary": [
                ValidationRule(
                    name="summary_length",
                    description="Professional summary length",
                    min_length=self.limits["summary_min_chars"],
                    max_length=self.limits["summary_max_chars"],
                    required=True,
                    severity="error"
                )
            ],
            "bullet": [
                ValidationRule(
                    name="bullet_length",
                    description="Bullet point length",
                    min_length=self.limits["bullet_min_chars"],
                    max_length=self.limits["bullet_max_chars"],
                    required=True,
                    severity="error"
                ),
                ValidationRule(
                    name="bullet_format",
                    description="Bullet point format (starts with capital)",
                    pattern=self.patterns["bullet_format"],
                    required=True,
                    severity="warning"
                )
            ]
        }

    def _validate_required_fields(self, request_data: Dict[str, Any], result: ValidationResult):
        """Validate required fields are present"""
        required_fields = ["target_role", "experience_level"]

        for required_field in required_fields:
            if required_field not in request_data or not request_data[required_field]:
                result.errors.append(f"Required field '{required_field}' is missing or empty")

    def _validate_personal_info(self, request_data: Dict[str, Any], result: ValidationResult):
        """Validate personal information"""
        personal_info = request_data.get("personal_info", {})

        # Validate name
        name = personal_info.get("name", "")
        if not name:
            result.errors.append("Personal name is required")
        elif len(name) < 2:
            result.errors.append("Name must be at least 2 characters long")
        elif len(name) > 50:
            result.errors.append("Name must be less than 50 characters long")
        elif not re.match(self.patterns["name"], name):
            result.warnings.append("Name contains unusual characters")

    def _validate_summary(self, request_data: Dict[str, Any], result: ValidationResult):
        """Validate professional summary (optional for generation requests)"""
        summary = request_data.get("professional_summary", "")

        # Summary is optional for generation requests - only validate if provided
        if summary:
            if len(summary) < self.limits["summary_min_chars"]:
                result.errors.append(
                    f"Summary too short ({len(summary)} chars). "
                    f"Minimum: {self.limits['summary_min_chars']}"
                )
            elif len(summary) > self.limits["summary_max_chars"]:
                result.errors.append(
                    f"Summary too long ({len(summary)} chars). "
                    f"Maximum: {self.limits['summary_max_chars']}"
                )
        # If summary is not provided, that's fine - it will be generated

    def _validate_experience(self, request_data: Dict[str, Any], result: ValidationResult):
        """Validate professional experience section"""
        experiences = request_data.get("professional_experience", [])

        if not experiences:
            result.errors.append("At least one professional experience is required")
        else:
            if len(experiences) > self.limits["max_experiences"]:
                result.warnings.append(
                    f"Too many experiences ({len(experiences)}). "
                    f"LinkedIn recommends max {self.limits['max_experiences']}."
                )

            for i, exp in enumerate(experiences):
                self._validate_single_experience(exp, f"experience_{i+1}", result)

    def _validate_single_experience(self, experience: Dict[str, Any], prefix: str, result: ValidationResult):
        """Validate a single experience entry"""
        # Validate company
        company = experience.get("company", "")
        if not company:
            result.errors.append(f"{prefix}: Company name is required")
        elif len(company) > self.limits["company_max_chars"]:
            result.errors.append(
                f"{prefix}: Company name too long ({len(company)} chars). "
                f"Max: {self.limits['company_max_chars']}"
            )

        # Validate role/title
        role = experience.get("title", "")
        if not role:
            result.errors.append(f"{prefix}: Job title is required")
        elif len(role) > self.limits["role_max_chars"]:
            result.errors.append(
                f"{prefix}: Job title too long ({len(role)} chars). "
                f"Max: {self.limits['role_max_chars']}"
            )

        # Validate bullet points
        bullets = experience.get("bullet_pool", experience.get("highlights", []))
        if bullets:
            bullet_result = self.validate_bullet_points(bullets)
            for error in bullet_result.errors:
                result.errors.append(f"{prefix}: {error}")
            for warning in bullet_result.warnings:
                result.warnings.append(f"{prefix}: {warning}")

    def _validate_skills(self, request_data: Dict[str, Any], result: ValidationResult):
        """Validate skills section"""
        skills = request_data.get("skills", {})

        for category, skill_list in skills.items():
            if len(skill_list) > self.limits["max_skills_per_category"]:
                result.warnings.append(
                    f"Skills category '{category}' has too many items ({len(skill_list)}). "
                    f"Max: {self.limits['max_skills_per_category']}"
                )

    def _validate_contact_info(self, request_data: Dict[str, Any], result: ValidationResult):
        """Validate contact information"""
        contact = request_data.get("contact_info", {})

        # Validate email if provided
        email = contact.get("email", "")
        if email and not re.match(self.patterns["email"], email):
            result.errors.append("Invalid email format")

        # Validate phone if provided
        phone = contact.get("phone", "")
        if phone and not re.match(self.patterns["phone"], phone.replace("-", "").replace(" ", "")):
            result.warnings.append("Phone number format may be invalid")

        # Validate LinkedIn URL if provided
        linkedin_url = contact.get("linkedin_url", "")
        if linkedin_url and not re.match(self.patterns["linkedin_url"], linkedin_url):
            result.errors.append("Invalid LinkedIn URL format")

    def _validate_single_bullet(self, bullet: str, prefix: str) -> ValidationResult:
        """Validate a single bullet point"""
        result = ValidationResult()

        if not bullet:
            result.errors.append(f"{prefix}: Bullet point cannot be empty")
        else:
            if len(bullet) < self.limits["bullet_min_chars"]:
                result.errors.append(
                    f"{prefix}: Bullet too short ({len(bullet)} chars). "
                    f"Minimum: {self.limits['bullet_min_chars']}"
                )
            elif len(bullet) > self.limits["bullet_max_chars"]:
                result.errors.append(
                    f"{prefix}: Bullet too long ({len(bullet)} chars). "
                    f"Maximum: {self.limits['bullet_max_chars']}"
                )

            # Check if bullet starts with action verb (LinkedIn best practice)
            action_verbs = [
                "Led", "Developed", "Implemented", "Created", "Managed",
                "Achieved", "Improved", "Increased", "Reduced", "Designed",
                "Built", "Launched", "Optimized", "Streamlined", "Coordinated"
            ]

            first_word = bullet.split()[0] if bullet.split() else ""
            if first_word not in action_verbs:
                result.warnings.append(
                    f"{prefix}: Bullet should start with action verb. "
                    f"Consider: {', '.join(action_verbs[:5])}..."
                )

        return result

    def _calculate_compliance_score(self, result: ValidationResult) -> float:
        """Calculate LinkedIn compliance score based on errors and warnings"""
        base_score = 100.0

        # Deduct points for errors (10 points each)
        error_penalty = len(result.errors) * 10

        # Deduct points for warnings (2 points each)
        warning_penalty = len(result.warnings) * 2

        score = max(0.0, base_score - error_penalty - warning_penalty)
        return round(score, 1)

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation rules and limits"""
        return {
            "platform": self.platform,
            "limits": self.limits,
            "validation_rules_count": sum(len(rules) for rules in self.validation_rules.values()),
            "supported_sections": list(self.validation_rules.keys()),
            "validator_version": "1.0.0"
        }

