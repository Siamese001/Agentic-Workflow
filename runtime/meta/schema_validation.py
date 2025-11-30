# schema_validation - Schema validation utilities
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SchemaVersion:
    """Schema version information"""
    version: str
    compatible: bool = True
    errors: list = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

def validate_schema_version(schema: Dict[str, Any], expected_version: str = "1.0") -> SchemaVersion:
    """Validate schema version compatibility"""
    # Handle Pydantic models by converting to dict
    if hasattr(schema, 'model_dump'):
        schema_dict = schema.model_dump()
    elif hasattr(schema, 'dict'):
        schema_dict = schema.dict()
    else:
        schema_dict = schema
    
    schema_version = schema_dict.get("version", "1.0")
    
    # Simple version validation
    if schema_version == expected_version:
        return SchemaVersion(version=schema_version, compatible=True)
    elif schema_version.startswith("1.") and expected_version.startswith("1."):
        return SchemaVersion(version=schema_version, compatible=True)
    else:
        return SchemaVersion(
            version=schema_version, 
            compatible=False, 
            errors=[f"Version mismatch: expected {expected_version}, got {schema_version}"]
        )
