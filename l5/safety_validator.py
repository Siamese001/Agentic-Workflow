"""L5 Safety Validator - Pure safety validation only."""

from typing import List
from dataclasses import dataclass
import re

@dataclass
class SafetyViolation:
    """Pure safety violation data - no business logic."""
    severity: str
    description: str
    policy_rule: str

class SafetyValidator:
    """Pure safety validation - no execution, no orchestration logic."""
    
    def __init__(self):
        self.policies = {
            'no_personal_info': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{3}\s\d{2}\s\d{4}\b',
            'no_prohibited_content': ['password', 'secret', 'private key'],
            'max_length': 50000
        }
    
    def validate_content(self, content: str) -> List[SafetyViolation]:
        """Validate content against safety policies - pure validation only."""
        violations = []
        
        # Check for personal information
        if re.search(self.policies['no_personal_info'], content):
            violations.append(SafetyViolation(
                severity='high',
                description='Personal information detected',
                policy_rule='no_personal_info'
            ))
        
        # Check for prohibited content
        content_lower = content.lower()
        for prohibited in self.policies['no_prohibited_content']:
            if prohibited in content_lower:
                violations.append(SafetyViolation(
                    severity='high',
                    description=f'Prohibited content: {prohibited}',
                    policy_rule='no_prohibited_content'
                ))
        
        # Check length
        if len(content) > self.policies['max_length']:
            violations.append(SafetyViolation(
                severity='medium',
                description='Content exceeds maximum length',
                policy_rule='max_length'
            ))
        
        return violations
    
    def is_safe(self, content: str) -> bool:
        """Check if content passes all safety validations."""
        violations = self.validate_content(content)
        return len(violations) == 0
