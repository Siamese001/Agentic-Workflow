"""
Generic Runtime Customization Package Contract

App-agnostic base contract for runtime customization packages.
All app-specific values must come from app-owned config, not this contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib
import json


class ValidationStatus(Enum):
    """Validation status for runtime packages."""
    VALID = "valid"
    INVALID = "invalid"
    AUTO_INJECTED = "auto_injected"
    EXPLICIT = "explicit"


@dataclass(frozen=True)
class RuntimeCustomizationPackage:
    """
    Generic runtime customization package contract.
    
    App-agnostic dataclass that holds package metadata and refs.
    App-specific defaults must NOT be added here - they belong in app config.
    
    Fields:
        package_id: Unique package identifier
        package_version: Package version string
        app_id: Target app identifier (resolved from request)
        task_class: Task class identifier (resolved from request or package)
        package_ref: Reference to app-owned package config file
        package_digest: Computed digest of package contents
        profile_refs: Dict of profile references (route, cache, etc.)
        policy_hash: Hash of policy configuration
        blueprint_hash: Hash of package blueprint
        registry_digest_set: Set of digests for registry validation
        package_origin: Origin of package (explicit, auto_injected, etc.)
        auto_injected_runtime_package: Whether package was auto-injected
        auto_injection_reason: Reason for auto-injection
        auto_injection_receipt_ref: Receipt reference for auto-injection
        validation_status: Package validation status
        validation_errors: List of validation error messages
        extra: Additional app-specific fields (validated against schema)
    """
    # Core identity fields
    package_id: str
    package_version: str = "1.0.0"
    app_id: str = ""
    task_class: str = ""
    
    # References (app-owned)
    package_ref: str = ""  # Path to app-owned package config
    package_digest: str = ""  # Computed digest
    
    # Profile refs (app-owned config paths)
    profile_refs: Dict[str, str] = field(default_factory=dict)
    
    # Policy/blueprint hashes
    policy_hash: str = ""
    blueprint_hash: str = ""
    registry_digest_set: List[str] = field(default_factory=list)
    
    # Origin tracking
    package_origin: str = "unknown"
    auto_injected_runtime_package: bool = False
    auto_injection_reason: str = ""
    auto_injection_receipt_ref: str = ""
    
    # Validation status
    validation_status: str = "unknown"
    validation_errors: List[str] = field(default_factory=list)
    
    # Extra fields container (for app-specific extensions)
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Compute package digest if not provided."""
        if not self.package_digest:
            digest = self._compute_digest()
            object.__setattr__(self, 'package_digest', digest)
    
    def _compute_digest(self) -> str:
        """Compute SHA-256 digest of package contents (excluding digest field)."""
        data = {
            "package_id": self.package_id,
            "package_version": self.package_version,
            "app_id": self.app_id,
            "task_class": self.task_class,
            "package_ref": self.package_ref,
            "profile_refs": self.profile_refs,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "extra": self.extra,
        }
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "package_id": self.package_id,
            "package_version": self.package_version,
            "app_id": self.app_id,
            "task_class": self.task_class,
            "package_ref": self.package_ref,
            "package_digest": self.package_digest,
            "profile_refs": self.profile_refs,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "registry_digest_set": self.registry_digest_set,
            "package_origin": self.package_origin,
            "auto_injected_runtime_package": self.auto_injected_runtime_package,
            "auto_injection_reason": self.auto_injection_reason,
            "auto_injection_receipt_ref": self.auto_injection_receipt_ref,
            "validation_status": self.validation_status,
            "validation_errors": self.validation_errors,
            "extra": self.extra,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuntimeCustomizationPackage":
        """Create from dictionary."""
        # Extract known fields
        known_fields = {
            "package_id", "package_version", "app_id", "task_class",
            "package_ref", "package_digest", "profile_refs", "policy_hash",
            "blueprint_hash", "registry_digest_set", "package_origin",
            "auto_injected_runtime_package", "auto_injection_reason",
            "auto_injection_receipt_ref", "validation_status", "validation_errors",
            "extra",
        }
        
        kwargs = {k: v for k, v in data.items() if k in known_fields}
        
        # Unknown fields go into extra
        extra_fields = {k: v for k, v in data.items() if k not in known_fields}
        if extra_fields:
            kwargs["extra"] = {**(kwargs.get("extra") or {}), **extra_fields}
        
        return cls(**kwargs)
    
    def validate_schema(self, schema: Optional[Dict[str, Any]] = None) -> tuple[bool, List[str]]:
        """
        Validate package against optional schema.
        
        Args:
            schema: Optional validation schema
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        if not self.package_id:
            errors.append("package_id is required")
        
        if not self.app_id:
            errors.append("app_id is required")
        
        if not self.task_class:
            errors.append("task_class is required")
        
        # Schema validation if provided
        if schema:
            schema_errors = self._validate_against_schema(schema)
            errors.extend(schema_errors)
        
        return len(errors) == 0, errors
    
    def _validate_against_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Validate extra fields against schema."""
        errors = []
        allowed_fields = schema.get("allowed_fields", [])
        required_fields = schema.get("required_fields", [])
        
        # Check for unknown fields in extra
        for field_name in self.extra:
            if field_name not in allowed_fields:
                errors.append(f"Unknown field in extra: {field_name}")
        
        # Check required fields
        for field_name in required_fields:
            if field_name not in self.extra:
                errors.append(f"Required field missing in extra: {field_name}")
        
        return errors


class UnknownPackageFieldError(Exception):
    """Raised when runtime_customization_package contains unknown fields."""
    
    def __init__(self, field: str, message: str = ""):
        self.field = field
        self.message = message or f"Unknown field in runtime customization package: {field}"
        super().__init__(self.message)


class PackageDigestMismatchError(Exception):
    """Raised when package digest verification fails."""
    
    def __init__(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Package digest mismatch: expected {expected[:16]}..., got {actual[:16]}...")


@dataclass(frozen=True)
class PackageValidationReceipt:
    """Receipt produced by U0 package validation."""
    
    package_id: str
    package_version: str
    task_class: str
    validation_passed: bool
    unknown_fields_found: List[str]
    digest_verified: bool
    timestamp_iso: str
    schema_version: str = "AG9.U0.PKG.1"


__all__ = [
    "RuntimeCustomizationPackage",
    "PackageValidationReceipt",
    "ValidationStatus",
    "UnknownPackageFieldError",
    "PackageDigestMismatchError",
]
