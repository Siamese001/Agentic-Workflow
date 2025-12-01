"""
L1 Cognitive Planning - Layer Validation Registry

Provides dynamic validator discovery and registration capabilities
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError

# Import all validator interfaces
from .validate_layer_dependencies import LayerDependenciesValidatorInterface
from .validate_layer_interfaces import LayerInterfacesValidatorInterface
from .validate_layer_compatibility import LayerCompatibilityValidatorInterface
from .validate_layer_security import LayerSecurityValidatorInterface
from .validate_layer_performance import LayerPerformanceValidatorInterface
from .validate_layer_reliability import LayerReliabilityValidatorInterface
from .validate_layer_scalability import LayerScalabilityValidatorInterface
from .validate_layer_maintainability import LayerMaintainabilityValidatorInterface
from .validate_layer_completeness import LayerCompletenessValidatorInterface


# ============================================================================
# REGISTRY TYPES AND INTERFACES
# ============================================================================

class ValidatorType(str, Enum):
    """Supported validator types for registry"""
    DEPENDENCIES = "dependencies"
    INTERFACES = "interfaces"
    COMPATIBILITY = "compatibility"
    SECURITY = "security"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    COMPLETENESS = "completeness"


@dataclass
class ValidatorRegistration:
    """Validator registration information"""
    validator_type: ValidatorType
    validator_class: Type
    factory_function: Callable
    instance: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


class ValidationRegistryInterface(ABC):
    """Abstract interface for validation registry"""
    
    @abstractmethod
    async def register_validator(self, registration: ValidatorRegistration) -> bool:
        """Register a validator in the registry"""
        pass
    
    @abstractmethod
    async def unregister_validator(self, validator_type: ValidatorType) -> bool:
        """Unregister a validator from the registry"""
        pass
    
    @abstractmethod
    async def get_validator(self, validator_type: ValidatorType) -> Optional[Any]:
        """Get validator instance by type"""
        pass
    
    @abstractmethod
    async def list_validators(self) -> List[ValidatorRegistration]:
        """List all registered validators"""
        pass
    
    @abstractmethod
    async def create_validator_instance(self, validator_type: ValidatorType, **kwargs) -> Optional[Any]:
        """Create new validator instance"""
        pass


# ============================================================================
# L5 SAFETY FOR REGISTRY
# ============================================================================

class RegistrySafetyPolicy(BaseModel):
    """L5 Safety policy for validation registry"""
    max_registered_validators: int = Field(default=20, description="Maximum registered validators")
    allowed_validator_types: List[str] = Field(default_factory=lambda: [t.value for t in ValidatorType])
    require_validator_validation: bool = Field(default=True)
    prevent_registry_overflow: bool = Field(default=True)
    enable_instance_caching: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class RegistrySafetyValidator:
    """L5 Safety validator for registry operations"""
    
    def __init__(self, policy: RegistrySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.RegistrySafetyValidator")
    
    def validate_registration(self, registration: ValidatorRegistration, current_count: int) -> tuple[bool, Optional[str]]:
        """Validates validator registration against L5 safety policies"""
        try:
            # Check validator type
            if registration.validator_type.value not in self.policy.allowed_validator_types:
                error_msg = f"Prohibited validator type: {registration.validator_type.value}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check registration limit
            if current_count >= self.policy.max_registered_validators:
                error_msg = f"Registry overflow: {current_count} >= {self.policy.max_registered_validators}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validator class
            if not registration.validator_class:
                error_msg = "Validator class cannot be None"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check factory function
            if not registration.factory_function:
                error_msg = "Factory function cannot be None"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            return True, None
            
        except Exception as e:
            error_msg = f"Registration validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class ValidationRegistry(ValidationRegistryInterface):
    """
    L1 Cognitive Planning implementation for validation registry.
    
    Provides dynamic validator discovery, registration, and management
    following L5 safety principles and comprehensive logging.
    """
    
    def __init__(self, safety_policy: Optional[RegistrySafetyPolicy] = None):
        self.safety_policy = safety_policy or RegistrySafetyPolicy()
        self.safety_validator = RegistrySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Registry storage
        self._registrations: Dict[ValidatorType, ValidatorRegistration] = {}
        self._instances: Dict[ValidatorType, Any] = {}
        
        # Register built-in validators
        self._register_builtin_validators()
        
        self.logger.info("ValidationRegistry initialized with L5 safety policies")
    
    async def register_validator(self, registration: ValidatorRegistration) -> bool:
        """
        Register a validator in the registry.
        
        Args:
            registration: Validator registration information
            
        Returns:
            bool: True if registration successful, False otherwise
            
        Raises:
            ValidationError: If registration fails
            SafetyError: If registration violates safety policies
        """
        self.logger.info(f"Registering validator for type {registration.validator_type}")
        
        try:
            # L5 Safety validation
            is_valid, error_msg = self.safety_validator.validate_registration(
                registration, 
                len(self._registrations)
            )
            if not is_valid:
                raise SafetyError(f"Registry safety validation failed: {error_msg}")
            
            # Check if validator type already exists
            if registration.validator_type in self._registrations:
                self.logger.warning(f"Validator type {registration.validator_type} already registered, updating")
            
            # Register validator
            self._registrations[registration.validator_type] = registration
            
            # Cache instance if caching is enabled
            if self.safety_policy.enable_instance_caching and registration.instance:
                self._instances[registration.validator_type] = registration.instance
            
            self.logger.info(f"Successfully registered validator for {registration.validator_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register validator: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            return False
    
    async def unregister_validator(self, validator_type: ValidatorType) -> bool:
        """
        Unregister a validator from the registry.
        
        Args:
            validator_type: Type of validator to unregister
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        self.logger.info(f"Unregistering validator for type {validator_type}")
        
        try:
            if validator_type not in self._registrations:
                self.logger.warning(f"Validator type {validator_type} not found in registry")
                return False
            
            # Remove registration
            del self._registrations[validator_type]
            
            # Remove cached instance
            if validator_type in self._instances:
                del self._instances[validator_type]
            
            self.logger.info(f"Successfully unregistered validator for {validator_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister validator: {str(e)}")
            return False
    
    async def get_validator(self, validator_type: ValidatorType) -> Optional[Any]:
        """
        Get validator instance by type.
        
        Args:
            validator_type: Type of validator to retrieve
            
        Returns:
            Validator instance or None if not found
        """
        try:
            # Check cached instance first
            if self.safety_policy.enable_instance_caching and validator_type in self._instances:
                return self._instances[validator_type]
            
            # Get registration
            registration = self._registrations.get(validator_type)
            if not registration:
                self.logger.warning(f"Validator type {validator_type} not found in registry")
                return None
            
            # Create instance using factory function
            instance = registration.factory_function()
            
            # Cache instance if caching is enabled
            if self.safety_policy.enable_instance_caching:
                self._instances[validator_type] = instance
            
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to get validator instance: {str(e)}")
            return None
    
    async def list_validators(self) -> List[ValidatorRegistration]:
        """
        List all registered validators.
        
        Returns:
            List of validator registrations
        """
        try:
            return list(self._registrations.values())
        except Exception as e:
            self.logger.error(f"Failed to list validators: {str(e)}")
            return []
    
    async def create_validator_instance(self, validator_type: ValidatorType, **kwargs) -> Optional[Any]:
        """
        Create new validator instance.
        
        Args:
            validator_type: Type of validator to create
            **kwargs: Additional arguments for validator creation
            
        Returns:
            New validator instance or None if creation failed
        """
        try:
            registration = self._registrations.get(validator_type)
            if not registration:
                self.logger.warning(f"Validator type {validator_type} not found in registry")
                return None
            
            # Create instance using factory function with kwargs
            if kwargs:
                instance = registration.factory_function(**kwargs)
            else:
                instance = registration.factory_function()
            
            self.logger.info(f"Created new instance for validator {validator_type}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to create validator instance: {str(e)}")
            return None
    
    async def get_validator_info(self, validator_type: ValidatorType) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a validator.
        
        Args:
            validator_type: Type of validator to get info for
            
        Returns:
            Validator information dictionary or None if not found
        """
        try:
            registration = self._registrations.get(validator_type)
            if not registration:
                return None
            
            return {
                "validator_type": registration.validator_type.value,
                "validator_class": registration.validator_class.__name__,
                "metadata": registration.metadata,
                "registered_at": registration.registered_at.isoformat(),
                "is_active": registration.is_active,
                "has_cached_instance": validator_type in self._instances
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get validator info: {str(e)}")
            return None
    
    async def clear_cache(self) -> bool:
        """
        Clear all cached validator instances.
        
        Returns:
            bool: True if cache cleared successfully
        """
        try:
            self._instances.clear()
            self.logger.info("Validator instance cache cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {str(e)}")
            return False
    
    async def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Registry statistics dictionary
        """
        try:
            active_validators = sum(1 for reg in self._registrations.values() if reg.is_active)
            cached_instances = len(self._instances)
            
            return {
                "total_registered": len(self._registrations),
                "active_validators": active_validators,
                "cached_instances": cached_instances,
                "validator_types": [vt.value for vt in self._registrations.keys()],
                "registry_capacity": f"{len(self._registrations)}/{self.safety_policy.max_registered_validators}"
            }
        except Exception as e:
            self.logger.error(f"Failed to get registry stats: {str(e)}")
            return {}
    
    def _register_builtin_validators(self):
        """Register built-in validators"""
        try:
            # Import factory functions
            from .validate_layer_dependencies import create_layer_dependencies_validator
            from .validate_layer_interfaces import create_layer_interfaces_validator
            from .validate_layer_compatibility import create_layer_compatibility_validator
            from .validate_layer_security import create_layer_security_validator
            from .validate_layer_performance import create_layer_performance_validator
            from .validate_layer_reliability import create_layer_reliability_validator
            from .validate_layer_scalability import create_layer_scalability_validator
            from .validate_layer_maintainability import create_layer_maintainability_validator
            from .validate_layer_completeness import create_layer_completeness_validator
            
            # Register built-in validators
            builtin_validators = [
                ValidatorRegistration(
                    validator_type=ValidatorType.DEPENDENCIES,
                    validator_class=LayerDependenciesValidatorInterface,
                    factory_function=create_layer_dependencies_validator,
                    metadata={"builtin": True, "category": "core"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.INTERFACES,
                    validator_class=LayerInterfacesValidatorInterface,
                    factory_function=create_layer_interfaces_validator,
                    metadata={"builtin": True, "category": "core"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.COMPATIBILITY,
                    validator_class=LayerCompatibilityValidatorInterface,
                    factory_function=create_layer_compatibility_validator,
                    metadata={"builtin": True, "category": "core"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.SECURITY,
                    validator_class=LayerSecurityValidatorInterface,
                    factory_function=create_layer_security_validator,
                    metadata={"builtin": True, "category": "quality"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.PERFORMANCE,
                    validator_class=LayerPerformanceValidatorInterface,
                    factory_function=create_layer_performance_validator,
                    metadata={"builtin": True, "category": "quality"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.RELIABILITY,
                    validator_class=LayerReliabilityValidatorInterface,
                    factory_function=create_layer_reliability_validator,
                    metadata={"builtin": True, "category": "quality"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.SCALABILITY,
                    validator_class=LayerScalabilityValidatorInterface,
                    factory_function=create_layer_scalability_validator,
                    metadata={"builtin": True, "category": "quality"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.MAINTAINABILITY,
                    validator_class=LayerMaintainabilityValidatorInterface,
                    factory_function=create_layer_maintainability_validator,
                    metadata={"builtin": True, "category": "quality"}
                ),
                ValidatorRegistration(
                    validator_type=ValidatorType.COMPLETENESS,
                    validator_class=LayerCompletenessValidatorInterface,
                    factory_function=create_layer_completeness_validator,
                    metadata={"builtin": True, "category": "quality"}
                )
            ]
            
            # Register all built-in validators
            for registration in builtin_validators:
                self._registrations[registration.validator_type] = registration
            
            self.logger.info(f"Registered {len(builtin_validators)} built-in validators")
            
        except Exception as e:
            self.logger.error(f"Failed to register built-in validators: {str(e)}")


# ============================================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================================

_global_registry: Optional[ValidationRegistry] = None


def get_validation_registry() -> ValidationRegistry:
    """
    Get the global validation registry instance.
    
    Returns:
        Global ValidationRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ValidationRegistry()
    return _global_registry


def set_validation_registry(registry: ValidationRegistry):
    """
    Set the global validation registry instance.
    
    Args:
        registry: ValidationRegistry instance to set as global
    """
    global _global_registry
    _global_registry = registry


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when registry operations violate safety policies"""
    pass


class RegistryError(Exception):
    """Raised for general registry errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_validation_registry(safety_policy: Optional[RegistrySafetyPolicy] = None) -> ValidationRegistry:
    """Factory function to create ValidationRegistry"""
    return ValidationRegistry(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def register_custom_validator(
    validator_type: ValidatorType,
    validator_class: Type,
    factory_function: Callable,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Utility function to register a custom validator.
    
    Args:
        validator_type: Type of validator
        validator_class: Validator class
        factory_function: Factory function to create validator instances
        metadata: Optional metadata for the validator
        
    Returns:
        bool: True if registration successful
    """
    registry = get_validation_registry()
    
    registration = ValidatorRegistration(
        validator_type=validator_type,
        validator_class=validator_class,
        factory_function=factory_function,
        metadata=metadata or {}
    )
    
    return await registry.register_validator(registration)


async def get_validator_instance(validator_type: ValidatorType) -> Optional[Any]:
    """
    Utility function to get a validator instance.
    
    Args:
        validator_type: Type of validator to retrieve
        
    Returns:
        Validator instance or None if not found
    """
    registry = get_validation_registry()
    return await registry.get_validator(validator_type)


async def list_available_validators() -> List[str]:
    """
    Utility function to list available validator types.
    
    Returns:
        List of validator type names
    """
    registry = get_validation_registry()
    registrations = await registry.list_validators()
    return [reg.validator_type.value for reg in registrations]
