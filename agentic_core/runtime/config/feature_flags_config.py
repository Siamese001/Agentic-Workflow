"""
Feature Flag Manager for controlled rollout of new capabilities.

Provides centralized feature flag management with environment variable support
and graceful degradation patterns.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "feature_flags_config", "p0_governance")
_emit_reads_policy_state("p0", "feature_flags_config", "policy_binding")
_emit_snapshots_state("p0", "feature_flags_config", "state_snapshot")
emit_replay_key("p0", "feature_flags_config")
emit_determinism_digest("p0", "feature_flags_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


@dataclass
class FeatureFlag:
    """Feature flag configuration."""

    name: str
    default: bool = False
    description: str = ""
    required_for_healing: bool = False


class FeatureFlagManager:
    """Centralized feature flag management.

    Flags can be controlled via environment variables.
    All flags default to False for safe rollout.
    """

    FLAGS: dict[str, FeatureFlag] = {
        "ENABLE_META_LEARNING": FeatureFlag(
            name="ENABLE_META_LEARNING",
            default=False,
            description="Enable meta-learning recall-or-execute pattern",
            required_for_healing=False,
        ),
        "ENABLE_AUDIT_TRAIL": FeatureFlag(
            name="ENABLE_AUDIT_TRAIL",
            default=False,
            description="Enable cryptographic audit trail logging",
            required_for_healing=True,
        ),
        "ENABLE_COST_GUARDRAIL": FeatureFlag(
            name="ENABLE_COST_GUARDRAIL",
            default=False,
            description="Enable cost monitoring and budget enforcement",
            required_for_healing=True,
        ),
        "ENABLE_HITL_WORKFLOW": FeatureFlag(
            name="ENABLE_HITL_WORKFLOW",
            default=False,
            description="Enable human-in-the-loop approval workflow",
            required_for_healing=True,
        ),
        "ENABLE_VERIFICATION_GATE": FeatureFlag(
            name="ENABLE_VERIFICATION_GATE",
            default=False,
            description="Enable verification gate for healing operations",
            required_for_healing=True,
        ),
        "ENABLE_DETECTION_SIGNAL": FeatureFlag(
            name="ENABLE_DETECTION_SIGNAL",
            default=False,
            description="Enable structured detection signal emission",
            required_for_healing=False,
        ),
    }

    _override_cache: dict[str, bool] = {}

    @classmethod
    def is_enabled(cls, flag_name: str, agent_name: str | None = None) -> bool:
        """Check if feature flag is enabled.

        Args:
            flag_name: Name of the feature flag
            agent_name: Optional agent name for logging

        Returns:
            True if flag is enabled, False otherwise
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FeatureFlagManager.is_enabled")

        # Check override cache first
        if flag_name in cls._override_cache:
            return cls._override_cache[flag_name]

        flag = cls.FLAGS.get(flag_name)
        if flag is None:
            logger.warning(f"Unknown feature flag: {flag_name}")
            return False

        # Check environment variable
        env_value = os.getenv(flag_name, str(flag.default)).lower()
        enabled = env_value in ("true", "1", "yes", "on")

        # Debug logging
        if agent_name:
            logger.debug(f"[FLAG] {flag_name}={enabled} for {agent_name}")

        return enabled

    @classmethod
    def set_override(cls, flag_name: str, value: bool) -> None:
        """Set a runtime override for a flag.

        Useful for testing and gradual rollout.

        Args:
            flag_name: Name of the flag
            value: Override value
        """
        cls._override_cache[flag_name] = value
        logger.info(f"[FLAG] Override set: {flag_name}={value}")

    @classmethod
    def clear_override(cls, flag_name: str) -> None:
        """Clear a runtime override.

        Args:
            flag_name: Name of the flag to clear
        """
        if flag_name in cls._override_cache:
            del cls._override_cache[flag_name]
            logger.info(f"[FLAG] Override cleared: {flag_name}")

    @classmethod
    def clear_all_overrides(cls) -> None:
        """Clear all runtime overrides."""
        cls._override_cache.clear()
        logger.info("[FLAG] All overrides cleared")

    @classmethod
    def required_for_healing(cls, flag_name: str) -> bool:
        """Check if flag is required for healing operations.

        Args:
            flag_name: Name of the flag

        Returns:
            True if required for healing
        """
        flag = cls.FLAGS.get(flag_name)
        return flag.required_for_healing if flag else False

    @classmethod
    def get_all_flags(cls) -> dict[str, bool]:
        """Get current state of all flags.

        Returns:
            Dictionary of flag names to their current values
        """
        return {name: cls.is_enabled(name) for name in cls.FLAGS.keys()}

    @classmethod
    def get_healing_required_flags(cls) -> dict[str, bool]:
        """Get flags required for healing operations.

        Returns:
            Dictionary of healing-required flag names to their values
        """
        return {name: cls.is_enabled(name) for name, flag in cls.FLAGS.items() if flag.required_for_healing}

    @classmethod
    def validate_healing_flags(cls, agent_name: str) -> tuple[bool, list[str]]:
        """Validate all healing-required flags are enabled.

        Args:
            agent_name: Name of the agent for logging

        Returns:
            Tuple of (all_enabled, list_of_disabled_flags)
        """
        disabled = []
        for name, flag in cls.FLAGS.items():
            if flag.required_for_healing and not cls.is_enabled(name, agent_name):
                disabled.append(name)

        if disabled:
            logger.warning(f"[FLAG] Agent {agent_name} missing healing flags: {disabled}")

        return len(disabled) == 0, disabled

    @classmethod
    def register_flag(cls, flag: FeatureFlag) -> None:
        """Register a new feature flag.

        Args:
            flag: FeatureFlag to register
        """
        cls.FLAGS[flag.name] = flag
        logger.info(f"[FLAG] Registered: {flag.name}")

    @classmethod
    def get_flag_info(cls, flag_name: str) -> dict[str, Any] | None:
        """Get information about a flag.

        Args:
            flag_name: Name of the flag

        Returns:
            Dictionary with flag info or None if not found
        """
        flag = cls.FLAGS.get(flag_name)
        if flag is None:
            return None

        return {
            "name": flag.name,
            "default": flag.default,
            "description": flag.description,
            "required_for_healing": flag.required_for_healing,
            "current_value": cls.is_enabled(flag_name),
            "has_override": flag_name in cls._override_cache,
        }
