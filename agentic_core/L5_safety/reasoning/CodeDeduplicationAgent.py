"""Code Deduplication Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_deduplication_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.1 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from agentic_core.L5_safety.reasoning.CodeDeduplicationAgent import` and `import agentic_core.L5_safety.reasoning.CodeDeduplicationAgent` across live code,
excluding self and archives/ paths — zero hits).
Unique logic: none (pure delegation to agentic_core.L5_safety.utils.code_deduplication_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__CodeDeduplicationAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_CodeDeduplicationAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_deduplication_util import (
    CodeDuplicateDetector as _CodeDuplicateDetector,
)


class CodeDeduplicationAgent(SovereignBaseAgent):
    """
    DEPRECATED: Code Deduplication Agent - now delegates to code_deduplication_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_deduplication_util directly.
    """

    _cache_prefix: str = "code_dedup"
    _namespace: str = "l2_fingerprints"

    def __init__(self, similarity_threshold: float = 1.0, min_lines: int = 8) -> None:
        """Initialize CodeDeduplicationAgent (deprecated, use code_deduplication_util instead)."""
        super().__init__(name="CodeDeduplicationAgent", layer="L5")

        warnings.warn(
            "CodeDeduplicationAgent is deprecated. Use agentic_core.L5_safety.utils.code_deduplication_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.threshold = 1.0
        self.min_lines = min_lines
        self._detector = _CodeDuplicateDetector(similarity_threshold, min_lines)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal deduplication violations."""
        violation_type = violation.get("type", "")
        file_path = violation.get("file")

        if not file_path:
            return {
                "status": "failed",
                "details": "No file path provided in violation",
                "artifacts": [],
                "errors": ["Missing file path"],
            }

        if "DUPLICATE" in violation_type or "IDENTICAL" in violation_type:
            return {
                "status": "manual_required",
                "details": "Code deduplication requires batch processing",
                "artifacts": [],
                "errors": [],
            }
        elif "FILENAME" in violation_type:
            return {
                "status": "manual_required",
                "details": "Filename duplicates require batch resolution",
                "artifacts": [],
                "errors": [],
            }
        else:
            return {
                "status": "skipped",
                "details": f"No healer available for violation type: {violation_type}",
                "artifacts": [],
                "errors": [],
            }

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L2 compliance."""
        assert hasattr(self, "threshold"), "Missing threshold"
        assert self.threshold == 1.0, "HARDENED: threshold must be 1.0 for SSOT"
        return True

    def scan_for_duplicates(self, python_files: list[str]) -> Any:
        """Scan for cross-file duplicates."""
        result = self._detector.scan_for_duplicates(python_files)

        # Copy results to agent state
        self.duplicate_groups = {k: v.members for k, v in result.duplicate_groups.items()}

        return result

    def _normalize_code(self, code: str) -> str:
        """Normalize for hashing."""
        from agentic_core.L5_safety.utils.code_deduplication_util import _normalize_code

        return _normalize_code(code)

    def _filter_code_lines(self, code: str) -> list[str]:
        """Filter code lines."""
        from agentic_core.L5_safety.utils.code_deduplication_util import _filter_code_lines

        return _filter_code_lines(code).splitlines()

    def _hash_block(self, code: str) -> str:
        """Generate AST fingerprint."""
        from agentic_core.L5_safety.utils.code_deduplication_util import _hash_block

        return _hash_block(code)

    def _block_similarity(self, norm_a: str, norm_b: str) -> float:
        """Conservative structural similarity."""
        from agentic_core.L5_safety.utils.code_deduplication_util import _block_similarity

        return _block_similarity(norm_a, norm_b)

    def _extract_functions_classes(self, file_path: Path) -> list[tuple[str, str, int]]:
        """Parse file and extract function/class bodies."""
        from agentic_core.L5_safety.utils.code_deduplication_util import _extract_functions_classes

        return _extract_functions_classes(file_path, self.min_lines)
