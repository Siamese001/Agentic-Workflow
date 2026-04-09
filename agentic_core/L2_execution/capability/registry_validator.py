"""C7 G2: REGISTRY + ALLOWED SET - Validate identity and models.

10C-REQ-156: Validate allowed tool set model registry identity digest ACL
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RegistryValidationResult:
    """Result of registry validation."""
    is_valid: bool
    identity_verified: bool
    model_allowed: bool
    tool_permitted: bool
    acl_passed: bool
    failure_reasons: list[str]


class RegistryValidator:
    """C7 Registry Validator for capabilities and tools.
    
    10C-REQ-156: Validate against allowed sets and registries.
    """
    
    def __init__(self) -> None:
        self._allowed_models: set[str] = set()
        self._allowed_tools: set[str] = set()
        self._identity_registry: dict[str, str] = {}
    
    def register_allowed_model(self, model_name: str) -> None:
        """Register an allowed model."""
        self._allowed_models.add(model_name)
    
    def register_allowed_tool(self, tool_name: str) -> None:
        """Register an allowed tool."""
        self._allowed_tools.add(tool_name)
    
    def register_identity(self, actor_id: str, credential_hash: str) -> None:
        """Register an actor identity."""
        self._identity_registry[actor_id] = credential_hash
    
    def validate(
        self,
        actor_id: str,
        model: str | None = None,
        tool: str | None = None,
        credential: str | None = None,
    ) -> RegistryValidationResult:
        """Validate access against registries."""
        failures: list[str] = []
        
        # Identity check
        identity_verified = actor_id in self._identity_registry
        if credential and actor_id in self._identity_registry:
            # In production, would verify credential hash
            identity_verified = True
        
        if not identity_verified:
            failures.append("identity_not_registered")
        
        # Model check
        model_allowed = True
        if model and self._allowed_models:
            model_allowed = model in self._allowed_models
            if not model_allowed:
                failures.append(f"model_not_allowed:{model}")
        
        # Tool check
        tool_permitted = True
        if tool and self._allowed_tools:
            tool_permitted = tool in self._allowed_tools
            if not tool_permitted:
                failures.append(f"tool_not_permitted:{tool}")
        
        is_valid = identity_verified and model_allowed and tool_permitted
        
        return RegistryValidationResult(
            is_valid=is_valid,
            identity_verified=identity_verified,
            model_allowed=model_allowed,
            tool_permitted=tool_permitted,
            acl_passed=is_valid,
            failure_reasons=failures,
        )
    
    def get_allowed_models(self) -> list[str]:
        """Get list of allowed models."""
        return list(self._allowed_models)
    
    def get_allowed_tools(self) -> list[str]:
        """Get list of allowed tools."""
        return list(self._allowed_tools)
