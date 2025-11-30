"""
Dependency and Prompt Injection Patterns

This module provides patterns and validators to detect and prevent various types of
injection attacks in prompts and dependencies.
"""

from typing import Dict, List, Pattern, Set, Optional, Tuple
import re
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class InjectionType(str, Enum):
    """Types of injection patterns to detect."""
    PROMPT_INJECTION = "prompt_injection"
    DEPENDENCY_CONFUSION = "dependency_confusion"
    CODE_INJECTION = "code_injection"
    COMMAND_INJECTION = "command_injection"
    SQL_INJECTION = "sql_injection"

class InjectionDetector:
    """Detects various types of injection patterns in text."""
    
    # Common patterns for prompt injection
    PROMPT_INJECTION_PATTERNS = [
        r'(?i)(ignore|forget|disregard|skip|stop|abort|halt|end|quit|exit)[\s\S]*(previous|prior|above|before|earlier|all|everything|all instructions)',
        r'(?i)(do not|don\'t|never|skip|ignore|forget|disregard|avoid)[\s\S]*(previous|prior|above|before|earlier|all|everything|instructions|rules|guidelines|policies)',
        r'(?i)(as a|act as|you are|you\'re|you are now|from now on|from this point)[\s\S]*(assistant|AI|model|agent|system|robot|bot|machine)',
    ]
    
    # Common patterns for dependency confusion
    DEPENDENCY_CONFUSION_PATTERNS = [
        r'(?i)(npm|pip|gem|nuget|maven|gradle|yarn|pnpm|composer|bundler|dotnet)',
        r'(?i)(install|add|update|upgrade|remove|uninstall)[\s\S]*(--save-dev|--global|-g|--production)',
    ]
    
    # Common patterns for code injection
    CODE_INJECTION_PATTERNS = [
        r'(?i)(eval\(|exec\(|compile\(|__import__\(|os\.system\()',
        r'(?i)(subprocess\.run\(|subprocess\.Popen\()',
    ]
    
    # Common patterns for command injection
    COMMAND_INJECTION_PATTERNS = [
        r'[;|&]\s*(rm -rf|wget|curl|bash|sh|python|perl|ruby|node|php)[\s|&]',
        r'(`|\$\()\s*(rm -rf|wget|curl|bash|sh|python|perl|ruby|node|php)',
    ]
    
    # Common patterns for SQL injection
    SQL_INJECTION_PATTERNS = [
        r'(?i)(select\s.*\sfrom|insert\s+into|update\s+\w+\s+set|delete\s+from\s+\w+|drop\s+table|truncate\s+table|union\s+select)',
        r'\'\s*(--|#|\/\*)[\s\S]*',
    ]
    
    def __init__(self):
        """Initialize the detector with compiled regex patterns."""
        self.patterns = {
            InjectionType.PROMPT_INJECTION: [re.compile(p, re.IGNORECASE) for p in self.PROMPT_INJECTION_PATTERNS],
            InjectionType.DEPENDENCY_CONFUSION: [re.compile(p, re.IGNORECASE) for p in self.DEPENDENCY_CONFUSION_PATTERNS],
            InjectionType.CODE_INJECTION: [re.compile(p, re.IGNORECASE) for p in self.CODE_INJECTION_PATTERNS],
            InjectionType.COMMAND_INJECTION: [re.compile(p, re.IGNORECASE) for p in self.COMMAND_INJECTION_PATTERNS],
            InjectionType.SQL_INJECTION: [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS],
        }
    
    def detect_injections(self, text: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        Detect potential injection patterns in the given text.
        
        Args:
            text: The text to analyze for injection patterns.
            
        Returns:
            A dictionary mapping injection types to lists of (start, end, matched_text) tuples.
        """
        results = {injection_type.value: [] for injection_type in InjectionType}
        
        for injection_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    results[injection_type].append((match.start(), match.end(), match.group(0)))
        
        return {k: v for k, v in results.items() if v}
    
    def contains_injection(self, text: str, injection_types: Optional[List[InjectionType]] = None) -> bool:
        """
        Check if the text contains any injection patterns.
        
        Args:
            text: The text to check.
            injection_types: Specific injection types to check for. If None, checks all types.
            
        Returns:
            True if any injection patterns are found, False otherwise.
        """
        if injection_types is None:
            injection_types = list(InjectionType)
        
        for injection_type in injection_types:
            for pattern in self.patterns[injection_type]:
                if pattern.search(text):
                    return True
        return False

# Singleton instance for easy import
injection_detector = InjectionDetector()

def validate_prompt_safety(prompt: str) -> Tuple[bool, Dict]:
    """
    Validate a prompt for potential injection attempts.
    
    Args:
        prompt: The prompt text to validate.
        
    Returns:
        A tuple of (is_safe, details) where details contains information about any detected issues.
    """
    detections = injection_detector.detect_injections(prompt)
    is_safe = not any(detections.values())
    
    return is_safe, {
        'is_safe': is_safe,
        'detections': detections,
        'suggestions': [
            'Avoid using commands that could modify system state',
            'Be cautious with user-provided input in prompts',
            'Use parameterized queries for database operations',
        ] if not is_safe else []
    }
