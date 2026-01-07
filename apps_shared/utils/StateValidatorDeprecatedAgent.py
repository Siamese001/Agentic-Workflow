"""
StateValidatorDeprecatedAgent - Extracted for 1:1 sovereign file structure.
Deprecated agent preserved for backward compatibility.
"""
from __future__ import annotations
import json
import os
import hashlib
from pathlib import Path

# Legacy class - use StateValidatorAgent instead
class StateValidatorDeprecatedAgent(HealerMixin, MCPHardenedMixin):
    """
    Validates state files against expected schemas
    """
    
    # Expected schemas for each HOP
    SCHEMAS = {
        "HOP-1": {
            "required_fields": ["Archetype", "confidence", "reasoning", "key_indicators"],
            "archetype_values": ["C_LEVEL", "EXECUTIVE", "SENIOR_TA", "RECRUITER"]
        },
        "HOP-2": {
            "required_fields": ["recipient_insights", "company_context", "rag_results"],
            "rag_result_fields": ["source", "SourceType", "text"]
        },
        "HOP-3": {
            "required_fields": ["team_members", "products", "case_studies"],
        },
        "HOP-4": {
            "required_fields": ["Route", "reasoning"],
            "route_values": ["INMAIL", "CONNECTION_REQ", "EMAIL", "FOLLOW_UP"]
        },
        "HOP-4.5": {
            "required_fields": ["Route", "Archetype", "sections", "constraints"],
        },
        "HOP-5": {
            "required_fields": ["candidates", "generation_temperature", "generation_attempts"],
        },
        "HOP-6": {
            "required_fields": ["validation_results", "passed", "critical_issues", "high_issues"],
        },
        "HOP-7": {
            "required_fields": ["decision", "reasoning"],
            "decision_values": ["FACTUAL_FAILURE", "CREATIVE_FAILURE", "PASS"]
        }
    }
    
    @classmethod
    def validate_state(cls, hop_id: str, state_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate state data against expected schema
        
        Args:
            hop_id: HOP identifier
            state_data: State data to validate
        
        Returns:
            (is_valid, list_of_errors)
        """
        # Normalize hop_id
        if not hop_id.startswith("HOP-"):
            hop_id = f"HOP-{hop_id}"
        
        if hop_id not in cls.SCHEMAS:
            return True, []  # No schema defined, skip validation
        
        schema = cls.SCHEMAS[hop_id]
        errors = []
        
        # Check required fields
        for field in schema.get("required_fields", []):
            if field not in state_data:
                errors.append(f"Missing required field: {field}")
        
        # Check enum values if specified
        for field_suffix in ["values"]:
            for key, valid_values in schema.items():
                if key.endswith(f"_{field_suffix}"):
                    field_name = key.replace(f"_{field_suffix}", "")
                    if field_name in state_data:
                        if state_data[field_name] not in valid_values:
                            errors.append(f"Invalid value for {field_name}: {state_data[field_name]}")
        
        is_valid = len(errors) == 0
        
        return is_valid, errors

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
