"""
ASCIIEnforcerAgent - Extracted for one-class-per-file pattern.

Originally from: ContentCleanlinessValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


@dataclass
class ASCIIEnforcerAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Enforce ASCII-only characters for LinkedIn compatibility
    GAP 1.10 from v10.22
    """

    UNICODE_REPLACEMENTS = {
        "•": "-",
        "–": "-",
        "—": "-",
        """: '"',
        """: '"',
        "'": "'",
        "'": "'",
        "…": "...",
    }

    def enforce_ascii(self, text: str) -> str:
        """
        Replace Unicode characters with ASCII equivalents.

        Args:
            text: Input text potentially containing Unicode characters

        Returns:
            Text with Unicode replaced by ASCII equivalents
        """
        for unicode_char, ascii_replacement in self.UNICODE_REPLACEMENTS.items():
            text = text.replace(unicode_char, ascii_replacement)

        # Remove any remaining non-ASCII
        text = text.encode("ascii", "ignore").decode("ascii")

        return text

    def validate(self, text: str) -> tuple[bool, str]:
        """
        Validate that text contains only ASCII characters.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            text.encode("ascii")
            return True, ""
        except UnicodeEncodeError:
            non_ascii_chars = [c for c in text if ord(c) > 127]
            return False, f"Non-ASCII characters: {set(non_ascii_chars[:5])}"

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, int]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: bool = False, **kwargs) -> Dict[str, int]:
        """
        return super().heal_repository(dry_run, execute, **kwargs)
