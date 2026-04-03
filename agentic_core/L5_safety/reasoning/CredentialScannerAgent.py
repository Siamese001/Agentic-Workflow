"""Credential Scanner Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.credential_scanner_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.credential_scanner_util import (
    CredentialScanner as _CredentialScanner,
    CredentialMatch,
    CredentialScanResult,
)


class CredentialScannerAgent(SovereignBaseAgent):
    """
    DEPRECATED: Credential Scanner Agent - now delegates to credential_scanner_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.credential_scanner_util directly.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize CredentialScannerAgent (deprecated, use credential_scanner_util instead)."""
        super().__init__(name="CredentialScannerAgent", layer="L5")

        warnings.warn(
            "CredentialScannerAgent is deprecated. Use agentic_core.L5_safety.utils.credential_scanner_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._scanner = _CredentialScanner()
        self.matches: list[CredentialMatch] = []

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal credential violations."""
        file_path = violation.get("file")
        if not file_path:
            return {
                "status": "failed",
                "details": "No file path provided in violation",
                "artifacts": [],
                "errors": ["Missing file path"],
            }
        return {
            "status": "manual_required",
            "details": "CredentialScannerAgent requires manual review for healing",
            "artifacts": [],
            "errors": [],
        }

    def scan_for_credentials(
        self,
        target_path: Path | None = None,
        file_patterns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Scan for hardcoded credentials."""
        result = self._scanner.scan_for_credentials(target_path, file_patterns)
        self.matches = result.matches
        return result.to_dict()

    def _get_scannable_files(self, root_path: Path) -> list[Path]:
        """Get list of files to scan."""
        return self._scanner._get_scannable_files(root_path)

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file."""
        self._scanner._scan_file(file_path)

    def _is_false_positive(self, line: str, pattern_name: str) -> bool:
        """Check if match is false positive."""
        from agentic_core.L5_safety.utils.credential_scanner_util import _is_false_positive
        return _is_false_positive(line, pattern_name)

    def _generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics."""
        from agentic_core.L5_safety.utils.credential_scanner_util import _generate_summary
        return _generate_summary(self.matches)

    def _generate_recommendations(self) -> list[str]:
        """Generate security recommendations."""
        from agentic_core.L5_safety.utils.credential_scanner_util import _generate_recommendations
        return _generate_recommendations(self.matches)

    def _match_to_dict(self, match: CredentialMatch) -> dict[str, Any]:
        """Convert match to dictionary."""
        return match.to_dict()

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Scan repository for hardcoded credentials."""
        result = self.scan_for_credentials()
        violations_found = result.get("total_matches", 0)
        
        return {
            "violations_found": violations_found,
            "violations_fixed": 0,
            "errors": 0,
            "skipped": violations_found,
            "agent": "CredentialScannerAgent",
            "dry_run": dry_run,
            "note": "Credential violations require manual review",
        }
