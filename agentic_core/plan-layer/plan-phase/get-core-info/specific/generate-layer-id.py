"""
L1 Cognitive Planning - Layer ID Generation

Implements pure planning operations for generating unique layer identifiers
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
import uuid
import hashlib
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

class IdGenerationType(str, Enum):
    """Supported ID generation types with L5 safety validation"""
    UUID = "uuid"
    HASH = "hash"
    SEQUENTIAL = "sequential"
    TIMESTAMP = "timestamp"
    COMPOSITE = "composite"
    NAMESPACE = "namespace"


class IdFormat(str, Enum):
    """ID format types with L5 safety enforcement"""
    STANDARD = "standard"
    SHORT = "short"
    LONG = "long"
    CUSTOM = "custom"


class LayerIdSafetyPolicy(BaseModel):
    """L5 Safety policy for layer ID generation operations"""
    max_id_length: int = Field(default=128, description="Maximum ID length")
    max_generation_attempts: int = Field(default=10, description="Maximum generation attempts for unique IDs")
    allowed_generation_types: List[str] = Field(default_factory=lambda: [t.value for t in IdGenerationType])
    allowed_formats: List[str] = Field(default_factory=lambda: [t.value for t in IdFormat])
    require_uniqueness_validation: bool = Field(default=True)
    prevent_id_collision: bool = Field(default=True)
    sanitize_id_content: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerIdSafetyValidator:
    """L5 Safety validator for layer ID generation operations"""
    
    def __init__(self, policy: LayerIdSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerIdSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._restricted_characters = [
            "/", "\\", ":", "*", "?", "\"", "<", ">", "|",
            ";", "&", "%", "$", "@", "!", "`", "~"
        ]
    
    def validate_id_generation_input(self, id_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates ID generation input against L5 safety policies"""
        try:
            # Check generation type
            generation_type = id_input.get("generation_type", "")
            if generation_type not in self.policy.allowed_generation_types:
                error_msg = f"Prohibited ID generation type: {generation_type}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check format
            id_format = id_input.get("format", "")
            if id_format not in self.policy.allowed_formats:
                error_msg = f"Prohibited ID format: {id_format}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check layer name for dangerous patterns
            layer_name = id_input.get("layer_name", "")
            if layer_name:
                for pattern in self._dangerous_patterns:
                    if pattern in layer_name.lower():
                        error_msg = f"Dangerous pattern in layer name: {pattern}"
                        self.logger.warning(f"Safety violation: {error_msg}")
                        return False, error_msg
                
                # Check for restricted characters
                for char in self._restricted_characters:
                    if char in layer_name:
                        error_msg = f"Restricted character in layer name: {char}"
                        self.logger.warning(f"Safety violation: {error_msg}")
                        return False, error_msg
            
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
class LayerIdRequest:
    """Input request for layer ID generation operations"""
    layer_name: str
    layer_type: str
    generation_type: IdGenerationType
    id_format: IdFormat
    context: Dict[str, Any]
    generation_options: Dict[str, Any] = field(default_factory=dict)
    namespace: Optional[str] = None
    safety_level: str = "standard"


@dataclass
class GeneratedLayerId:
    """Structured representation of a generated layer ID"""
    layer_id: str
    generation_type: IdGenerationType
    id_format: IdFormat
    namespace: Optional[str]
    metadata: Dict[str, Any]
    checksum: str
    timestamp: datetime


@dataclass
class LayerIdGenerationResult:
    """Output result from layer ID generation operations"""
    generated_id: GeneratedLayerId
    generation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    generation_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerIdGeneratorInterface(ABC):
    """Abstract interface for layer ID generation operations"""
    
    @abstractmethod
    async def generate_layer_id(self, request: LayerIdRequest) -> LayerIdGenerationResult:
        """Generate unique layer identifier"""
        pass
    
    @abstractmethod
    async def validate_id_uniqueness(self, layer_id: str, existing_ids: List[str]) -> bool:
        """Validate ID uniqueness against existing IDs"""
        pass
    
    @abstractmethod
    async def generate_namespace_id(self, namespace: str, name: str, generation_type: IdGenerationType) -> str:
        """Generate namespaced layer ID"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerIdGenerator(LayerIdGeneratorInterface):
    """
    L1 Cognitive Planning implementation for generating layer identifiers.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerIdSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerIdSafetyPolicy()
        self.safety_validator = LayerIdSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # ID generation patterns and configurations
        self._generation_configs = {
            IdGenerationType.UUID: {
                "standard_length": 36,
                "short_length": 8,
                "long_length": 36
            },
            IdGenerationType.HASH: {
                "standard_length": 64,
                "short_length": 16,
                "long_length": 128
            },
            IdGenerationType.SEQUENTIAL: {
                "standard_length": 10,
                "short_length": 6,
                "long_length": 15
            },
            IdGenerationType.TIMESTAMP: {
                "standard_length": 19,
                "short_length": 10,
                "long_length": 25
            },
            IdGenerationType.COMPOSITE: {
                "standard_length": 32,
                "short_length": 16,
                "long_length": 64
            },
            IdGenerationType.NAMESPACE: {
                "standard_length": 48,
                "short_length": 24,
                "long_length": 96
            }
        }
        
        self.logger.info("LayerIdGenerator initialized with L5 safety policies")
    
    async def generate_layer_id(self, request: LayerIdRequest) -> LayerIdGenerationResult:
        """
        Generate unique layer identifier.
        
        Args:
            request: Layer ID generation request with layer details and generation options
            
        Returns:
            LayerIdGenerationResult: Structured result with generated ID and metadata
            
        Raises:
            ValidationError: If ID generation fails
            SafetyError: If ID generation violates safety policies
        """
        self.logger.info(f"Generating layer ID for {request.layer_name} using {request.generation_type} type")
        
        try:
            # L5 Safety validation
            id_input = {
                "generation_type": request.generation_type.value,
                "format": request.id_format.value,
                "layer_name": request.layer_name
            }
            
            is_valid, error_msg = self.safety_validator.validate_id_generation_input(id_input)
            if not is_valid:
                raise SafetyError(f"Layer ID generation safety validation failed: {error_msg}")
            
            # Generate ID based on type
            if request.generation_type == IdGenerationType.UUID:
                layer_id = await self._generate_uuid_id(request)
            elif request.generation_type == IdGenerationType.HASH:
                layer_id = await self._generate_hash_id(request)
            elif request.generation_type == IdGenerationType.SEQUENTIAL:
                layer_id = await self._generate_sequential_id(request)
            elif request.generation_type == IdGenerationType.TIMESTAMP:
                layer_id = await self._generate_timestamp_id(request)
            elif request.generation_type == IdGenerationType.COMPOSITE:
                layer_id = await self._generate_composite_id(request)
            elif request.generation_type == IdGenerationType.NAMESPACE:
                layer_id = await self.generate_namespace_id(
                    request.namespace or "default",
                    request.layer_name,
                    request.generation_type
                )
            else:
                raise ValidationError(f"Unsupported ID generation type: {request.generation_type}")
            
            # Validate ID length
            if len(layer_id) > self.safety_policy.max_id_length:
                raise ValidationError(f"Generated ID too long: {len(layer_id)} > {self.safety_policy.max_id_length}")
            
            # Generate checksum
            checksum = self._calculate_checksum(layer_id)
            
            # Create generated ID structure
            generated_id = GeneratedLayerId(
                layer_id=layer_id,
                generation_type=request.generation_type,
                id_format=request.id_format,
                namespace=request.namespace,
                metadata={
                    "layer_name": request.layer_name,
                    "layer_type": request.layer_type,
                    "generation_options": request.generation_options,
                    "id_length": len(layer_id)
                },
                checksum=checksum,
                timestamp=datetime.now()
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_id_risk_score(generated_id),
                "security_flags": self._extract_security_flags(generated_id)
            }
            
            # Generate unique generation ID
            generation_id = self._generate_generation_id(request, generated_id)
            
            result = LayerIdGenerationResult(
                generated_id=generated_id,
                generation_metadata={
                    "generation_duration_ms": 1.0,  # Rough estimate
                    "generation_attempts": 1,
                    "complexity_estimate": await self._estimate_generation_complexity(request)
                },
                safety_validation=safety_validation,
                generation_id=generation_id
            )
            
            self.logger.info(f"Successfully generated layer ID: {layer_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate layer ID: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback ID in non-fail-closed mode
            return self._create_fallback_id(request, str(e))
    
    async def validate_id_uniqueness(self, layer_id: str, existing_ids: List[str]) -> bool:
        """Validate ID uniqueness against existing IDs"""
        try:
            return layer_id not in existing_ids
            
        except Exception as e:
            self.logger.error(f"ID uniqueness validation failed: {str(e)}")
            return False
    
    async def generate_namespace_id(self, namespace: str, name: str, generation_type: IdGenerationType) -> str:
        """Generate namespaced layer ID"""
        try:
            # Combine namespace and name
            combined = f"{namespace}:{name}"
            
            if generation_type == IdGenerationType.HASH:
                # Generate hash of combined string
                hash_obj = hashlib.sha256(combined.encode('utf-8'))
                return f"{namespace}_{hash_obj.hexdigest()[:16]}"
            elif generation_type == IdGenerationType.UUID:
                # Generate UUID5 with namespace
                namespace_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, namespace)
                return f"{namespace}_{str(namespace_uuid)[:8]}"
            else:
                # Default to hash-based generation
                hash_obj = hashlib.sha256(combined.encode('utf-8'))
                return f"{namespace}_{hash_obj.hexdigest()[:12]}"
                
        except Exception as e:
            self.logger.error(f"Namespace ID generation failed: {str(e)}")
            raise
    
    async def _generate_uuid_id(self, request: LayerIdRequest) -> str:
        """Generate UUID-based layer ID"""
        try:
            if request.id_format == IdFormat.STANDARD:
                generated_uuid = str(uuid.uuid4())
            elif request.id_format == IdFormat.SHORT:
                generated_uuid = str(uuid.uuid4())[:8]
            elif request.id_format == IdFormat.LONG:
                generated_uuid = str(uuid.uuid4())
            else:  # CUSTOM
                # Generate custom format with layer name prefix
                layer_prefix = request.layer_name.lower().replace("-", "_")[:8]
                generated_uuid = f"{layer_prefix}_{str(uuid.uuid4())[:8]}"
            
            # Add layer type suffix if specified in options
            if request.generation_options.get("include_type_suffix"):
                type_suffix = request.layer_type.lower()[:3]
                generated_uuid = f"{generated_uuid}_{type_suffix}"
            
            return generated_uuid
            
        except Exception as e:
            self.logger.error(f"UUID ID generation failed: {str(e)}")
            raise
    
    async def _generate_hash_id(self, request: LayerIdRequest) -> str:
        """Generate hash-based layer ID"""
        try:
            # Create content for hashing
            content = {
                "layer_name": request.layer_name,
                "layer_type": request.layer_type,
                "timestamp": datetime.now().isoformat(),
                "context": request.context
            }
            content_str = json.dumps(content, sort_keys=True)
            
            # Generate hash
            if request.id_format == IdFormat.STANDARD:
                hash_obj = hashlib.sha256(content_str.encode('utf-8'))
                layer_id = hash_obj.hexdigest()
            elif request.id_format == IdFormat.SHORT:
                hash_obj = hashlib.sha256(content_str.encode('utf-8'))
                layer_id = hash_obj.hexdigest()[:16]
            elif request.id_format == IdFormat.LONG:
                hash_obj = hashlib.sha512(content_str.encode('utf-8'))
                layer_id = hash_obj.hexdigest()
            else:  # CUSTOM
                hash_obj = hashlib.sha256(content_str.encode('utf-8'))
                layer_prefix = request.layer_name.lower().replace("-", "_")[:6]
                layer_id = f"{layer_prefix}_{hash_obj.hexdigest()[:12]}"
            
            return layer_id
            
        except Exception as e:
            self.logger.error(f"Hash ID generation failed: {str(e)}")
            raise
    
    async def _generate_sequential_id(self, request: LayerIdRequest) -> str:
        """Generate sequential layer ID"""
        try:
            # Get sequence number from context or options
            sequence_number = request.generation_options.get("sequence_number", 1)
            
            if request.id_format == IdFormat.STANDARD:
                layer_id = f"layer_{sequence_number:06d}"
            elif request.id_format == IdFormat.SHORT:
                layer_id = f"l{sequence_number:04d}"
            elif request.id_format == IdFormat.LONG:
                layer_id = f"layer_{request.layer_type}_{sequence_number:08d}"
            else:  # CUSTOM
                layer_prefix = request.layer_name.lower().replace("-", "_")[:6]
                layer_id = f"{layer_prefix}_{sequence_number:06d}"
            
            return layer_id
            
        except Exception as e:
            self.logger.error(f"Sequential ID generation failed: {str(e)}")
            raise
    
    async def _generate_timestamp_id(self, request: LayerIdRequest) -> str:
        """Generate timestamp-based layer ID"""
        try:
            now = datetime.now()
            
            if request.id_format == IdFormat.STANDARD:
                timestamp_str = now.strftime("%Y%m%d_%H%M%S")
                layer_id = f"layer_{timestamp_str}"
            elif request.id_format == IdFormat.SHORT:
                timestamp_str = now.strftime("%Y%m%d")
                layer_id = f"l{timestamp_str}"
            elif request.id_format == IdFormat.LONG:
                timestamp_str = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
                layer_id = f"layer_{request.layer_type}_{timestamp_str}"
            else:  # CUSTOM
                timestamp_str = now.strftime("%Y%m%d_%H%M%S")
                layer_prefix = request.layer_name.lower().replace("-", "_")[:6]
                layer_id = f"{layer_prefix}_{timestamp_str}"
            
            return layer_id
            
        except Exception as e:
            self.logger.error(f"Timestamp ID generation failed: {str(e)}")
            raise
    
    async def _generate_composite_id(self, request: LayerIdRequest) -> str:
        """Generate composite layer ID combining multiple elements"""
        try:
            # Combine multiple elements
            elements = [
                request.layer_name.lower().replace("-", "_"),
                request.layer_type.lower(),
                datetime.now().strftime("%Y%m%d"),
                str(uuid.uuid4())[:8]
            ]
            
            if request.id_format == IdFormat.STANDARD:
                layer_id = "_".join(elements)
            elif request.id_format == IdFormat.SHORT:
                layer_id = "_".join([elem[:6] for elem in elements])
            elif request.id_format == IdFormat.LONG:
                # Include full elements with additional timestamp
                elements.append(datetime.now().strftime("%H%M%S"))
                layer_id = "_".join(elements)
            else:  # CUSTOM
                # Custom composite based on options
                custom_elements = request.generation_options.get("composite_elements", elements)
                layer_id = "_".join(custom_elements)
            
            return layer_id
            
        except Exception as e:
            self.logger.error(f"Composite ID generation failed: {str(e)}")
            raise
    
    def _calculate_checksum(self, layer_id: str) -> str:
        """Calculate checksum for generated layer ID"""
        try:
            return hashlib.sha256(layer_id.encode('utf-8')).hexdigest()[:16]
        except Exception as e:
            self.logger.error(f"Checksum calculation failed: {str(e)}")
            return "checksum_error"
    
    async def _estimate_generation_complexity(self, request: LayerIdRequest) -> str:
        """Estimate ID generation complexity"""
        complexity_score = 1  # Base complexity
        
        # Add complexity for generation type
        if request.generation_type in [IdGenerationType.COMPOSITE, IdGenerationType.NAMESPACE]:
            complexity_score += 2
        elif request.generation_type == IdGenerationType.HASH:
            complexity_score += 1
        
        # Add complexity for format
        if request.id_format == IdFormat.CUSTOM:
            complexity_score += 1
        
        if complexity_score <= 2:
            return "low"
        elif complexity_score <= 4:
            return "medium"
        else:
            return "high"
    
    def _calculate_id_risk_score(self, generated_id: GeneratedLayerId) -> float:
        """Calculate risk score for the generated ID (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for very long IDs
        if len(generated_id.layer_id) > 64:
            risk_score += 0.1
        
        # Increase risk for predictable patterns
        if generated_id.generation_type in [IdGenerationType.SEQUENTIAL, IdGenerationType.TIMESTAMP]:
            risk_score += 0.2
        
        # Increase risk for custom formats (potential injection)
        if generated_id.id_format == IdFormat.CUSTOM:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _extract_security_flags(self, generated_id: GeneratedLayerId) -> List[str]:
        """Extract security flags from generated ID"""
        security_flags = []
        
        # Check for predictable patterns
        if generated_id.generation_type in [IdGenerationType.SEQUENTIAL, IdGenerationType.TIMESTAMP]:
            security_flags.append("predictable_pattern")
        
        # Check for custom format risks
        if generated_id.id_format == IdFormat.CUSTOM:
            security_flags.append("custom_format")
        
        # Check for potential injection in ID
        dangerous_chars = ["<", ">", "&", ";", "'", "\""]
        if any(char in generated_id.layer_id for char in dangerous_chars):
            security_flags.append("potential_injection")
        
        return security_flags
    
    def _generate_generation_id(self, request: LayerIdRequest, generated_id: GeneratedLayerId) -> str:
        """Generate unique generation identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{generated_id.layer_id}:{timestamp}"
        return f"gen_{hash(content) % 1000000:06d}"
    
    def _create_fallback_id(self, request: LayerIdRequest, error: str) -> LayerIdGenerationResult:
        """Create safe fallback ID when main generation fails"""
        fallback_id = f"fallback_layer_{hash(error) % 10000:04d}"
        
        generated_id = GeneratedLayerId(
            layer_id=fallback_id,
            generation_type=IdGenerationType.UUID,
            id_format=IdFormat.STANDARD,
            namespace=None,
            metadata={"fallback": True, "error": error},
            checksum=self._calculate_checksum(fallback_id),
            timestamp=datetime.now()
        )
        
        return LayerIdGenerationResult(
            generated_id=generated_id,
            generation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            generation_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when ID generation violates safety policies"""
    
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


class LayerIdGenerationError(Exception):
    """Raised for general layer ID generation errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, id_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "LAYER_ID_GENERATION_ERROR"
        self.operation = operation
        self.id_type = id_type
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        type_info = f" for {self.id_type}" if self.id_type else ""
        return f"[{self.error_code}]{op_info}{type_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_id_generator(safety_policy: Optional[LayerIdSafetyPolicy] = None) -> LayerIdGenerator:
    """Factory function to create LayerIdGenerator with optional custom safety policy"""
    return LayerIdGenerator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_id_request(request: LayerIdRequest) -> tuple[bool, Optional[str]]:
    """Validate layer ID request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not request.layer_type or not request.layer_type.strip():
            return False, "Layer type cannot be empty"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        if not isinstance(request.generation_options, dict):
            return False, "Generation options must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
