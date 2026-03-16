"""
AppBase - Common base class for both LIC and RG applications.

Provides unified inheritance hierarchy for apps_lic and apps_rg.
Phase 2A.3 - Base Class Standardization

NOTE: This is a CLASS (blueprint/template), NOT an active worker agent.
Zero-Ambiguity Standard: Removed "Agent" suffix to clarify its role.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "app_base_util", "p0_governance")
_emit_reads_policy_state("p0", "app_base_util", "policy_binding")
_emit_snapshots_state("p0", "app_base_util", "state_snapshot")
emit_replay_key("p0", "app_base_util")
emit_determinism_digest("p0", "app_base_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

try:
    from agentic_core.interfaces.mixins import MetaLearningMixin
except ImportError:

    class MetaLearningMixin:
        """Fallback MetaLearningMixin when not available."""

        pass


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:

    class HealerMixin:
        """Fallback HealerMixin when not available."""

        pass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class AppBase(MetaLearningMixin, SovereignBaseAgent, HealerMixin):
    """
    AppBase: Common foundation for all application-level agents.

    Provides unified base class for both apps_lic (LinkedIn Outreach) and
    apps_rg (Resume Generation) applications, ensuring consistent behavior
    and capabilities across all application agents.

    Architecture:
        - Inherits from SovereignBaseAgent for core sovereignty
        - Includes MetaLearningMixin for learning capabilities
        - Includes HealerMixin for self-healing capabilities

    NOTE: This is a CLASS (blueprint), NOT an active worker agent.
    The "Agent" suffix was removed per Zero-Ambiguity Naming Standard.
    """

    domain_root: Path = field(default_factory=lambda: Path("apps"))
    _app_version: Final[str] = "2.5.0-unified"
    _namespace: str = field(default="apps", init=False)
    _similarity_threshold: float = field(default=0.85, init=False)
    _resource_prefix: str = field(default="app", init=False)

    def __post_init__(self) -> None:
        """
        Initialize app-level capabilities after core hardening.
        """
        super().__post_init__()
        if not self.domain_root.exists():
            self.domain_root.mkdir(parents=True, exist_ok=True)

    def get_app_context(self) -> dict[str, Any]:
        """
        Return app-specific context wrapper.

        Returns:
            Dictionary with app context information
        """
        return {
            "domain": str(self.domain_root),
            "version": self._app_version,
            "namespace": self._namespace,
            "capabilities": self.get_sovereign_capabilities(),
            "resource_prefix": self._resource_prefix,
        }

    def get_resource_key(self, key: str) -> str:
        """
        Generate namespaced resource key for isolation.

        Args:
            key: Base resource key

        Returns:
            Namespaced resource key
        """
        return f"{self._resource_prefix}:{self._namespace}:{key}"

    def validate_app_config(self) -> bool:
        """
        Validate application-specific configuration.

        Returns:
            True if configuration is valid
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AppBase.validate_app_config")

        # guardian: allow-config-with-logic
        if not self.domain_root.exists():
            return False
        # guardian: allow-config-with-logic
        if not self._namespace or self._namespace == "":
            return False
        return True

    def get_app_metadata(self) -> dict[str, Any]:
        """
        Get application metadata for telemetry and monitoring.

        Returns:
            Dictionary with app metadata
        """
        return {
            "agent_class": self.__class__.__name__,
            "domain": str(self.domain_root),
            "namespace": self._namespace,
            "version": self._app_version,
            "similarity_threshold": self._similarity_threshold,
        }

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
