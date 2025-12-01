"""
L1 Cognitive Planning - Prepare Information Registry

Provides dynamic preparer discovery and registration capabilities
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

# Import preparer interfaces
from .format_registry_context import RegistryContextFormatterInterface
from .prepare_core_payload import CorePayloadPreparerInterface


# ============================================================================
# REGISTRY TYPES AND INTERFACES
# ============================================================================

class PreparerType(str, Enum):
    """Supported preparer types for registry"""
    CONTEXT_FORMATTING = "context_formatting"
    PAYLOAD_PREPARATION = "payload_preparation"


@dataclass
class PreparerRegistration:
    """Preparer registration information"""
    preparer_type: PreparerType
    preparer_class: Type
    factory_function: Callable
    instance: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


class PrepareInformationRegistryInterface(ABC):
    """Abstract interface for prepare information registry"""
    
    @abstractmethod
    async def register_preparer(self, registration: PreparerRegistration) -> bool:
        """Register a preparer in the registry"""
        pass
    
    @abstractmethod
    async def unregister_preparer(self, preparer_type: PreparerType) -> bool:
        """Unregister a preparer from the registry"""
        pass
    
    @abstractmethod
    async def get_preparer(self, preparer_type: PreparerType) -> Optional[Any]:
        """Get preparer instance by type"""
        pass
    
    @abstractmethod
    async def list_preparers(self) -> List[PreparerRegistration]:
        """List all registered preparers"""
        pass
    
    @abstractmethod
    async def create_preparer_instance(self, preparer_type: PreparerType, **kwargs) -> Optional[Any]:
        """Create new preparer instance"""
        pass


# ============================================================================
# L5 SAFETY FOR REGISTRY
# ============================================================================

class PrepareRegistrySafetyPolicy(BaseModel):
    """L5 Safety policy for preparation registry"""
    max_registered_preparers: int = Field(default=10, description="Maximum registered preparers")
    allowed_preparer_types: List[str] = Field(default_factory=lambda: [t.value for t in PreparerType])
    require_preparer_validation: bool = Field(default=True)
    prevent_registry_overflow: bool = Field(default=True)
    enable_instance_caching: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class PrepareRegistrySafetyValidator:
    """L5 Safety validator for preparation registry operations"""
    
    def __init__(self, policy: PrepareRegistrySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.PrepareRegistrySafetyValidator")
    
    def validate_registration(self, registration: PreparerRegistration, current_count: int) -> tuple[bool, Optional[str]]:
        """Validates preparer registration against L5 safety policies"""
        try:
            # Check preparer type
            if registration.preparer_type.value not in self.policy.allowed_preparer_types:
                error_msg = f"Prohibited preparer type: {registration.preparer_type.value}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check registration limit
            if current_count >= self.policy.max_registered_preparers:
                error_msg = f"Registry overflow: {current_count} >= {self.policy.max_registered_preparers}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check preparer class
            if not registration.preparer_class:
                error_msg = "Preparer class cannot be None"
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

class PrepareInformationRegistry(PrepareInformationRegistryInterface):
    """
    L1 Cognitive Planning implementation for prepare information registry.
    
    Provides dynamic preparer discovery, registration, and management
    following L5 safety principles and comprehensive logging.
    """
    
    def __init__(self, safety_policy: Optional[PrepareRegistrySafetyPolicy] = None):
        self.safety_policy = safety_policy or PrepareRegistrySafetyPolicy()
        self.safety_validator = PrepareRegistrySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Registry storage
        self._registrations: Dict[PreparerType, PreparerRegistration] = {}
        self._instances: Dict[PreparerType, Any] = {}
        
        # Register built-in preparers
        self._register_builtin_preparers()
        
        self.logger.info("PrepareInformationRegistry initialized with L5 safety policies")
    
    async def register_preparer(self, registration: PreparerRegistration) -> bool:
        """
        Register a preparer in the registry.
        
        Args:
            registration: Preparer registration information
            
        Returns:
            bool: True if registration successful, False otherwise
            
        Raises:
            ValidationError: If registration fails
            SafetyError: If registration violates safety policies
        """
        self.logger.info(f"Registering preparer for type {registration.preparer_type}")
        
        try:
            # L5 Safety validation
            is_valid, error_msg = self.safety_validator.validate_registration(
                registration, 
                len(self._registrations)
            )
            if not is_valid:
                raise SafetyError(f"Prepare registry safety validation failed: {error_msg}")
            
            # Check if preparer type already exists
            if registration.preparer_type in self._registrations:
                self.logger.warning(f"Preparer type {registration.preparer_type} already registered, updating")
            
            # Register preparer
            self._registrations[registration.preparer_type] = registration
            
            # Cache instance if caching is enabled
            if self.safety_policy.enable_instance_caching and registration.instance:
                self._instances[registration.preparer_type] = registration.instance
            
            self.logger.info(f"Successfully registered preparer for {registration.preparer_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register preparer: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            return False
    
    async def unregister_preparer(self, preparer_type: PreparerType) -> bool:
        """
        Unregister a preparer from the registry.
        
        Args:
            preparer_type: Type of preparer to unregister
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        self.logger.info(f"Unregistering preparer for type {preparer_type}")
        
        try:
            if preparer_type not in self._registrations:
                self.logger.warning(f"Preparer type {preparer_type} not found in registry")
                return False
            
            # Remove registration
            del self._registrations[preparer_type]
            
            # Remove cached instance
            if preparer_type in self._instances:
                del self._instances[preparer_type]
            
            self.logger.info(f"Successfully unregistered preparer for {preparer_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister preparer: {str(e)}")
            return False
    
    async def get_preparer(self, preparer_type: PreparerType) -> Optional[Any]:
        """
        Get preparer instance by type.
        
        Args:
            preparer_type: Type of preparer to retrieve
            
        Returns:
            Preparer instance or None if not found
        """
        try:
            # Check cached instance first
            if self.safety_policy.enable_instance_caching and preparer_type in self._instances:
                return self._instances[preparer_type]
            
            # Get registration
            registration = self._registrations.get(preparer_type)
            if not registration:
                self.logger.warning(f"Preparer type {preparer_type} not found in registry")
                return None
            
            # Create instance using factory function
            instance = registration.factory_function()
            
            # Cache instance if caching is enabled
            if self.safety_policy.enable_instance_caching:
                self._instances[preparer_type] = instance
            
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to get preparer instance: {str(e)}")
            return None
    
    async def list_preparers(self) -> List[PreparerRegistration]:
        """
        List all registered preparers.
        
        Returns:
            List of preparer registrations
        """
        try:
            return list(self._registrations.values())
        except Exception as e:
            self.logger.error(f"Failed to list preparers: {str(e)}")
            return []
    
    async def create_preparer_instance(self, preparer_type: PreparerType, **kwargs) -> Optional[Any]:
        """
        Create new preparer instance.
        
        Args:
            preparer_type: Type of preparer to create
            **kwargs: Additional arguments for preparer creation
            
        Returns:
            New preparer instance or None if creation failed
        """
        try:
            registration = self._registrations.get(preparer_type)
            if not registration:
                self.logger.warning(f"Preparer type {preparer_type} not found in registry")
                return None
            
            # Create instance using factory function with kwargs
            if kwargs:
                instance = registration.factory_function(**kwargs)
            else:
                instance = registration.factory_function()
            
            self.logger.info(f"Created new instance for preparer {preparer_type}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to create preparer instance: {str(e)}")
            return None
    
    async def get_preparer_info(self, preparer_type: PreparerType) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a preparer.
        
        Args:
            preparer_type: Type of preparer to get info for
            
        Returns:
            Preparer information dictionary or None if not found
        """
        try:
            registration = self._registrations.get(preparer_type)
            if not registration:
                return None
            
            return {
                "preparer_type": registration.preparer_type.value,
                "preparer_class": registration.preparer_class.__name__,
                "metadata": registration.metadata,
                "registered_at": registration.registered_at.isoformat(),
                "is_active": registration.is_active,
                "has_cached_instance": preparer_type in self._instances
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get preparer info: {str(e)}")
            return None
    
    async def clear_cache(self) -> bool:
        """
        Clear all cached preparer instances.
        
        Returns:
            bool: True if cache cleared successfully
        """
        try:
            self._instances.clear()
            self.logger.info("Preparer instance cache cleared")
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
            active_preparers = sum(1 for reg in self._registrations.values() if reg.is_active)
            cached_instances = len(self._instances)
            
            return {
                "total_registered": len(self._registrations),
                "active_preparers": active_preparers,
                "cached_instances": cached_instances,
                "preparer_types": [pt.value for pt in self._registrations.keys()],
                "registry_capacity": f"{len(self._registrations)}/{self.safety_policy.max_registered_preparers}"
            }
        except Exception as e:
            self.logger.error(f"Failed to get registry stats: {str(e)}")
            return {}
    
    def _register_builtin_preparers(self):
        """Register built-in preparers"""
        try:
            # Import factory functions
            from .format_registry_context import create_registry_context_formatter
            from .prepare_core_payload import create_core_payload_preparer
            
            # Register built-in preparers
            builtin_preparers = [
                PreparerRegistration(
                    preparer_type=PreparerType.CONTEXT_FORMATTING,
                    preparer_class=RegistryContextFormatterInterface,
                    factory_function=create_registry_context_formatter,
                    metadata={"builtin": True, "category": "formatting"}
                ),
                PreparerRegistration(
                    preparer_type=PreparerType.PAYLOAD_PREPARATION,
                    preparer_class=CorePayloadPreparerInterface,
                    factory_function=create_core_payload_preparer,
                    metadata={"builtin": True, "category": "preparation"}
                )
            ]
            
            # Register all built-in preparers
            for registration in builtin_preparers:
                self._registrations[registration.preparer_type] = registration
            
            self.logger.info(f"Registered {len(builtin_preparers)} built-in preparers")
            
        except Exception as e:
            self.logger.error(f"Failed to register built-in preparers: {str(e)}")


# ============================================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================================

_global_registry: Optional[PrepareInformationRegistry] = None


def get_prepare_information_registry() -> PrepareInformationRegistry:
    """
    Get the global prepare information registry instance.
    
    Returns:
        Global PrepareInformationRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PrepareInformationRegistry()
    return _global_registry


def set_prepare_information_registry(registry: PrepareInformationRegistry):
    """
    Set the global prepare information registry instance.
    
    Args:
        registry: PrepareInformationRegistry instance to set as global
    """
    global _global_registry
    _global_registry = registry


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when preparation registry operations violate safety policies"""
    
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


class PrepareRegistryError(Exception):
    """Raised for general preparation registry errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, registry_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "PREPARE_REGISTRY_ERROR"
        self.operation = operation
        self.registry_type = registry_type
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        type_info = f" for {self.registry_type}" if self.registry_type else ""
        return f"[{self.error_code}]{op_info}{type_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_prepare_information_registry(safety_policy: Optional[PrepareRegistrySafetyPolicy] = None) -> PrepareInformationRegistry:
    """Factory function to create PrepareInformationRegistry"""
    return PrepareInformationRegistry(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def register_custom_preparer(
    preparer_type: PreparerType,
    preparer_class: Type,
    factory_function: Callable,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Utility function to register a custom preparer.
    
    Args:
        preparer_type: Type of preparer
        preparer_class: Preparer class
        factory_function: Factory function to create preparer instances
        metadata: Optional metadata for the preparer
        
    Returns:
        bool: True if registration successful
    """
    registry = get_prepare_information_registry()
    
    registration = PreparerRegistration(
        preparer_type=preparer_type,
        preparer_class=preparer_class,
        factory_function=factory_function,
        metadata=metadata or {}
    )
    
    return await registry.register_preparer(registration)


async def get_preparer_instance(preparer_type: PreparerType) -> Optional[Any]:
    """
    Utility function to get a preparer instance.
    
    Args:
        preparer_type: Type of preparer to retrieve
        
    Returns:
        Preparer instance or None if not found
    """
    registry = get_prepare_information_registry()
    return await registry.get_preparer(preparer_type)


async def list_available_preparers() -> List[str]:
    """
    Utility function to list available preparer types.
    
    Returns:
        List of preparer type names
    """
    registry = get_prepare_information_registry()
    registrations = await registry.list_preparers()
    return [reg.preparer_type.value for reg in registrations]
