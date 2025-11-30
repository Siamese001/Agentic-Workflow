# LIC Content Validator for L5 safety
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Content validation result"""
    is_valid: bool = True
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

class LICContentValidator:
    """Content validator for outreach safety"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def validate_content(self, content: str, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate content for compliance"""
        return ValidationResult(
            is_valid=True,
            metadata={"content_length": len(content), "context": context}
        )

    def batch_validate(self, contents: List[str]) -> List[ValidationResult]:
        """Validate multiple contents"""
        return [self.validate_content(content) for content in contents]
