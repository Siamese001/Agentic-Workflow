"""Bootstrap Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.bootstrap_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.1 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from agentic_core.L5_safety.reasoning.BootstrapAgent import` and `import agentic_core.L5_safety.reasoning.BootstrapAgent` across live code,
excluding self and archives/ paths — zero hits).
Unique logic: none (pure delegation to agentic_core.L5_safety.utils.bootstrap_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__BootstrapAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_BootstrapAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.L0RoutingBase import L0RoutingBase
from agentic_core.L5_safety.utils.bootstrap_util import (
    heal_bootstrap_issues as _heal_bootstrap_issues,
)
from agentic_core.L5_safety.utils.bootstrap_util import (
    run_bootstrap as _run_bootstrap,
)
from agentic_core.L5_safety.utils.bootstrap_util import (
    verify_redis_connection as _verify_redis_connection,
)


class BootstrapAgent(L0RoutingBase):
    """
    DEPRECATED: Bootstrap Agent - now delegates to bootstrap_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.bootstrap_util directly.
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize BootstrapAgent (deprecated, use bootstrap_util instead)."""
        self.project_root = project_root.resolve()
        super().__init__()

        warnings.warn(
            "BootstrapAgent is deprecated. Use agentic_core.L5_safety.utils.bootstrap_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def _verify_redis_connection(self) -> bool:
        """Verify Redis connection."""
        return _verify_redis_connection()

    def run_bootstrap(self) -> bool:
        """Run bootstrap verification."""
        print("[BOOT] Verifying Sovereign Systems...")
        result = _run_bootstrap(self.project_root)
        return result.redis_connected

    def heal_repository(self, target_path: str | None = None, dry_run: bool = False) -> dict[str, Any]:
        """Heal bootstrap configuration."""
        return _heal_bootstrap_issues(self.project_root, target_path)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations."""
        file_path = violation.get("file") or violation.get("file_path")
        try:
            result = self.heal_repository(target_path=file_path)
            return {
                "status": "success" if len(result.get("violations_fixed", [])) > 0 else "skipped",
                "details": f"BootstrapAgent healed {len(result.get('violations_fixed', []))} violations",
                "artifacts": [file_path] if file_path else [],
                "errors": result.get("errors", []),
            }
        except (RuntimeError, OSError) as e:
            return {
                "status": "failed",
                "details": f"BootstrapAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
