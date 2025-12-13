"""Input Sanitizer - Security Utility for Agentic Workflow.

This module provides a centralized sanitization utility that acts as a decontamination
chamber for all incoming data before it reaches the LLM context. Treat user input
like radioactive material - it must be sterilized before use.
"""

import json
import logging
import re
import xml.sax.saxutils
from typing import Dict, List, Any, Union

logger = logging.getLogger(__name__)


class SecurityIntegrityError(Exception):
    """Raised when input fails security validation."""
    pass


class InputSanitizer:
    """Stateless utility class for sanitizing all user input.
    
    Provides methods to sanitize XML, JSON, and text content to prevent
    prompt injection attacks and ensure system security.
    """
    
    # Attack pattern regexes for injection detection
    ATTACK_PATTERNS = [
        # Instruction override attempts
        r"(?i)(ignore previous instructions|system override|delete all files)",
        # Tag spoofing attempts
        r"(?i)(<SYSTEM_PRIME>|<DIRECTIVES>|</SYSTEM_PRIME>|</DIRECTIVES>)",
        # Role hijacking attempts
        r"(?i)(you are now|from now on you|act as a|pretend to be)",
        # Context boundary breaking
        r"(?i)(<END_CONTEXT>|</CONTEXT_DATA>|<NEW_DIRECTIVE>)",
        # JSON/XML tunneling
        r"(?i)(<script>|</script>|javascript:|data:)",
        # Control character injection
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        # Unicode control characters
        r"[\u200B-\u200D\uFEFF\u2060\u180E]",
    ]
    
    @staticmethod
    def sanitize_xml_content(content: str) -> str:
        """Sanitize XML content to prevent injection attacks.
        
        Args:
            content: Raw string content to sanitize
            
        Returns:
            Sanitized XML-safe string
        """
        if not isinstance(content, str):
            content = str(content)
        
        # First, escape XML special characters
        sanitized = xml.sax.saxutils.escape(content, entities={
            "'": "&apos;",
            '"': "&quot;"
        })
        
        # Remove control characters except newline (10) and tab (9)
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)
        
        # Remove Unicode control characters
        sanitized = re.sub(r"[\u200B-\u200D\uFEFF\u2060\u180E]", "", sanitized)
        
        # Log if any changes were made
        if sanitized != content:
            logger.warning("XML content sanitized - potential injection attempt detected")
            
        return sanitized
    
    @staticmethod
    def sanitize_json_content(content: Union[Dict, List, str]) -> str:
        """Sanitize JSON content to prevent XML tunneling attacks.
        
        Args:
            content: JSON object, list, or string to sanitize
            
        Returns:
            Sanitized JSON string with escaped angle brackets
        """
        # Convert to JSON string if not already
        if isinstance(content, (dict, list)):
            json_str = json.dumps(content, ensure_ascii=False)
        elif isinstance(content, str):
            json_str = content
        else:
            json_str = str(content)
        
        # Escape angle brackets to prevent XML tunneling
        json_str = json_str.replace("<", "\\u003c")
        json_str = json_str.replace(">", "\\u003e")
        
        # Remove control characters
        json_str = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", json_str)
        
        # Log if any changes were made
        if json_str != str(content):
            logger.warning("JSON content sanitized - potential XML tunneling detected")
            
        return json_str
    
    @staticmethod
    def validate_injection_safety(pattern_name: str, content: str) -> bool:
        """Validate content against known injection attack patterns.
        
        Args:
            pattern_name: Name of the pattern being validated
            content: Content to validate
            
        Returns:
            True if safe, False if suspicious patterns found
            
        Raises:
            SecurityIntegrityError: If dangerous patterns are detected
        """
        if not isinstance(content, str):
            content = str(content)
        
        # Check against all attack patterns
        for pattern in InputSanitizer.ATTACK_PATTERNS:
            if re.search(pattern, content):
                logger.error(
                    f"Security violation in pattern '{pattern_name}': "
                    f"matched injection pattern '{pattern}'"
                )
                raise SecurityIntegrityError(
                    f"Dangerous pattern detected in {pattern_name}: {pattern}"
                )
        
        return True
    
    @staticmethod
    def sanitize_context_data(context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all values in a context dictionary.
        
        Args:
            context: Dictionary with potentially unsafe values
            
        Returns:
            Sanitized context dictionary
        """
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")
        
        sanitized = {}
        for key, value in context.items():
            # Skip internal system keys
            if key.startswith("_"):
                sanitized[key] = value
                continue
                
            # Sanitize based on type
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_xml_content(value)
            elif isinstance(value, (dict, list)):
                # For complex types, convert to JSON and sanitize
                sanitized[key] = InputSanitizer.sanitize_json_content(value)
            else:
                # For other types, convert to string and sanitize
                sanitized[key] = InputSanitizer.sanitize_xml_content(str(value))
        
        return sanitized
    
    @staticmethod
    def validate_template_integrity(template: str, expected_tags: List[str]) -> bool:
        """Validate that template tags haven't been spoofed or duplicated.
        
        Args:
            template: The assembled template string
            expected_tags: List of expected tag names
            
        Returns:
            True if integrity is maintained
            
        Raises:
            SecurityIntegrityError: If tag integrity is compromised
        """
        # Count occurrences of each expected tag
        for tag in expected_tags:
            open_tag = f"<{tag}>"
            close_tag = f"</{tag}>"
            
            open_count = template.count(open_tag)
            close_count = template.count(close_tag)
            
            # Tags should appear exactly once
            if open_count != 1 or close_count != 1:
                raise SecurityIntegrityError(
                    f"Tag integrity violation: {tag} appears "
                    f"{open_count} open times and {close_count} close times"
                )
        
        # Check for unexpected system tags
        system_tags = ["SYSTEM_PRIME", "DIRECTIVES", "CONTEXT_DATA"]
        for tag in system_tags:
            if tag not in expected_tags:
                if f"<{tag}>" in template or f"</{tag}>" in template:
                    raise SecurityIntegrityError(
                        f"Unexpected system tag detected: {tag}"
                    )
        
        return True
    
    @staticmethod
    def validate_xml_structure(xml_string: str) -> bool:
        """Validate that XML is well-formed.
        
        Args:
            xml_string: XML string to validate
            
        Returns:
            True if XML is valid
            
        Raises:
            SecurityIntegrityError: If XML is malformed
        """
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(xml_string)
            return True
        except ET.ParseError as e:
            raise SecurityIntegrityError(f"Malformed XML detected: {e}")
    
    @staticmethod
    def sanitize_prompt_components(components: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive sanitization of all prompt components.
        
        Args:
            components: Dictionary of prompt components
            
        Returns:
            Fully sanitized components dictionary
        """
        sanitized = {}
        
        for key, value in components.items():
            # Skip metadata fields
            if key.startswith("_"):
                sanitized[key] = value
                continue
            
            # Validate field name
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                raise SecurityIntegrityError(f"Invalid field name: {key}")
            
            # Sanitize based on type
            if isinstance(value, str):
                # First validate for injection patterns
                InputSanitizer.validate_injection_safety(key, value)
                sanitized[key] = InputSanitizer.sanitize_xml_content(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_xml_content(str(item)) 
                    for item in value
                ]
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_context_data(value)
            else:
                sanitized[key] = InputSanitizer.sanitize_xml_content(str(value))
        
        return sanitized
