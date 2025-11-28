"""
L2 Tool Output Validator - Defends against Tool Injection (ID 7)

Validates all tool outputs at the L2 execution boundary before they
propagate to L1 planning or L3 orchestration layers.

Layer: L2 (Execution)
Injection Type: Tool Injection Defense (ID 7)
"""

from __future__ import annotations

import re
import json
from typing import Any, List, Optional

from l2.interfaces import L2ToolOutputValidatorInterface, ToolOutputValidationResult


class L2ToolOutputValidator(L2ToolOutputValidatorInterface):
    """
    Concrete implementation of tool output validation for L2 layer.
    
    Defends against Tool Injection by detecting and sanitizing malicious
    content in tool outputs before they reach L1/L3 layers.
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
        Initialize the tool output validator.
        
        Args:
            strict_mode: If True, reject outputs with any detected threats.
                        If False, sanitize and allow with warnings.
        """
        self.strict_mode = strict_mode
        self._compiled_patterns = [
            (re.compile(pattern), threat_type) 
            for pattern, threat_type in self.INJECTION_PATTERNS
        ]
    
    def validate_tool_output(self, tool_name: str, output: Any) -> ToolOutputValidationResult:
        """
        Validate tool output for potential injection attacks.
        
        Must be called by all L2 executors before returning results.
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
        Sanitize tool output by removing or escaping potentially malicious content.
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
        Detect injection patterns in string content from tool outputs.
        """
        detected = []
        for compiled_pattern, threat_type in self._compiled_patterns:
            if compiled_pattern.search(content):
                detected.append(threat_type)
        return detected
    
    def _to_string(self, output: Any) -> str:
        """Convert any output to string for pattern matching."""
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
        """Sanitize a string by escaping or removing dangerous patterns."""
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
