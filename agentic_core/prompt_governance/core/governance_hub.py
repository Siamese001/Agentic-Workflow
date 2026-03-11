# Governance Orchestrator
# Strategy: Central hub for all safety checks

from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.prompt_governance.security.detectors.pii_scrubber import PIIScrubber


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class GovernanceHub:
    """
    Main entry point for safety validation.
    Usage: hub.validate_input(user_prompt)
    """

    def __init__(self):
        self.pii_scrubber = PIIScrubber()
        self.injection_detector = InjectionDetector()

    def validate_input(self, text: str) -> str:
        """
        Runs injection checks first, then scrubs PII.
        Returns sanitized text.
        """
        # 1. Security Check (Blocking)
        self.injection_detector.scan(text)

        # 2. Privacy Scrubbing (Mutating)
        safe_text = self.pii_scrubber.scrub(text)

        return safe_text

    def validate_output(self, text: str) -> str:
        """
        Scans LLM output for data leaks (PII).
        """
        # We also scrub PII from model outputs to prevent leaks
        return self.pii_scrubber.scrub(text)
