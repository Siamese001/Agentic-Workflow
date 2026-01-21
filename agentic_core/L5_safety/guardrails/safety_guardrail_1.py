from __future__ import annotations

"""
Safety Guardrail - L5 Safety Layer

Verifies code changes are constructive rather than destructive.
Provides special whitelist for ATOMIC_FISSION mode where mass deletion
is expected (monolith → facade conversion).

Strategy:
- HEAL mode: Prevents >110 line deletions
- ATOMIC_FISSION mode: Allows facade pattern (large → small file)
- Ensures zero-loss transitions during fission
"""
import logging
from dataclasses import dataclass
from typing import Any

Logger: Any = logging.getLogger(__name__)

@dataclass
class SafetyResult:
    """Result of safety verification."""
    is_safe: bool
    message: str
    delta: int
    mode: str

class SafetyGuardrail:
    """
    L5 Safety Layer: Decides if code change is constructive or destructive.

    Modes:
    - HEAL: Standard healing with 110-line deletion limit
    - ATOMIC_FISSION: Allows facade pattern (monolith → small file)

    Strategy:
    - Protects against accidental mass deletions
    - Whitelists intentional fission transformations
    - Ensures backward compatibility preservation
    """

    def __init__(self, deletion_limit: int=110, facade_size_threshold: int=50):
        """
        Initialize Safety Guardrail.

        Args:
            deletion_limit: Max lines that can be deleted in HEAL mode
            facade_size_threshold: Typical facade file size
        """
        self.deletion_limit = deletion_limit
        self.facade_size_threshold = facade_size_threshold

    def verify_change(self, original_lines: list[str], new_lines: list[str], mode: str='HEAL') -> tuple[bool, str]:
        """
        L5 Safety: Decides if a code change is constructive or destructive.

        Args:
            original_lines: Original file lines
            new_lines: New file lines after modification
            mode: "HEAL" or "ATOMIC_FISSION"

        Returns:
            Tuple of (is_safe, message)
        """
        delta: Any = abs(len(original_lines) - len(new_lines))
        if mode == 'ATOMIC_FISSION':
            if len(new_lines) < self.facade_size_threshold:
                Logger.info(f'[OK] Fission Whitelist: Monolith converted to Facade ({len(new_lines)} lines)')
                return (True, f'Fission Whitelist: Monolith converted to Facade ({len(new_lines)} lines).')
            Logger.info('[OK] Fission Whitelist: Multi-file distribution active')
            return (True, 'Fission Whitelist: Multi-file distribution active.')
        if delta > self.deletion_limit:
            Logger.error(f'[X] Safety Violation: Mass deletion detected ({delta} lines > {self.deletion_limit} limit)')
            return (False, f'Safety Violation: Mass deletion detected ({delta} lines).')
        Logger.info(f'[OK] Safety Pass: {delta} lines changed (within {self.deletion_limit} limit)')
        return (True, 'Safety Pass.')

    def verify_change_detailed(self, original_lines: list[str], new_lines: list[str], mode: str='HEAL') -> SafetyResult:
        """
        Detailed safety verification with full result object.

        Args:
            original_lines: Original file lines
            new_lines: New file lines after modification
            mode: "HEAL" or "ATOMIC_FISSION"

        Returns:
            SafetyResult with detailed information
        """
        delta: Any = abs(len(original_lines) - len(new_lines))
        if mode == 'ATOMIC_FISSION':
            if len(new_lines) < self.facade_size_threshold:
                return SafetyResult(is_safe=True, message=f'Fission Whitelist: Monolith converted to Facade ({len(new_lines)} lines)', delta=delta, mode=mode)
            return SafetyResult(is_safe=True, message='Fission Whitelist: Multi-file distribution active', delta=delta, mode=mode)
        if delta > self.deletion_limit:
            return SafetyResult(is_safe=False, message=f'Safety Violation: Mass deletion detected ({delta} lines)', delta=delta, mode=mode)
        return SafetyResult(is_safe=True, message='Safety Pass', delta=delta, mode=mode)

    def verify_fission_output(self, original_file: str, new_files: dict) -> tuple[bool, str]:
        """
        Verify fission output maintains total line count.

        Args:
            original_file: Path to original monolithic file
            new_files: Dictionary of new file paths to content

        Returns:
            Tuple of (is_safe, message)
        """
        try:
            with open(original_file, encoding='utf-8') as f:
                original_line_count: Any = len(f.readlines())
            new_total_lines: Any = sum(len(content.splitlines()) for content in new_files.values())
            variance: Any = abs(original_line_count - new_total_lines) / original_line_count
            if variance > 0.05:
                Logger.warning(f'[!]  Line count variance: {variance:.1%} (original: {original_line_count}, new: {new_total_lines})')
                return (False, f'Line count variance too high: {variance:.1%} (expected ±5%)')
            Logger.info(f'[OK] Fission output verified: {original_line_count} → {new_total_lines} lines ({variance:.1%} variance)')
            return (True, f'Fission output verified: {original_line_count} → {new_total_lines} lines')
        except Exception as e:
            Logger.error(f'[X] Failed to verify fission output: {e}')
            return (False, f'Verification failed: {e}')

def get_safety_guardrail() -> SafetyGuardrail:
    """
    Factory function to create SafetyGuardrail instance.

    Returns:
        SafetyGuardrail instance
    """
    return SafetyGuardrail()
