from __future__ import annotations

"""
BootstrapAgent: Sovereign Boot Integrity.
[PHASE 18 REFACTOR] Force Clean.
"""
from dataclasses import dataclass
from pathlib import Path

from agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent import L0MaintenanceBaseAgent
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import subatomic_testing_mixin


@dataclass
class BootstrapAgent(SubatomicTestingMixin, L0MaintenanceBaseAgent):
    """
    Autonomous boot integrity agent - Phase 21.1 Normalized.
    Inherits from L0MaintenanceBaseAgent which inherits from SovereignBaseAgent.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        super().__init__()

    def _verify_redis_connection(self) -> bool:
        try:
            self.cache_set("boot_check", "ok", ttl=5)
            return self.cache_get("boot_check") == "ok"
        except Exception:
            return False

    def run_bootstrap(self) -> bool:
        print("[BOOT] Verifying Sovereign Systems...")
        return self._verify_redis_connection()
