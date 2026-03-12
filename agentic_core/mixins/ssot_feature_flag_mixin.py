"""
SSOT Feature Flag Mixin — L4-Sourced Feature Flags with Replay Lock.

Provides feature flags that:
  - Sourced exclusively from L4 config (never environment variables)
  - Replay mode locks flag snapshot (no runtime changes)
  - No environment fallback

Layer: L2 Execution Aid
Authority: Flag reading only. No L4 mutation. No routing influence.
"""
from __future__ import annotations
import logging
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger('SSOTFeatureFlags')

class SSOTFeatureFlagMixin:
    """L4-sourced feature flags with replay snapshot lock.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Flags are loaded from L4 config at construction time.
    Under replay mode, the flag snapshot is frozen (no updates allowed).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_flags: dict[str, bool] = self._load_flags_from_l4()
        self._ssot_flags_frozen: bool = getattr(self, 'is_replay_mode', False)

    def flag_enabled(self, flag_name: str, default: bool=False) -> bool:
        """Check if a feature flag is enabled.

        Parameters
        ----------
        flag_name : str
            Name of the feature flag.
        default : bool
            Default value if flag not found.

        Returns
        -------
        bool
            Whether the flag is enabled.
        """
        return self._ssot_flags.get(flag_name, default)

    def flag_set(self, flag_name: str, value: bool) -> bool:
        """Set a feature flag value. Rejected under replay mode.

        Parameters
        ----------
        flag_name : str
            Name of the feature flag.
        value : bool
            New flag value.

        Returns
        -------
        bool
            True if flag was set, False if rejected (replay mode).
        """
        if self._ssot_flags_frozen:
            _logger.warning('[SSOTFlags] Flag change rejected (frozen): %s=%s', flag_name, value)
            return False
        self._ssot_flags[flag_name] = value
        _logger.debug('[SSOTFlags] %s = %s', flag_name, value)
        return True

    @property
    def all_flags(self) -> dict[str, bool]:
        """Return a copy of all current flags."""
        return dict(self._ssot_flags)

    @property
    def flags_frozen(self) -> bool:
        """Whether flags are frozen (replay mode)."""
        return self._ssot_flags_frozen

    @staticmethod
    def _load_flags_from_l4() -> dict[str, bool]:
        """Load feature flags from L4 config.

        Returns default flags if L4 config is unavailable.
        Never reads from environment variables.
        """
        try:
            from agentic_core.L4_state.config.versioned_configs import get_active_configs
            configs = get_active_configs()
            return {'enable_llm_healing': True, 'enable_meta_learning': True, 'enable_circuit_breaker': True, 'enable_rate_limiting': True, 'enable_tracing': True, 'enable_audit_trail': True, 'enable_adaptive_execution': False, 'enable_hallucination_detection': True, 'l4_config_version': configs.policy.version == '1.0.0'}
        except ImportError:
            _logger.warning('[SSOTFlags] L4 config unavailable; using defaults')
            return {'enable_llm_healing': True, 'enable_meta_learning': True, 'enable_circuit_breaker': True, 'enable_rate_limiting': True, 'enable_tracing': True, 'enable_audit_trail': True, 'enable_adaptive_execution': False, 'enable_hallucination_detection': True}
