"""Prepare Execution Payload - Utility for preparing operation execution payloads.

This module provides utilities for preparing and validating payloads for
operation execution, including parameter serialization and security checks.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class PayloadType(Enum):
    """Types of execution payloads."""
    COMMAND = "command"
    QUERY = "query"
    DATA = "data"
    CONFIG = "config"
    CUSTOM = "custom"


class ValidationLevel(Enum):
    """Levels of payload validation."""
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    SECURITY = "security"


@dataclass
class PayloadField:
    """Definition of a payload field."""
    name: str
    type: str
    required: bool = False
    default_value: Any = None
    validation_rules: List[str] = field(default_factory=list)
    sensitive: bool = False


@dataclass
class PayloadTemplate:
    """Template for execution payload."""
    name: str
    version: str
    payload_type: PayloadType
    fields: Dict[str, PayloadField]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PayloadConfig:
    """Configuration for payload preparation."""
    validation_level: ValidationLevel = ValidationLevel.BASIC
    sanitize_inputs: bool = True
    encrypt_sensitive: bool = False
    compute_checksum: bool = True


@dataclass
class PreparedPayload:
    """Prepared execution payload."""
    payload_id: str
    payload_type: PayloadType
    data: Dict[str, Any]
    template: PayloadTemplate
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionPayloadPreparer:
    """Main class for preparing execution payloads."""

    def __init__(self, config: Optional[PayloadConfig] = None):
        self.config = config or PayloadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validators = self._initialize_validators()
        self._sanitizers = self._initialize_sanitizers()

    def prepare_payload(self, data: Dict[str, Any], 
                       template: PayloadTemplate) -> PreparedPayload:
        """Prepare execution payload from data and template.
        
        Args:
            data: Raw data for payload
            template: Payload template definition
            
        Returns:
            PreparedPayload: Prepared payload with validation
        """
        self.logger.info(f"Preparing payload: {template.name}")
        
        try:
            # Validate and process data against template
            processed_data, errors = self._process_data(data, template)
            
            # Check for validation errors
            if errors and self.config.validation_level == ValidationLevel.STRICT:
                raise ValueError(f"Payload validation failed: {errors}")
            
            # Sanitize inputs if configured
            if self.config.sanitize_inputs:
                processed_data = self._sanitize_data(processed_data, template)
            
            # Encrypt sensitive fields if configured
            if self.config.encrypt_sensitive:
                processed_data = self._encrypt_sensitive_fields(processed_data, template)
            
            # Compute checksum if configured
            checksum = None
            if self.config.compute_checksum:
                checksum = self._compute_checksum(processed_data)
            
            # Generate payload ID
            payload_id = self._generate_payload_id(template.name, processed_data)
            
            payload = PreparedPayload(
                payload_id=payload_id,
                payload_type=template.payload_type,
                data=processed_data,
                template=template,
                checksum=checksum,
                metadata={
                    "prepared_at": datetime.utcnow().isoformat(),
                    "validation_level": self.config.validation_level.value,
                    "field_count": len(processed_data)
                }
            )
            
            self.logger.info(f"Payload prepared successfully: {payload_id}")
            return payload
            
        except Exception as e:
            self.logger.error(f"Payload preparation failed: {str(e)}")
            raise

    def prepare_from_dict(self, data: Dict[str, Any], 
                         template_def: Dict[str, Any]) -> PreparedPayload:
        """Prepare payload from dictionary template.
        
        Args:
            data: Raw data for payload
            template_def: Template definition as dictionary
            
        Returns:
            PreparedPayload: Prepared payload
        """
        template = self._convert_template_from_dict(template_def)
        return self.prepare_payload(data, template)

    def prepare_command_payload(self, command: str, 
                               args: List[Any] = None,
                               kwargs: Dict[str, Any] = None,
                               template: Optional[PayloadTemplate] = None) -> PreparedPayload:
        """Prepare command execution payload.
        
        Args:
            command: Command to execute
            args: Command arguments
            kwargs: Command keyword arguments
            template: Optional template
            
        Returns:
            PreparedPayload: Command payload
        """
        if template is None:
            # Create default command template
            fields = {
                "command": PayloadField("command", "string", required=True),
                "args": PayloadField("args", "array", required=False, default_value=[]),
                "kwargs": PayloadField("kwargs", "object", required=False, default_value={})
            }
            template = PayloadTemplate(
                name="default_command",
                version="1.0",
                payload_type=PayloadType.COMMAND,
                fields=fields
            )
        
        data = {
            "command": command,
            "args": args or [],
            "kwargs": kwargs or {}
        }
        
        return self.prepare_payload(data, template)

    def prepare_query_payload(self, query: str, 
                            parameters: Dict[str, Any] = None,
                            template: Optional[PayloadTemplate] = None) -> PreparedPayload:
        """Prepare query execution payload.
        
        Args:
            query: Query string
            parameters: Query parameters
            template: Optional template
            
        Returns:
            PreparedPayload: Query payload
        """
        if template is None:
            # Create default query template
            fields = {
                "query": PayloadField("query", "string", required=True),
                "parameters": PayloadField("parameters", "object", required=False, default_value={})
            }
            template = PayloadTemplate(
                name="default_query",
                version="1.0",
                payload_type=PayloadType.QUERY,
                fields=fields
            )
        
        data = {
            "query": query,
            "parameters": parameters or {}
        }
        
        return self.prepare_payload(data, template)

    def validate_payload(self, payload: PreparedPayload) -> Tuple[bool, List[str]]:
        """Validate prepared payload.
        
        Args:
            payload: Payload to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # Check payload ID
        if not payload.payload_id:
            errors.append("Missing payload ID")
        
        # Check data against template
        _, validation_errors = self._process_data(payload.data, payload.template)
        errors.extend(validation_errors)
        
        # Verify checksum if present
        if payload.checksum:
            computed_checksum = self._compute_checksum(payload.data)
            if computed_checksum != payload.checksum:
                errors.append("Checksum verification failed")
        
        return len(errors) == 0, errors

    def serialize_payload(self, payload: PreparedPayload, 
                          format: str = "json") -> str:
        """Serialize payload to string format.
        
        Args:
            payload: Payload to serialize
            format: Serialization format
            
        Returns:
            str: Serialized payload
        """
        if format == "json":
            data = {
                "payload_id": payload.payload_id,
                "payload_type": payload.payload_type.value,
                "data": payload.data,
                "template": {
                    "name": payload.template.name,
                    "version": payload.template.version
                },
                "checksum": payload.checksum,
                "metadata": payload.metadata
            }
            return json.dumps(data, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported serialization format: {format}")

    def _process_data(self, data: Dict[str, Any], 
                     template: PayloadTemplate) -> Tuple[Dict[str, Any], List[str]]:
        """Process data against template."""
        processed = {}
        errors = []
        
        # Process each field in template
        for field_name, field_def in template.fields.items():
            value = data.get(field_name)
            
            # Check required fields
            if field_def.required and value is None:
                if field_def.default_value is not None:
                    value = field_def.default_value
                else:
                    errors.append(f"Required field missing: {field_name}")
                    continue
            
            # Validate field if present
            if value is not None:
                validation_errors = self._validate_field(value, field_def)
                if validation_errors:
                    if self.config.validation_level == ValidationLevel.STRICT:
                        errors.extend(validation_errors)
                    elif self.config.validation_level == ValidationLevel.BASIC:
                        # Log but don't fail for basic validation
                        for error in validation_errors:
                            self.logger.warning(f"Field validation warning: {error}")
                
                # Type conversion
                try:
                    value = self._convert_type(value, field_def.type)
                except Exception as e:
                    errors.append(f"Type conversion failed for {field_name}: {str(e)}")
                    continue
            
            processed[field_name] = value
        
        return processed, errors

    def _validate_field(self, value: Any, field_def: PayloadField) -> List[str]:
        """Validate field value."""
        errors = []
        
        for rule in field_def.validation_rules:
            if rule in self._validators:
                validator = self._validators[rule]
                if not validator(value):
                    errors.append(f"Validation failed for {field_def.name}: {rule}")
        
        return errors

    def _sanitize_data(self, data: Dict[str, Any], 
                       template: PayloadTemplate) -> Dict[str, Any]:
        """Sanitize data fields."""
        sanitized = data.copy()
        
        for field_name, field_def in template.fields.items():
            if field_name in sanitized:
                value = sanitized[field_name]
                
                # Apply sanitizers based on field type
                if field_def.type == "string":
                    value = self._sanitizers["string"](value)
                elif field_def.type == "json":
                    value = self._sanitizers["json"](value)
                
                sanitized[field_name] = value
        
        return sanitized

    def _encrypt_sensitive_fields(self, data: Dict[str, Any], 
                                 template: PayloadTemplate) -> Dict[str, Any]:
        """Encrypt sensitive fields."""
        # Simple placeholder encryption - in production, use proper encryption
        encrypted = data.copy()
        
        for field_name, field_def in template.fields.items():
            if field_def.sensitive and field_name in encrypted:
                value = encrypted[field_name]
                if isinstance(value, str):
                    # Simple XOR encryption (placeholder)
                    key = "sensitive_key"
                    encrypted_value = ''.join(
                        chr(ord(c) ^ ord(k)) for c, k in zip(value, key * len(value))
                    )
                    encrypted[field_name] = encrypted_value
        
        return encrypted

    def _compute_checksum(self, data: Dict[str, Any]) -> str:
        """Compute checksum for data."""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _generate_payload_id(self, template_name: str, data: Dict[str, Any]) -> str:
        """Generate unique payload ID."""
        timestamp = datetime.utcnow().isoformat()
        data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        return f"{template_name}_{timestamp}_{data_hash[:8]}"

    def _convert_type(self, value: Any, target_type: str) -> Any:
        """Convert value to target type."""
        if target_type == "string":
            return str(value)
        elif target_type == "integer":
            return int(value)
        elif target_type == "float":
            return float(value)
        elif target_type == "boolean":
            return bool(value)
        elif target_type == "array":
            return list(value) if not isinstance(value, list) else value
        elif target_type == "object":
            return dict(value) if not isinstance(value, dict) else value
        else:
            return value

    def _convert_template_from_dict(self, template_def: Dict[str, Any]) -> PayloadTemplate:
        """Convert template from dictionary."""
        fields = {}
        for name, field_def in template_def.get("fields", {}).items():
            fields[name] = PayloadField(
                name=name,
                type=field_def.get("type", "string"),
                required=field_def.get("required", False),
                default_value=field_def.get("default"),
                validation_rules=field_def.get("validation_rules", []),
                sensitive=field_def.get("sensitive", False)
            )
        
        return PayloadTemplate(
            name=template_def.get("name", "unnamed"),
            version=template_def.get("version", "1.0"),
            payload_type=PayloadType(template_def.get("payload_type", "custom")),
            fields=fields,
            metadata=template_def.get("metadata", {})
        )

    def _initialize_validators(self) -> Dict[str, Callable]:
        """Initialize field validators."""
        return {
            "non_empty": lambda x: isinstance(x, str) and len(x.strip()) > 0,
            "positive": lambda x: isinstance(x, (int, float)) and x > 0,
            "non_negative": lambda x: isinstance(x, (int, float)) and x >= 0,
            "email": lambda x: isinstance(x, str) and "@" in x,
            "url": lambda x: isinstance(x, str) and (x.startswith("http://") or x.startswith("https://")),
            "alpha": lambda x: isinstance(x, str) and x.isalpha(),
            "alphanumeric": lambda x: isinstance(x, str) and x.isalnum(),
            "min_length_3": lambda x: isinstance(x, str) and len(x) >= 3,
            "max_length_100": lambda x: isinstance(x, str) and len(x) <= 100
        }

    def _initialize_sanitizers(self) -> Dict[str, Callable]:
        """Initialize field sanitizers."""
        return {
            "string": lambda x: str(x).strip() if isinstance(x, str) else x,
            "json": lambda x: json.loads(x) if isinstance(x, str) else x
        }


# Factory function for easy instantiation
def create_execution_payload_preparer(
    validation_level: str = "basic",
    sanitize_inputs: bool = True,
    encrypt_sensitive: bool = False,
    **kwargs
) -> ExecutionPayloadPreparer:
    """Create a configured execution payload preparer."""
    config = PayloadConfig(
        validation_level=ValidationLevel(validation_level),
        sanitize_inputs=sanitize_inputs,
        encrypt_sensitive=encrypt_sensitive,
        **kwargs
    )
    return ExecutionPayloadPreparer(config)


# Convenience function for direct usage
def prepare_execution_payload(
    data: Dict[str, Any],
    template: Dict[str, Any],
    validation_level: str = "basic"
) -> Dict[str, Any]:
    """Prepare execution payload.
    
    Args:
        data: Raw data for payload
        template: Payload template definition
        validation_level: Level of validation to apply
        
    Returns:
        Dict: Prepared payload
    """
    preparer = create_execution_payload_preparer(validation_level=validation_level)
    
    payload = preparer.prepare_from_dict(data, template)
    
    return {
        "payload_id": payload.payload_id,
        "payload_type": payload.payload_type.value,
        "data": payload.data,
        "checksum": payload.checksum,
        "metadata": payload.metadata
    }
