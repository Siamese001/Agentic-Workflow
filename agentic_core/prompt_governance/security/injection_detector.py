# Prompt Injection Heuristics
# Strategy: Keyword blocking (heuristic) for speed. Phase 5 adds model-based checks.

import logging

from agentic_core.prompt_governance.security.normalization_util import normalize_and_decode
from agentic_core.runtime.exceptions.sovereign_errors import SecurityViolationError

Logger = logging.getLogger(__name__)


class InjectionDetector:
    """
    Scans text for adversarial patterns.
    """

    # Common jailbreak phrases (lowercase for normalization)
    BLOCKLIST = [
        "ignore previous instructions",
        "ignore all prior instructions",
        "system override",
        "dan mode",
        "developer mode on",
        "act as an unrestricted",
    ]

    def scan(self, text: str) -> bool:
        """
        Checks for injection patterns.
        Raises SecurityViolationError if found.
        Returns True if safe.

        Scans both the original (lowered) text and the fully normalized+decoded
        form so that obfuscated payloads (Unicode tricks, URL-encoding, Base64,
        leetspeak) are detected.
        """
        if not text:
            return True

        # Phase 1: scan original (backwards-compatible path)
        original_lower = text.lower()
        self._check_blocklist(original_lower)

        # Phase 2: scan normalized+decoded form
        normalized_text, meta = normalize_and_decode(text)
        if normalized_text != original_lower:
            self._check_blocklist(normalized_text)

        return True

    def _check_blocklist(self, text: str) -> None:
        """Raise SecurityViolationError if any blocklist phrase is found in *text*."""
        for phrase in self.BLOCKLIST:
            if phrase in text:
                Logger.warning("Injection signature matched: sig_id=%s", phrase[:40])
                raise SecurityViolationError(
                    message=f"Detected potential prompt injection (sig_id='{phrase[:40]}')",
                    violation_type="PROMPT_INJECTION",
                )
