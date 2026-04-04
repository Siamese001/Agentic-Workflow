"""Code Detector Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_detector_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
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
        warnings.warn("Detection is deprecated. Use code_detector_util.Detection instead.", DeprecationWarning)
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
