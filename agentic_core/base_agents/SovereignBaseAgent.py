"""
SovereignBaseAgent - Sovereign Single Source of Truth (SSOT) Root.

Provides foundational capabilities for agents with sovereign authority.

PHASE 9 MIGRATION (Jan 2026):
- Global Injection of Phase 4-6 Architectures.
- Native capabilities: Config, LLM, Embedding, Healing, Validation.
- Resolves "Opt-In" drift by enforcing capabilities at the root.

PHASE 2 META-LEARNING (Feb 2026):
- MetaLearningClientMixin integration for healing pattern memory.
- Redis hot-path caching for expensive AST analysis results.
- Pinecone semantic retrieval for successful healing strategies.
- Domain isolation for apps_lic and apps_rg territories.

L0 DNA FLATTENING:
infrastructure_mixin consolidates core capabilities (legacy).
New Mixins provide Gateway access (modern).

MRO HARDENING:
- This is the ROOT of the agent hierarchy
- infrastructure_mixin is injected HERE so all agents get full infrastructure
- Layer bases add specialized mixins BEFORE SovereignBaseAgent
- MRO Flow: Specialized -> Layer -> SovereignBaseAgent -> [Mixins] -> object
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.infrastructure_mixin import infrastructure_mixin

# [PHASE 9] Global Architecture Injection
from agentic_core.config.core.config_mixin_config import ConfigMixin

# [COGNITIVE HARDENING] Anti-Context Drift and Token Overload
from agentic_core.L1_cognition.memory.golden_context_mixin import GoldenContextMixin
from agentic_core.L2_execution.mcp.embedding_mixin import EmbeddingMixin
from agentic_core.L2_execution.mcp.llm_provider_mixin import LLMProviderMixin
from agentic_core.L4_state.utils.telemetry_sanitizer import sanitize_tool_output
from agentic_core.L5_safety.validators.core.healing_strategy_mixin import HealingStrategyMixin
from agentic_core.L5_safety.validators.core.validator_mixin import ValidatorMixin
from agentic_core.utils.core_integrity_verifier_validator import (
    CoreIntegrityVerifier,
    emergency_shutdown,
)
from agentic_core.utils.HealerError import ConfigurationError, SovereignError

logger = logging.getLogger(__name__)


@dataclass
class SovereignBaseAgent(
    infrastructure_mixin,
    SubatomicTestingMixin,
    ConfigMixin,
    LLMProviderMixin,
    EmbeddingMixin,
    HealingStrategyMixin,
    ValidatorMixin,
    AuditTrailMixin,  # ADDED: Black Box telemetry
    MetaLearningClientMixin,  # [PHASE 2] Meta-Learning integration
    GoldenContextMixin,  # [COGNITIVE HARDENING] Anti-Context Drift
    RuntimeSafetyMixin,  # [OPERATIONAL SAFETY] Process lifecycle management
):
    """
    Sovereign Single Source of Truth (SSOT) Root.
    HARDENED: SSOT Root with comprehensive type safety and security validation.
    """

    project_root: Path = field(default_factory=Path.cwd)
    _initialized: bool = field(default=False, init=False)
    _security_validator: Any = field(default=None, init=False)

    def __post_init__(self) -> None:
        """
        Initialize sovereign capabilities with Hardening AND Integrity Lock.
        """
        # Initialize infrastructure first (calls super().__init__() internally)
        try:
            super().__post_init__()
        except AttributeError:
            # Some mixins don't have __post_init__, that's okay
            pass

        # 1. THE IMMUTABLE LOCK CHECK
        # If this fails, the agent refuses to exist.
        try:
            CoreIntegrityVerifier.verify_core_integrity()
        except Exception as e:
            # Panic mode: Log fatal error and die
            emergency_shutdown(f"CORE INTEGRITY COMPROMISED. TERMINATING AGENT. {e}")

        # 2. Security Validation
        self._security_hardening_validation()

        # 3. Telemetry Signal
        self.log_sovereign_event(
            "BOOT",
            {"status": "initialized", "mode": "hardened", "integrity_verified": True},
        )

        self._initialized = True

    def _security_hardening_validation(self) -> None:
        """
        Validate security constraints during initialization.
        HARDENED: Prevents insecure configurations and validates project structure.
        """
        try:
            # Validate project root is within allowed boundaries
            if not self._is_safe_path(self.project_root):
                raise ConfigurationError(f"Unsafe project root: {self.project_root}")

            # Validate required directories exist and are secure
            required_dirs = ["agentic_core"]
            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if dir_path.exists() and not self._is_safe_directory(dir_path):
                    raise ConfigurationError(f"Unsafe directory detected: {dir_path}")

        except Exception as e:
            raise ConfigurationError(f"Security validation failed: {str(e)}") from e

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe for access."""
        try:
            path.resolve().relative_to(Path.cwd().resolve())
            return True
        except ValueError:
            return False

    def _is_safe_directory(self, dir_path: Path) -> bool:
        """Check if directory is safe for modification."""
        return self._is_safe_path(dir_path) and dir_path.is_dir()

    def get_sovereign_capabilities(self) -> dict[str, Any]:
        """
        Get comprehensive list of sovereign capabilities.
        HARDENED: Returns capability map with security metadata.
        """
        if not self._initialized:
            raise SovereignError("SovereignBaseAgent not properly initialized")

        return {
            "healing": hasattr(self, "heal_repository"),
            "validation": hasattr(self, "validate_repository"),
            "testing": hasattr(self, "run_subatomic_tests"),
            "meta_learning": hasattr(self, "ml_recall_healing_pattern"),
            "security_validated": True,
            "mro_hardened": True,
            "project_root": str(self.project_root),
        }

    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function."""
        raise NotImplementedError("Subclasses must implement execute()")

    def get_state(self, key: str) -> Any | None:
        """Get state value."""
        return getattr(self, "_state", {}).get(key)

    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        if not hasattr(self, "_state"):
            self._state = {}
        self._state[key] = value

    def get_authority_level(self) -> str:
        """Get the agent's authority level."""
        return getattr(self, "_authority_level", "standard")

    def elevate_authority(self, level: str) -> None:
        """Elevate the agent's authority level."""
        self._authority_level = level
        logger.info(f"Authority elevated to: {level}")

    def log_info(self, message: str) -> None:
        """Log an info message."""
        logger.info(f"[{getattr(self, 'name', 'SovereignAgent')}] {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        logger.warning(f"[{getattr(self, 'name', 'SovereignAgent')}] {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logger.error(f"[{getattr(self, 'name', 'SovereignAgent')}] {message}")

    def log_feedback(
        self,
        workflow_id: str,
        action: str,
        status: str,
        details: dict[str, Any] = None,
    ) -> None:
        """Log feedback for a workflow action."""
        logger.info(
            f"[{getattr(self, 'name', 'SovereignAgent')}] Workflow {workflow_id}: "
            f"{action} - {status} - {details or {}}",
        )

    def heal(self, violation: dict[str, Any], **kwargs) -> dict[str, Any]:
        """
        Enhanced healing interface with meta-learning integration.

        Args:
            violation: Dictionary detailing the detected violation.
            **kwargs: Future-proofing for protocol expansions.

        Returns:
            Dict containing status and metadata with meta-learning enhancement.
        """
        # Use meta-learning enhanced heal if available
        if hasattr(self, "ml_enhanced_heal") and hasattr(self, "_do_heal"):
            return self.ml_enhanced_heal(violation, self._do_heal, **kwargs)

        # Fallback to default implementation
        return {
            "status": "skipped",
            "reason": "default_base_implementation",
            "handler": self.__class__.__name__,
            "violation_id": violation.get("id", "unknown"),
        }

    def _do_heal(self, violation: dict[str, Any], **kwargs) -> dict[str, Any]:
        """
                Actual healing implementation to be called by meta-learning enhanced heal.

                Subclasses should override this method instead of heal() to benefit
                from meta-learning capabilities.
        from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

                Args:
                    violation: Dictionary detailing the detected violation.
                    **kwargs: Additional arguments for healing.

                Returns:
                    Dict containing healing result.
        """
        return {
            "status": "skipped",
            "reason": "default_base_implementation",
            "handler": self.__class__.__name__,
            "violation_id": violation.get("id", "unknown"),
        }

    # =========================================================================
    # COGNITIVE ENDURANCE INFRASTRUCTURE (Feb 2026)
    # Landmine #3 & #4 Prevention: Context Drift and Token Overload
    # =========================================================================

    def sanitize_output(self, output: str, max_chars: int = 2000) -> str:
        """
        Sanitize tool output to prevent token overload.

        Wraps the telemetry_sanitizer.sanitize_tool_output function for
        convenient access from agent instances.

        Args:
            output: The raw tool output string.
            max_chars: Maximum allowed characters before pruning.

        Returns:
            Sanitized output string, pruned if necessary.
        """
        return sanitize_tool_output(output, max_chars=max_chars)

    def prepare_messages_for_llm(
        self,
        messages: list[dict[str, Any]],
        inject_context: bool = True,
        context_threshold: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Prepare messages for LLM call with cognitive hardening.

        This method should be called before any LLM invocation to:
        1. Optionally inject golden context (anti-drift)
        2. Future: Apply other cognitive safeguards

        Args:
            messages: The current message list.
            inject_context: Whether to inject golden context.
            context_threshold: Message count threshold for injection.

        Returns:
            Prepared message list ready for LLM call.
        """
        if inject_context and self.should_inject_golden_context(messages, context_threshold):
            return self.inject_golden_context(messages)
        return messages


__all__ = ["SovereignBaseAgent", "sanitize_tool_output", "RuntimeSafetyMixin"]
