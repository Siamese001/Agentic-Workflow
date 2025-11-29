#!/usr/bin/env python3
"""
Resume Engine State Management
Immutable staging buffer, text sanitization, and validation context infrastructure
"""

import copy
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..utils.rg_models import ValidationResult, ValidationSeverity


# Exception classes
class StagingBufferError(Exception):
    """Exception raised for staging buffer operations"""
    pass


class ImmutableStagingBuffer:
    """Immutable staging buffer for storing resume generation data"""

    def __init__(self):
        self._data = {}
        self._locked = False
        self._lock_timestamp = None

    def set(self, key: str, value: Any):
        """Set a value in the buffer (only if not locked)"""
        if self._locked:
            raise StagingBufferError(f"Cannot set '{key}': buffer is locked")
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the buffer"""
        return self._data.get(key, default)

    def lock(self):
        """Lock the buffer to prevent further modifications"""
        if not self._locked:
            self._locked = True
            self._lock_timestamp = datetime.now().isoformat()

    def is_locked(self) -> bool:
        """Check if buffer is locked"""
        return self._locked

    @property
    def data(self) -> Dict:
        """Get a deep copy of the buffer data"""
        return copy.deepcopy(self._data)


# Default hyphenation rules data
HYPHENATION_RULES_DATA = {
    "rules": {
        "unnatural_hyphens_remove": [
            r'\b\w+(?:\-|–|—)\w+\b',  # Words with hyphens
            r'\b\w+(?:‑|‒|–|—|―)\w+\b',  # Various dash types
        ],
        "unnatural_hyphens_replace": [
            (r'\b(\w+)(?:\-|–|—)(\w+)\b', r'\1 \2'),  # Replace hyphens with spaces
        ],
        "placeholder_patterns": [
            r'\[.*?\]',  # [placeholder text]
            r'<.*?>',    # <placeholder text>
            r'\{.*?\}',  # {placeholder text}
        ]
    }
}


class TextSanitizer:
    """Enhanced text sanitizer with improved hyphenation and placeholder removal"""

    # Unicode characters to clean
    FORBIDDEN_DASHES: str = (
        "\u2012\u2013\u2014\u2015\u2212\uFE58\uFF0D\u2010\u2011"
        "\u2043\u2E3A\u2E3B\u30A0\u058A"
    )
    FORBIDDEN_INVISIBLE: str = (
        "\u00A0\u00AD\u200B\u200C\u200D\u200E\u202F\u2060\uFEFF"
    )
    
    # Compiled patterns
    FORBIDDEN_DASH_PATTERN = re.compile(f"[{FORBIDDEN_DASHES}]")
    FORBIDDEN_INVISIBLE_PATTERN = re.compile(f"[{FORBIDDEN_INVISIBLE}]")
    POTENTIAL_HYPHEN_PATTERN = re.compile(r'\b\w*(\-)\w*\b')

    def __init__(self, hyphenation_rules: Optional[Dict] = None):
        self.rules = hyphenation_rules or HYPHENATION_RULES_DATA

        if not isinstance(self.rules, dict) or 'rules' not in self.rules:
            raise ValueError("Invalid hyphenation rules format")

        self.unnatural_hyphens_remove = self.rules['rules'].get('unnatural_hyphens_remove', [])
        self.unnatural_hyphens_replace = self.rules['rules'].get('unnatural_hyphens_replace', [])
        self.placeholder_patterns = self.rules['rules'].get('placeholder_patterns', [])

    def sanitize_text(self, text: str) -> str:
        """Comprehensive text sanitization"""
        if not text:
            return text

        sanitized = text
        
        # Remove forbidden invisible characters
        sanitized = self.FORBIDDEN_INVISIBLE_PATTERN.sub('', sanitized)
        
        # Replace forbidden dashes with standard hyphens
        sanitized = self.FORBIDDEN_DASH_PATTERN.sub('-', sanitized)
        
        # Remove unnatural hyphens
        for pattern in self.unnatural_hyphens_remove:
            sanitized = re.sub(pattern, '', sanitized)
        
        # Replace unnatural hyphens with spaces
        for pattern, replacement in self.unnatural_hyphens_replace:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        # Remove placeholders
        for pattern in self.placeholder_patterns:
            sanitized = re.sub(pattern, '', sanitized)
        
        # Clean up extra whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized

    def sanitize_and_stage(self, artist_output: Dict) -> Dict:
        """Sanitize artist output and stage it in buffer"""
        staged_output = {}
        
        for section_key, content in artist_output.items():
            if isinstance(content, str):
                staged_output[section_key] = self.sanitize_text(content)
            elif isinstance(content, dict):
                staged_output[section_key] = {
                    k: self.sanitize_text(v) if isinstance(v, str) else v
                    for k, v in content.items()
                }
            elif isinstance(content, list):
                staged_output[section_key] = [
                    self.sanitize_text(item) if isinstance(item, str) else item
                    for item in content
                ]
            else:
                staged_output[section_key] = content
        
        return staged_output

    def _find_placeholders(self, text: str) -> List[str]:
        """Find placeholder patterns in text"""
        placeholders = []
        for pattern in self.placeholder_patterns:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)
        return placeholders

    def _unify_structure(self, section_key: str, content: Any) -> Dict:
        """Unify content structure for staging"""
        return {
            "section": section_key,
            "content": content,
            "sanitized": True,
            "timestamp": datetime.now().isoformat()
        }


class ValidationContext:
    """Validation context for managing validation state and results"""

    def __init__(self, validation_config: Optional[Dict] = None):
        self.validation_results: List[ValidationResult] = []
        self.validation_config = validation_config or {}
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)

    def add_validation_result(self, result: ValidationResult) -> None:
        """Add a validation result to the context"""
        self.validation_results.append(result)
        
        if result.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]:
            self.logger.warning(f"Validation {result.severity.value}: {result.message}")

    def get_failed_validations(self) -> List[ValidationResult]:
        """Get all failed validation results"""
        return [r for r in self.validation_results if not r.passed]

    def get_critical_failures(self) -> List[ValidationResult]:
        """Get critical validation failures"""
        return [r for r in self.validation_results 
                if not r.passed and r.severity == ValidationSeverity.CRITICAL]

    def get_high_failures(self) -> List[ValidationResult]:
        """Get high severity validation failures"""
        return [r for r in self.validation_results 
                if not r.passed and r.severity == ValidationSeverity.HIGH]

    def has_critical_failures(self) -> bool:
        """Check if there are any critical failures"""
        return len(self.get_critical_failures()) > 0

    def has_high_or_critical_failures(self) -> bool:
        """Check if there are any high or critical failures"""
        return len(self.get_critical_failures()) + len(self.get_high_failures()) > 0

    def get_validation_summary(self) -> Dict:
        """Get summary of validation results"""
        total = len(self.validation_results)
        passed = len([r for r in self.validation_results if r.passed])
        failed = total - passed
        
        severity_counts = {}
        for result in self.validation_results:
            severity = result.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0.0,
            "severity_breakdown": severity_counts,
            "critical_failures": len(self.get_critical_failures()),
            "high_failures": len(self.get_high_failures()),
            "validation_duration": (datetime.now() - self.start_time).total_seconds()
        }

    def clear_results(self) -> None:
        """Clear all validation results"""
        self.validation_results.clear()
        self.start_time = datetime.now()

    def export_results(self) -> List[Dict]:
        """Export validation results as dictionaries"""
        return [
            {
                "rule_id": r.rule_id,
                "passed": r.passed,
                "severity": r.severity.value,
                "message": r.message,
                "details": r.details
            }
            for r in self.validation_results
        ]


class RGStateManager:
    """Resume Generation State Manager - compatibility wrapper for runtime layer"""
    
    def __init__(self):
        """Initialize state manager with staging buffer and validation context"""
        self.staging_buffer = ImmutableStagingBuffer()
        self.validation_context = ValidationContext()
        self.workflow_states = {}
        self.logger = logging.getLogger(__name__)
    
    def create_workflow_state(self, workflow_id: str, input_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow state"""
        workflow_state = {
            "workflow_id": workflow_id,
            "input_parameters": input_parameters,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "staging_buffer": self.staging_buffer,
            "validation_context": self.validation_context
        }
        
        self.workflow_states[workflow_id] = workflow_state
        self.staging_buffer.set(f"workflow_{workflow_id}", workflow_state)
        
        self.logger.info(f"Created workflow state: {workflow_id}")
        return workflow_state
    
    def update_workflow_state(self, workflow_id: str, phase: str, data: Any) -> None:
        """Update workflow state with new phase data"""
        if workflow_id not in self.workflow_states:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_state = self.workflow_states[workflow_id]
        workflow_state["current_phase"] = phase
        workflow_state["phase_data"] = data
        workflow_state["updated_at"] = datetime.now().isoformat()
        
        # Store phase data in staging buffer
        self.staging_buffer.set(f"{workflow_id}_{phase}", data)
        
        self.logger.info(f"Updated workflow state {workflow_id} for phase: {phase}")
    
    def complete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Mark workflow as completed and return final state"""
        if workflow_id not in self.workflow_states:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_state = self.workflow_states[workflow_id]
        workflow_state["status"] = "completed"
        workflow_state["completed_at"] = datetime.now().isoformat()
        
        # Lock the staging buffer to prevent further modifications
        self.staging_buffer.lock()
        
        self.logger.info(f"Completed workflow: {workflow_id}")
        return workflow_state
    
    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow state"""
        return self.workflow_states.get(workflow_id)
    
    def get_validation_summary(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get validation summary for workflow"""
        if workflow_id in self.workflow_states:
            validation_context = self.workflow_states[workflow_id].get("validation_context")
            if validation_context:
                return validation_context.get_validation_summary()
        return None
