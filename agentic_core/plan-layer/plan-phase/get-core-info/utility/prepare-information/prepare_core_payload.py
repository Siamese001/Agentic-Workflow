"""
L1 Cognitive Planning - Core Payload Preparation

Implements pure planning operations for preparing core registry payloads
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
import json
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


# ============================================================================
# L5 SAFETY & LOGGING INFRASTRUCTURE
# ============================================================================

class PayloadType(str, Enum):
    """Supported payload types with L5 safety validation"""
    REGISTRY_QUERY = "registry_query"
    LAYER_REQUEST = "layer_request"
    COORDINATION_MESSAGE = "coordination_message"
    VALIDATION_REQUEST = "validation_request"
    MONITORING_DATA = "monitoring_data"
    CONFIGURATION_UPDATE = "configuration_update"


class PayloadFormat(str, Enum):
    """Payload format types with L5 safety enforcement"""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    BINARY = "binary"
    COMPRESSED = "compressed"


class PayloadSafetyPolicy(BaseModel):
    """L5 Safety policy for core payload preparation operations"""
    max_payload_size: int = Field(default=1048576, description="Maximum payload size in bytes (1MB)")
    allowed_payload_types: List[str] = Field(default_factory=lambda: [t.value for t in PayloadType])
    allowed_formats: List[str] = Field(default_factory=lambda: [t.value for t in PayloadFormat])
    require_content_validation: bool = Field(default=True)
    prevent_data_leakage: bool = Field(default=True)
    encrypt_sensitive_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class PayloadSafetyValidator:
    """L5 Safety validator for core payload preparation operations"""
    
    def __init__(self, policy: PayloadSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.PayloadSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._sensitive_patterns = [
            r"password", r"secret", r"token", r"key", r"credential",
            r"private", r"confidential", r"restricted"
        ]
        self._dangerous_content_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\("
        ]
    
    def validate_payload_input(self, payload_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates payload input against L5 safety policies"""
        try:
            # Check payload size
            payload_data = payload_input.get("data", {})
            payload_size = len(str(payload_data).encode('utf-8'))
            
            if payload_size > self.policy.max_payload_size:
                error_msg = f"Payload too large: {payload_size} > {self.policy.max_payload_size} bytes"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check payload type
            payload_type = payload_input.get("payload_type", "")
            if payload_type not in self.policy.allowed_payload_types:
                error_msg = f"Prohibited payload type: {payload_type}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check format
            payload_format = payload_input.get("format", "")
            if payload_format not in self.policy.allowed_formats:
                error_msg = f"Prohibited payload format: {payload_format}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous content
            content_str = str(payload_data).lower()
            for pattern in self._dangerous_content_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous content pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for sensitive data that should be encrypted
            if self.policy.encrypt_sensitive_data:
                for pattern in self._sensitive_patterns:
                    if pattern in content_str:
                        self.logger.warning(f"Sensitive data pattern detected: {pattern}")
                        # In production, this would trigger encryption
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class PayloadRequest:
    """Input request for core payload preparation operations"""
    payload_type: PayloadType
    payload_format: PayloadFormat
    data: Dict[str, Any]
    target_layer: str
    context: Dict[str, Any]
    preparation_options: Dict[str, Any] = field(default_factory=dict)
    security_requirements: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class PreparedPayload:
    """Structured representation of a prepared payload"""
    payload_type: PayloadType
    payload_format: PayloadFormat
    content: Union[str, bytes, Dict[str, Any]]
    metadata: Dict[str, Any]
    headers: Dict[str, str]
    size_bytes: int
    checksum: Optional[str]
    encrypted: bool


@dataclass
class PayloadValidationResult:
    """Result of payload validation"""
    is_valid: bool
    validation_errors: List[str]
    warnings: List[str]
    compliance_score: float
    security_flags: List[str]


@dataclass
class CorePayloadResult:
    """Output result from core payload preparation operations"""
    prepared_payload: PreparedPayload
    validation_result: PayloadValidationResult
    preparation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    payload_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class CorePayloadPreparerInterface(ABC):
    """Abstract interface for core payload preparation operations"""
    
    @abstractmethod
    async def prepare_payload(self, request: PayloadRequest) -> CorePayloadResult:
        """Prepare core registry payload"""
        pass
    
    @abstractmethod
    async def validate_payload_structure(self, payload: PreparedPayload) -> PayloadValidationResult:
        """Validate payload structure and content"""
        pass
    
    @abstractmethod
    async def serialize_payload(self, data: Dict[str, Any], format: PayloadFormat) -> Union[str, bytes]:
        """Serialize payload data to specified format"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class CorePayloadPreparer(CorePayloadPreparerInterface):
    """
    L1 Cognitive Planning implementation for preparing core registry payloads.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[PayloadSafetyPolicy] = None):
        self.safety_policy = safety_policy or PayloadSafetyPolicy()
        self.safety_validator = PayloadSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Payload preparation templates and patterns
        self._payload_templates = {
            PayloadType.REGISTRY_QUERY: {
                "required_fields": ["query", "target_layer", "timestamp"],
                "optional_fields": ["filters", "limit", "offset"]
            },
            PayloadType.LAYER_REQUEST: {
                "required_fields": ["layer_name", "operation", "parameters"],
                "optional_fields": ["context", "priority", "timeout"]
            },
            PayloadType.COORDINATION_MESSAGE: {
                "required_fields": ["message_type", "source_layer", "target_layers"],
                "optional_fields": ["payload", "correlation_id", "timestamp"]
            },
            PayloadType.VALIDATION_REQUEST: {
                "required_fields": ["validation_type", "target", "criteria"],
                "optional_fields": ["context", "strict_mode", "timeout"]
            },
            PayloadType.MONITORING_DATA: {
                "required_fields": ["metric_type", "source", "timestamp"],
                "optional_fields": ["metrics", "labels", "annotations"]
            },
            PayloadType.CONFIGURATION_UPDATE: {
                "required_fields": ["config_type", "target", "updates"],
                "optional_fields": ["version", "rollback_enabled", "validation_required"]
            }
        }
        
        self.logger.info("CorePayloadPreparer initialized with L5 safety policies")
    
    async def prepare_payload(self, request: PayloadRequest) -> CorePayloadResult:
        """
        Prepare core registry payload.
        
        Args:
            request: Core payload preparation request with data and formatting options
            
        Returns:
            CorePayloadResult: Structured result with prepared payload and validation
            
        Raises:
            ValidationError: If payload preparation fails
            SafetyError: If payload violates safety policies
        """
        self.logger.info(f"Preparing {request.payload_format} payload of type {request.payload_type} for {request.target_layer}")
        
        try:
            # L5 Safety validation
            payload_input = {
                "data": request.data,
                "payload_type": request.payload_type.value,
                "format": request.payload_format.value
            }
            
            is_valid, error_msg = self.safety_validator.validate_payload_input(payload_input)
            if not is_valid:
                raise SafetyError(f"Payload validation failed: {error_msg}")
            
            # Validate payload structure
            structure_valid, structure_errors = await self._validate_payload_structure_by_type(
                request.data, request.payload_type
            )
            if not structure_valid:
                raise ValidationError(f"Payload structure validation failed: {structure_errors}")
            
            # Prepare payload content
            prepared_data = await self._prepare_payload_content(request)
            
            # Serialize payload
            serialized_content = await self.serialize_payload(prepared_data, request.payload_format)
            
            # Generate metadata
            metadata = await self._generate_payload_metadata(request, prepared_data)
            
            # Generate headers
            headers = await self._generate_payload_headers(request, metadata)
            
            # Calculate size and checksum
            content_bytes = serialized_content.encode('utf-8') if isinstance(serialized_content, str) else serialized_content
            size_bytes = len(content_bytes)
            checksum = self._calculate_checksum(content_bytes)
            
            # Check if encryption is required
            encrypted = await self._should_encrypt_payload(request, prepared_data)
            if encrypted:
                serialized_content = await self._encrypt_payload(serialized_content)
            
            # Create prepared payload
            prepared_payload = PreparedPayload(
                payload_type=request.payload_type,
                payload_format=request.payload_format,
                content=serialized_content,
                metadata=metadata,
                headers=headers,
                size_bytes=size_bytes,
                checksum=checksum,
                encrypted=encrypted
            )
            
            # Validate final payload
            validation_result = await self.validate_payload_structure(prepared_payload)
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_payload_risk_score(prepared_payload),
                "security_flags": validation_result.security_flags
            }
            
            # Generate unique payload ID
            payload_id = self._generate_payload_id(request, prepared_payload)
            
            result = CorePayloadResult(
                prepared_payload=prepared_payload,
                validation_result=validation_result,
                preparation_metadata={
                    "preparation_duration_ms": size_bytes * 0.001,  # Rough estimate
                    "original_size": len(str(request.data)),
                    "final_size": size_bytes,
                    "compression_ratio": size_bytes / len(str(request.data)) if request.data else 1.0,
                    "complexity_estimate": await self._estimate_preparation_complexity(request)
                },
                safety_validation=safety_validation,
                payload_id=payload_id
            )
            
            self.logger.info(f"Successfully prepared payload {payload_id} ({size_bytes} bytes)")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to prepare core payload: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback payload in non-fail-closed mode
            return self._create_fallback_payload(request, str(e))
    
    async def validate_payload_structure(self, payload: PreparedPayload) -> PayloadValidationResult:
        """Validate payload structure and content"""
        try:
            errors = []
            warnings = []
            security_flags = []
            
            # Basic structure validation
            if not payload.content:
                errors.append("Payload content is empty")
            
            # Size validation
            if payload.size_bytes > self.safety_policy.max_payload_size:
                errors.append(f"Payload exceeds maximum size: {payload.size_bytes} > {self.safety_policy.max_payload_size}")
            
            # Format-specific validation
            if payload.payload_format == PayloadFormat.JSON:
                if isinstance(payload.content, str):
                    try:
                        json.loads(payload.content)
                    except json.JSONDecodeError as e:
                        errors.append(f"Invalid JSON format: {str(e)}")
            
            # Security validation
            content_str = str(payload.content).lower()
            for pattern in self._dangerous_content_patterns:
                if pattern in content_str:
                    security_flags.append(f"dangerous_content:{pattern}")
            
            # Sensitive data validation
            for pattern in self._sensitive_patterns:
                if pattern in content_str and not payload.encrypted:
                    warnings.append(f"Unencrypted sensitive data detected: {pattern}")
            
            # Calculate compliance score
            compliance_score = 1.0
            if errors:
                compliance_score -= 0.5
            if warnings:
                compliance_score -= 0.1 * len(warnings)
            if security_flags:
                compliance_score -= 0.2 * len(security_flags)
            
            compliance_score = max(0.0, compliance_score)
            
            return PayloadValidationResult(
                is_valid=len(errors) == 0,
                validation_errors=errors,
                warnings=warnings,
                compliance_score=compliance_score,
                security_flags=security_flags
            )
            
        except Exception as e:
            return PayloadValidationResult(
                is_valid=False,
                validation_errors=[f"Validation error: {str(e)}"],
                warnings=[],
                compliance_score=0.0,
                security_flags=["validation_failed"]
            )
    
    async def serialize_payload(self, data: Dict[str, Any], format: PayloadFormat) -> Union[str, bytes]:
        """Serialize payload data to specified format"""
        try:
            if format == PayloadFormat.JSON:
                return json.dumps(data, indent=2, ensure_ascii=False)
            elif format == PayloadFormat.YAML:
                import yaml
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)
            elif format == PayloadFormat.XML:
                return self._dict_to_xml(data)
            elif format == PayloadFormat.BINARY:
                return json.dumps(data).encode('utf-8')
            elif format == PayloadFormat.COMPRESSED:
                import gzip
                json_data = json.dumps(data).encode('utf-8')
                return gzip.compress(json_data)
            else:
                raise ValidationError(f"Unsupported payload format: {format}")
                
        except Exception as e:
            self.logger.error(f"Payload serialization failed: {str(e)}")
            raise
    
    async def _validate_payload_structure_by_type(
        self, 
        data: Dict[str, Any], 
        payload_type: PayloadType
    ) -> Tuple[bool, List[str]]:
        """Validate payload structure based on type"""
        try:
            template = self._payload_templates.get(payload_type, {})
            required_fields = template.get("required_fields", [])
            errors = []
            
            # Check required fields
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
            
            # Validate field types
            for field, value in data.items():
                if field == "timestamp" and not isinstance(value, (str, int, float)):
                    errors.append(f"Invalid timestamp type for field: {field}")
                elif field == "parameters" and not isinstance(value, dict):
                    errors.append(f"Invalid parameters type for field: {field}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Structure validation error: {str(e)}"]
    
    async def _prepare_payload_content(self, request: PayloadRequest) -> Dict[str, Any]:
        """Prepare payload content with standard fields"""
        prepared = request.data.copy()
        
        # Add standard metadata
        prepared["_metadata"] = {
            "payload_type": request.payload_type.value,
            "target_layer": request.target_layer,
            "prepared_at": datetime.now().isoformat(),
            "safety_level": request.safety_level
        }
        
        # Add context information
        if request.context:
            prepared["_context"] = request.context
        
        # Add security requirements
        if request.security_requirements:
            prepared["_security"] = request.security_requirements
        
        return prepared
    
    async def _generate_payload_metadata(
        self, 
        request: PayloadRequest, 
        prepared_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate payload metadata"""
        return {
            "payload_type": request.payload_type.value,
            "target_layer": request.target_layer,
            "format": request.payload_format.value,
            "prepared_at": datetime.now().isoformat(),
            "field_count": len(prepared_data),
            "has_sensitive_data": await self._contains_sensitive_data(prepared_data),
            "preparation_options": request.preparation_options
        }
    
    async def _generate_payload_headers(
        self, 
        request: PayloadRequest, 
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate payload headers"""
        headers = {
            "Content-Type": self._get_content_type(request.payload_format),
            "X-Payload-Type": request.payload_type.value,
            "X-Target-Layer": request.target_layer,
            "X-Safety-Level": request.safety_level,
            "X-Prepared-At": metadata["prepared_at"]
        }
        
        # Add security headers
        if request.security_requirements.get("authentication"):
            headers["X-Auth-Required"] = "true"
        
        if metadata.get("has_sensitive_data"):
            headers["X-Sensitive-Data"] = "true"
        
        return headers
    
    def _get_content_type(self, format: PayloadFormat) -> str:
        """Get content type for payload format"""
        content_types = {
            PayloadFormat.JSON: "application/json",
            PayloadFormat.XML: "application/xml",
            PayloadFormat.YAML: "application/x-yaml",
            PayloadFormat.BINARY: "application/octet-stream",
            PayloadFormat.COMPRESSED: "application/gzip"
        }
        return content_types.get(format, "application/octet-stream")
    
    def _calculate_checksum(self, content: bytes) -> str:
        """Calculate checksum for payload content"""
        import hashlib
        return hashlib.sha256(content).hexdigest()
    
    async def _should_encrypt_payload(self, request: PayloadRequest, data: Dict[str, Any]) -> bool:
        """Determine if payload should be encrypted"""
        if not self.safety_policy.encrypt_sensitive_data:
            return False
        
        return await self._contains_sensitive_data(data)
    
    async def _contains_sensitive_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains sensitive information"""
        data_str = str(data).lower()
        for pattern in self._sensitive_patterns:
            if pattern in data_str:
                return True
        return False
    
    async def _encrypt_payload(self, content: Union[str, bytes]) -> Union[str, bytes]:
        """Encrypt payload content (placeholder implementation)"""
        # In production, this would implement actual encryption
        self.logger.warning("Encryption requested but not implemented - returning original content")
        return content
    
    def _dict_to_xml(self, data: Dict[str, Any], root: str = "payload") -> str:
        """Convert dictionary to XML string"""
        xml_parts = [f"<{root}>"]
        
        for key, value in data.items():
            if isinstance(value, dict):
                xml_parts.append(self._dict_to_xml(value, key))
            elif isinstance(value, list):
                for item in value:
                    xml_parts.append(f"<{key}>{str(item)}</{key}>")
            else:
                xml_parts.append(f"<{key}>{str(value)}</{key}>")
        
        xml_parts.append(f"</{root}>")
        return "".join(xml_parts)
    
    async def _estimate_preparation_complexity(self, request: PayloadRequest) -> str:
        """Estimate preparation complexity"""
        complexity_score = len(request.data) // 10
        
        # Add complexity for different formats
        if request.payload_format in [PayloadFormat.XML, PayloadFormat.YAML]:
            complexity_score += 2
        elif request.payload_format == PayloadFormat.COMPRESSED:
            complexity_score += 3
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_payload_risk_score(self, payload: PreparedPayload) -> float:
        """Calculate risk score for the payload (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for large payloads
        if payload.size_bytes > 512000:  # 512KB
            risk_score += 0.2
        
        # Increase risk for unencrypted sensitive data
        if payload.metadata.get("has_sensitive_data") and not payload.encrypted:
            risk_score += 0.4
        
        # Increase risk for certain payload types
        if payload.payload_type in [PayloadType.CONFIGURATION_UPDATE, PayloadType.COORDINATION_MESSAGE]:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _generate_payload_id(self, request: PayloadRequest, payload: PreparedPayload) -> str:
        """Generate unique payload identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.payload_type.value}:{request.target_layer}:{payload.size_bytes}:{timestamp}"
        return f"payload_{hash(content) % 1000000:06d}"
    
    def _create_fallback_payload(self, request: PayloadRequest, error: str) -> CorePayloadResult:
        """Create safe fallback payload when main preparation fails"""
        fallback_data = {
            "error": "payload_preparation_failed",
            "message": "Safe fallback payload",
            "original_type": request.payload_type.value,
            "target_layer": request.target_layer
        }
        
        fallback_payload = PreparedPayload(
            payload_type=PayloadType.REGISTRY_QUERY,  # Safe default
            payload_format=PayloadFormat.JSON,
            content=json.dumps(fallback_data),
            metadata={"fallback": True, "error": error},
            headers={"Content-Type": "application/json", "X-Fallback": "true"},
            size_bytes=len(json.dumps(fallback_data)),
            checksum=self._calculate_checksum(json.dumps(fallback_data).encode()),
            encrypted=False
        )
        
        fallback_validation = PayloadValidationResult(
            is_valid=True,
            validation_errors=[],
            warnings=["Using fallback payload"],
            compliance_score=0.5,
            security_flags=["fallback_mode"]
        )
        
        return CorePayloadResult(
            prepared_payload=fallback_payload,
            validation_result=fallback_validation,
            preparation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            payload_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when payload violates safety policies"""
    
    def __init__(self, message: str, policy_violation: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.policy_violation = policy_violation
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.policy_violation:
            return f"[SAFETY_VIOLATION: {self.policy_violation}] {base_msg}"
        return f"[SAFETY_ERROR] {base_msg}"


class PayloadPreparationError(Exception):
    """Raised for general payload preparation errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, payload_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "PAYLOAD_PREPARATION_ERROR"
        self.operation = operation
        self.payload_type = payload_type
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        type_info = f" for {self.payload_type}" if self.payload_type else ""
        return f"[{self.error_code}]{op_info}{type_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_core_payload_preparer(safety_policy: Optional[PayloadSafetyPolicy] = None) -> CorePayloadPreparer:
    """Factory function to create CorePayloadPreparer with optional custom safety policy"""
    return CorePayloadPreparer(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_payload_request(request: PayloadRequest) -> tuple[bool, Optional[str]]:
    """Validate core payload request parameters"""
    try:
        if not request.target_layer or not request.target_layer.strip():
            return False, "Target layer cannot be empty"
        
        if not isinstance(request.data, dict):
            return False, "Payload data must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"