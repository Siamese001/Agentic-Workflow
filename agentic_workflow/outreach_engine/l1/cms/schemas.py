"""
CMS schemas for resume generation prompt validation.

Provides schema definitions for prompt validation to ensure
consistent resume improvement and job alignment.
"""

from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum


class PromptType(str, Enum):
    """
    Types of prompts supported by the CMS for resume generation.

    Defines prompt categories for consistent resume improvement workflows.
    """
    SIMPLE = "simple"
    TEMPLATE = "template"
    CONDITIONAL = "conditional"
    CHAINED = "chained"


@dataclass
class PromptSchema:
    """
    Schema definition for resume generation prompt validation.

    Ensures consistent prompt structure for improved resume quality.
    """
    name: str
    prompt_type: PromptType
    required_fields: List[str]
    optional_fields: List[str] = None
    validation_rules: Dict[str, Any] = None


@dataclass
class ValidationResult:
    """
    Result of resume generation prompt validation.

    Tracks validation outcomes for consistent resume improvement.
    """
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


def validate_prompt(prompt: str, schema: PromptSchema) -> ValidationResult:
    """
    Validates resume generation prompt against schema.

    Ensures prompt structure supports consistent resume improvement.
    """
    errors = []
    warnings = []
    
    # Basic validation logic
    if not prompt:
        errors.append("Prompt cannot be empty")
    
    # Check required fields based on schema
    if schema.prompt_type == PromptType.TEMPLATE:
        if "{" not in prompt or "}" not in prompt:
            errors.append("Template prompt must contain placeholder fields")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
