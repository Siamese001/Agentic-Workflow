"""
Shared Validation Utilities
LEVEL 5 - Common validation functions and classes shared across engines
"""

import logging
import re
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationResult(BaseModel):
    """Result of a validation operation"""
    is_valid: bool = Field(..., description="Whether the validation passed")
    level: ValidationLevel = Field(..., description="Severity level of the validation result")
    message: str = Field(..., description="Validation message")
    field: Optional[str] = Field(None, description="Field that was validated")
    value: Optional[Any] = Field(None, description="Value that was validated")
    suggestion: Optional[str] = Field(None, description="Suggestion for fixing validation issues")

    class Config:
        use_enum_values = True

class ValidationReport(BaseModel):
    """Comprehensive validation report"""
    overall_valid: bool = Field(..., description="Whether all validations passed")
    results: List[ValidationResult] = Field(..., description="List of validation results")
    error_count: int = Field(..., description="Number of error-level failures")
    warning_count: int = Field(..., description="Number of warning-level failures")
    info_count: int = Field(..., description="Number of info-level results")
    validation_timestamp: str = Field(..., description="When validation was performed")
    processing_time_ms: float = Field(..., description="Time taken to validate in milliseconds")

class ValidationUtils:
    """Shared validation utilities for both engines"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Common validation patterns
        self.email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
        self.phone_pattern = re.compile(r'^\+?1[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
        self.url_pattern = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$')
        self.name_pattern = re.compile(r'^[A-Za-z\s\-\'\.]{2,50}$')
        self.linkedin_pattern = re.compile(r'^https?://(?:www\.)?linkedin\.com/in/[\w\-]+/?$')
        self.github_pattern = re.compile(r'^https?://(?:www\.)?github\.com/[\w\-]+/?$')

    async def validate_email(self, email: str, field_name: str = "email") -> ValidationResult:
        """Validate email address"""
        try:
            if not email:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Email is required",
                    field=field_name,
                    suggestion="Please provide a valid email address"
                )

            if not isinstance(email, str):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Email must be a string",
                    field=field_name,
                    value=email,
                    suggestion="Ensure email is provided as a string"
                )

            email = email.strip()

            if not self.email_pattern.match(email):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Invalid email format",
                    field=field_name,
                    value=email,
                    suggestion="Please provide a valid email address (e.g., user@example.com)"
                )

            # Additional checks
            if email.count('@') != 1:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Email must contain exactly one @ symbol",
                    field=field_name,
                    value=email
                )

            local, domain = email.split('@')

            if len(local) < 1 or len(domain) < 4:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message="Email format may be incomplete",
                    field=field_name,
                    value=email
                )

            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Email is valid",
                field=field_name,
                value=email
            )

        except Exception as e:
            self.logger.error(f"Error validating email: {e}")
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Email validation failed: {str(e)}",
                field=field_name,
                value=email
            )

    async def validate_phone(self, phone: str, field_name: str = "phone") -> ValidationResult:
        """Validate phone number"""
        try:
            if not phone:
                return ValidationResult(
                    is_valid=True,  # Phone is often optional
                    level=ValidationLevel.INFO,
                    message="Phone number not provided",
                    field=field_name
                )

            if not isinstance(phone, str):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Phone must be a string",
                    field=field_name,
                    value=phone
                )

            phone = phone.strip()

            # Remove common formatting characters for validation
            clean_phone = re.sub(r'[^\d+]', '', phone)

            if len(clean_phone) < 10 or len(clean_phone) > 15:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message="Phone number length appears unusual",
                    field=field_name,
                    value=phone,
                    suggestion="Ensure phone number has 10-15 digits"
                )

            if not self.phone_pattern.match(phone):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message="Phone number format may be non-standard",
                    field=field_name,
                    value=phone,
                    suggestion="Use format: +1 (555) 123-4567 or 555-123-4567"
                )

            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Phone number is valid",
                field=field_name,
                value=phone
            )

        except Exception as e:
            self.logger.error(f"Error validating phone: {e}")
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Phone validation failed: {str(e)}",
                field=field_name,
                value=phone
            )

    async def validate_url(self, url: str, field_name: str = "url",
                          allowed_schemes: Optional[List[str]] = None) -> ValidationResult:
        """Validate URL"""
        try:
            if not url:
                return ValidationResult(
                    is_valid=True,  # URL is often optional
                    level=ValidationLevel.INFO,
                    message="URL not provided",
                    field=field_name
                )

            if not isinstance(url, str):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="URL must be a string",
                    field=field_name,
                    value=url
                )

            url = url.strip()

            if not self.url_pattern.match(url):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Invalid URL format",
                    field=field_name,
                    value=url,
                    suggestion="Please provide a valid URL (e.g., https://example.com)"
                )

            # Check scheme
            if allowed_schemes:
                scheme = url.split('://')[0] if '://' in url else None
                if scheme not in allowed_schemes:
                    return ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.WARNING,
                        message=f"URL scheme '{scheme}' may not be allowed",
                        field=field_name,
                        value=url,
                        suggestion=f"Use one of: {', '.join(allowed_schemes)}"
                    )

            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="URL is valid",
                field=field_name,
                value=url
            )

        except Exception as e:
            self.logger.error(f"Error validating URL: {e}")
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"URL validation failed: {str(e)}",
                field=field_name,
                value=url
            )

    async def validate_name(self, name: str, field_name: str = "name",
                           min_length: int = 2, max_length: int = 50) -> ValidationResult:
        """Validate person name"""
        try:
            if not name:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name.title()} is required",
                    field=field_name,
                    suggestion=f"Please provide a valid {field_name}"
                )

            if not isinstance(name, str):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name.title()} must be a string",
                    field=field_name,
                    value=name
                )

            name = name.strip()

            if len(name) < min_length:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name.title()} is too short",
                    field=field_name,
                    value=name,
                    suggestion=f"{field_name.title()} must be at least {min_length} characters"
                )

            if len(name) > max_length:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"{field_name.title()} is quite long",
                    field=field_name,
                    value=name,
                    suggestion=f"Consider abbreviating {field_name} to under {max_length} characters"
                )

            if not self.name_pattern.match(name):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"{field_name.title()} contains unusual characters",
                    field=field_name,
                    value=name,
                    suggestion=f"Use only letters, spaces, hyphens, and apostrophes in {field_name}"
                )

            # Check for common issues
            if name.count(' ') > 4:  # Too many spaces
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"{field_name.title()} may contain extra spaces",
                    field=field_name,
                    value=name
                )

            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"{field_name.title()} is valid",
                field=field_name,
                value=name
            )

        except Exception as e:
            self.logger.error(f"Error validating name: {e}")
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"{field_name.title()} validation failed: {str(e)}",
                field=field_name,
                value=name
            )

    async def validate_text_length(self, text: str, field_name: str,
                                  min_length: int = 0, max_length: int = 10000) -> ValidationResult:
        """Validate text length constraints"""
        try:
            if not isinstance(text, str):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name.title()} must be a string",
                    field=field_name,
                    value=text
                )

            text_length = len(text.strip())

            if text_length < min_length:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{field_name.title()} is too short",
                    field=field_name,
                    value=text,
                    suggestion=f"{field_name.title()} must be at least {min_length} characters"
                )

            if text_length > max_length:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=f"{field_name.title()} exceeds maximum length",
                    field=field_name,
                    value=text,
                    suggestion=f"{field_name.title()} should be under {max_length} characters"
                )

            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"{field_name.title()} length is valid",
                field=field_name,
                value=text
            )

        except Exception as e:
            self.logger.error(f"Error validating text length: {e}")
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Length validation failed: {str(e)}",
                field=field_name,
                value=text
            )

    async def validate_social_profile(self, profile_url: str, platform: str,
                                     field_name: str = "social_profile") -> ValidationResult:
        """Validate social media profile URLs"""
        try:
            if not profile_url:
                return ValidationResult(
                    is_valid=True,  # Social profiles are often optional
                    level=ValidationLevel.INFO,
                    message=f"{platform.title()} profile not provided",
                    field=field_name
                )

            if not isinstance(profile_url, str):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"{platform.title()} profile must be a string",
                    field=field_name,
                    value=profile_url
                )

            profile_url = profile_url.strip()

            # Platform-specific validation
            if platform.lower() == "linkedin":
                if not self.linkedin_pattern.match(profile_url):
                    return ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.WARNING,
                        message="LinkedIn profile URL format is non-standard",
                        field=field_name,
                        value=profile_url,
                        suggestion="Use format: https://www.linkedin.com/in/username"
                    )

            elif platform.lower() == "github":
                if not self.github_pattern.match(profile_url):
                    return ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.WARNING,
                        message="GitHub profile URL format is non-standard",
                        field=field_name,
                        value=profile_url,
                        suggestion="Use format: https://github.com/username"
                    )

            else:
                # Generic URL validation for other platforms
                url_result = await self.validate_url(profile_url, field_name)
                if not url_result.is_valid:
                    return url_result

            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message=f"{platform.title()} profile URL is valid",
                field=field_name,
                value=profile_url
            )

        except Exception as e:
            self.logger.error(f"Error validating social profile: {e}")
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Social profile validation failed: {str(e)}",
                field=field_name,
                value=profile_url
            )

    async def validate_date(self, date_string: str, field_name: str = "date") -> ValidationResult:
        """Validate date string"""
        try:
            if not date_string:
                return ValidationResult(
                    is_valid=True,  # Dates are often optional
                    level=ValidationLevel.INFO,
                    message="Date not provided",
                    field=field_name
                )

            if not isinstance(date_string, str):
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Date must be a string",
                    field=field_name,
                    value=date_string
                )

            date_string = date_string.strip()

            # Try to parse different date formats
            date_formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%B %d, %Y",
                "%b %d, %Y",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y %H:%M:%S"
            ]

            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_string, fmt)
                    break
                except ValueError:
                    continue

            if not parsed_date:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Date format is not recognized",
                    field=field_name,
                    value=date_string,
                    suggestion="Use formats: YYYY-MM-DD, MM/DD/YYYY, or Month DD, YYYY"
                )

            # Check if date is in the future (for most use cases)
            if parsed_date > datetime.now():
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message="Date is in the future",
                    field=field_name,
                    value=date_string,
                    suggestion="Please verify the date is correct"
                )

            # Check if date is too old (before 1900)
            if parsed_date.year < 1900:
                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message="Date is unusually old",
                    field=field_name,
                    value=date_string,
                    suggestion="Please verify the date is correct"
                )

            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Date is valid",
                field=field_name,
                value=date_string
            )

        except Exception as e:
            self.logger.error(f"Error validating date: {e}")
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Date validation failed: {str(e)}",
                field=field_name,
                value=date_string
            )

    async def validate_required_fields(self, data: Dict[str, Any],
                                     required_fields: List[str]) -> List[ValidationResult]:
        """Validate that required fields are present and not empty"""
        results = []

        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Required field '{field}' is missing or empty",
                    field=field,
                    suggestion=f"Please provide a value for '{field}'"
                ))
            else:
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.INFO,
                    message=f"Required field '{field}' is present",
                    field=field,
                    value=data[field]
                ))

        return results

    async def validate_data_consistency(self, data: Dict[str, Any],
                                       consistency_rules: Dict[str, Callable]) -> List[ValidationResult]:
        """Validate data consistency using custom rules"""
        results = []

        for field, rule in consistency_rules.items():
            try:
                if field in data:
                    is_valid, message = rule(data[field], data)
                    results.append(ValidationResult(
                        is_valid=is_valid,
                        level=ValidationLevel.WARNING if is_valid else ValidationLevel.ERROR,
                        message=message,
                        field=field,
                        value=data[field]
                    ))
            except Exception as e:
                self.logger.error(f"Error in consistency rule for {field}: {e}")
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Consistency validation failed for {field}: {str(e)}",
                    field=field,
                    value=data.get(field)
                ))

        return results

    async def generate_validation_report(self, validation_results: List[ValidationResult]) -> ValidationReport:
        """Generate a comprehensive validation report"""
        start_time = datetime.utcnow()

        error_count = sum(1 for r in validation_results if r.level == ValidationLevel.ERROR and not r.is_valid)
        warning_count = sum(1 for r in validation_results if r.level == ValidationLevel.WARNING and not r.is_valid)
        info_count = sum(1 for r in validation_results if r.level == ValidationLevel.INFO)

        overall_valid = error_count == 0

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return ValidationReport(
            overall_valid=overall_valid,
            results=validation_results,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            validation_timestamp=datetime.utcnow().isoformat(),
            processing_time_ms=round(processing_time, 2)
        )

    async def validate_profile_data(self, profile_data: Dict[str, Any]) -> ValidationReport:
        """Comprehensive profile data validation"""
        results = []

        # Required fields validation
        required_fields = ["name", "email"]
        required_results = await self.validate_required_fields(profile_data, required_fields)
        results.extend(required_results)

        # Field-specific validation
        if "name" in profile_data:
            name_result = await self.validate_name(profile_data["name"], "name")
            results.append(name_result)

        if "email" in profile_data:
            email_result = await self.validate_email(profile_data["email"], "email")
            results.append(email_result)

        if "phone" in profile_data:
            phone_result = await self.validate_phone(profile_data["phone"], "phone")
            results.append(phone_result)

        if "linkedin" in profile_data:
            linkedin_result = await self.validate_social_profile(
                profile_data["linkedin"], "linkedin", "linkedin"
            )
            results.append(linkedin_result)

        if "github" in profile_data:
            github_result = await self.validate_social_profile(
                profile_data["github"], "github", "github"
            )
            results.append(github_result)

        # Generate report
        return await self.generate_validation_report(results)
