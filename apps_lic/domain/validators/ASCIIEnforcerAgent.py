from dataclasses import dataclass
"""
ASCIIEnforcerAgent - Extracted for one-class-per-file pattern.

Originally from: ContentCleanlinessValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

@dataclass
class ASCIIEnforcerAgent(HealerMixin, MCPHardenedMixin):
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
        """Replace Unicode with ASCII equivalents"""
        for unicode_char, ascii_replacement in self.UNICODE_REPLACEMENTS.items():
            text = text.replace(unicode_char, ascii_replacement)
        
        # Remove any remaining non-ASCII
        text = text.encode("ascii", "ignore").decode("ascii")
        
        return text
    
    def validate(self, text: str) -> Tuple[bool, str]:
        """Validate text is ASCII-only"""
        try:
            text.encode("ascii")
            return True, ""
        except UnicodeEncodeError as e:
            non_ascii_chars = [c for c in text if ord(c) > 127]
            return False, f"Non-ASCII characters: {set(non_ascii_chars[:5])}"

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
