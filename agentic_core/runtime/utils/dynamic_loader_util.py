"""
Dynamic Dependency Resolver for avoiding circular imports.

Provides lazy loading of implementations to prevent circular dependencies
between base agents and L5 components.
"""

import importlib
import logging
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DynamicLoader:
    """Dynamically loads implementations to avoid circular dependencies.

    Uses lazy loading and caching to efficiently resolve dependencies
    at runtime rather than import time.
    """

    _cache: dict[str, Any] = {}
    _instance_cache: dict[str, Any] = {}

    # Registry of protocol to implementation mappings
    IMPLEMENTATION_REGISTRY: dict[str, dict[str, str]] = {
        "verification": {
            "module": "agentic_core.L5_safety.enforcement.verification_gate",
            "class": "VerificationGate",
        },
        "detection": {
            "module": "agentic_core.L0_routing.enforcement.detection_signal",
            "class": "DetectionSignalEmitter",
        },
        "review": {
            "module": "agentic_core.L5_safety.enforcement.review_queue",
            "class": "HumanReviewQueue",
        },
        "meta_learning": {
            "module": "agentic_core.mixins.meta_learning_mixin",
            "class": "MetaLearningService",
        },
    }

    @classmethod
    def load_class(
        cls,
        module_path: str,
        class_name: str,
    ) -> type[T] | None:
        """Load a class dynamically.

        Args:
            module_path: Full module path (e.g., 'agentic_core.L5_safety.enforcement.verification_gate')
            class_name: Name of the class to load

        Returns:
            Class type or None if loading fails
        """
        cache_key = f"{module_path}:{class_name}"

        if cache_key in cls._cache:
            return cls._cache[cache_key]

        try:
            module = importlib.import_module(module_path)
            implementation = getattr(module, class_name)
            cls._cache[cache_key] = implementation
            logger.debug(f"[LOADER] Loaded {class_name} from {module_path}")
            return implementation

        except ImportError as e:
            logger.warning(f"[LOADER] Could not import {module_path}: {e}")
            return None
        except AttributeError as e:
            logger.warning(f"[LOADER] Class {class_name} not found in {module_path}: {e}")
            return None

    @classmethod
    def load_implementation(
        cls,
        protocol_name: str,
    ) -> type[T] | None:
        """Load implementation for a protocol.

        Args:
            protocol_name: Name of the protocol (e.g., 'verification')

        Returns:
            Implementation class or None if not found
        """
        registry_entry = cls.IMPLEMENTATION_REGISTRY.get(protocol_name)
        if registry_entry is None:
            logger.warning(f"[LOADER] Unknown protocol: {protocol_name}")
            return None

        return cls.load_class(
            module_path=registry_entry["module"],
            class_name=registry_entry["class"],
        )

    @classmethod
    def create_instance(
        cls,
        protocol_name: str,
        *args: Any,
        singleton: bool = True,
        **kwargs: Any,
    ) -> T | None:
        """Create instance of implementation.

        Args:
            protocol_name: Name of the protocol
            *args: Positional arguments for constructor
            singleton: If True, return cached instance
            **kwargs: Keyword arguments for constructor

        Returns:
            Instance or None if creation fails
        """
        if singleton and protocol_name in cls._instance_cache:
            return cls._instance_cache[protocol_name]

        implementation = cls.load_implementation(protocol_name)
        if implementation is None:
            return None

        try:
            instance = implementation(*args, **kwargs)
            if singleton:
                cls._instance_cache[protocol_name] = instance
            logger.debug(f"[LOADER] Created instance of {protocol_name}")
            return instance

        except Exception as e:
            logger.warning(f"[LOADER] Could not create instance of {protocol_name}: {e}")
            return None

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached classes and instances."""
        cls._cache.clear()
        cls._instance_cache.clear()
        logger.info("[LOADER] Cache cleared")

    @classmethod
    def clear_instance_cache(cls, protocol_name: str | None = None) -> None:
        """Clear instance cache.

        Args:
            protocol_name: Specific protocol to clear, or None for all
        """
        if protocol_name:
            if protocol_name in cls._instance_cache:
                del cls._instance_cache[protocol_name]
        else:
            cls._instance_cache.clear()

    @classmethod
    def register_implementation(
        cls,
        protocol_name: str,
        module_path: str,
        class_name: str,
    ) -> None:
        """Register a custom implementation.

        Args:
            protocol_name: Name of the protocol
            module_path: Module path
            class_name: Class name
        """
        cls.IMPLEMENTATION_REGISTRY[protocol_name] = {
            "module": module_path,
            "class": class_name,
        }
        # Clear any cached version
        cache_key = f"{module_path}:{class_name}"
        if cache_key in cls._cache:
            del cls._cache[cache_key]
        if protocol_name in cls._instance_cache:
            del cls._instance_cache[protocol_name]

        logger.info(f"[LOADER] Registered {protocol_name} -> {module_path}:{class_name}")

    @classmethod
    def is_available(cls, protocol_name: str) -> bool:
        """Check if an implementation is available.

        Args:
            protocol_name: Name of the protocol

        Returns:
            True if implementation can be loaded
        """
        implementation = cls.load_implementation(protocol_name)
        return implementation is not None

    @classmethod
    def get_registered_protocols(cls) -> list[str]:
        """Get list of registered protocol names."""
        return list(cls.IMPLEMENTATION_REGISTRY.keys())
