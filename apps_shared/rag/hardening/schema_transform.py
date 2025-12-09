"""
runtime/shared/schema_transform.py
Schema Transformation Gate

Ported from legacy resume gen Job_Workflow_v61.27.json
Implements schema transformation and validation:
  - Key mapping between internal and external schemas
  - Controlled vocabulary validation
  - Enum validation against QA specs
  - Data loss prevention
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class TransformAction(Enum):
    """Actions for unmapped or invalid keys."""
    HALT_AND_REPORT = "HALT_AND_REPORT"
    WARN_AND_SKIP = "WARN_AND_SKIP"
    USE_DEFAULT = "USE_DEFAULT"
    PASSTHROUGH = "PASSTHROUGH"


class ValidationPolicy(Enum):
    """Policies for validation behavior."""
    MAP_AND_VALIDATE_TO_SCHEMA = auto()
    HALT_ON_POTENTIAL_DATA_LOSS = auto()
    VALIDATE_ENUMS_AGAINST_QA_SPEC = auto()
    STRICT_TYPE_CHECKING = auto()


class TransformResult(Enum):
    """Results of transformation operations."""
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    HALTED = "HALTED"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class KeyMapping:
    """Mapping between source and target keys."""
    source_key: str
    target_key: str
    required: bool = True
    default_value: Optional[Any] = None
    transformer: Optional[Callable[[Any], Any]] = None
    validator: Optional[Callable[[Any], bool]] = None
    
    def transform(self, value: object) -> object:
        """Apply transformation to value."""
        if self.transformer:
            return self.transformer(value)
        return value
    
    def validate(self, value: object) -> bool:
        """Validate the value."""
        if self.validator:
            return self.validator(value)
        return True


@dataclass
class EnumSpec:
    """Specification for enum validation."""
    field_name: str
    allowed_values: List[str]
    case_sensitive: bool = False
    allow_null: bool = False
    
    def validate(self, value: object) -> Tuple[bool, str]:
        """Validate value against enum spec."""
        if value is None:
            if self.allow_null:
                return (True, "Null value allowed")
            return (False, f"Null not allowed for {self.field_name}")
            
        check_value = str(value) if self.case_sensitive else str(value).lower()
        check_allowed = self.allowed_values if self.case_sensitive else [v.lower() for v in self.allowed_values]
        
        if check_value in check_allowed:
            return (True, f"Valid enum value: {value}")
        return (False, f"Invalid enum value '{value}' for {self.field_name}. Allowed: {self.allowed_values}")


@dataclass
class TransformViolation:
    """A violation detected during transformation."""
    violation_type: str
    field: str
    message: str
    source_value: Optional[Any] = None
    expected: Optional[str] = None
    severity: str = "ERROR"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.violation_type,
            "field": self.field,
            "message": self.message,
            "source_value": str(self.source_value)[:100] if self.source_value else None,
            "expected": self.expected,
            "severity": self.severity,
        }


@dataclass
class TransformReport:
    """Report from schema transformation."""
    result: TransformResult
    transformed_data: Dict[str, Any]
    violations: List[TransformViolation]
    mapped_keys: List[str]
    unmapped_keys: List[str]
    missing_required: List[str]
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def success(self) -> bool:
        """Check if transformation was successful."""
        return self.result == TransformResult.SUCCESS
    
    @property
    def has_data_loss(self) -> bool:
        """Check if there was potential data loss."""
        return len(self.unmapped_keys) > 0 or len(self.missing_required) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result": self.result.value,
            "success": self.success,
            "has_data_loss": self.has_data_loss,
            "mapped_keys": self.mapped_keys,
            "unmapped_keys": self.unmapped_keys,
            "missing_required": self.missing_required,
            "violation_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class SchemaTransformConfig:
    """Configuration for schema transformation."""
    on_unmapped_key: TransformAction = TransformAction.HALT_AND_REPORT
    on_validation_failure: TransformAction = TransformAction.HALT_AND_REPORT
    on_missing_required: TransformAction = TransformAction.HALT_AND_REPORT
    strict_type_checking: bool = True
    preserve_unmapped: bool = False
    validate_enums: bool = True


@dataclass
class QASpec:
    """Quality Assurance specification for validation."""
    schema_version: str
    enum_specs: Dict[str, EnumSpec] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    field_types: Dict[str, Type] = field(default_factory=dict)
    custom_validators: Dict[str, Callable[[Any], bool]] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QASpec:
        """Create QASpec from dictionary."""
        enum_specs = {}
        for field_name, spec in data.get("enums", {}).items():
            enum_specs[field_name] = EnumSpec(
                field_name=field_name,
                allowed_values=spec.get("values", []),
                case_sensitive=spec.get("case_sensitive", False),
                allow_null=spec.get("allow_null", False),
            )
            
        return cls(
            schema_version=data.get("version", "unknown"),
            enum_specs=enum_specs,
            required_fields=data.get("required", []),
        )
    
    @classmethod
    def from_json_file(cls, filepath: str) -> QASpec:
        """Load QASpec from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# =============================================================================
# SCHEMA TRANSFORMER
# =============================================================================

class SchemaTransformer:
    """
    Schema Transformation Gate.
    
    Transforms data between internal and external schemas with:
    - Key mapping
    - Type validation
    - Enum validation
    - Data loss prevention
    """
    
    def __init__(
        self,
        config: Optional[SchemaTransformConfig] = None,
        key_map: Optional[Dict[str, str]] = None,
        qa_spec: Optional[QASpec] = None,
    ) -> None:
        self.config = config or SchemaTransformConfig()
        self._key_mappings: Dict[str, KeyMapping] = {}
        self._qa_spec = qa_spec
        
        # Initialize from simple key map
        if key_map:
            for source, target in key_map.items():
                self.add_mapping(KeyMapping(source_key=source, target_key=target))
                
    def add_mapping(self, mapping: KeyMapping) -> None:
        """Add a key mapping."""
        self._key_mappings[mapping.source_key] = mapping
        
    def set_qa_spec(self, qa_spec: QASpec) -> None:
        """Set the QA specification."""
        self._qa_spec = qa_spec
        
    def transform(self, source_data: Dict[str, Any]) -> TransformReport:
        """
        Transform source data to target schema.
        
        Args:
            source_data: Data in source schema
            
        Returns:
            TransformReport with results
        """
        import time
        start_time = time.time()
        
        violations: List[TransformViolation] = []
        transformed: Dict[str, Any] = {}
        mapped_keys: List[str] = []
        unmapped_keys: List[str] = []
        missing_required: List[str] = []
        
        # Process each source key
        for source_key, value in source_data.items():
            mapping = self._key_mappings.get(source_key)
            
            if mapping:
                # Apply transformation
                try:
                    transformed_value = mapping.transform(value)
                    
                    # Validate
                    if not mapping.validate(transformed_value):
                        violations.append(TransformViolation(
                            violation_type="VALIDATION_FAILED",
                            field=source_key,
                            message=f"Validation failed for {source_key}",
                            source_value=value,
                        ))
                        if self.config.on_validation_failure == TransformAction.HALT_AND_REPORT:
                            continue
                            
                    transformed[mapping.target_key] = transformed_value
                    mapped_keys.append(source_key)
                    
                except (ValueError, TypeError, RuntimeError, KeyError) as e:
                    violations.append(TransformViolation(
                        violation_type="TRANSFORM_ERROR",
                        field=source_key,
                        message=f"Transform error: {str(e)}",
                        source_value=value,
                    ))
            else:
                unmapped_keys.append(source_key)
                
                if self.config.preserve_unmapped:
                    transformed[source_key] = value
                elif self.config.on_unmapped_key == TransformAction.HALT_AND_REPORT:
                    violations.append(TransformViolation(
                        violation_type="UNMAPPED_KEY",
                        field=source_key,
                        message=f"No mapping defined for key: {source_key}",
                        source_value=value,
                        severity="WARNING",
                    ))
                    
        # Check for missing required keys
        for source_key, mapping in self._key_mappings.items():
            if mapping.required and source_key not in source_data:
                if mapping.default_value is not None:
                    transformed[mapping.target_key] = mapping.default_value
                else:
                    missing_required.append(source_key)
                    violations.append(TransformViolation(
                        violation_type="MISSING_REQUIRED",
                        field=source_key,
                        message=f"Required key missing: {source_key}",
                        expected=mapping.target_key,
                    ))
                    
        # Validate against QA spec
        if self._qa_spec and self.config.validate_enums:
            enum_violations = self._validate_enums(transformed)
            violations.extend(enum_violations)
            
        # Determine result
        if missing_required and self.config.on_missing_required == TransformAction.HALT_AND_REPORT:
            result = TransformResult.HALTED
        elif violations and any(v.severity == "ERROR" for v in violations):
            result = TransformResult.FAILED
        elif violations:
            result = TransformResult.PARTIAL
        else:
            result = TransformResult.SUCCESS
            
        return TransformReport(
            result=result,
            transformed_data=transformed,
            violations=violations,
            mapped_keys=mapped_keys,
            unmapped_keys=unmapped_keys,
            missing_required=missing_required,
            duration_ms=(time.time() - start_time) * 1000,
        )
    
    def _validate_enums(self, data: Dict[str, Any]) -> List[TransformViolation]:
        """Validate enum fields against QA spec."""
        violations = []
        
        if not self._qa_spec:
            return violations
            
        for field_name, enum_spec in self._qa_spec.enum_specs.items():
            if field_name in data:
                is_valid, message = enum_spec.validate(data[field_name])
                if not is_valid:
                    violations.append(TransformViolation(
                        violation_type="INVALID_ENUM",
                        field=field_name,
                        message=message,
                        source_value=data[field_name],
                        expected=str(enum_spec.allowed_values),
                    ))
                    
        return violations
    
    def reverse_transform(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reverse transform from target schema to source schema.
        
        Args:
            target_data: Data in target schema
            
        Returns:
            Data in source schema
        """
        # Build reverse mapping
        reverse_map = {m.target_key: m.source_key for m in self._key_mappings.values()}
        
        result = {}
        for target_key, value in target_data.items():
            source_key = reverse_map.get(target_key, target_key)
            result[source_key] = value
            
        return result


# =============================================================================
# DATA LOSS PREVENTION GATE
# =============================================================================

class DataLossPreventionGate:
    """
    Gate to prevent silent data loss during transformations.
    
    Implements VG_NO_SILENT_TRUNCATION policy.
    """
    
    def __init__(
        self,
        max_string_length: int = 10000,
        max_array_length: int = 1000,
        check_truncation: bool = True,
    ) -> None:
        self.max_string_length = max_string_length
        self.max_array_length = max_array_length
        self.check_truncation = check_truncation
        
    def check(self, original: object, transformed: object, field_name: str) -> List[TransformViolation]:
        """
        Check for potential data loss between original and transformed values.
        
        Args:
            original: Original value
            transformed: Transformed value
            field_name: Name of the field
            
        Returns:
            List of violations if data loss detected
        """
        violations = []
        
        # Check string truncation
        if isinstance(original, str) and isinstance(transformed, str):
            if len(original) > len(transformed) and self.check_truncation:
                violations.append(TransformViolation(
                    violation_type="POTENTIAL_TRUNCATION",
                    field=field_name,
                    message=f"String may have been truncated: {len(original)} -> {len(transformed)} chars",
                    source_value=original[:100],
                ))
                
        # Check array truncation
        if isinstance(original, list) and isinstance(transformed, list):
            if len(original) > len(transformed):
                violations.append(TransformViolation(
                    violation_type="ARRAY_TRUNCATION",
                    field=field_name,
                    message=f"Array truncated: {len(original)} -> {len(transformed)} items",
                ))
                
        # Check for None replacement
        if original is not None and transformed is None:
            violations.append(TransformViolation(
                violation_type="VALUE_NULLIFIED",
                field=field_name,
                message=f"Non-null value replaced with null",
                source_value=original,
            ))
            
        return violations
    
    def validate_batch(
        self,
        original_data: Dict[str, Any],
        transformed_data: Dict[str, Any],
    ) -> List[TransformViolation]:
        """Validate entire data batch for data loss."""
        violations = []
        
        for key, original_value in original_data.items():
            transformed_value = transformed_data.get(key)
            field_violations = self.check(original_value, transformed_value, key)
            violations.extend(field_violations)
            
        # Check for dropped keys
        dropped_keys = set(original_data.keys()) - set(transformed_data.keys())
        for key in dropped_keys:
            violations.append(TransformViolation(
                violation_type="KEY_DROPPED",
                field=key,
                message=f"Key was dropped during transformation",
                source_value=original_data[key],
            ))
            
        return violations


# =============================================================================
# CONTROLLED VOCABULARY VALIDATOR
# =============================================================================

class ControlledVocabularyValidator:
    """
    Validates values against controlled vocabularies.
    
    Implements VG_CONTROLLED_VOCABULARY policy.
    """
    
    def __init__(self) -> None:
        self._vocabularies: Dict[str, Set[str]] = {}
        self._case_sensitive: Dict[str, bool] = {}
        
    def register_vocabulary(
        self,
        field_name: str,
        allowed_values: List[str],
        case_sensitive: bool = False,
    ) -> None:
        """Register a controlled vocabulary for a field."""
        if case_sensitive:
            self._vocabularies[field_name] = set(allowed_values)
        else:
            self._vocabularies[field_name] = {v.lower() for v in allowed_values}
        self._case_sensitive[field_name] = case_sensitive
        
    def validate(self, field_name: str, value: object) -> Tuple[bool, str]:
        """Validate a value against its controlled vocabulary."""
        if field_name not in self._vocabularies:
            return (True, "No vocabulary defined")
            
        vocab = self._vocabularies[field_name]
        case_sensitive = self._case_sensitive[field_name]
        
        check_value = str(value) if case_sensitive else str(value).lower()
        
        if check_value in vocab:
            return (True, f"Valid vocabulary value: {value}")
        return (False, f"Invalid value '{value}' for {field_name}")
    
    def validate_data(self, data: Dict[str, Any]) -> List[TransformViolation]:
        """Validate all fields in data against vocabularies."""
        violations = []
        
        for field_name, value in data.items():
            if field_name in self._vocabularies:
                is_valid, message = self.validate(field_name, value)
                if not is_valid:
                    violations.append(TransformViolation(
                        violation_type="VOCABULARY_VIOLATION",
                        field=field_name,
                        message=message,
                        source_value=value,
                        expected=str(list(self._vocabularies[field_name])[:10]),
                    ))
                    
        return violations


# =============================================================================
# SCHEMA TRANSFORMATION GATE (COMPOSITE)
# =============================================================================

class SchemaTransformationGate:
    """
    Complete Schema Transformation Gate.
    
    Combines:
    - Schema transformation
    - Data loss prevention
    - Controlled vocabulary validation
    - Enum validation
    """
    
    gate_id = "VG-FINAL-SCHEMA-TRANSFORM"
    execution_point = "BEFORE_TRACKER_GENERATION"
    blocking = True
    
    def __init__(
        self,
        config: Optional[SchemaTransformConfig] = None,
        key_map: Optional[Dict[str, str]] = None,
        qa_spec: Optional[QASpec] = None,
    ) -> None:
        self.config = config or SchemaTransformConfig()
        self.transformer = SchemaTransformer(config, key_map, qa_spec)
        self.dlp_gate = DataLossPreventionGate()
        self.vocab_validator = ControlledVocabularyValidator()
        
    def add_mapping(self, mapping: KeyMapping) -> None:
        """Add a key mapping."""
        self.transformer.add_mapping(mapping)
        
    def set_key_map(self, key_map: Dict[str, str]) -> None:
        """Set key mappings from dictionary."""
        for source, target in key_map.items():
            self.transformer.add_mapping(KeyMapping(source_key=source, target_key=target))
            
    def set_qa_spec(self, qa_spec: QASpec) -> None:
        """Set QA specification."""
        self.transformer.set_qa_spec(qa_spec)
        
    def register_vocabulary(
        self,
        field_name: str,
        allowed_values: List[str],
        case_sensitive: bool = False,
    ) -> None:
        """Register controlled vocabulary."""
        self.vocab_validator.register_vocabulary(field_name, allowed_values, case_sensitive)
        
    def execute(self, source_data: Dict[str, Any]) -> TransformReport:
        """
        Execute the complete transformation gate.
        
        Args:
            source_data: Source data to transform
            
        Returns:
            TransformReport with all results
        """
        # Run transformation
        report = self.transformer.transform(source_data)
        
        # Run data loss prevention check
        dlp_violations = self.dlp_gate.validate_batch(source_data, report.transformed_data)
        report.violations.extend(dlp_violations)
        
        # Run vocabulary validation
        vocab_violations = self.vocab_validator.validate_data(report.transformed_data)
        report.violations.extend(vocab_violations)
        
        # Update result based on new violations
        if dlp_violations or vocab_violations:
            if report.result == TransformResult.SUCCESS:
                report.result = TransformResult.PARTIAL
                
        return report


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_default_transformer() -> SchemaTransformer:
    """Create a transformer with default configuration."""
    return SchemaTransformer()


def create_strict_transformer() -> SchemaTransformer:
    """Create a transformer with strict validation."""
    config = SchemaTransformConfig(
        on_unmapped_key=TransformAction.HALT_AND_REPORT,
        on_validation_failure=TransformAction.HALT_AND_REPORT,
        on_missing_required=TransformAction.HALT_AND_REPORT,
        strict_type_checking=True,
        validate_enums=True,
    )
    return SchemaTransformer(config=config)


def create_transformation_gate(
    key_map: Optional[Dict[str, str]] = None,
    qa_spec_path: Optional[str] = None,
) -> SchemaTransformationGate:
    """
    Create a complete transformation gate.
    
    Args:
        key_map: Dictionary mapping source keys to target keys
        qa_spec_path: Path to QA specification JSON file
        
    Returns:
        Configured SchemaTransformationGate
    """
    qa_spec = None
    if qa_spec_path:
        qa_spec = QASpec.from_json_file(qa_spec_path)
        
    return SchemaTransformationGate(key_map=key_map, qa_spec=qa_spec)


# =============================================================================
# COMMON KEY MAPS
# =============================================================================

# Example key map from legacy resume gen
RESUME_TRACKER_KEY_MAP = {
    "versioned_resume_filename": "Versioned Resume",
    "company_name": "Company",
    "category": "Category",
    "sub_category": "Sub-Category",
    "job_title": "Job Title",
    "primary_job_role": "Primary Job Role",
    "job_url": "JD URL",
}
