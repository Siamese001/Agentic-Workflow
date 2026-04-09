"""C0 G4: REGISTRY + ALLOWED SET - Registry validation.

10C-REQ-113: Validate identity enforce allowed_models execution_mode locks
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result of registry validation."""
    is_valid: bool
    identity_valid: bool
    model_allowed: bool
    execution_mode_locked: bool
    digest_match: bool
    acl_verified: bool
    rejection_reason: str = ""


class RegistryValidator:
    """C0 G4: Registry validator.
    
    10C-REQ-113: Validate identity enforce allowed_models execution_mode
    locks registry digest integrity match ACL verification.
    """
    
    def __init__(self) -> None:
        self._allowed_models: set[str] = set()
        self._allowed_identities: set[str] = set()
        self._execution_mode_locks: dict[str, str] = {}  # actor -> mode
        self._digest_registry: dict[str, str] = {}
        self._acl_rules: list[tuple[str, str]] = []  # (identity, resource)
    
    def validate(
        self,
        identity: str,
        model: str,
        requested_mode: str,
        digest: str,
        resource: str,
    ) -> ValidationResult:
        """Validate against all registries."""
        id_valid = self._validate_identity(identity)
        model_valid = self._validate_model(model)
        mode_valid = self._validate_execution_mode(identity, requested_mode)
        digest_valid = self._validate_digest(identity, digest)
        acl_valid = self._validate_acl(identity, resource)
        
        all_valid = all([id_valid, model_valid, mode_valid, digest_valid, acl_valid])
        
        if not all_valid:
            reasons = []
            if not id_valid:
                reasons.append("identity_not_registered")
            if not model_valid:
                reasons.append("model_not_allowed")
            if not mode_valid:
                reasons.append("execution_mode_locked")
            if not digest_valid:
                reasons.append("digest_mismatch")
            if not acl_valid:
                reasons.append("acl_denied")
            
            return ValidationResult(
                is_valid=False,
                identity_valid=id_valid,
                model_allowed=model_valid,
                execution_mode_locked=mode_valid,
                digest_match=digest_valid,
                acl_verified=acl_valid,
                rejection_reason=";".join(reasons),
            )
        
        return ValidationResult(
            is_valid=True,
            identity_valid=True,
            model_allowed=True,
            execution_mode_locked=True,
            digest_match=True,
            acl_verified=True,
        )
    
    def _validate_identity(self, identity: str) -> bool:
        """Validate identity is registered."""
        if not self._allowed_identities:
            return True  # Open if no registry
        return identity in self._allowed_identities
    
    def _validate_model(self, model: str) -> bool:
        """Validate model is in allowed set."""
        if not self._allowed_models:
            return True  # Open if no registry
        return model in self._allowed_models
    
    def _validate_execution_mode(self, identity: str, requested_mode: str) -> bool:
        """Validate execution mode is not locked or matches."""
        locked_mode = self._execution_mode_locks.get(identity)
        if locked_mode is None:
            return True
        return locked_mode == requested_mode
    
    def _validate_digest(self, identity: str, digest: str) -> bool:
        """Validate digest integrity."""
        expected_digest = self._digest_registry.get(identity)
        if expected_digest is None:
            return True
        return expected_digest == digest
    
    def _validate_acl(self, identity: str, resource: str) -> bool:
        """Validate ACL rule."""
        if not self._acl_rules:
            return True  # Open if no ACL
        
        for allowed_id, allowed_res in self._acl_rules:
            if identity == allowed_id and resource.startswith(allowed_res):
                return True
        return False
    
    def register_allowed_model(self, model: str) -> None:
        """Register an allowed model."""
        self._allowed_models.add(model)
    
    def register_allowed_identity(self, identity: str) -> None:
        """Register an allowed identity."""
        self._allowed_identities.add(identity)
    
    def lock_execution_mode(self, identity: str, mode: str) -> None:
        """Lock execution mode for an identity."""
        self._execution_mode_locks[identity] = mode
    
    def register_digest(self, identity: str, digest: str) -> None:
        """Register expected digest for identity."""
        self._digest_registry[identity] = digest
    
    def add_acl_rule(self, identity: str, resource_pattern: str) -> None:
        """Add ACL rule."""
        self._acl_rules.append((identity, resource_pattern))
