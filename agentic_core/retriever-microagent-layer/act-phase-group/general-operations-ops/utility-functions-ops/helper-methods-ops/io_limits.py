"""
L2 Tool Output Validator for resume processing security.

Validates tool outputs at L2 execution boundary to protect
resume improvement workflows from injection attacks.
"""

from __future__ import annotations

import re
import json
from typing import Any, List, Optional

from l2.interfaces import L2ToolOutputValidatorInterface, ToolOutputValidationResult


class L2ToolOutputValidator(L2ToolOutputValidatorInterface):
    """
    Concrete tool output validation for resume processing L2 layer.

    Defends against injection attacks by detecting and sanitizing
    malicious content in resume processing tool outputs.
    """
    
    # Injection patterns to detect in tool outputs
    INJECTION_PATTERNS = [
        # Prompt injection attempts
        (r'(?i)(ignore|forget|disregard).*(previous|above|earlier).*(instructions|prompts|rules)', 
         "prompt_override_attempt"),
        (r'(?i)(you are now|act as|pretend to be|roleplay as)', 
         "role_hijacking_attempt"),
        (r'(?i)(system prompt|hidden instructions|secret commands)', 
         "system_prompt_leak_attempt"),
        
        # Indirection injection (encoded content)
        (r'(?i)base64[:\s]*[A-Za-z0-9+/=]{20,}', 
         "base64_encoded_content"),
        (r'(?i)\\x[0-9a-fA-F]{2}', 
         "hex_encoded_content"),
        (r'(?i)&#x?[0-9a-fA-F]+;', 
         "html_entity_encoding"),
        
        # Command injection attempts
        (r'(?i)(exec|eval|system|subprocess|os\.)', 
         "code_execution_attempt"),
        (r'(?i)(\$\{|\{\{|<%|%>)', 
         "template_injection_attempt"),
        
        # Data exfiltration attempts
        (r'(?i)(api[_\s]?key|password|secret|token|credential)', 
         "sensitive_data_reference"),
    ]
    
    def __init__(self, strict_mode: bool = True):
        """
        Initializes resume processing tool output validator.

        Args:
            strict_mode: If True, reject outputs with detected threats.
        """
        self.strict_mode = strict_mode
        self._compiled_patterns = [
            (re.compile(pattern), threat_type) 
            for pattern, threat_type in self.INJECTION_PATTERNS
        ]
    
    def validate_tool_output(self, tool_name: str, output: Any) -> ToolOutputValidationResult:
        """
        Validates resume processing tool output for injection attacks.

        Protects resume improvement workflows from security threats.
        """
        # Convert output to string for pattern matching
        output_str = self._to_string(output)
        
        # Detect injection patterns
        detected_threats = self.detect_injection_patterns(output_str)
        
        if detected_threats:
            if self.strict_mode:
                return ToolOutputValidationResult(
                    is_safe=False,
                    original_output=output,
                    sanitized_output=None,
                    detected_threats=detected_threats,
                    confidence=0.9
                )
            else:
                # Sanitize and allow with warnings
                sanitized = self.sanitize_output(output)
                return ToolOutputValidationResult(
                    is_safe=True,
                    original_output=output,
                    sanitized_output=sanitized,
                    detected_threats=detected_threats,
                    confidence=0.7
                )
        
        return ToolOutputValidationResult(
            is_safe=True,
            original_output=output,
            sanitized_output=output,
            detected_threats=[],
            confidence=1.0
        )
    
    def sanitize_output(self, output: Any) -> Any:
        """
        Sanitizes resume processing tool output from malicious content.

        Protects resume improvement workflows from security threats.
        """
        if isinstance(output, str):
            return self._sanitize_string(output)
        elif isinstance(output, dict):
            return {k: self.sanitize_output(v) for k, v in output.items()}
        elif isinstance(output, list):
            return [self.sanitize_output(item) for item in output]
        else:
            return output
    
    def detect_injection_patterns(self, content: str) -> List[str]:
        """
        Detects injection patterns in resume processing tool outputs.

        Identifies security threats to protect resume workflows.
        """
        detected = []
        for compiled_pattern, threat_type in self._compiled_patterns:
            if compiled_pattern.search(content):
                detected.append(threat_type)
        return detected
    
    def _to_string(self, output: Any) -> str:
        """Converts resume processing output to string for pattern matching."""
        if isinstance(output, str):
            return output
        elif isinstance(output, (dict, list)):
            try:
                return json.dumps(output)
            except (TypeError, ValueError):
                return str(output)
        else:
            return str(output)
    
    def _sanitize_string(self, content: str) -> str:
        """Sanitizes resume processing string by removing dangerous patterns."""
        sanitized = content
        
        # Escape potential injection markers
        sanitized = sanitized.replace("{{", "{ {")
        sanitized = sanitized.replace("}}", "} }")
        sanitized = sanitized.replace("${", "$ {")
        sanitized = sanitized.replace("<%", "< %")
        sanitized = sanitized.replace("%>", "% >")
        
        # Remove base64-like long encoded strings (potential payloads)
        sanitized = re.sub(r'base64[:\s]*[A-Za-z0-9+/=]{50,}', '[REDACTED_ENCODED_CONTENT]', sanitized, flags=re.IGNORECASE)
        
        return sanitized


# Singleton instance for easy access
_default_validator: Optional[L2ToolOutputValidator] = None


def get_tool_output_validator(strict_mode: bool = True) -> L2ToolOutputValidator:
    """Get the default tool output validator instance."""
    global _default_validator
    if _default_validator is None:
        _default_validator = L2ToolOutputValidator(strict_mode=strict_mode)
    return _default_validator


def validate_tool_output(tool_name: str, output: Any) -> ToolOutputValidationResult:
    """
    Convenience function to validate tool output using default validator.
    
    Should be called by all L2 executors before returning results.
    """
    return get_tool_output_validator().validate_tool_output(tool_name, output)
