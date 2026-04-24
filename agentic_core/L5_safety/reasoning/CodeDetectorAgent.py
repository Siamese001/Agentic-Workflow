"""Code Detector Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_detector_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.3 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling = consumer migration window)
Category: deprecated-delegating-shim
Canonical replacement: agentic_core.L5_safety.utils.code_detector_util
Consumers at authorization (2):
  - agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py (dispatch-dict value in _get_classified_agents)
  - ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py (rename-mapping data)

Policy interpretation (pragmatic constitutional \u00a73): This agent is
self-documented DEPRECATED with an explicit canonical replacement. The 90-day
cooling period serves as the formal consumer migration window. W6 archive
sweep on or after 2026-07-23 will verify zero live consumers via regex grep
BEFORE physical archive. If consumers remain, W6 blocks the archive and
schedules per-consumer follow-up; authorization is NOT revoked but the
archive action is deferred.

Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__CodeDetectorAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w_final_CodeDetectorAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_detector_util import (
    CodeDetector as _CodeDetector,
)
from agentic_core.L5_safety.utils.code_detector_util import (
    Detection as _Detection,
)


class Detection:
    """DEPRECATED: Use code_detector_util.Detection instead."""

    def __init__(self, **kwargs):
        warnings.warn(
            "Detection is deprecated. Use code_detector_util.Detection instead.", DeprecationWarning
        )
        self._impl = _Detection(**kwargs)


class CodeDetectorAgent(SovereignBaseAgent):
    """
    DEPRECATED: Code Detector Agent - now delegates to code_detector_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_detector_util directly.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize CodeDetectorAgent (deprecated, use code_detector_util instead)."""
        super().__init__(name="CodeDetectorAgent", layer="L5")

        warnings.warn(
            "CodeDetectorAgent is deprecated. Use agentic_core.L5_safety.utils.code_detector_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._detector = _CodeDetector(project_root or Path.cwd())

    def run_full_scan(self) -> list[Any]:
        """Run a full code quality scan."""
        return self._detector.run_full_scan()

    def detect_dead_code(self, file_path: Path) -> list[Any]:
        """Detect dead code in a file."""
        return self._detector.detect_dead_code(file_path)
