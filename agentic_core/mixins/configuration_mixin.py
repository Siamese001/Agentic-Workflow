"""
ConfigMixin - Unified configuration Access for Agents

[PHASE 6 MIGRATION] Provides access to SovereignConfigManager.
"""

from agentic_core.config.core.sovereign_config import (
    SovereignConfigManager,
    get_sovereign_config,
)


class ConfigMixin:
    """
    Mixin providing typed configuration access.

    Usage:
        class MyAgent(ConfigMixin):
            def run(self):
                limit = self.config.max_audit_log_size
    """

    _config_manager: SovereignConfigManager | None = None

    @property
    def config(self) -> SovereignConfigManager:
        """Lazy-load config singleton."""
        if self._config_manager is None:
            self._config_manager = get_sovereign_config()
        return self._config_manager
