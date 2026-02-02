"""
ValidatorOrchestrator - Unified Validation Gateway

[PHASE 5 MIGRATION] Consolidates all validator operations:
- Code validation
- Structure validation
- Logic validation
- Centralized audit logging
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from agentic_core.config.sovereign_config_manager_config import get_sovereign_config

Logger = logging.getLogger(__name__)


class ValidatorProtocol(Protocol):
    """Protocol for validators."""

    def validate(self, content: Any, context: dict) -> dict:
        """
        Validate content.
        Returns: {"valid": bool, "errors": list[str]}
        """
        ...


@dataclass
class ValidatorOrchestrator:
    """
    Unified Validator Orchestrator.

    [PHASE 5 MIGRATION] Absorbed from:
    - CodeValidatorAgent.py
    - StructuralValidatorAgent.py
    - CodeValidatorAgent.py (Duplicate)
    """

    _instance: ValidatorOrchestrator | None = None

    # [PHASE 6] configuration now managed by SovereignConfigManager

    # State
    _validators: dict[str, ValidatorProtocol] = field(default_factory=dict)

    operation_stats: dict[str, Any] = field(
        default_factory=lambda: {"total_validations": 0, "valid": 0, "invalid": 0, "errors": 0}
    )

    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """[TESTING ONLY] Reset singleton state."""
        cls._instance = None

    @property
    def config(self):
        """[PHASE 6] Access centralized config."""
        return get_sovereign_config()

    def register_validator(self, name: str, validator: ValidatorProtocol) -> None:
        """Register a named validator."""
        self._validators[name] = validator
        Logger.info(f"[Validator Orchestrator] Registered: {name}")

    def _audit(self, validator_name: str, valid: bool, latency_ms: float) -> None:
        """Record validation event with FIFO rotation."""
        # [PHASE 6] Dynamic limit from config
        limit = self.config.max_audit_log_size

        if len(self.audit_log) >= limit:
            prune_count = max(1, int(limit * 0.1))
            self.audit_log = self.audit_log[prune_count:]

        self.audit_log.append(
            {
                "validator": validator_name,
                "valid": valid,
                "latency_ms": latency_ms,
                "ts": time.time(),
            }
        )

        self.operation_stats["total_validations"] += 1
        if valid:
            self.operation_stats["valid"] += 1
        else:
            self.operation_stats["invalid"] += 1

    async def validate(self, content: Any, validator_name: str, context: dict = None) -> dict:
        """
        Execute specific validation.
        """
        context = context or {}
        start = time.time()

        validator = self._validators.get(validator_name)
        if not validator:
            Logger.error(f"Validator not found: {validator_name}")
            return {"valid": False, "errors": [f"Validator {validator_name} not found"]}

        try:
            result = validator.validate(content, context)
            latency = (time.time() - start) * 1000

            is_valid = result.get("valid", False)
            self._audit(validator_name, is_valid, latency)

            return result

        except Exception as e:
            latency = (time.time() - start) * 1000
            self._audit(validator_name, False, latency)
            self.operation_stats["errors"] += 1
            Logger.error(f"Validation failed ({validator_name}): {e}")
            return {"valid": False, "errors": [str(e)]}


# Singleton accessor
def get_validator_orchestrator() -> ValidatorOrchestrator:
    """Get or create the global validator orchestrator."""
    return ValidatorOrchestrator()
